# Trigger Optimization Guide for Agent Skills

## Why Trigger Optimization Matters

In the Agent Skills ecosystem (Claude Code, Antigravity, OpenClaw, Codex, etc.), skills operate on **Progressive Disclosure**:
1. At session startup, the model **only** pre-loads the YAML frontmatter (`name` and `description`) of all available skills.
2. The full body of `SKILL.md` is **only** loaded into context when the user's prompt matches the skill's `description`.
3. If the description is too narrow, the skill will **under-trigger** (fail to load when needed).
4. If the description is too broad or generic, the skill will **over-trigger** (load unnecessarily, consuming context window and polluting attention).

---

## The Golden Formula for `description`

An optimal `description` contains three components:

```yaml
description: "Use when [Action / User Goal], such as [Concrete Scenarios / Tasks]. Triggers on phrases like [Key Phrases / Keywords]."
```

### 1. Third-Person Perspective
Write descriptions from the agent's point of view in third-person:
* ✅ **Good:** `"Use when the user asks to parse, merge, or validate Excel/CSV spreadsheets..."`
* ❌ **Bad:** `"I can help you process your spreadsheets..."`

### 2. Explicit Trigger Conditions ("Use when...")
Lead with clear intent boundaries:
* ✅ **Good:** `"Use when generating interactive React UI components or optimizing frontend design systems..."`
* ❌ **Bad:** `"This is a React design tool."`

### 3. Concrete Trigger Phrases & Keywords
Include specific keywords and common user colloquialisms:
* For a database skill: `Trigger on: 'SQL schema', 'migrate database', 'RLS policy', 'Supabase table', 'optimize query'.`
* For a test skill: `Trigger on: 'write e2e test', 'playwright check', 'flaky test', 'regression suite'.`

---

## Common Anti-Patterns & Fixes

| Anti-Pattern | Example Problem | Recommended Fix |
| :--- | :--- | :--- |
| **Too Vague** | `"Helpful for programming tasks."` | `"Use when refactoring TypeScript modules or designing deep interfaces."` |
| **Explaining HOW instead of WHEN** | `"Uses pandas to read csv and applies regex to find emails."` | `"Use when extracting, cleaning, or parsing email addresses from tabular data."` |
| **Oversized Frontmatter** | >1024 characters describing internal theory. | Keep under 500 characters. Move explanations into `SKILL.md` body. |
| **First-Person Prose** | `"Let me know if you want to deploy to Docker."` | `"Use when configuring Dockerfiles, docker-compose, or container networking."` |
