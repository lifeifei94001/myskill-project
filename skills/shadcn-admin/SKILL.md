---
name: shadcn-admin
description: "Use when scaffolding, building, or customizing admin dashboard projects based on the shadcn-admin template (Vite + React + TypeScript + Tailwind CSS v4 + Shadcn UI + TanStack Router). Triggers on: 'admin dashboard', 'shadcn admin', 'shadcn-admin', 'dashboard template', 'admin panel', 'React admin', 'Vite admin', 'management dashboard', '管理后台', '仪表盘', '后台管理系统', 'admin scaffold'."
---

# Shadcn Admin — Dashboard Scaffold & Customization Skill

## Overview

This skill enables agents to scaffold, extend, and customize admin dashboard projects based on [satnaing/shadcn-admin](https://github.com/satnaing/shadcn-admin) — a production-ready admin dashboard UI built with **Vite + React 19 + TypeScript + Tailwind CSS v4 + Shadcn UI (New York style) + TanStack Router**.

**Source repo location:** `d:\APP\development_projects\shadcn-admin`

---

## Quick Reference

| Aspect | Detail |
|---|---|
| **Framework** | React 19 + TypeScript 6 |
| **Build Tool** | Vite 8 |
| **Styling** | Tailwind CSS v4 + Shadcn UI (New York style, `slate` base) |
| **Routing** | TanStack Router (file-based, auto code-splitting) |
| **State** | Zustand (client), TanStack React Query (server) |
| **Forms** | React Hook Form + Zod v4 |
| **Tables** | TanStack React Table v8 |
| **Charts** | Recharts v3 |
| **Icons** | Lucide React + Tabler Icons (brand only) |
| **Auth (partial)** | Clerk React |
| **Testing** | Vitest + Playwright (browser mode) |
| **Linting** | ESLint + Prettier |
| **Package Manager** | pnpm |

---

## Project Architecture

```
shadcn-admin/
├── public/images/                  # Static assets (favicon, preview images)
├── src/
│   ├── assets/                     # SVG logos, static brand assets
│   ├── components/                 # Shared & global components
│   │   ├── ui/                     # Shadcn UI primitives (30+ components)
│   │   ├── layout/                 # App shell: sidebar, header, nav, team-switcher
│   │   │   └── data/sidebar-data.ts  # ← Navigation menu config
│   │   ├── data-table/             # Reusable DataTable (pagination, filter, sort)
│   │   ├── command-menu.tsx        # Global ⌘K command palette
│   │   ├── confirm-dialog.tsx      # Reusable confirmation modal
│   │   └── ...                     # Theme switch, search, password input, etc.
│   ├── features/                   # Feature-first business modules
│   │   ├── dashboard/              # Analytics overview + charts
│   │   ├── users/                  # CRUD users with data table
│   │   ├── tasks/                  # CRUD tasks with data table
│   │   ├── apps/                   # App integrations catalog
│   │   ├── chats/                  # Chat/messaging UI
│   │   ├── settings/               # Profile, account, appearance, notifications, display
│   │   ├── auth/                   # Sign-in, sign-up, forgot-password, OTP
│   │   └── errors/                 # Error pages (401, 403, 404, 500, 503)
│   ├── routes/                     # TanStack Router file-based routes
│   │   ├── __root.tsx              # Root layout (devtools, toaster, progress bar)
│   │   ├── (auth)/                 # Public auth routes
│   │   ├── (errors)/               # Error pages
│   │   ├── _authenticated/         # Protected routes (behind auth guard)
│   │   │   ├── index.tsx           # Dashboard home
│   │   │   ├── tasks/
│   │   │   ├── users/
│   │   │   ├── apps/
│   │   │   ├── chats/
│   │   │   ├── settings/
│   │   │   └── help-center/
│   │   └── clerk/                  # Clerk auth integration routes
│   ├── hooks/                      # Custom hooks (use-mobile, use-dialog-state, etc.)
│   ├── lib/                        # Utilities (cn, cookies, error handling)
│   ├── stores/                     # Zustand stores (auth-store)
│   ├── context/                    # React contexts (font, theme, search, direction)
│   ├── config/                     # App config
│   └── styles/                     # Global CSS (index.css + theme.css)
├── components.json                 # Shadcn CLI config (new-york style, slate base)
├── vite.config.ts                  # Vite + TanStack Router plugin + Tailwind
├── tsconfig.json                   # TypeScript config
└── package.json                    # Dependencies & scripts
```

---

## Step-by-Step Workflows

### Workflow 1: Scaffold a New Admin Dashboard from Template

1. **Copy the template:**
   ```bash
   cp -r d:\APP\development_projects\shadcn-admin <target-directory>
   cd <target-directory>
   rm -rf .git
   git init
   ```

2. **Install dependencies:**
   ```bash
   pnpm install
   ```

3. **Customize project identity:**
   - Edit `package.json` → `name`, `version`
   - Edit `src/components/layout/data/sidebar-data.ts` → teams, user, nav items
   - Replace `public/images/` with project branding

4. **Start development:**
   ```bash
   pnpm run dev
   ```

5. **Verify build:**
   ```bash
   pnpm run build
   ```

### Workflow 2: Add a New Feature Page

1. **Create feature module** under `src/features/<feature-name>/`:
   ```
   src/features/<feature-name>/
   ├── components/          # Feature-specific components
   ├── data/                # Mock data, schemas, types
   └── index.tsx            # Main feature page export
   ```

2. **Create route file** under `src/routes/_authenticated/<feature-name>/index.tsx`:
   ```tsx
   import { createFileRoute } from '@tanstack/react-router'
   import { FeaturePage } from '@/features/<feature-name>'

   export const Route = createFileRoute('/_authenticated/<feature-name>/')({
     component: FeaturePage,
   })
   ```

3. **Add to sidebar navigation** in `src/components/layout/data/sidebar-data.ts`:
   ```typescript
   {
     title: 'Feature Name',
     url: '/<feature-name>',
     icon: SomeIcon, // from lucide-react
   }
   ```

4. **Register in command menu** if needed: edit `src/components/command-menu.tsx`.

### Workflow 3: Add a CRUD Data Table Page

Follow the pattern established by `users` and `tasks` features:

1. **Define Zod schema** in `src/features/<name>/data/schema.ts`:
   ```typescript
   import { z } from 'zod'

   export const itemSchema = z.object({
     id: z.string(),
     name: z.string(),
     status: z.string(),
     // ... fields
   })
   export type Item = z.infer<typeof itemSchema>
   ```

2. **Create mock data** in `src/features/<name>/data/<name>.ts`

3. **Define table columns** in `src/features/<name>/components/<name>-columns.tsx` using `@tanstack/react-table` `ColumnDef`.

4. **Create the table component** using the shared `DataTable` from `src/components/data-table/`.

5. **Add CRUD dialogs** (create/edit drawer, delete dialog) following `tasks-mutate-drawer.tsx` and `users-action-dialog.tsx` patterns.

6. **Wire up provider context** for dialog state management — see `tasks-provider.tsx` / `users-provider.tsx`.

### Workflow 4: Customize Theme & Appearance

1. **CSS Variables:** Edit `src/styles/theme.css` for color tokens.
2. **Shadcn base color:** Change `baseColor` in `components.json` (default: `slate`).
3. **Dark mode:** Already supported via `@custom-variant dark (&:is(.dark *))` in `index.css`.
4. **RTL support:** Already baked in — toggle via DirectionProvider in `src/context/`.

### Workflow 5: Add Authentication Backend

The template ships with mock auth + optional Clerk integration:

1. **Mock auth store:** `src/stores/auth-store.ts` (Zustand)
2. **Clerk integration:** Set `VITE_CLERK_PUBLISHABLE_KEY` in `.env`, use routes under `src/routes/clerk/`
3. **Custom auth:** Replace auth store logic + update `_authenticated/route.tsx` guard.

---

## Key Patterns & Conventions

### File Naming
- Components: `kebab-case.tsx` (e.g., `data-table-row-actions.tsx`)
- Types/Schemas: `kebab-case.ts` (e.g., `schema.ts`, `data.ts`)
- Tests: colocated as `*.test.ts` / `*.test.tsx`

### Component Organization
- **UI primitives** → `src/components/ui/` (managed by Shadcn CLI)
- **Layout shell** → `src/components/layout/`
- **Feature components** → `src/features/<name>/components/`
- **Shared reusable** → `src/components/` (top level)

### Import Aliases
- `@/` → `src/` (configured in `vite.config.ts` + `tsconfig.json`)

### State Management Pattern
- **Client state:** Zustand stores in `src/stores/`
- **Server state:** TanStack React Query
- **Form state:** React Hook Form + Zod resolvers
- **UI state (dialogs):** Custom `useDialogState` hook

### Customized Shadcn Components
These components have been modified from stock Shadcn UI — **do NOT overwrite with `npx shadcn@latest add`**:
- **Modified:** `scroll-area`, `sonner`, `separator`
- **RTL Updated:** `alert-dialog`, `calendar`, `command`, `dialog`, `dropdown-menu`, `select`, `table`, `sheet`, `sidebar`, `switch`

---

## Available npm Scripts

| Script | Description |
|---|---|
| `pnpm run dev` | Start Vite dev server |
| `pnpm run build` | TypeScript check + Vite build |
| `pnpm run preview` | Preview production build |
| `pnpm run lint` | ESLint check |
| `pnpm run format` | Prettier format |
| `pnpm run format:check` | Prettier check |
| `pnpm run test` | Run tests (headless browser) |
| `pnpm run test:watch` | Watch mode tests |
| `pnpm run test:coverage` | Coverage report |
| `pnpm run knip` | Dead code detection |

---

## Reference Files

For deeper technical details, see:
- `references/architecture.md` — Full component dependency graph and data flow
- `references/shadcn-components.md` — Complete list of Shadcn UI primitives used and their customizations
- `references/tanstack-router-guide.md` — TanStack Router file-based routing patterns
