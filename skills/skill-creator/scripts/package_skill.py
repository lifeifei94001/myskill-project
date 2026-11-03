#!/usr/bin/env python3
"""
Package a skill directory into a distributable .zip or .skill archive.
"""

import argparse
import sys
import zipfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def package_skill(skill_path: str | Path, output_file: str | None = None) -> Path | None:
    """Package a skill directory into a zip archive."""
    src = Path(skill_path).resolve()
    if not src.exists() or not src.is_dir():
        print(f"❌ Error: '{src}' is not a valid directory.", file=sys.stderr)
        return None

    skill_md = src / "SKILL.md"
    if not skill_md.exists():
        print(f"❌ Error: 'SKILL.md' not found in '{src}'.", file=sys.stderr)
        return None

    skill_name = src.name
    if not output_file:
        out_path = src.parent / f"{skill_name}.skill"
    else:
        out_path = Path(output_file).resolve()

    try:
        with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for item in src.rglob("*"):
                # Skip hidden files or caches (.git, __pycache__, etc.)
                if any(part.startswith(".") or part == "__pycache__" for part in item.parts):
                    continue
                rel_path = item.relative_to(src)
                zf.write(item, arcname=str(rel_path))

        print(f"✓ Skill successfully packaged to: {out_path}")
        return out_path
    except Exception as e:
        print(f"❌ Packaging failed: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(description="Package an AI agent skill folder into a .skill archive.")
    parser.add_argument("skill_path", type=str, help="Path to the skill directory")
    parser.add_argument("-o", "--output", type=str, default=None, help="Output file path (default: <skill_name>.skill)")

    args = parser.parse_args()
    res = package_skill(args.skill_path, args.output)
    if res is None:
        sys.exit(1)


if __name__ == "__main__":
    main()
