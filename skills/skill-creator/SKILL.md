---
name: skill-creator
description: "Use when the user wants to create a new skill, update or improve an existing skill, scaffold SKILL.md templates, optimize frontmatter trigger descriptions, or package and validate agent skills. Trigger phrases: '创建skill', '新建skill', '编写skill', '优化skill', 'create a skill', 'init skill', 'package skill'."
---

# Skill Creator

## Overview
Skill Creator is the meta-skill for designing, scaffolding, validating, optimizing, and packaging modular Agent Skills (`SKILL.md` packages) for Claude Code, Antigravity, and the broader Agent ecosystem.

It brings software engineering rigor to skill authoring:
- **Progressive Disclosure**: Keeps context windows lean by separating metadata, core procedural instructions, deep references, and executable scripts.
- **Trigger Optimization**: Refines YAML frontmatter descriptions to eliminate under-triggering (missing user requests) and over-triggering (unwanted activations).
- **Automated Validation**: Provides verification tools to ensure directory layout, YAML syntax, and formatting conform to ecosystem standards.

---

## The 5-Step Skill Creation Lifecycle

```
① Clarify Intent & Examples ➔ ② Plan Progressive Disclosure ➔ ③ Initialize Scaffold ➔ ④ Implement & Refactor ➔ ⑤ Validate & Package
```

### Step 1: Clarify Intent & Examples
Before writing any instructions or code:
1. Identify the skill's primary objective and domain.
2. Formulate 3–5 concrete user prompt examples that **should** trigger this skill.
3. Formulate 1–2 negative examples that **should NOT** trigger this skill.

### Step 2: Plan Progressive Disclosure
Map out how knowledge will be partitioned:
- **`SKILL.md` (Core instructions)**: High-level procedural workflow, checklists, and decision trees (keep under 500 lines).
- **`references/` (On-demand documentation)**: Detailed API manuals, cheat-sheets, domain rules, or style guides loaded into context only when needed.
- **`scripts/` (Deterministic logic)**: Scripts for validation, parsing, conversion, or automation that run via terminal commands rather than LLM token generation.
- **`assets/` (Static resources)**: Theme CSS, boilerplate project templates, starter files.

### Step 3: Initialize Scaffold
Use the bundled initialization script to scaffold a standardized directory layout:

```bash
python scripts/init_skill.py <skill-name> --path <target-directory>
```

Example:
```bash
python scripts/init_skill.py pdf-extractor --path d:\APP\development_projects\.agents\skills
```

This creates:
```text
<skill-name>/
├── SKILL.md
├── scripts/
├── references/
└── assets/
```

### Step 4: Implement & Refine
1. **Refine Frontmatter**:
   - `name`: Must match folder name (lowercase, alphanumeric + hyphens).
   - `description`: Write in third person using the formula in `references/trigger_optimization.md`:
     `"Use when [User Action], such as [Tasks]. Triggers on: [Keywords]."`
2. **Draft Core Instructions in `SKILL.md`**:
   - Use imperative, concise steps.
   - Reference scripts and reference docs explicitly when relevant.
3. **Add Supporting Files**:
   - Put large templates or manuals in `references/`.
   - Put executable Python/Bash tools in `scripts/`.

### Step 5: Validate & Package
Run the quick validator to ensure your skill adheres to all specification rules:

```bash
python scripts/quick_validate.py <path-to-skill-directory>
```

When ready to distribute or share:
```bash
python scripts/package_skill.py <path-to-skill-directory>
```
This produces a ready-to-install `.skill` (or `.zip`) archive.

---

## Reference Guides
- **Trigger Optimization**: See `references/trigger_optimization.md` for writing high-recall, high-precision descriptions.
- **Specification**: See `references/anthropic_skill_specification.md` for directory standards and schema requirements.
