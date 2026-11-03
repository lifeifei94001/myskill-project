#!/usr/bin/env python3
"""
Add a new feature module to a shadcn-admin project.

Usage:
    python add_feature.py <feature-name> [--project-dir <path>] [--with-table]
    
Example:
    python add_feature.py products --project-dir d:\projects\my-dashboard --with-table
"""

import argparse
import os
import sys


def kebab_to_pascal(name: str) -> str:
    """Convert kebab-case to PascalCase."""
    return ''.join(word.capitalize() for word in name.split('-'))


def kebab_to_camel(name: str) -> str:
    """Convert kebab-case to camelCase."""
    pascal = kebab_to_pascal(name)
    return pascal[0].lower() + pascal[1:]


def add_feature(feature_name: str, project_dir: str, with_table: bool):
    """Scaffold a new feature module."""
    
    pascal = kebab_to_pascal(feature_name)
    camel = kebab_to_camel(feature_name)
    singular = feature_name.rstrip('s')  # Naive singularization
    singular_pascal = kebab_to_pascal(singular)
    
    feature_dir = os.path.join(project_dir, 'src', 'features', feature_name)
    route_dir = os.path.join(project_dir, 'src', 'routes', '_authenticated', feature_name)
    
    if os.path.exists(feature_dir):
        print(f"❌ Feature '{feature_name}' already exists at {feature_dir}")
        sys.exit(1)
    
    # Create directories
    os.makedirs(os.path.join(feature_dir, 'components'), exist_ok=True)
    os.makedirs(os.path.join(feature_dir, 'data'), exist_ok=True)
    os.makedirs(route_dir, exist_ok=True)
    
    # Create index.tsx (main page)
    index_content = f"""import {{ Header }} from '@/components/layout/header'
import {{ Main }} from '@/components/layout/main'

export default function {pascal}Page() {{
  return (
    <>
      <Header fixed>
        <div className='ms-auto flex items-center space-x-4'>
          {{/* Add header actions here */}}
        </div>
      </Header>
      <Main>
        <div className='mb-2 flex flex-wrap items-center justify-between space-y-2'>
          <div>
            <h2 className='text-2xl font-bold tracking-tight'>{pascal}</h2>
            <p className='text-muted-foreground'>
              Manage your {feature_name} here.
            </p>
          </div>
        </div>
        <div className='-mx-4 flex-1 overflow-auto px-4 py-1 lg:flex-row lg:space-x-12 lg:space-y-0'>
          {{/* Add content here */}}
        </div>
      </Main>
    </>
  )
}}
"""
    
    # Create route file
    route_content = f"""import {{ createFileRoute }} from '@tanstack/react-router'
import {pascal}Page from '@/features/{feature_name}'

export const Route = createFileRoute('/_authenticated/{feature_name}/')('{{
  component: {pascal}Page,
}}')
"""
    
    # Create schema
    schema_content = f"""import {{ z }} from 'zod'

export const {camel}Schema = z.object({{
  id: z.string(),
  name: z.string(),
  status: z.string(),
  createdAt: z.coerce.date(),
  updatedAt: z.coerce.date(),
}})

export type {singular_pascal} = z.infer<typeof {camel}Schema>
"""
    
    # Write files
    files = {
        os.path.join(feature_dir, 'index.tsx'): index_content,
        os.path.join(route_dir, 'index.tsx'): route_content,
        os.path.join(feature_dir, 'data', 'schema.ts'): schema_content,
    }
    
    if with_table:
        columns_content = f"""import {{ type ColumnDef }} from '@tanstack/react-table'
import {{ type {singular_pascal} }} from '../data/schema'
import {{ DataTableColumnHeader }} from '@/components/data-table/column-header'

export const columns: ColumnDef<{singular_pascal}>[] = [
  {{
    accessorKey: 'name',
    header: ({{ column }}) => (
      <DataTableColumnHeader column={{column}} title='Name' />
    ),
    cell: ({{ row }}) => <span>{{row.getValue('name')}}</span>,
  }},
  {{
    accessorKey: 'status',
    header: ({{ column }}) => (
      <DataTableColumnHeader column={{column}} title='Status' />
    ),
    cell: ({{ row }}) => <span>{{row.getValue('status')}}</span>,
  }},
]
"""
        files[os.path.join(feature_dir, 'components', f'{feature_name}-columns.tsx')] = columns_content
    
    for filepath, content in files.items():
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print(f"""
✅ Feature '{feature_name}' scaffolded successfully!

Created:
  📂 src/features/{feature_name}/
  ├── index.tsx
  ├── data/schema.ts
  {'├── components/' + feature_name + '-columns.tsx' if with_table else '├── components/'}
  └── data/

  📂 src/routes/_authenticated/{feature_name}/
  └── index.tsx

Next steps:
  1. Add navigation item to src/components/layout/data/sidebar-data.ts
  2. Restart dev server to regenerate route tree
  3. Customize the schema and page content
""")


def main():
    parser = argparse.ArgumentParser(description='Add a new feature to shadcn-admin project')
    parser.add_argument('name', help='Feature name in kebab-case (e.g., products, order-items)')
    parser.add_argument('--project-dir', default='.', help='Project root directory')
    parser.add_argument('--with-table', action='store_true', help='Include data table column definitions')
    
    args = parser.parse_args()
    add_feature(args.name, args.project_dir, args.with_table)


if __name__ == '__main__':
    main()
