#!/usr/bin/env python3
"""
Initialize a new AI agent skill template directory with standard SKILL.md and resource folders.
"""

import argparse
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def title_case_skill_name(skill_name: str) -> str:
    """Convert a hyphenated skill name to Title Case for display."""
    return " ".join(word.capitalize() for word in skill_name.split("-"))


def init_skill(skill_name: str, path: str = ".") -> Path | None:
    """Initialize a new skill directory with a template SKILL.md and subdirectories.

    Args:
        skill_name: Name of the skill (typically hyphen-separated lowercase).
        path: Base path where the skill directory should be created.

    Returns:
        Path to the created skill directory, or None if creation failed.
    """
    # Clean and validate skill name
    skill_name = skill_name.strip().lower()
    if not skill_name.replace("-", "").isalnum():
        print(f"❌ Error: Skill name '{skill_name}' must contain only alphanumeric characters and hyphens.")
        return None

    base_path = Path(path).resolve()
    skill_dir = base_path / skill_name

    if skill_dir.exists():
        print(f"❌ Error: Skill directory already exists: {skill_dir}")
        return None

    try:
        # Create core directories following standard progressive disclosure architecture
        skill_dir.mkdir(parents=True, exist_ok=False)
        (skill_dir / "scripts").mkdir(exist_ok=True)
        (skill_dir / "references").mkdir(exist_ok=True)
        (skill_dir / "assets").mkdir(exist_ok=True)

        display_name = title_case_skill_name(skill_name)

        # Generate standard template SKILL.md
        skill_md_content = f"""---
name: {skill_name}
description: "Use when the user asks to [TODO: specify concrete trigger conditions, e.g., perform {display_name}]. Explicitly list key trigger phrases and conditions."
---

# {display_name}

## Overview
Provide a concise 1-2 paragraph description of what this skill accomplishes and its intended outcomes.

## When to Use This Skill
- [Trigger scenario 1]
- [Trigger scenario 2]
- [Keywords / user phrases that indicate this skill applies]

## Core Workflow / Instructions
1. **Step 1: Clarification & Preparation**
   - Gather necessary inputs from user or workspace.
2. **Step 2: Execution**
   - Step-by-step guidance for the agent.
   - Reference bundled scripts (`scripts/`) or detailed reference manuals (`references/`) on demand.
3. **Step 3: Verification & Delivery**
   - Verify outputs against expected standards before confirming completion.

## Resources & Directory Structure
- `scripts/`: Executable scripts (deterministic or complex operations)
- `references/`: In-depth documentation loaded into context only when needed
- `assets/`: Templates, boilerplates, or static artifacts
"""

        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text(skill_md_content, encoding="utf-8")

        print(f"✓ Successfully initialized skill '{skill_name}' at: {skill_dir}")
        print(f"  ├── SKILL.md (Core instructions and YAML frontmatter)")
        print(f"  ├── scripts/ (Deterministic scripts and automation)")
        print(f"  ├── references/ (Deep documentation loaded on demand)")
        print(f"  └── assets/ (Templates, boilerplates, or assets)")
        return skill_dir

    except Exception as e:
        print(f"❌ Error creating skill directory: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Initialize a standardized AI agent skill template directory."
    )
    parser.add_argument(
        "skill_name",
        type=str,
        help="The name of the skill to create (e.g. 'doc-converter', 'api-tester')"
    )
    parser.add_argument(
        "-p",
        "--path",
        type=str,
        default=".",
        help="Target directory where the skill directory will be created (default: current directory)"
    )

    args = parser.parse_args()
    res = init_skill(args.skill_name, args.path)
    if res is None:
        sys.exit(1)


if __name__ == "__main__":
    main()
