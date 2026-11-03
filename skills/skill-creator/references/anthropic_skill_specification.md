# Agent Skill Specification & Progressive Disclosure

## Standard Directory Layout

```text
skill-name/
├── SKILL.md                 # Mandatory: Frontmatter metadata + procedural instructions
├── scripts/                 # Optional: Executable automation scripts
├── references/              # Optional: Deep reference manuals, API docs, schemas
└── assets/                  # Optional: Templates, theme stylesheets, static files
```

---

## Frontmatter Schema

Every skill MUST begin with a YAML frontmatter block:

```yaml
---
name: skill-name-with-hyphens
description: Clear, third-person trigger explanation starting with 'Use when...'
---
```

### Constraints:
* `name`: Lowercase letters, digits, and hyphens (`[a-z0-9-]+`). Must match the parent directory name.
* `description`: String (max 1024 characters). High precision trigger conditions.

---

## Progressive Disclosure Rules

1. **Context Window is a Shared Resource:**
   - Keep `SKILL.md` under 500 lines.
   - Separate "What to do" (procedural steps in `SKILL.md`) from "Deep domain knowledge" (put in `references/`).
2. **Deterministic Operations Go to Scripts:**
   - If an operation can be performed deterministically (e.g. file format conversion, validation, AST parsing), write a Python script in `scripts/` instead of asking the LLM to hallucinate the execution.
3. **Reference Relative Paths:**
   - Refer to files using relative paths, e.g. `references/api-docs.md` or `scripts/helper.py`.
