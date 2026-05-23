# Session: Upstream Doctrine Adoption — Skills v2, ADR System, Shift-Left Hook

**Date**: 2026-05-22
**Branch**: main
**Tags**: #session #infra #doctrine #docs #complete #pillar-2 #pillar-4 #pillar-5

**Documents**: [pillars.md](../design/pillars.md) — All 5 pillars touched indirectly via doctrine artifacts
**References**: [.claude/upstream-update.md](../../.claude/upstream-update.md) — 2026-05-19 utils propagation entry (processed)
**Follows**: [20260521_honest_status_and_timeout_diagnostics.md](20260521_honest_status_and_timeout_diagnostics.md)
**Cites**: utils [ADR-0001](https://github.com/jhutchison0/utils/blob/main/docs/adr/0001-directory-form-mandatory-for-new-skills.md); Anthropic Skills Open Standard (Dec 2025); Matt Pocock [`mattpocock/skills`](https://github.com/mattpocock/skills)

---

## Summary

Adopted the largest upstream `utils` doctrine cycle to date (2026-05-19) in a single session: 6 new directory-form skills, the ADR system, paperboy-customized `LANGUAGE.md` + `CONTEXT.md`, a PostToolUse shift-left audit hook, Python 3.11 minimum, and a test-first inversion of the `python-prototyper` agent. Five legacy single-file skills (`shift-left-testing`, `configuration-management`, `python-venv-management`, `session-end`, `SKILLS_FRAMEWORK`) were deleted in favor of the v2 directory form. 40 files changed, 161 tests still passing. Audited by `pipeline-sme` and `code-reviewer` agents in parallel — 7 follow-up fixes applied before commit.

## Work Completed

### 1. Pre-flight Adaptation

Paperboy's repo state required three adjustments before the upstream helper could run cleanly:

- **Flat `src/` layout vs upstream's `src/<pkg>/` assumption.** Paperboy keeps modules directly under `src/` (`src/agent_runner.py`, `src/pipeline.py`, etc.). The helper's hook substitution replaces `myproject` in `*/src/myproject/*.py` — which would match nothing here. Resolved by hand-editing the generated hook glob to `*/src/*.py` post-copy.
- **5 existing single-file skills.** The helper's skip-if-exists semantics meant the new directory-form skills wouldn't land. Diffed each against upstream first to confirm no paperboy-specific content existed in the legacy files, then deleted them so the directory forms could be copied.
- **`.claude/settings.local.json` had team-wide content.** Renamed to `.claude/settings.json` (Anthropic convention) *before* running the helper so the PostToolUse hook block merged into the right file. Existing `env` (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) and `permissions` blocks were preserved.

### 2. Mechanical Adoption

Ran `python ~/projects/github/utils/scripts/adopt_doctrine.py --package paperboy --yes`. Helper copied:

- 6 directory-form skills (3 new doctrine skills + 3 refactored legacy skills)
- `docs/adr/ADR-FORMAT.md`, `docs/session-doc-format.md`
- `.claude/skills/SKILLS_FRAMEWORK.md` (v2 single-file spec)
- `.claude/hooks/post-tool-shift-left-audit.sh` with `myproject` → `paperboy` substitution
- PostToolUse hook block merged into `.claude/settings.json`
- `.gitignore` appended with `.claude/audits/` and `docs/design/hold/`

The `.claude/commands/session-end.md` was skipped by the helper (paperboy had local customizations); merged by hand to preserve paperboy commit tags while adopting the slimmed structure that references `docs/session-doc-format.md`.

### 3. Judgment-Required Artifacts

Customized for paperboy's domain:

- **`LANGUAGE.md`** — glossary organized around paperboy's domains: Pipeline Data Model (Paper, Article, ScoredPaper, Briefing, **Eight-Section Structure**, PipelineResult), Pipeline Stages, Sources, Backends (API / Agent / Auto / Keyword-Only), Result Semantics (Success / Partial / Error / Last Error), Agent Framework, Escalation Ladder, Governance, Workflow Artifacts, Military↔Civilian crosswalk, Anti-Glossary. Decision Science section from upstream was dropped — paperboy's scoring is a 2-criterion weighted sum, not MAUT.
- **`CONTEXT.md`** — paperboy-as-downstream framing (not a doctrine hub), 5 pillars woven into the Mission section so every pillar has a mission-level voice (not just framing in Constraints).
- **`docs/adr/0001-directory-form-mandatory-for-new-skills.md`** — re-attributed for paperboy. The local context: paperboy inherited 5 single-file skills from upstream v1 and had not refactored any of them, validating the upstream argument that the "migrate at >N lines" trigger self-violates.

### 4. Updated Agent + CLAUDE.md

- **`.claude/agents/python-prototyper.md`** — workflow inverted from "implement → test alongside" to test-first vertical-slice TDD with RED→GREEN cycles. `src/myproject/` references replaced with flat `src/`. Added a dataclass-additions carve-out (per `pipeline-sme` audit): pure field additions on `Paper`/`Article`/`ScoredPaper` are tested at the consumer, not in isolation.
- **`CLAUDE.md`** — Shift-Left Testing principle strengthened with explicit test-first vertical-slice language and references to the new hook + ENFORCEMENT.md gradient.

### 5. PostToolUse Audit Hook

`.claude/hooks/post-tool-shift-left-audit.sh` fires after every `Write`/`Edit` to `src/*.py`. Logs `OK_TEST_EXISTS` or `MISSING_TEST` to `.claude/audits/shift-left-violations.log`. Never blocks (exits 0 always). Verified end-to-end:

```
$ echo '{"tool_name":"Edit","tool_input":{"file_path":"...src/agent_runner.py"}}' \
    | .claude/hooks/post-tool-shift-left-audit.sh
exit=0
$ tail -1 .claude/audits/shift-left-violations.log
[2026-05-22T21:11:37-05:00] OK_TEST_EXISTS file=...src/agent_runner.py partner=tests/test_agent_runner.py
```

### 6. Audit + Fix Loop

Spawned `pipeline-sme` and `code-reviewer` agents in parallel. Verdicts: both `ADOPT WITH FIXES`. Applied 7 fixes before commit:

| Source | Fix | File |
|---|---|---|
| pipeline-sme | Add "Score for relevance" bullet to Mission | `CONTEXT.md` |
| pipeline-sme | Define **Eight-Section Structure** glossary entry | `LANGUAGE.md` |
| pipeline-sme | Verify backend order (API → Agent → keyword-only) in `_resolve_backend` | `src/pipeline.py:301` (no change needed; glossary correct) |
| pipeline-sme | Add dataclass-additions carve-out to test-first rule | `python-prototyper.md` |
| code-reviewer | Replace 3× `src/myproject/` with `src/` | `shift-left-testing/ENFORCEMENT.md` |
| code-reviewer | Add `PAPERBOY-NOTES.md` carving out skill sections that don't apply (profiles, ConfigLoader, `${ENV_VAR}` substitution) | `configuration-management/` |
| code-reviewer | Verify session-end command not truncated | `.claude/commands/session-end.md` (verified, 75 lines, complete) |

The `PAPERBOY-NOTES.md` was load-bearing: without it, the next time an agent invokes the `configuration-management` skill, it would recommend creating `config/profiles/` and a `ConfigLoader` class with `${ENV_VAR}` substitution — directly contradicting Pillar 5's "YAML files are the source of truth, Python reads YAML directly" stance.

## Key Decisions

| Decision | Rationale |
|---|---|
| Hand-edit hook glob to `*/src/*.py` rather than refactor to `src/paperboy/` | Refactor would touch every import statement in the repo. The glob edit is one line and matches paperboy's actual layout. Future `src/paperboy/` refactor needs only the glob updated. |
| Drop Decision Science section from `LANGUAGE.md` | Paperboy's selector is a 2-criterion weighted sum (~30 lines). The MAUT vocabulary (utility, value function, sensitivity analysis, robust pick) is upstream-specific and would be aspirational here. Decision-scientist agent was already adopted earlier under similar logic (per existing memory). |
| Add `PAPERBOY-NOTES.md` rather than fork the configuration-management skill | Forking diverges from upstream and complicates future doctrine adoption. A sidecar that explicitly carves out non-applicable sections preserves the option to adopt those sections later if paperboy's config grows, without silent expansion. |
| Annotate upstream-update.md rather than delete it | The file already follows an "annotate when applied" pattern for earlier entries (2026-03-26, 2026-03-31). Annotating the 2026-05-19 entry with disposal per-artifact preserves the propagation history for future reference. |
| Skip `docs/propagation-protocol.md` | Paperboy is a downstream consumer, not a propagation hub. The protocol is only relevant to repos that serve doctrine to others. |
| One bundled commit rather than 6+ topical commits | Doctrine adoption is one logical unit — splitting would produce false-independent commits where every piece references the others. A single bundled commit with a structured message gives `git log` the right grain. |

## Pillar Compliance

| Pillar | Status | Notes |
|---|---|---|
| **Content Quality First** | UNCHANGED | No briefing/distillation code touched. |
| **Source Diversity & Resilience** | UNCHANGED | No sourcer code touched. |
| **Relevance Through Hybrid Scoring** | UNCHANGED | No selector code touched. Pillar now explicitly named in `CONTEXT.md` Mission. |
| **Pipeline Idempotency** | PASS | Hook writes to `.claude/audits/` only — does not contaminate `tests/` or `output/`. Same date + same config still produces same briefing. |
| **Extensibility by Design** | PASS | Skills framework v2 (progressive disclosure via sidecars) is itself an extensibility win. ADR system creates a durable surface for future decisions. |

## Commits

| Hash | Subject |
|---|---|
| `c61b79d` | `[doc][infra] Adopt upstream utils 2026-05-19 doctrine cycle` |

40 files changed, 6001 insertions(+), 4027 deletions(-).

## What This Doesn't Change

- No pipeline code (`src/`) was modified. Selection, distillation, sourcing, agent runner all unchanged.
- 161 tests pass identically to the baseline. The adoption added no new tests because no new pipeline behavior shipped.
- The known reliability concerns from prior sessions (blog feed audit, no temperature control on CLI path, batch_size=1) remain on `docs/tasks.md`.

## Next Steps

- [ ] Push `c61b79d` to `origin/main` (1 commit ahead).
- [ ] Pre-existing P3 tasks still standing:
  - [ ] Blog feed audit (5 of 6 feeds returned 0 articles on 2026-05-19; Pillar 2 risk)
  - [ ] Agent backend: no temperature control on CLI path (Pillar 4 — idempotency gap)
  - [ ] Batch scoring: batch_size=1 vs target 5
  - [ ] Update CONOP checklist phases with completion status
- [ ] Cosmetic follow-up flagged by code-reviewer (non-blocking): 5 src modules (`selector.py`, `distiller.py`, `models.py`, `config.py`, `pipeline.py`) don't have strict `tests/test_<name>.py` partners — their behavior is covered by behavioral test files (`test_pipeline_backend.py`, `test_config_validation.py`, `test_dedup.py`, `test_pipeline_outcomes.py`) but the audit will log `MISSING_TEST` on every future edit. Decide whether to add convention waiver to `ENFORCEMENT.md` or rename test files.
- [ ] First real exercise of the new doctrine: next non-trivial code change should invoke `recording-architecture-decisions` to gauge how often the triple filter actually trips, and use `maintaining-ubiquitous-language` when a new pipeline term emerges.
