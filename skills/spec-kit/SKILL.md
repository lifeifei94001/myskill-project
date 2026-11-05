---
name: spec-kit
description: >
  Specification-Driven Development (SDD) toolkit by GitHub. Use when planning, specifying,
  structuring, or executing software features via rigorous living specifications before code
  is written. Triggers on: "SDD", "spec kit", "specify", "speckit", "write spec", "feature spec",
  "constitution", "task decomposition", "requirements specification", "plan before code".
---

# GitHub Spec Kit (Specification-Driven Development)

Spec Kit brings disciplined Specification-Driven Development (SDD) to AI coding workflows. Rather than unstructured "vibe coding", it establishes living documents that serve as the single source of truth across the lifecycle.

## Core Phases & Workflow

The Spec Kit pipeline moves through these phases:

```
Idea / Need
    ↓
1. Constitution (Project Standards & Principles)
    ↓
2. Specify (Feature Requirements & User Stories -> spec.md)
    ↓
3. Clarify (Resolve Ambiguities & Edge Cases)
    ↓
4. Plan (Architecture & Tech Stack -> plan.md)
    ↓
5. Tasks (Dependency-Ordered Breakdown -> tasks.md)
    ↓
6. Implement (Step-by-step Execution with Verification)
```

### 1. Constitution (`/speckit.constitution`)
Define non-negotiable project boundaries, architectural standards, code style, and test coverage rules in `.specify/memory/constitution.md`.

### 2. Specify (`/speckit.specify`)
Capture the what and why in `<feature_dir>/spec.md`:
- User scenarios and personas
- Functional requirements (must be verifiable)
- Non-functional requirements (performance, accessibility, security)
- Success criteria and out-of-scope boundaries

### 3. Clarify (`/speckit.clarify`)
Inspect the specification for gaps, assumptions, and edge cases. Ask targeted questions to clarify before committing to a technical design.

### 4. Plan (`/speckit.plan`)
Translate requirements into an architectural blueprint in `<feature_dir>/plan.md`:
- Data model and API contracts
- Component boundaries and interactions
- Error handling and resilience strategy
- Deployment and testing strategy

### 5. Tasks (`/speckit.tasks`)
Break down the plan into small, independently testable tasks in `<feature_dir>/tasks.md`:
- Explicit dependency order (`depends_on`)
- Clear verification steps per task
- Small units of work to minimize agent context degradation

### 6. Implement (`/speckit.implement`)
Execute tasks sequentially:
- TDD loop: red -> green -> refactor
- Verify each task against specification success criteria
- Keep context hygiene between distinct task executions

## CLI Integration

Spec Kit provides the `specify` CLI:
```bash
specify init <project-name> --ai claude
specify check
specify run
```

## Presets and References

Detailed command instructions and templates are stored under `presets/lean/commands/`:
- `speckit.constitution.md`
- `speckit.specify.md`
- `speckit.plan.md`
- `speckit.tasks.md`
- `speckit.implement.md`
