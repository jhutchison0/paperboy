# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Principles

### Shift-Left Testing (test-first, vertical-slice)
Every new behavior in `src/` is driven by a **failing test written first**, followed by the **minimum implementation** that makes it pass, then the next slice. This is vertical-slice (tracer-bullet) TDD; see [`.claude/skills/shift-left-testing/VERTICAL-SLICING.md`](.claude/skills/shift-left-testing/VERTICAL-SLICING.md).

Do not write a horizontal slice (all tests first, then all impl). Do not write production code without a failing test driving it.

A `PostToolUse` audit hook (`.claude/hooks/post-tool-shift-left-audit.sh`) fires after every `Write`/`Edit` to `src/**/*.py` and logs evidence to `.claude/audits/shift-left-violations.log`. The hook does not block; it produces an audit trail. See [`.claude/skills/shift-left-testing/ENFORCEMENT.md`](.claude/skills/shift-left-testing/ENFORCEMENT.md) for the full enforcement gradient.

- **Python** (`tests/`) — pytest suites for sourcing, selection, distillation, pipeline, config

### Simplicity First
Make every change as simple as possible. Avoid massive or complex changes. Every change should impact as little code as necessary. When in doubt, prefer the simpler solution. Prefer deep modules (small interfaces hiding meaningful implementation) over shallow ones; before declaring an interface done, ask whether each parameter is load-bearing or whether the function could derive it from one it already has.

### Branching (short-lived topic branches by work shape)
Branch on the shape of the work, not on a permanent partition of the codebase. Lead-only doc/ADR/small-refactor work lands directly on `main`. Team-deployed or multi-agent code work with an audit gate uses a short-lived `topic/<scope>-<slug>` branch, merged via merge-commit at the gate and **deleted (local + origin) immediately after merge**. No permanent domain branches. See [`.claude/skills/using-topic-branches/SKILL.md`](.claude/skills/using-topic-branches/SKILL.md), which also covers auditing standing branches.

### Session Documentation
Document work in `docs/sessions/YYYYMMDD_*.md`. See `config/project.yaml` for phase tracking.

### Bulk Data Storage
Paperboy is scope: personal (`config/project.yaml`). Bulk data it may someday write (Phase 4 audio, archives) goes to home storage per `.claude/skills/lake-conventions/HOME-STORAGE.md`, never the work lake. No storage address goes in git; role-named `HOME_*` variables in `.env` carry the real paths. Today the pipeline writes only small gitignored markdown to `output/`, so no `HOME_*` variables exist yet; add them with the first bulk-data write.

### Knowledge-Base Traversal
The docs form a link graph (typed session-doc headers, markdown links, path mentions). Walk it before you grep it: recipes in [`.claude/skills/traversing-the-knowledge-base/SKILL.md`](.claude/skills/traversing-the-knowledge-base/SKILL.md). `/pcc` check 5 verifies the references still resolve.

### Documentation Style
When creating diagrams in markdown documentation, **prefer Mermaid over ASCII art**. Mermaid renders natively in GitHub and provides clear, maintainable visualizations.

## Prose Style

All prose artifacts follow the writing-simple-and-direct skill. The kernel:

1. Have a point; state it in the first sentence. No throat-clearing.
2. Prefer the concrete word: name the file, the number, the failure.
3. One idea per sentence. Link sentences; do not pack them.
4. Active voice unless the actor is unknown or irrelevant.
5. Cut cruft words. The banned list lives in LANGUAGE.md.
6. Hedge with numbers or not at all.
7. Read it back; if you would not say it, do not write it.
8. No em dashes in running prose. Choose the mark that states the relationship.

Schemas define what a document contains; this defines how the words go.
Never cut a required section to save tokens.

## Figure Style

All data displays follow the designing-clear-data-displays skill. The kernel:

1. Show the data; erase ink that carries none, within reason.
2. Label the data where it lives; a key the eye must decode fails.
3. Make every distinction as subtle as it can be and still be seen.
4. Two marks too close make a third; move one, do not shrink both.
5. Show the effect at its true size: lie factor between 0.95 and 1.05.
6. Answer "compared to what?"; small multiples over one lonely chart.
7. Document the display: title, source, units, scale on the figure.
8. Content counts most: simple design, intense content.

Schemas and a repo's UX rules define what a display must contain; this defines how the ink goes.
Before the eight: could a table or a sentence carry these numbers? Under about twenty, a table usually does (VDQI p. 56).
A UX rule that asks for a less dense display wins; state the override.

## Claim Style

Every claim a reader will act on (that something works, landed, synced, exists, or is absent) follows the verifying-claims skill. The kernel:

1. Name the state: written, tested, deployed, or observed. Claim no higher than your evidence reaches. An absence is a claim too.
2. Evidence comes from this turn, after the last change to the thing claimed. Earlier output is stale: re-run the check, re-measure the number.
3. Check the outcome the claim names, with a check that can fail. A launcher's exit 0 is not the outcome; no error is not evidence.
4. Under each claim a reader will act on, put an `Evidence:` line with the command and its output, or `UNVERIFIED: <blocker>`. A skipped check is not a blocker; run it.
5. A checkout a timer or service runs from is deployed only when clean: `git status --porcelain` prints nothing.
6. Probes read; they never write to the system they check.

A plan, an opinion, or an explanation of code is not a claim. The belief a plan rests on is one: check it before you act.
A diff shown in the same message is its own evidence. Say what you did not do; that needs no `Evidence:` line.
`/session-end` gathers the session's claims into a `## Claims` table.

## Picture Style

Every statement about what is true now (a host, a count, a schedule, a coverage figure, a version) follows the maintaining-the-common-operating-picture skill. The kernel:

1. The rendered picture is never hand-edited; its inputs may be.
2. Every line is a measurement or an estimate, and an input or an outcome, and says which. A measurement carries value, time, collector, subject, universe and shape; an estimate carries a range, its basis, and the observation that would prove it wrong.
3. Every quantity declares how it moves (constant, drifting, scheduled) and what would be a surprise; the picture shows the last measurement, its age, and the projection, and flags the surprise.
4. Supersede in place, never overwrite; tests count unmarked lines only.
5. Gaps are listed, each naming its collector and the decision it blocks, and the list is never empty.
6. Read the picture before you measure or assert state; re-measure for a named cause, never for comfort.
7. One horizon per line, not per document: current operations measured by command, the running estimate maintained, plans as intent with gates that name their command. Records keep every horizon and are never rewritten.
8. Never report clean: checked with its fields, or unchecked with a reason and no value.

A claim about what this turn changed follows Claim Style; a standing fact this turn did not touch follows this.
`assessment` is the process, never a line. A periodic report is a measurement at its stamp and an estimate thereafter.

## Environment Setup

This project uses **uv** (Astral) for interpreters, environments, and packages. **All commands must run inside the venv.**

```bash
# First-time setup
curl -LsSf https://astral.sh/uv/install.sh | sh   # If uv is not installed
uv python install 3.12             # uv-managed interpreter (no system coupling)
uv venv --managed-python           # Create .venv on the managed interpreter
uv pip install -r requirements.txt
cp .env.example .env               # Add your ANTHROPIC_API_KEY
```

**Always use the venv's Python/pytest**:
```bash
source .venv/bin/activate           # Activate before working
# OR use the venv directly:
.venv/bin/pytest                    # Run tests without activating
.venv/bin/python main.py run        # Run pipeline without activating
```

## Quick Commands

```bash
# Run tests (venv must be active, or use .venv/bin/pytest)
pytest                             # All tests
pytest -k test_sourcer             # Tests matching pattern
pytest -k "selector and keyword"   # Multiple keywords
pytest -x                          # Stop on first failure
pytest --pdb                       # Debug on failure

# CLI
python main.py --help              # Show all commands
python main.py run                 # Run full pipeline (today's date)
python main.py run --date 2026-03-10  # Run for specific date
python main.py source              # Source papers only
python main.py select              # Score and select only
python main.py distill             # Distill briefing only

# Task Management (slash commands)
/task                              # List active tasks
/task add <description>            # Add a new task (default P2)
/task done <task>                  # Mark task complete
/task block <task> — <reason>      # Mark task blocked
/task promote <task>               # Escalate to TCS/CONOP/OPORD
/task brief                        # Generate session backbrief
/task plan <task>                  # Get planning recommendation
```

## Project Overview

Paperboy is an AI research podcast pipeline. It sources academic papers from ArXiv and blog articles from RSS feeds, scores them for relevance using hybrid keyword + Claude semantic scoring, distills the best into structured markdown briefings optimized for Google NotebookLM's two-voice podcast generation.

The target user is a research scientist who wants daily AI briefings tailored to their work, consumed during exercise or commute via podcast.

### About the Name

The name "Paperboy" is a lighthearted nod to the 1985 arcade game: the image of riding an exercise bike while getting ArXiv papers delivered. But the arcade and fitness angles are flavor, not focus. This repo's primary mission is **daily academic paper curation and delivery**. The delivery mechanism happens to be TTS consumed during a workout, which makes the name fun, but code, features, and documentation should stay grounded in the research pipeline domain. Don't theme things around arcades, bikes, or fitness.

## Tech Stack

- **Language**: Python (3.11+)
- **Dependencies**: arxiv, feedparser, anthropic, click, pyyaml, python-slugify, python-dotenv, python-dateutil

## Architecture

```mermaid
flowchart TD
    AX[ArXiv API] --> SM[SourceManager]
    RSS[RSS Feeds] --> SM
    SM --> SEL[PaperSelector<br/>keyword + Claude scoring]
    SEL --> DIST[BriefingDistiller<br/>Claude-powered 8-section output]
    DIST --> MD[Markdown Briefing]
    MD --> NLM[Google NotebookLM<br/>two-voice podcast]

    subgraph Sources["Source Layer (sourcer.py)"]
        AX
        RSS
        SM
    end

    subgraph Selection["Selection Layer (selector.py)"]
        SEL
    end

    subgraph Distillation["Distillation Layer (distiller.py)"]
        DIST
    end
```

**Key principle**: The pipeline is modular. Each stage (source, select, distill) can run independently and produces a well-defined output that feeds the next stage.

## Workflow Commands

The project uses military-inspired slash commands for structured development workflow:

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/session-start` | Load context, check health, review tasks | Start of every session |
| `/session-end` | Commit, update tasks, write session doc | End of every session |
| `/task` | Manage task list, escalate work items | Track and plan work |
| `/pcc` | Pre-Code Check — fast pass/fail checklist | Before every push |
| `/pci` | Pre-Code Inspection — context-aware review | Before merge/PR or when PCC passes but confidence is low |
| `/sitrep` | Status report — narrative outbrief with concrete details | Team updates, progress summaries, scope-filtered status |
| `/implement-source` | Guided workflow for adding a new content source | Adding ArXiv categories, RSS feeds, API sources |

### Planning Escalation

Work scales through four levels. Use `/task promote` or `/task plan` to evaluate:

1. **Task** — One person, one session, clear action (`docs/tasks.md`)
2. **TCS** — Multi-step with pass/fail criteria (Task, Condition, Standard); also the universal task detail unit within all plan types
3. **CONOP** — Multi-wave with design decisions and parallel tracks (`docs/plans/`)
4. **OPORD** — Sequential execution of a decided strategy in waves (`docs/plans/`)

**Terminology**: *Phases* are strategic roadmap milestones (`project.yaml`). *Waves* are tactical parallel execution units within CONOPs/OPORDs where agent teams deploy.

## Project Structure

```
paperboy/
├── main.py                    # CLI entry point (click)
├── src/
│   ├── __init__.py
│   ├── config.py              # YAML config loader + validation
│   ├── models.py              # Paper, Article, ScoredPaper, BriefingDocument
│   ├── sourcer.py             # ContentSourcer ABC, ArxivSourcer, BlogSourcer, SourceManager
│   ├── selector.py            # PaperSelector (keyword + Claude scoring)
│   ├── distiller.py           # BriefingDistiller (Claude-powered, 8-section output)
│   ├── pipeline.py            # DailyPipeline orchestrator, PipelineResult
│   ├── agent_runner.py        # AgentRunner: claude -p subprocess backend
│   ├── machine.py             # Machine roster lookup (config/project.yaml machines:)
│   ├── gaps.py                # Gap register checker (docs/gaps.md)
│   └── tts_interface.py       # TTSProvider ABC, stubs for future TTS
├── config/
│   ├── paperboy.yaml          # ArXiv categories, blogs, keywords, Claude settings
│   └── project.yaml           # Project identity, version, phases
├── tests/                     # pytest suites
│   └── test_pipeline.py       # Integration tests
├── docs/
│   ├── tasks.md               # Task list; the ## Focus section at its head
│   ├── gaps.md                # Gap register: what nobody can see yet
│   ├── design/
│   │   ├── pillars.md         # 5 design pillars
│   │   └── roadmap.md         # Project roadmap
│   ├── sessions/              # Session documentation
│   └── plans/                 # Implementation plans
├── output/                    # Generated briefings (gitignored)
├── requirements.txt
├── .env.example
└── CLAUDE.md
```

## Current Phase

**Phase 2 — Configuration & Polish**: Agent/command alignment, error handling, CLI refinements. Phase 1 (core pipeline: Source, Select, Distill, Save) is complete and working end-to-end.

See `config/project.yaml` for all 6 build phases with status tracking.

## Config Workflow

YAML files in `config/` are the source of truth. Python reads YAML directly; no JSON sync step is needed.

- `config/project.yaml` — Project identity, phases, paths
- `config/paperboy.yaml` — ArXiv categories, blog feeds, focus keywords, Claude API settings, selector weights, distiller preferences

API keys live in `.env` (never committed). See `.env.example` for required variables.

## Agents and Teams

**IMPORTANT**: Before deploying any agent team or multi-agent plan, read `.claude/README.md` for the current roster and usage guide. Match agents to the work; don't invent ad-hoc roles when a prepositioned agent already covers the need.

### Agent Roster

Defined in `.claude/agents/`. See `.claude/README.md` for detailed usage guidance.

| Agent | Model | Writes Code? | Primary Domain |
|---|---|---|---|
| `pipeline-sme` | inherit | No | Mission alignment, roadmap, pillars |
| `proposer` | sonnet | No | Solution space exploration, pre-implementation proposals and debate |
| `content-curator` | sonnet | Yes | Sources, selection, scoring |
| `distiller-dev` | sonnet | Yes | Briefing quality, prompts |
| `test-runner` | haiku | No | All — runs pytest, reports results |
| `python-prototyper` | sonnet | Yes | Pipeline implementation |
| `code-reviewer` | inherit | No | All — reviews against pillars |
| `decision-scientist` | inherit | No | Weights, scoring fairness, bias, stats |

All have persistent memory in `.claude/agent-memory/`. Manage with `/agents`.

### Team Templates

Defined in `.claude/teams/`. Choose the template that matches the work domain:

| Template | Domain | Agents |
|---|---|---|
| `source-development.md` | ArXiv/RSS sourcing | proposer + content-curator + test-runner + code-reviewer |
| `feature-development.md` | Pipeline features | proposer + python-prototyper + test-runner + code-reviewer |
| `briefing-quality.md` | Distillation & output | proposer + distiller-dev + test-runner + pipeline-sme |
| `bug-fix.md` | Regression-first bug fixes | python-prototyper + test-runner |
| `code-review.md` | Quality audits (no code changes) | code-reviewer + test-runner |

**File ownership is critical**: structure tasks so each teammate owns distinct files. See the team template for recommended ownership splits.

**Key commands for team leads**:
- `Shift+Up/Down` — Navigate between teammates
- `Shift+Tab` — Toggle delegate mode (coordination-only)
- `Ctrl+T` — Toggle shared task list
