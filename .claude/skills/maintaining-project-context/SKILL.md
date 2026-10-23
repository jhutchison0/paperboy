---
name: maintaining-project-context
description: Maintain CONTEXT.md at the repo root capturing the project's identity, mission, current state, and key constraints. Use at the start of significant new work, when the project mission or scope changes, when an agent needs to understand the project quickly, or when the project's relationship with downstream consumers changes.
version: "1.1.0"
---

# Maintaining Project Context

CONTEXT.md is a one-page narrative of what a project is, what it cares about, and the constraints on how it operates. It is the file you would hand to a new contributor (human or agent) who has 60 seconds to understand the project well enough to act in alignment with it.

Adapted from Matt Pocock's `grill-with-docs` pattern, distinct from LANGUAGE.md (which defines terms) and `config/project.yaml` (which holds machine-readable identity).

## When to Use

Invoke this skill when:

- Significant new work begins: a new phase, a new mission, a structural change to how the project relates to its consumers.
- The project's mission or scope materially shifts (not for routine task progress).
- A new agent or human contributor needs to ramp up quickly and needs project orientation.
- The relationship with downstream consumers changes (new repos joining, repos leaving, propagation protocol changes).
- A key constraint is discovered or relaxed (e.g., a hard rule becomes a soft preference, or vice versa).

Do **not** invoke this skill for:
- Routine task completion or session progress — those go in session docs.
- Code-level decisions — those are commits or, when warranted, ADRs.
- Status updates — those are SITREP / status-report.

## CONTEXT.md Format

The canonical sections, in order:

```markdown
# CONTEXT.md — What This Project Is

[One-paragraph orientation. What this project is. Why it exists.]

## Identity
[1–2 paragraphs. What the project IS, not what it does. Distinguishing facts.]

## Mission
[Bullet list. Goals at the project level, not task level.]

## Current State
[Where each part of the current state lives, never a snapshot of it: version and phase in config/project.yaml, the campaign focus in docs/tasks.md, known unknowns in docs/gaps.md, the last session in docs/sessions/, and the command that measures anything that drifts. A count or a "most recent" written here reads as current after it stops being true.]

## Constraints
[Pillars, hard rules, anti-rules. Things that govern decision-making.]

## Key Relationships
[Downstream consumers, agent roster summary, team templates.]

## Reading Order for New Agents and Contributors
[Numbered list of files to read, in order.]

## Distinguishing This File from Adjacent Artifacts
[Small table: CONTEXT vs LANGUAGE vs project.yaml vs CLAUDE.md vs sessions vs plans.]
```

The body should fit on one or two screens. If CONTEXT.md is creeping past ~250 lines, it's drifting into spec territory: extract the detail to a design doc and link.

## Distinguishing CONTEXT.md from Adjacent Artifacts

| Artifact | What it answers |
|---|---|
| `CONTEXT.md` | *What is this project and what does it care about?* |
| `LANGUAGE.md` | *What do specific terms mean in this project?* |
| `config/project.yaml` | *What is the project's machine-readable identity?* |
| `docs/tasks.md` | *What comes next, and in what order?* (the `## Focus` section) |
| `docs/gaps.md` | *What can nobody see yet, and what does that block?* |
| `CLAUDE.md` | *What conventions and commands does the agent need at hand?* |
| `docs/sessions/` | *What was just worked on?* |
| `docs/plans/` | *What is planned next?* |
| `docs/adr/` | *Why was a hard-to-reverse decision made?* |

Do not duplicate content across these files. When tempted, ask: "Which one of these is this *really* about?" and put it there.

CONTEXT.md is the **narrative** counterpart to `config/project.yaml`'s **structured** identity. They reinforce each other. If they disagree on version or phase, treat `project.yaml` as authoritative and update CONTEXT.md. Neither holds measured state: that is measured by command when it is needed (the `maintaining-the-common-operating-picture` skill).

## Workflow

When CONTEXT.md needs an update:

1. **Identify the trigger.** Which one of the "When to Use" conditions fired?
2. **Locate the right section.** Identity, Mission, Current State, Constraints, Key Relationships, or Reading Order? Most updates touch one section.
3. **Make the minimum change.** A new constraint = one new bullet. A new downstream relationship = one row in the Key Relationships section.
4. **Cross-check `config/project.yaml`.** If your update touches identity (version, phase), make sure the YAML still agrees. If not, update the YAML in the same change. Active work is not here: it is the `## Focus` section of `docs/tasks.md`.
5. **Update the `Last Updated` date at the bottom of CONTEXT.md.**
6. **Confirm with the user.** Changes to CONTEXT.md are policy-level. Always confirm before committing.

## What CONTEXT.md Is Not

- A status report (use SITREP / status-report).
- A specification of any specific feature (use design docs in `docs/design/`).
- A glossary of terms (use LANGUAGE.md).
- A history of what changed (use `docs/sessions/` and git log).
- A list of every constraint imaginable (only the ones that actively govern decisions belong).

## Sources

- Matt Pocock, [`mattpocock/skills/skills/engineering/grill-with-docs/`](https://github.com/mattpocock/skills) — the inspiration; we adapted format and discipline.
- This project's [CONTEXT.md](../../../CONTEXT.md) — the artifact this skill maintains.
- This project's [LANGUAGE.md](../../../LANGUAGE.md) — companion glossary.
- This project's [config/project.yaml](../../../config/project.yaml) — machine-readable identity.

## Version History

- **1.1.0** (2026-10-04): Current State names where each part of the state lives instead of holding a snapshot, and `config/project.yaml` is identity, not state. The hub's own snapshot still named the 2026-04-21 propagation as the latest after three later cycles. Slice 2 of the hub's common operating picture.
- **1.0.0** (2026-05-19): First version.
