#!/usr/bin/env python3
"""
Validate a skill directory and its SKILL.md file for structural correctness, YAML frontmatter compliance, and best practices.
"""

import argparse
import os
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

try:
    import yaml
except ImportError:
    yaml = None


def validate_skill(skill_path: str | Path) -> tuple[bool, list[str], list[str]]:
    """Validate a skill directory.

    Returns:
        (is_valid, errors, warnings)
    """
    errors: list[str] = []
    warnings: list[str] = []

    path = Path(skill_path).resolve()

    # 1. Directory checks
    if not path.exists():
        return False, [f"Path does not exist: {path}"], []
    if not path.is_dir():
        return False, [f"Path is not a directory: {path}"], []

    skill_file = path / "SKILL.md"
    if not skill_file.exists():
        return False, [f"Required file 'SKILL.md' not found in {path}"], []

    # 2. Read content
    try:
        content = skill_file.read_text(encoding="utf-8")
    except Exception as e:
        return False, [f"Failed to read SKILL.md: {e}"], []

    lines = content.splitlines()

    # 3. YAML Frontmatter check
    if not content.startswith("---"):
        errors.append("SKILL.md must start with '---' YAML frontmatter delimiter.")
    
    fm_match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n(.*)$", content, re.DOTALL)
    if not fm_match:
        errors.append("Invalid or unclosed YAML frontmatter. Expected opening and closing '---'.")
        return False, errors, warnings

    fm_text = fm_match.group(1)
    body_text = fm_match.group(2)

    # Parse YAML
    data = {}
    if yaml is not None:
        try:
            data = yaml.safe_load(fm_text) or {}
        except Exception as e:
            errors.append(f"YAML frontmatter syntax error: {e}")
    else:
        # Fallback simple parser if yaml module is not installed
        for line in fm_text.splitlines():
            line = line.strip()
            if line.startswith("name:"):
                data["name"] = line[5:].strip().strip("\"'")
            elif line.startswith("description:"):
                data["description"] = line[12:].strip().strip("\"'")

    # Validate name
    name = data.get("name")
    if not name:
        errors.append("YAML frontmatter missing required field: 'name'")
    elif not isinstance(name, str):
        errors.append("'name' must be a string")
    else:
        if not re.match(r"^[a-z0-9-]+$", name):
            errors.append(f"Invalid name '{name}'. Use only lowercase letters, numbers, and hyphens.")
        if path.name != name:
            warnings.append(f"Directory name '{path.name}' does not match skill name '{name}'.")

    # Validate description
    desc = data.get("description")
    if not desc:
        errors.append("YAML frontmatter missing required field: 'description'")
    elif not isinstance(desc, str):
        errors.append("'description' must be a string")
    else:
        desc_clean = desc.strip()
        if len(desc_clean) < 15:
            errors.append("Description is too short. Describe clearly when this skill should be invoked.")
        if len(desc_clean) > 1024:
            warnings.append(f"Description length ({len(desc_clean)} chars) exceeds recommended max 1024 characters.")
        if not re.search(r"\b(use when|trigger|invoked|when user)\b", desc_clean, re.IGNORECASE):
            warnings.append("Description should ideally specify trigger conditions using phrases like 'Use when...'.")

    # 4. Check for template leftovers & placeholders
    placeholder_matches = re.findall(r"(\[TODO[^\]]*\]|TODO:|[<]TODO[>]|\[perform specific task[^\]]*\])", content)
    if placeholder_matches:
        for match in set(placeholder_matches):
            warnings.append(f"Unfinished placeholder detected: '{match}'")

    # 5. Progressive disclosure & size check
    if len(lines) > 500:
        warnings.append(
            f"SKILL.md has {len(lines)} lines. Consider moving extensive documentation or code into 'references/' or 'scripts/' to conserve context tokens."
        )

    # 6. Check referenced files exist
    ref_files = re.findall(r"`(?:references|scripts|assets)/([^`\n\r]+)`", body_text)
    for ref in ref_files:
        ref_path = path / "references" / ref
        script_path = path / "scripts" / ref
        asset_path = path / "assets" / ref
        if not (ref_path.exists() or script_path.exists() or asset_path.exists()):
            warnings.append(f"Referenced path '{ref}' not found in references/, scripts/, or assets/.")

    is_valid = len(errors) == 0
    return is_valid, errors, warnings


def main():
    parser = argparse.ArgumentParser(
        description="Quickly validate an AI agent skill folder and its SKILL.md file."
    )
    parser.add_argument(
        "skill_path",
        type=str,
        default=".",
        nargs="?",
        help="Path to the skill directory (default: current directory)"
    )

    args = parser.parse_args()
    is_valid, errors, warnings = validate_skill(args.skill_path)

    print(f"\n🔍 Validating Skill at: {Path(args.skill_path).resolve()}")
    print("-" * 50)

    if errors:
        print("❌ Errors:")
        for err in errors:
            print(f"  • {err}")
    else:
        print("✅ Core structural validation passed!")

    if warnings:
        print("\n⚠️ Warnings & Suggestions:")
        for warn in warnings:
            print(f"  • {warn}")

    print("-" * 50)
    if is_valid:
        print("🎉 Ready for deployment!")
        sys.exit(0)
    else:
        print("🛑 Please fix the errors above before deploying.")
        sys.exit(1)


if __name__ == "__main__":
    main()
