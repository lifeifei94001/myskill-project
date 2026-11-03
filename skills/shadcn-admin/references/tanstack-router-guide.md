# TanStack Router — File-Based Routing Guide for shadcn-admin

## Overview

shadcn-admin uses **TanStack Router** with file-based routing via `@tanstack/router-plugin/vite`. Routes are auto-generated from `src/routes/` into `src/routeTree.gen.ts`.

## Route File Conventions

| Pattern | Meaning | URL Segment |
|---|---|---|
| `__root.tsx` | Root layout | None |
| `index.tsx` | Index route | `/` of parent dir |
| `route.tsx` | Layout route | None (wraps children) |
| `$param.tsx` | Dynamic param | `/:param` |
| `(group)/` | Route group | None (organizational) |
| `_layout/` | Layout prefix | None (layout wrapper) |

## Creating a New Route

### Simple Page Route

```tsx
// src/routes/_authenticated/my-page/index.tsx
import { createFileRoute } from '@tanstack/react-router'
import MyPage from '@/features/my-feature'

export const Route = createFileRoute('/_authenticated/my-page/')({
  component: MyPage,
})
```

### Route with Data Loading

```tsx
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/_authenticated/products/')({
  loader: async ({ context: { queryClient } }) => {
    await queryClient.ensureQueryData(productsQueryOptions())
  },
  component: ProductsPage,
})
```

### Route with Search Params

```tsx
import { createFileRoute } from '@tanstack/react-router'
import { z } from 'zod'

const searchSchema = z.object({
  page: z.number().optional().default(1),
  search: z.string().optional(),
})

export const Route = createFileRoute('/_authenticated/items/')({
  validateSearch: searchSchema,
  component: ItemsPage,
})
```

### Layout Route

```tsx
// src/routes/_authenticated/settings/route.tsx
import { createFileRoute, Outlet } from '@tanstack/react-router'
import SettingsLayout from '@/features/settings'

export const Route = createFileRoute('/_authenticated/settings')({
  component: () => (
    <SettingsLayout>
      <Outlet />
    </SettingsLayout>
  ),
})
```

## Auth Guard Pattern

The `_authenticated` prefix creates a layout route that checks authentication:

```tsx
// src/routes/_authenticated/route.tsx
import { createFileRoute, redirect } from '@tanstack/react-router'
import { AuthenticatedLayout } from '@/components/layout/authenticated-layout'

export const Route = createFileRoute('/_authenticated')({
  beforeLoad: ({ context }) => {
    // Check auth state, redirect if not authenticated
    if (!isAuthenticated()) {
      throw redirect({ to: '/sign-in' })
    }
  },
  component: AuthenticatedLayout,
})
```

## Auto Code-Splitting

The Vite plugin config enables automatic code-splitting:

```ts
// vite.config.ts
tanstackRouter({
  target: 'react',
  autoCodeSplitting: true,  // Each route = separate chunk
})
```

## Route Tree Regeneration

The route tree is auto-generated. After adding/removing route files:
1. Restart the dev server (`pnpm run dev`)
2. Or run `pnpm exec tsr generate` manually
3. **Never manually edit** `src/routeTree.gen.ts`

## Navigation

```tsx
import { Link, useNavigate } from '@tanstack/react-router'

// Declarative
<Link to="/users" className="...">Users</Link>

// Imperative
const navigate = useNavigate()
navigate({ to: '/tasks' })
```
