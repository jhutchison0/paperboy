# Briefing Quality Team

**Goal**: Improve distillation output — prompt engineering, section structure, word count, NotebookLM optimization — with mission alignment validated before implementation begins.

**When to use**: When changing how briefings are written: prompt rewrites, adding or reordering sections, tuning style guidance (3Blue1Brown framing, intuition-first depth), adjusting word counts, or optimizing output for two-voice podcast dialogue. Also use when auditing output quality against a sample of generated briefings.

## Composition

| Teammate | Role | Responsibility |
|----------|------|----------------|
| `proposer` | Analyst | Identify the quality gap or format requirement, survey existing prompt structure, propose approach to `docs/plans/` |
| `distiller-dev` | Implementer | Implement prompt changes, section structure, and style guidance in `src/distiller.py` |
| `test-runner` | Validator | Run `pytest` after each implementation step, report pass/fail counts and coverage gaps |
| `pipeline-sme` | Alignment gate | Validate that proposed changes serve Content Quality First (Pillar 1) and NotebookLM optimization — not just surface-level variety |

## File Ownership

| File | Owner |
|------|-------|
| `src/distiller.py` | distiller-dev |
| `src/models.py` | distiller-dev (BriefingDocument fields only) |
| `tests/` | distiller-dev (writes), test-runner (runs) |
| `docs/plans/` | proposer (writes) |
| `docs/` (analysis, findings) | pipeline-sme (writes) |

No changes to `src/pipeline.py` or `src/config.py` without explicit coordination with python-prototyper.

## Workflow

1. Lead assigns the quality task — include the gap observed (e.g., "sections run too long for listening," "opening hook isn't punchy enough") and any target briefing samples to reference
2. `proposer` reads `src/distiller.py` (full prompt templates), `src/models.py` (BriefingDocument), and recent output samples in `output/`; writes a proposal to `docs/plans/` covering: what changes, why they address the gap, and how they interact with the 8-section structure
3. `pipeline-sme` reviews the proposal against Pillar 1 (Content Quality First) and the NotebookLM optimization goal — writes a brief alignment note to `docs/`; flags if proposed changes optimize for novelty at the expense of depth or podcast listenability
4. Lead decides to proceed, revise, or reject
5. `distiller-dev` implements the approved changes in `src/distiller.py`; writes or updates tests in `tests/` to cover the changed prompt structure or section output
6. `test-runner` runs `pytest` and confirms new tests pass and no existing tests regress
7. If tests fail, `distiller-dev` fixes and `test-runner` re-validates
8. `pipeline-sme` does a final alignment check — reads a sample output if available, confirms the briefing still serves two-voice dialogue and 3Blue1Brown style
9. Lead reviews, commits, and updates `docs/sessions/` per session documentation policy

## Scaling Notes

- For minor wording tweaks or word-count adjustments in a single prompt section, `proposer` and `pipeline-sme` may be omitted — distiller-dev + test-runner is sufficient.
- For structural changes (adding a section, reordering the 8-section structure, changing the framing model), use the full 4-agent composition. Structural changes have cascading effects on all downstream briefings.
- `pipeline-sme` is the key differentiator for this team. Prompt engineering can drift toward what sounds good in isolation rather than what serves the podcast mission. The pipeline-sme holds that line.
- `test-runner` must never be removed. Prompt changes that break structured output format are silent failures without tests.
