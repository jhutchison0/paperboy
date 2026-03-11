# Session: Live End-to-End Test with Agent Backend

**Date**: 2026-03-11
**Branch**: main
**Tags**: #session #pipeline #agent #cli #config #test #complete #pillar-1 #pillar-2 #pillar-5

**Documents**: [pillars.md](../design/pillars.md) — Pillar 1 (Content Quality), Pillar 2 (Resilience), Pillar 5 (Extensibility)
**Follows**: [20260311_phase2_error_handling_and_cli.md](20260311_phase2_error_handling_and_cli.md)
**CONOP Success Criterion**: P0 live end-to-end run with `--backend agent` against real ArXiv data — **ACHIEVED**

---

## Summary

First live end-to-end pipeline run using the AgentRunner (Claude Code CLI) backend against real ArXiv papers and RSS feeds. Pipeline successfully sourced 97 candidates, scored top 5 via Claude CLI, selected a winner, distilled a 4058-word briefing, and saved it to disk. The briefing was uploaded to Google NotebookLM and produced a ~20-minute two-voice podcast episode. Two bugs were found and fixed during testing.

## Live Test Results

| Stage | Result | Details |
|-------|--------|---------|
| Source | PASS | 84 ArXiv papers + 13 blog articles (97 total) |
| Select (agent) | PASS | 5 papers Claude-scored via CLI, top pick: MedMASLab (0.65) |
| Distill (agent) | PASS (2nd run) | 4058-word briefing, all 8 sections, ~2.5 min generation |
| Save | PASS | `output/briefings/2026-03-11_medmaslab-...md` |
| NotebookLM | PASS | ~20 min podcast episode generated successfully |

### First run failure

The first `run --backend agent` attempt failed at distillation — both attempts timed out at 120s. The 4500-word briefing generation through the CLI subprocess needed more time than the configured timeout allowed. After bumping `distill_timeout` to 300s, the second run succeeded in ~163s.

## Bugs Found & Fixed

| Bug | Root Cause | Fix |
|-----|-----------|------|
| Distill timeout too short | `distill_timeout: 120` insufficient for 4500-word CLI generation | Bumped to 300s in `config/paperboy.yaml` |
| Misleading success message | `backend == "keyword-only"` string check missed `auto` resolving to keyword-only | Changed to `pipeline.distiller is None` (checks actual state, not CLI arg) |

The second fix was caught during PCI review (dice hook Nat 1). The original code would have told users "Briefing generation failed" when `auto` mode legitimately resolved to keyword-only — confusing but not data-losing.

## Design Decisions

- **300s distill timeout**: Based on observed ~163s generation time. Provides ~2x headroom for longer papers or slower CLI responses. Configurable in YAML if users need to tune further.
- **`pipeline.distiller is None` over string check**: Tests actual pipeline state rather than the CLI argument string. This respects the auto-resolution chain and is resilient to future backend additions (Pillar 5).

## Pillar Alignment

- **Pillar 1 (Content Quality)**: First real briefing produced and validated through NotebookLM. All 8 sections present, 3Blue1Brown style confirmed, ~20 min podcast generated.
- **Pillar 2 (Resilience)**: Timeout fix improves graceful degradation. Pipeline survived Anthropic RSS parse error and 2/5 scoring retries without crashing.
- **Pillar 5 (Extensibility)**: State-based check (`distiller is None`) is more robust than string matching against backend names.

## Observations (Not Bugs)

| Observation | Severity | Notes |
|-------------|----------|-------|
| Anthropic RSS feed parse error | Low | Feed may have changed XML format. Pipeline degrades gracefully. |
| 2/5 scoring attempts get preamble-only CLI output | Low | Retries succeed. CLI hooks/preamble text interferes with JSON parsing. |
| YAML frontmatter wrapped in markdown code fence | Cosmetic | NotebookLM handled it fine. |

## Test Coverage

- **5 new tests** in `tests/test_cli_output.py` covering all 3 output branches in the `run` command
- Key test: `test_auto_resolving_to_keyword_only_shows_keyword_message` — validates the PCI fix
- Full suite: 94/94 passing (was 89, +5 new)

## Next Session Plan

1. **Deferred items from previous session**: I5 (keyword-only paper retention after Claude scoring), I6 (blog `content` lost in `to_paper()`), I9 (temperature flag for `claude -p`)
2. **Phase 2 completion assessment** — most P0/P1 items are done; evaluate readiness for Phase 3
3. **Consider**: Scoring retry noise (preamble-only responses) — worth investigating `claude -p` output format options?
