# Shadcn Admin Frontend Conventions & RuoYi API Integration

This guide details how to integrate the React 19 + Tailwind v4 + Shadcn UI frontend with a RuoYi backend.

---

## 1. Unified Axios Client for RuoYi (`src/lib/api-client.ts`)

Create `src/lib/api-client.ts` to automatically handle RuoYi's JWT authentication, response unwrapping, and 401 token expiry:

```typescript
import axios from 'axios'
import { toast } from 'sonner'
import { getCookie, removeCookie } from '@/lib/cookies'

const ACCESS_TOKEN_KEY = 'ruoyi_access_token'

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/dev-api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json;charset=utf-8',
  },
})

// Request Interceptor: Inject RuoYi JWT Token
apiClient.interceptors.request.use(
  (config) => {
    const rawToken = getCookie(ACCESS_TOKEN_KEY)
    if (rawToken) {
      try {
        const token = JSON.parse(rawToken)
        config.headers['Authorization'] = `Bearer ${token}`
      } catch {
        config.headers['Authorization'] = `Bearer ${rawToken}`
      }
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response Interceptor: Parse RuoYi { code, msg, rows/data }
apiClient.interceptors.response.use(
  (response) => {
    const res = response.data
    // Binary or file download
    if (response.request.responseType === 'blob' || response.request.responseType === 'arraybuffer') {
      return res
    }

    const code = res.code || 200
    const msg = res.msg || '未知业务错误'

    if (code === 401) {
      removeCookie(ACCESS_TOKEN_KEY)
      toast.error('登录状态已失效，请重新登录')
      window.location.href = '/sign-in'
      return Promise.reject(new Error(msg))
    }

    if (code !== 200) {
      toast.error(msg)
      return Promise.reject(new Error(msg))
    }

    return res
  },
  (error) => {
    let message = error.message
    if (error.response?.status === 401) {
      removeCookie(ACCESS_TOKEN_KEY)
      window.location.href = '/sign-in'
      message = '认证失效，请重新登录'
    } else if (error.response?.status === 403) {
      message = '抱歉，您没有访问该资源的权限'
    } else if (error.response?.status === 500) {
      message = '后端服务器异常，请联系管理员'
    }
    toast.error(message)
    return Promise.reject(error)
  }
)
```

---

## 2. Feature API Hooks using TanStack React Query

For every business feature (e.g., `villagers`), create `src/features/<feature>/api/<feature>-api.ts`:

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { toast } from 'sonner'
import { Villager, VillagerFormValues } from '../data/schema'

export interface PageParams {
  pageNum: number
  pageSize: number
  [key: string]: any
}

export interface RuoYiTableResponse<T> {
  total: number
  rows: T[]
  code: number
  msg: string
}

// 1. Fetch Paginated List
export function useVillagersQuery(params: PageParams) {
  return useQuery({
    queryKey: ['villagers', params],
    queryFn: async () => {
      const res = await apiClient.get<any, RuoYiTableResponse<Villager>>('/village/villager/list', {
        params,
      })
      return res
    },
    placeholderData: (prev) => prev,
  })
}

// 2. Create Villager Mutation
export function useCreateVillagerMutation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: VillagerFormValues) => apiClient.post('/village/villager', data),
    onSuccess: () => {
      toast.success('新增村民成功')
      queryClient.invalidateQueries({ queryKey: ['villagers'] })
    },
  })
}

// 3. Update Villager Mutation
export function useUpdateVillagerMutation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: VillagerFormValues & { id: number | string }) =>
      apiClient.put('/village/villager', data),
    onSuccess: () => {
      toast.success('更新村民成功')
      queryClient.invalidateQueries({ queryKey: ['villagers'] })
    },
  })
}

// 4. Delete Villager Mutation (supports batch comma-separated ids)
export function useDeleteVillagerMutation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (ids: (number | string)[]) =>
      apiClient.delete(`/village/villager/${ids.join(',')}`),
    onSuccess: () => {
      toast.success('删除成功')
      queryClient.invalidateQueries({ queryKey: ['villagers'] })
    },
  })
}
```

---

## 3. Standard Feature Directory Layout

```text
src/features/<feature-name>/
├── api/
│   └── <feature>-api.ts          # TanStack Query hooks (list, create, update, delete)
├── components/
│   ├── <feature>-columns.tsx     # TanStack Table column definitions
│   ├── <feature>-table.tsx       # Table wrapper with pagination & search
│   ├── <feature>-mutate-dialog.tsx # React Hook Form + Zod create/edit modal
│   └── <feature>-delete-dialog.tsx # Confirm modal for deletion
├── data/
│   └── schema.ts                 # Zod validation schema + TypeScript types
└── index.tsx                     # Main feature page export
```
