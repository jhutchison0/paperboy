---
name: traversing-the-knowledge-base
description: Traverse this repo's knowledge base by its existing link graph (typed session-doc headers, markdown links, path mentions) instead of blind keyword search. Use when tracing why an artifact exists, assessing blast radius before editing a living doc, orienting on session lineage, or checking reference integrity.
---

# Traversing the Knowledge Base

The corpus is already a graph; walk it before you grep it. Session docs declare typed edges, CONTEXT.md hand-maintains a Reading Order, and every doc references others by link or path. Keyword search finds words; traversal finds structure: where a rule came from, what depends on it, and what a change will break.

## The graph that already exists

| Edge type | Where it lives | Snapshot (2026-09-10) |
|---|---|---|
| Typed relations: Follows, Documents, Implements, References, Completes, Requires, Cites | Session-doc headers, pinned by `docs/session-doc-format.md` | 15 of 15 session docs carry them |
| Markdown links `[text](path.md)` | All docs | 108 |
| Bare path mentions (backticked or plain prose) | Heaviest in `docs/tasks.md`, `.claude/upstream-update.md` | 875, outnumbering links 8:1 |
| Reading Order | `CONTEXT.md` | Hand-maintained orientation list |

Counts are method-dependent snapshots; the load-bearing fact is the ratio. A traversal that only follows `[text](path)` syntax misses most of the real graph. Match paths, not just links.

## Core traversals

**1. Lineage: where did this come from?** Walk the Follows chain backward from any session doc; walk Documents/Implements to the artifacts it produced.

```bash
grep -n "^\*\*Follows\*\*:" docs/sessions/<doc>.md      # one hop back; repeat
grep -rn "^\*\*Follows\*\*:.*<doc>" docs/sessions/       # one hop forward
```

**2. Blast radius: who depends on this?** Run before editing any living doc (CLAUDE.md, CONTEXT.md, LANGUAGE.md, format specs, skills). Inbound references are the dependents your edit can break.

```bash
grep -rln "$(basename <path>)" --include="*.md" . | grep -v ".venv"
```

**3. Neighbors: both directions, always.** Outbound = the links and paths inside the doc (read them). Inbound = the blast-radius grep above. One direction alone is half an answer.

**4. Why does this exist?** Chase the path between two docs from both ends: outbound links from A, backlinks to B, meet in the middle. Doctrine entries cite session docs; session docs cite reviews; reviews cite the evidence.

**5. Integrity: do the references still resolve?** `/pcc` check 5 runs this over the orientation surfaces (CLAUDE.md, CONTEXT.md, README.md, LANGUAGE.md, `.claude/README.md`, active tasks). Expected output: empty. Any MISSING line is a finding: record the check's count in the session doc, and a nonzero count fires the build trigger below.

Check 5 has three blind spots, listed in `.claude/commands/pcc.md` under the check: it cannot
see directory references, it resolves every path against the repo root, and a missing surface
costs coverage silently. A zero is clean only within those. Two foreign-corpus runs
(`contract-knowledge-graph` 2026-08-21, `aar_ai_pipeline` 2026-08-22) found all three.

## What grep cannot do here

`orphans()` (nothing links to a doc) and full-corpus `validate()` need the whole file universe enumerated first. Those are deferred to a ~150-line utility slice specified in the hub's `docs/plans/20260813_kb_graph_traversal_proposal.md` (tacsop, as amended 2026-08-14). Build trigger, either condition: an agent demonstrably misses an edge this skill's recipes should have surfaced, or `/pcc` check 5 reports a MISSING path beyond the baseline. When the trigger fires, build test-first per shift-left doctrine; do not build before.

## Evidence line

When a traversal informs your work, record one line in the session doc under Work Completed:

```
KB-graph: <traversal run> → <what it changed or confirmed>
```

Example: `KB-graph: backlinks of pillars.md → found 6 dependents, updated episode length in 2`. This line is the uptake metric; without it the skill cannot be evaluated.

## Success criterion (the falsifiable bet)

Window: the next five sessions after 2026-09-10 that touch docs/, tasks, or any cross-doc question.

- **M1 uptake**: at least 3 of 5 session docs carry a `KB-graph:` line. Measure: `grep -l "KB-graph:" docs/sessions/<the five>.md`.
- **M2 integrity**: `/pcc` check 5 stays at zero MISSING, and each run's count is recorded in the session doc (an unrecorded run is indistinguishable from an unrun check). Any MISSING line is simultaneously caught drift (good) and a build-trigger event.
- **M3 routing value**: at least 1 of the recorded KB-graph lines names an artifact the session then actually edited, verified at window close by someone other than the line's author (a decorative line written after the edit fails verification).

Outcomes at window close, full matrix, no undefined cells:

| | M3 >= 1 (verified) | M3 = 0 |
|---|---|---|
| **M1 >= 3/5** | Keep; report uptake upstream | Read but not load-bearing: extend the window 3 sessions; if still M3 = 0, drop the evidence-line requirement and keep the recipes as reference |
| **M1 < 3/5** | Value shown, uptake weak: one escalation rung (orientation pointer in `/session-start`) | Retire-or-escalate decision per the gradient philosophy in `.claude/skills/shift-left-testing/ENFORCEMENT.md` |

No cell triggers automatically; each outcome is a recorded human decision in `docs/tasks.md`.

## Version History

- **1.0.0** (2026-08-14): Initial in the hub. Adopted into paperboy 2026-09-10 with local edge counts, a fresh five-session window, and the hub's March allowlist dropped from traversal 5.
