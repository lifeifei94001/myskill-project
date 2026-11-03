# Shadcn UI Components Reference — shadcn-admin

## Configuration

- **Style:** New York
- **Base Color:** Slate
- **CSS Variables:** Enabled
- **Icon Library:** Lucide
- **RSC:** Disabled (Vite SPA)

## Component Inventory

### Standard Shadcn UI Components (safe to update via CLI)

| Component | File | Radix Dependency |
|---|---|---|
| Alert | `ui/alert.tsx` | — |
| Avatar | `ui/avatar.tsx` | `@radix-ui/react-avatar` |
| Badge | `ui/badge.tsx` | — |
| Button | `ui/button.tsx` | `@radix-ui/react-slot` |
| Card | `ui/card.tsx` | — |
| Checkbox | `ui/checkbox.tsx` | `@radix-ui/react-checkbox` |
| Collapsible | `ui/collapsible.tsx` | `@radix-ui/react-collapsible` |
| Form | `ui/form.tsx` | `react-hook-form` |
| Input | `ui/input.tsx` | — |
| Input OTP | `ui/input-otp.tsx` | `input-otp` |
| Label | `ui/label.tsx` | `@radix-ui/react-label` |
| Popover | `ui/popover.tsx` | `@radix-ui/react-popover` |
| Radio Group | `ui/radio-group.tsx` | `@radix-ui/react-radio-group` |
| Skeleton | `ui/skeleton.tsx` | — |
| Tabs | `ui/tabs.tsx` | `@radix-ui/react-tabs` |
| Textarea | `ui/textarea.tsx` | — |
| Tooltip | `ui/tooltip.tsx` | `@radix-ui/react-tooltip` |

### Modified Components (DO NOT update via CLI)

| Component | File | Modification |
|---|---|---|
| Scroll Area | `ui/scroll-area.tsx` | Custom scroll behavior |
| Sonner | `ui/sonner.tsx` | Toast customization |
| Separator | `ui/separator.tsx` | Styling changes |

### RTL-Updated Components (safe to update ONLY if RTL not needed)

| Component | File | RTL Changes |
|---|---|---|
| Alert Dialog | `ui/alert-dialog.tsx` | Layout/positioning |
| Calendar | `ui/calendar.tsx` | Date picker direction |
| Command | `ui/command.tsx` | Search palette direction |
| Dialog | `ui/dialog.tsx` | Modal positioning |
| Dropdown Menu | `ui/dropdown-menu.tsx` | Menu alignment |
| Select | `ui/select.tsx` | Dropdown alignment |
| Table | `ui/table.tsx` | Column ordering |
| Sheet | `ui/sheet.tsx` | Slide direction |
| Sidebar | `ui/sidebar.tsx` | Navigation placement |
| Switch | `ui/switch.tsx` | Toggle direction |

## Adding New Components

```bash
# Standard Shadcn CLI (safe for non-modified components)
npx shadcn@latest add <component-name>

# Example
npx shadcn@latest add accordion
npx shadcn@latest add progress
npx shadcn@latest add slider
```

## Custom Project Components

| Component | Location | Purpose |
|---|---|---|
| `CommandMenu` | `components/command-menu.tsx` | Global ⌘K search palette |
| `ConfirmDialog` | `components/confirm-dialog.tsx` | Reusable confirmation modal |
| `DataTable` | `components/data-table/` | Full-featured data table with pagination, filters, sorting |
| `PasswordInput` | `components/password-input.tsx` | Password field with visibility toggle |
| `DatePicker` | `components/date-picker.tsx` | Date selection component |
| `SelectDropdown` | `components/select-dropdown.tsx` | Enhanced select dropdown |
| `LongText` | `components/long-text.tsx` | Truncated text with tooltip |
| `ComingSoon` | `components/coming-soon.tsx` | Placeholder for WIP pages |
| `LearnMore` | `components/learn-more.tsx` | Information link component |
| `NavigationProgress` | `components/navigation-progress.tsx` | Top loading bar during navigation |
| `SkipToMain` | `components/skip-to-main.tsx` | Accessibility skip link |
| `ThemeSwitch` | `components/theme-switch.tsx` | Light/dark mode toggle |
| `SignOutDialog` | `components/sign-out-dialog.tsx` | Sign out confirmation |
| `ConfigDrawer` | `components/config-drawer.tsx` | App configuration panel |

## DataTable Sub-components

| Component | File | Purpose |
|---|---|---|
| `DataTable` | `data-table/index.ts` | Main table export |
| `BulkActions` | `data-table/bulk-actions.tsx` | Multi-select actions bar |
| `ColumnHeader` | `data-table/column-header.tsx` | Sortable column header |
| `FacetedFilter` | `data-table/faceted-filter.tsx` | Faceted filter popover |
| `Pagination` | `data-table/pagination.tsx` | Page navigation controls |
| `Toolbar` | `data-table/toolbar.tsx` | Table toolbar with search/filters |
| `ViewOptions` | `data-table/view-options.tsx` | Column visibility toggle |
