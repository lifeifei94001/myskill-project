#!/usr/bin/env python3
"""
Scaffold a new admin dashboard project from the shadcn-admin template.

Usage:
    python scaffold_project.py <project-name> [--target-dir <path>]
    
Example:
    python scaffold_project.py my-dashboard --target-dir d:\projects
"""

import argparse
import json
import os
import shutil
import sys


def scaffold_project(project_name: str, target_dir: str, source_dir: str):
    """Copy shadcn-admin template to a new project directory."""
    
    dest = os.path.join(target_dir, project_name)
    
    if os.path.exists(dest):
        print(f"❌ Error: Directory already exists: {dest}")
        sys.exit(1)
    
    print(f"📦 Scaffolding '{project_name}' from shadcn-admin template...")
    print(f"   Source: {source_dir}")
    print(f"   Target: {dest}")
    
    # Copy template, excluding .git and node_modules
    def ignore_patterns(directory, files):
        ignored = set()
        for f in files:
            if f in ('.git', 'node_modules', 'pnpm-lock.yaml'):
                ignored.add(f)
        return ignored
    
    shutil.copytree(source_dir, dest, ignore=ignore_patterns)
    print("✅ Template copied")
    
    # Update package.json
    pkg_path = os.path.join(dest, 'package.json')
    if os.path.exists(pkg_path):
        with open(pkg_path, 'r', encoding='utf-8') as f:
            pkg = json.load(f)
        
        pkg['name'] = project_name
        pkg['version'] = '0.1.0'
        pkg['private'] = True
        
        with open(pkg_path, 'w', encoding='utf-8') as f:
            json.dump(pkg, f, indent=2, ensure_ascii=False)
        print(f"✅ Updated package.json (name: {project_name})")
    
    # Initialize git
    os.system(f'cd "{dest}" && git init')
    print("✅ Initialized git repository")
    
    print(f"""
🎉 Project '{project_name}' scaffolded successfully!

Next steps:
  cd {dest}
  pnpm install
  pnpm run dev
    """)


def main():
    parser = argparse.ArgumentParser(description='Scaffold a new shadcn-admin project')
    parser.add_argument('name', help='Project name (will be used as directory name)')
    parser.add_argument('--target-dir', default='.', help='Parent directory for the new project')
    parser.add_argument('--source-dir', 
                        default=r'd:\APP\development_projects\shadcn-admin',
                        help='Path to shadcn-admin template')
    
    args = parser.parse_args()
    scaffold_project(args.name, args.target_dir, args.source_dir)


if __name__ == '__main__':
    main()
