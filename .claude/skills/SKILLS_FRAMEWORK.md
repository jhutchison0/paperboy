# Claude Skills Framework

**Created**: 2025-11-13
**Last Updated**: 2025-12-07
**Status**: Active

## Overview

This document defines a portable skills framework for Claude Code that separates universal best practices from project-specific knowledge. Skills are organized hierarchically to maximize reuse across projects.

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

## Level 0: Universal Foundation Skills

These skills are **100% portable** to any software project. They contain no project names, no domain-specific content, and represent pure software engineering best practices.

### configuration-management.md
**Focus**: Hierarchical configuration systems with profiles, secrets, and environment management

**Key Concepts**:
- Configuration priority order (default → components → profiles → env vars)
- Secrets management (.env vs .env.example, never commit secrets)
- Profile-based environments (dev/test/staging/production)
- YAML configuration with environment variable substitution
- Schema validation with Pydantic
- Testing strategies for configuration

**Use when**: Setting up config systems, managing secrets, switching environments, refactoring hardcoded values

### session-end.md
**Focus**: End-of-session git workflow and documentation

**Key Concepts**:
- Branch strategy (dev-* branches, merge to main at milestones)
- Conventional commits (feat:, fix:, refactor:, docs:, test:)
- Session documentation template (YYYYMMDD_*.md format)
- Diagram guidelines (ASCII for simple, Mermaid for complex)
- Session-end checklist

**Use when**: Ending development sessions, preparing commits, documenting progress

### shift-left-testing.md
**Focus**: Early testing with multi-tier strategy, mocks, and simulated data

**Key Concepts**:
- Test pyramid (unit → integration → system → external)
- Test organization (fixtures/, unit/, integration/)
- Mock implementation patterns (simple, configurable, realistic)
- Test independence and isolation
- CI/CD integration with coverage thresholds
- Testing anti-patterns to avoid

**Use when**: Setting up test infrastructure, designing test strategy, implementing mocks

### python-venv-management.md
**Focus**: Python virtual environment creation and troubleshooting

**Key Concepts**:
- When to use single vs multiple environments
- Dependency conflict resolution
- Setup script patterns
- Environment activation and management
- Requirements file organization

**Use when**: Setting up Python environments, resolving dependency conflicts

### task-management (command: `/task`)
**Focus**: Military-inspired work tracking with structured escalation from tasks to operations orders

**Key Concepts**:
- Task list management (add, complete, block, unblock, assign, update)
- Escalation ladder: Task → TCS → CONOP → OPORD
- Decision point guidance for promotion between levels
- Backbrief generation for session progress reporting
- Team composition recommendations based on work domain
- Integration with session-start (review tasks) and session-end (update tasks)

**Use when**: Tracking work items, deciding how to scope work, promoting simple tasks to structured plans, generating progress reports, assigning agent teams to work

---

## Level 1: Project-Specific Skills

These skills are tailored to this specific project's domain and tooling.

*[Project-specific skills would be added here based on the project's domain]*

For paperboy, potential Level 1 skills might include:
- **source-integration.md**: News source connectors, API adapters, feed parsing
- **briefing-optimization.md**: Content curation, summarization, delivery formatting
- **scoring-tuning.md**: Relevance scoring, priority ranking, personalization algorithms

---

## Skill Structure Template

Every skill should follow this structure:

```markdown
---
name: skill-name
description: One-sentence description of when to use this skill
version: "1.0.0"
---

# Skill Title

**When to use**: Specific trigger conditions

---

## Overview

Brief description of the skill's purpose (2-3 sentences max)

**Philosophy**: "Core principle in quotes"

---

## Quick Reference

Tables, commands, or checklists for fast lookup

---

## Detailed Procedures

Step-by-step instructions for common tasks

---

## Examples

Real-world usage examples with code

---

## Troubleshooting

Common issues and solutions

---

## References

Links to relevant docs, tools, standards
```

---

## Content Guidelines

### DO:
- Include exact commands that can be copy-pasted
- Provide expected output examples
- Add safety warnings where relevant
- Use code blocks with syntax highlighting
- Add tables for quick reference
- Keep descriptions concise and actionable

### DON'T:
- Write overly verbose prose
- Include project-specific references in Level 0 skills
- Use vague descriptions ("might work", "usually")
- Duplicate information across skills
- Make assumptions about user knowledge

---

## Skill Maintenance

### When to Update Skills
- After discovering better procedures
- When finding new troubleshooting solutions
- After dependency or platform version changes
- When project structure changes (Level 1 only)

### Version Numbering
- **Patch** (1.0.0 → 1.0.1): Minor fixes, typos
- **Minor** (1.0.0 → 1.1.0): New sections, procedures added
- **Major** (1.0.0 → 2.0.0): Breaking changes, complete rewrites

---

## Skills vs Documentation

| Skills (`.claude/skills/`) | Docs (`docs/`) |
|---------------------------|----------------|
| HOW to do things | WHY and WHAT |
| Procedures, commands | Architecture, design decisions |
| Troubleshooting | Specifications |
| Quick reference | Learning resources |
| Interactive guidance | Historical context |

---

## Current Skill Inventory

```
.claude/skills/
├── SKILLS_FRAMEWORK.md          # This file
│
├── [Level 0: Universal]
│   ├── configuration-management.md
│   ├── session-end.md
│   ├── shift-left-testing.md
│   └── python-venv-management.md
│
├── [Level 0: Workflow Commands]
│   └── task management           # .claude/commands/task.md — escalation ladder, backbriefs
│
└── [Level 1: Project-Specific]
    └── (add as needed)
```

---

## Porting Skills to New Projects

When starting a new project:

1. **Copy Level 0 skills** directly (they're universal)
2. **Create project-specific Level 1 skills** as needed
3. **Update SKILLS_FRAMEWORK.md** to list project's Level 1 skills
4. **Never modify Level 0 content** for project-specific needs (create Level 1 instead)

---

**Maintained by**: Skills Framework
**Next Review**: When adding new skills or updating framework
