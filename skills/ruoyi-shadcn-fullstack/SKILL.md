---
name: ruoyi-shadcn-fullstack
description: "Use when designing, scaffolding, or generating full-stack admin applications combining RuoYi backend standards (Spring Boot, MyBatis-Plus, MySQL, Redis, JWT/RBAC) with Shadcn Admin frontend standards (Vite, React 19, TypeScript, Tailwind CSS v4, TanStack Router & Table). Triggers on: '若依shadcn', '若依前端替换', '若依+react', 'ruoyi shadcn', '若依后端shadcn前端', '生成全栈后台', '若依接口对接shadcn', 'ruoyi-react-admin'."
---

# RuoYi + Shadcn Admin Full-Stack Skill

## Overview

This skill guides agents in generating and integrating **enterprise-grade full-stack admin systems** using:
- **Backend**: **RuoYi (若依)** architecture — Spring Boot (2.x/3.x) + MyBatis-Plus + MySQL + Redis + Spring Security RBAC.
- **Frontend**: **Shadcn Admin** architecture — Vite 8 + React 19 + TypeScript + Tailwind CSS v4 + Shadcn UI (New York style) + TanStack Router/Table/Query.

```
┌──────────────────────────────────────┐          HTTP / JSON API          ┌──────────────────────────────────────┐
│  Shadcn Admin Frontend (React 19)    │ ─────────────────────────────────> │     RuoYi Backend (Spring Boot)      │
│  - Tailwind v4 + Shadcn UI (Visual)  │                                    │  - Spring Security + JWT RBAC        │
│  - TanStack Table (Data grid)        │ <───────────────────────────────── │  - MyBatis-Plus + MySQL + Redis      │
│  - TanStack Query + Axios (Sync)     │   Authorization: Bearer <Token>    │  - Industrial Audit & Data Perms     │
└──────────────────────────────────────┘                                    └──────────────────────────────────────┘
```

---

## 5-Phase Development Workflow

```
① Database Schema ➔ ② RuoYi Backend API ➔ ③ Frontend Feature Scaffold ➔ ④ API Client Wiring ➔ ⑤ Verification
```

### Phase 1: Database Schema & RuoYi Audit Design
1. Every business table MUST include standard RuoYi audit columns:
   - `status` (`char(1) DEFAULT '0' COMMENT '状态（0正常 1停用）'`)
   - `del_flag` (`char(1) DEFAULT '0' COMMENT '删除标志（0代表存在 2代表删除）'`)
   - `create_by`, `create_time`, `update_by`, `update_time`, `remark`
2. **Deterministic Tool**: Run the bundled DDL generator to generate compliant SQL & menu inserts:
   ```bash
   python scripts/generate_ruoyi_ddl.py --table <table_name> --comment <table_comment> --module <module_name> --business <business_name>
   ```
3. Import the generated `.sql` into the local MySQL database (database name typically `ry-vue` or custom).

---

### Phase 2: RuoYi Spring Boot Backend Implementation
1. **Domain Entity**: Extend `BaseEntity` (see [references/ruoyi_backend_conventions.md](references/ruoyi_backend_conventions.md)).
2. **Controller Pattern**:
   - Paginated list: call `startPage()` before mapper query, return `getDataTable(list)`.
   - Single item query: return `AjaxResult.success(entity)`.
   - Insert/Update/Delete: annotate with `@Log` and `@PreAuthorize("@ss.hasPermi('module:business:add')")`, return `toAjax(rows)`.
3. **CORS Configuration**:
   - Ensure `ResourcesConfig.java` has a `CorsFilter` allowing `http://localhost:5173` (or configure Vite reverse proxy in Phase 4).

---

### Phase 3: Shadcn Admin Frontend Scaffolding
Organize every business module under `src/features/<feature-name>/`:

```text
src/features/<feature-name>/
├── api/
│   └── <feature>-api.ts          # TanStack Query useQuery & useMutation hooks
├── components/
│   ├── <feature>-columns.tsx     # TanStack Table column definitions
│   ├── <feature>-table.tsx       # Table wrapper (search, pagination, filters)
│   ├── <feature>-mutate-dialog.tsx # React Hook Form + Zod create/edit modal
│   └── <feature>-delete-dialog.tsx # AlertDialog for single/batch delete
├── data/
│   └── schema.ts                 # Zod validation schema + inferred TypeScript types
└── index.tsx                     # Main feature page export
```

*See [references/end_to_end_example.md](references/end_to_end_example.md) for full reference code.*

---

### Phase 4: API Client Wiring & Auth Integration
1. **Axios Client**:
   - Create or update `src/lib/api-client.ts` (see [references/shadcn_frontend_conventions.md](references/shadcn_frontend_conventions.md)).
   - Intercept requests to inject `Authorization: Bearer ${token}`.
   - Intercept responses: on `res.code === 401`, clear token cookies and redirect to `/sign-in`.
2. **Vite Reverse Proxy** (`vite.config.ts`):
   ```typescript
   server: {
     port: 5173,
     proxy: {
       '/dev-api': {
         target: 'http://localhost:8080',
         changeOrigin: true,
         rewrite: (path) => path.replace(/^\/dev-api/, ''),
       },
     },
   }
   ```
3. **Connect TanStack Table to RuoYi Pagination**:
   - RuoYi queries accept: `pageNum` (1-indexed) and `pageSize`.
   - RuoYi responses provide: `{ total: number, rows: T[] }`.
   - Map `table.pagination.pageIndex + 1` to `pageNum`.

---

### Phase 5: Verification & Testing Checklist
- [ ] **Redis running**: Execute `start-redis` in terminal (port 6379 listening).
- [ ] **MySQL connected**: RuoYi backend starts cleanly with exit code 0 on port 8080.
- [ ] **Frontend starts**: `pnpm run dev` starts cleanly on port 5173.
- [ ] **Auth Token handshake**: Login via `/sign-in` obtains RuoYi JWT and routes to dashboard.
- [ ] **CRUD operations**: Table fetches from MySQL, mutate dialog successfully inserts, delete removes row.

---

## Detailed References
- **RuoYi Backend Standards**: See [references/ruoyi_backend_conventions.md](references/ruoyi_backend_conventions.md).
- **Shadcn Frontend Integration**: See [references/shadcn_frontend_conventions.md](references/shadcn_frontend_conventions.md).
- **Complete End-to-End Example**: See [references/end_to_end_example.md](references/end_to_end_example.md).
