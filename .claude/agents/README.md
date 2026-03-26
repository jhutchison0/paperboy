# Agent Roster

This directory contains the project's prepositioned agents. **Read this before deploying any multi-agent plan or CONOP.**

Each agent's `.md` file is the authoritative definition of its role, boundaries, and workflow. This README is the index and composition guide -- it tells you which agents to pick and how to wire them into teams.

## The Roster

| Agent | Model | Writes Code? | Primary Domain |
|-------|-------|-------------|----------------|
| `pipeline-sme` | inherit | No | Mission alignment, roadmap, pillars, design direction |
| `proposer` | sonnet | No | Solution space exploration, proposal writing, pre-implementation debate |
| `content-curator` | sonnet | Yes | Source configuration, selection tuning, keyword/scoring weights |
| `distiller-dev` | sonnet | Yes | Briefing quality, prompt engineering, NotebookLM optimization |
| `test-runner` | haiku | No | All -- runs pytest, reports results |
| `python-prototyper` | sonnet | Yes | Full Python implementation across pipeline, CLI, config |
| `code-reviewer` | inherit | No | Reviews against 5 pillars, code quality, security |

For detailed usage, boundaries, and workflow for each agent, read its `.md` file in this directory.

## How to Compose a Team

### Scope Matrix

| Path | test-runner | code-reviewer | proposer | pipeline-sme | python-prototyper | content-curator | distiller-dev |
|------|:-----------:|:-------------:|:--------:|:------------:|:-----------------:|:---------------:|:-------------:|
| `src/sourcer.py`, `src/selector.py` | Read/Run | Read | Read | Read | Write | **Write** | — |
| `src/distiller.py` | Read/Run | Read | Read | Read | Write | — | **Write** |
| `src/pipeline.py`, `src/config.py`, `main.py` | Read/Run | Read | Read | Read | **Write** | — | — |
| `src/agent_runner.py`, `src/models.py` | Read/Run | Read | Read | Read | **Write** | Write | Write |
| `config/paperboy.yaml` | Read | Read | Read | Read | Write | **Write** | Write |
| `config/project.yaml` | Read | Read | Read | Read | Write | — | — |
| `tests/` | **Read/Run** | Read | Read | — | **Write** | Write | — |
| `docs/` | — | **Write** (reports) | **Write** (proposals) | **Write** (analysis) | Write | — | — |
| `.claude/` | — | Read | Read | Read | — | — | — |

**Bold** = primary owner. Regular "Write" = secondary. Dash = no access needed.

### Step 1: Match the template

Check `.claude/teams/` for a template that fits:
- **New content source** -> `source-development.md`
- **Pipeline feature / CLI** -> `feature-development.md`
- **Briefing quality work** -> `briefing-quality.md`
- **Bug fix** -> `bug-fix.md`
- **Quality audit** -> `code-review.md`

Each template documents its own task ordering, scaling options, and tips.

### Step 2: Scale to the work

Not every task needs 7 agents. Scale to fit:

| Work Size | Example | Agents |
|-----------|---------|--------|
| Config tweak | Add a new RSS feed URL | content-curator + test-runner (2) |
| Scoring tune | Adjust keyword weights or threshold | content-curator + test-runner + code-reviewer (3) |
| New source type | Add a new ContentSourcer implementation | python-prototyper + test-runner + code-reviewer (3) |
| Prompt rewrite | Overhaul distillation prompt sections | distiller-dev + test-runner + code-reviewer (3) |
| New pipeline stage | Add PDF extraction or TTS export | python-prototyper + test-runner + code-reviewer + pipeline-sme (4) |
| Full CONOP | New output format or major architecture change | proposer + code-reviewer + pipeline-sme (design phase), then python-prototyper + test-runner + code-reviewer (build phase) |

### Step 3: Assign file ownership

Every file must have exactly one owner. If two agents need to touch the same file, restructure the task. See the team template for ownership splits.

Typical ownership boundaries:
- `src/sourcer.py`, `src/selector.py`, `config/paperboy.yaml` -> content-curator or python-prototyper
- `src/distiller.py`, `src/models.py` (BriefingDocument) -> distiller-dev or python-prototyper
- `src/pipeline.py`, `src/config.py`, `main.py` -> python-prototyper
- `tests/` -> python-prototyper (writes), test-runner (runs)

## Common Mistakes

**Inventing ad-hoc roles**: If a CONOP says "create a scoring agent" -- check if `content-curator` already covers the need. Don't create a new agent persona when a prepositioned one exists.

**Skipping the pipeline-sme on new CONOPs**: New plans are exactly when mission alignment matters most. The pipeline-sme costs little and catches drift early -- before code is written, not after.

**Letting distiller-dev and content-curator overlap**: The curator owns what goes IN (sources, selection). The distiller-dev owns what comes OUT (briefing quality, prompt engineering). If work touches both sides of the pipeline, split it into two tasks with clear ownership.

**Forgetting source resilience**: Any change to sourcing must handle failure gracefully. If one feed or ArXiv category breaks, the pipeline must continue. The code-reviewer enforces this.

## Updating the Roster

When the project's needs evolve, update:
1. The agent file in this directory (authoritative source)
2. This README's roster table
3. The agent table in `CLAUDE.md`
