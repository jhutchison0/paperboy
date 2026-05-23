# Claude Skills Framework

**Created**: 2025-11-13
**Last Updated**: 2026-05-19
**Status**: Active per Anthropic Skills open standard (December 18, 2025)

## Overview

This document defines the skills framework for Claude Code in this project, aligned with the Anthropic Skills open standard. Skills are organized hierarchically to maximize reuse across projects and downstream consumers.

A **skill** is a self-loading capability with a name and a description. At session start, only the YAML frontmatter (`name` + `description`) is loaded into Claude's context — Anthropic measures this at roughly 30–80 tokens per skill in practice. The body of `SKILL.md` loads only when Claude judges the skill relevant; supporting files in the skill directory load only when the body references them.

This is **progressive disclosure** — see [Anthropic's skills documentation](https://code.claude.com/docs/en/skills) for the canonical reference.

---

## Skill Hierarchy

```
Level 0: Universal Foundation
├── Applicable to ANY software project
├── No project names, no domain-specific content
├── Pure software engineering best practices
└── Portable across all repositories

Level 1: Project-Specific Skills
├── Tailored to this project's domain
├── References specific APIs, tools, patterns
└── Built on top of Level 0 foundation
```

---

## Skill File Forms

The Anthropic open standard supports two valid forms. Both work; we use both.

### Directory form (preferred for new skills)

```
.claude/skills/<skill-name>/
├── SKILL.md          # Required. Frontmatter + body. Under 500 lines.
├── REFERENCE.md      # Optional. Loaded only when SKILL.md cites it.
├── EXAMPLES.md       # Optional. Loaded only when SKILL.md cites it.
└── scripts/          # Optional. Helper scripts the skill can invoke.
```

Use directory form when the skill carries reference content, examples, or scripts that should not load by default. This is the standard form for progressive disclosure.

### Single-file form (legacy)

```
.claude/skills/<skill-name>.md
```

Use single-file form for short, self-contained skills that don't need sidecar files. As of 2026-05-19 all Level 0 skills in this template have migrated to directory form — the legacy single-file form is documented for reference and remains valid for any future skill small enough not to need sidecars.

---

## Frontmatter Specification

Every skill (in either form) starts with YAML frontmatter:

```yaml
---
name: skill-name-in-gerund-form
description: One sentence that includes BOTH what the skill does AND when to invoke it. The description is the only discovery signal Claude uses — it must read naturally.
version: "1.0.0"
allowed-tools: ["Read", "Write", "Edit"]   # optional; restricts what the skill may invoke
---
```

**Naming rules** (from Anthropic's skill-authoring guidance):
- Names are **gerund form** — `maintaining-ubiquitous-language`, not `ubiquitous-language-manager`.
- Names are **kebab-case** — lowercase with hyphens.
- Names are **action-oriented** — they describe what the skill does, not what it is.

**Description rules**:
- One sentence.
- Must include **what** the skill does.
- Must include **when** to invoke it (the trigger conditions Claude uses to decide auto-activation).
- Third-person, present tense.
- Concrete enough to disambiguate from neighboring skills.

**Good description**: "Maintain a project-specific glossary of domain terms in LANGUAGE.md at the repo root. Use when a new domain term emerges in conversation, when reviewing code with inconsistent terminology, or when onboarding a new contributor or agent."

**Bad description**: "Manages vocabulary." (No when, no what, no specificity.)

---

## Progressive Disclosure

**Rule**: SKILL.md body stays under 500 lines.

Detailed reference content lives in sidecar files (`REFERENCE.md`, `EXAMPLES.md`, `<topic>.md`) inside the skill directory. SKILL.md cites them by relative path when needed. Sidecar files are loaded into Claude's context **only when SKILL.md body references them** — this keeps the per-skill token cost bounded.

If a skill's SKILL.md is creeping past 400 lines, the right move is usually to extract reference material into a sidecar.

---

## Level 0: Universal Foundation Skills

These skills are portable to any software project. They contain no project names, no domain-specific content. All current Level 0 skills use directory form with sidecars for progressive disclosure.

### configuration-management (directory form)

**Path**: `.claude/skills/configuration-management/SKILL.md` + 5 sidecars (`STRUCTURE-AND-FILES.md`, `LOADER.md`, `SECRETS.md`, `VALIDATION.md`, `TESTING-AND-PATTERNS.md`).

**Focus**: Hierarchical YAML configuration systems with profiles, secrets, and environment management.

**Use when**: Setting up config systems, managing secrets, switching environments, refactoring hardcoded values, auditing config architecture.

### shift-left-testing (directory form)

**Path**: `.claude/skills/shift-left-testing/SKILL.md` + 7 sidecars (`TIERS.md`, `PATTERNS.md`, `MOCKS.md`, `FIXTURES.md`, `VERTICAL-SLICING.md`, `CI.md`, `ANTIPATTERNS.md`).

**Focus**: Multi-tier testing strategy with vertical-slicing (tracer-bullet) TDD, mocks, fixtures, simulation, CI integration, and explicit anti-patterns.

**Use when**: Setting up test infrastructure, designing test strategy, implementing mocks, driving feature work via test-first TDD.

### python-venv-management (directory form)

**Path**: `.claude/skills/python-venv-management/SKILL.md` + 2 sidecars (`SETUP.md`, `TROUBLESHOOTING.md`).

**Focus**: Python virtual environment creation, management, and troubleshooting.

**Use when**: Setting up Python environments, resolving dependency conflicts, automating setup, migrating off system Python.

### maintaining-ubiquitous-language (directory form)

**Path**: `.claude/skills/maintaining-ubiquitous-language/SKILL.md`

**Focus**: Maintain LANGUAGE.md at the repo root as the project's living glossary of domain terms.

**Key concepts**: one-sentence definitions, define-what-it-IS-not-what-it-does, `_Avoid:_` synonyms, glossary-not-spec discipline.

**Use when**: A new domain term emerges; terminology is inconsistent in code review; a new contributor or agent onboards; an existing definition becomes stale.

### maintaining-project-context (directory form)

**Path**: `.claude/skills/maintaining-project-context/SKILL.md`

**Focus**: Maintain CONTEXT.md at the repo root capturing project identity, mission, current state, and constraints.

**Key concepts**: project identity vs config state, narrative-not-machine-readable, distinguishes from LANGUAGE.md (terms) and project.yaml (machine-readable state).

**Use when**: Significant new work starts; mission or scope changes; an agent needs project context quickly; downstream relationships change.

### recording-architecture-decisions (directory form)

**Path**: `.claude/skills/recording-architecture-decisions/SKILL.md`

**Focus**: Record architectural decisions in `docs/adr/NNNN-slug.md` only when the triple filter passes.

**Key concepts**: triple filter (hard-to-reverse AND surprising-without-context AND result-of-real-trade-off), sequential numbering, never-ADR-routine-choices.

**Use when**: A decision is made that satisfies all three filter conditions. Do not write an ADR otherwise.

### task management (command: `/task`)

**Focus**: Military-inspired work tracking with structured escalation from tasks to operations orders.

**Key concepts**: Task list management, escalation ladder (Task → TCS → CONOP → OPORD), decision-point guidance for promotion, backbrief generation, team composition recommendations.

**Use when**: Tracking work items, deciding how to scope work, promoting simple tasks to structured plans, generating progress reports.

---

## Level 1: Project-Specific Skills

This template has no Level 1 skills yet. Project-specific skills would be added by downstream consumers based on their domain.

Examples from downstream repos:
- A data pipeline project might add `validating-input-schemas` or `generating-pipeline-reports`.
- A decision-support tool might add `eliciting-criterion-weights` or `comparing-scenarios`.

---

## Skill Structure Template

For directory-form skills:

```markdown
---
name: skill-name-in-gerund-form
description: One sentence with both what and when.
version: "1.0.0"
---

# Skill Title

## When to Use

Specific trigger conditions. Match the description, expanded.

## Procedure

Step-by-step guidance. Code blocks for commands. Tables for quick reference.

## Examples

Real-world usage examples.

## Sidecar Files

- `REFERENCE.md` — detailed reference (loaded only on demand)
- `EXAMPLES.md` — extended examples (loaded only on demand)

## References

External sources, prior art, related skills.
```

For single-file skills, use the same structure without a directory wrapper.

---

## Content Guidelines

### Do
- Include exact commands that can be copy-pasted.
- Provide expected output examples.
- Add safety warnings where relevant.
- Use code blocks with syntax highlighting.
- Add tables for quick reference.
- Keep descriptions concise and actionable.
- Cite external sources when adopting patterns.

### Don't
- Write verbose prose without action.
- Include project-specific references in Level 0 skills.
- Use vague descriptions ("might work", "usually").
- Duplicate information across skills.
- Assume user knowledge — say what to check.

---

## Civilian / Military Vocabulary Crosswalk

This template's internal docs use military-derived vocabulary (PCC, PCI, SITREP, OPORD, CONOP, TCS, wave). Externally-shared content — anything that propagates downstream or appears in skill descriptions visible to downstream maintainers — uses the civilian equivalent.

| Internal (military) | External (civilian) |
|---|---|
| PCC | pre-commit-check |
| PCI | pre-merge-inspection |
| SITREP | status-report |
| OPORD | operations-order |
| CONOP | concept-of-operations |
| TCS | task-condition-standard |
| wave | execution-phase |
| backbrief | progress-summary |
| METL | mission-essential-task-list |

**Rule**: Skill descriptions and any sidecar files that travel downstream substitute civilian terms. Internal commentary, session docs, and `docs/plans/` content stay in military vocabulary.

The full crosswalk lives in [`LANGUAGE.md`](../../LANGUAGE.md).

---

## Skill Maintenance

### When to update skills
- After discovering better procedures.
- When finding new troubleshooting solutions.
- After dependency or platform version changes.
- When project structure changes (Level 1 only).
- When the Anthropic open standard evolves (re-check December 18, 2025 spec annually).

### Version numbering (semver-style)
- **Patch** (1.0.0 → 1.0.1): minor fixes, typos.
- **Minor** (1.0.0 → 1.1.0): new sections, procedures added.
- **Major** (1.0.0 → 2.0.0): breaking changes, complete rewrites.

---

## Skills vs Commands vs Documentation

| Skills (`.claude/skills/`) | Commands (`.claude/commands/`) | Docs (`docs/`) |
|---|---|---|
| Self-loading capability | User-invoked workflow | Reference content |
| Claude decides when to use | User decides when to use | Read on demand |
| Auto-trigger or explicit `/name` | Always explicit `/name` | Linked from skills/commands |
| Best for: reusable expertise | Best for: deterministic workflows with side effects | Best for: stable reference |

**Rule of thumb**: if it has side effects (commits, file writes, destructive operations), it should be a **command**, not a skill — explicit user invocation is required. Skills are for capability that Claude can self-trigger safely.

This is why `session-end`, `pcc`, `pci`, `sitrep`, `session-start`, and `task` remain commands and **are not** migrated to skills.

---

## Current Skill Inventory

```
.claude/skills/
├── SKILLS_FRAMEWORK.md                       # This file
│
├── # Level 0 — directory form (current standard)
├── configuration-management/
│   ├── SKILL.md
│   ├── STRUCTURE-AND-FILES.md
│   ├── LOADER.md
│   ├── SECRETS.md
│   ├── VALIDATION.md
│   └── TESTING-AND-PATTERNS.md
│
├── shift-left-testing/
│   ├── SKILL.md
│   ├── TIERS.md
│   ├── PATTERNS.md
│   ├── MOCKS.md
│   ├── FIXTURES.md
│   ├── VERTICAL-SLICING.md
│   ├── CI.md
│   └── ANTIPATTERNS.md
│
├── python-venv-management/
│   ├── SKILL.md
│   ├── SETUP.md
│   └── TROUBLESHOOTING.md
│
├── maintaining-ubiquitous-language/
│   └── SKILL.md
│
├── maintaining-project-context/
│   └── SKILL.md
│
├── recording-architecture-decisions/
│   └── SKILL.md
│
└── # Level 1 — Project-Specific
    (none — this is a template; downstream repos add as needed)
```

**Retired skills**:
- `.claude/skills/session-end.md` (2026-05-19) — reference content moved to `docs/session-doc-format.md`. The `/session-end` workflow continues at `.claude/commands/session-end.md`.
- `.claude/skills/configuration-management.md` (2026-05-19) — replaced by directory-form skill above.
- `.claude/skills/shift-left-testing.md` (2026-05-19) — replaced by directory-form skill above.
- `.claude/skills/python-venv-management.md` (2026-05-19) — replaced by directory-form skill above.

---

## Porting Skills to New Projects

When starting a new project from this template:

1. **Copy Level 0 skills** directly (they're universal). All current Level 0 skills are portable.
2. **Create project-specific Level 1 skills** as needed.
3. **Update this file** to list the project's Level 1 skills.
4. **Never modify Level 0 content** for project-specific needs — create a Level 1 skill instead, or propose a doctrine update so all consumers benefit.
5. **For LANGUAGE.md and CONTEXT.md**, start with the template files at the repo root and customize. These are project-specific by nature; the skills that maintain them are Level 0 (universal pattern, project-specific content).

---

## References

- [Anthropic Skills documentation](https://code.claude.com/docs/en/skills) — canonical reference
- [Anthropic Skills open standard announcement](https://www.anthropic.com/news/skills) — December 18, 2025
- Matt Pocock's `mattpocock/skills` repo — source of CONTEXT-FORMAT.md, ADR-FORMAT.md, and tracer-bullet TDD patterns we adapted
- [Jesse Vincent's `obra/superpowers`](https://github.com/obra/superpowers) — official Anthropic plugin marketplace entry; reference for skills-driven methodology (we do not install, only reference)

---

**Maintained by**: Skills Framework
**Next Review**: When adding new skills, when Anthropic updates the open standard, or annually.
