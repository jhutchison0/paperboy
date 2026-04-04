# Paperboy — Task List

**Last Updated**: 2026-04-04

---

## Active

- [ ] [P3] Agent backend: no temperature control on CLI path (Pillar 4 — idempotency gap) — owner: unassigned
- [ ] [P3] Distiller raises RuntimeError on agent failure instead of graceful degradation (Pillar 2) — owner: unassigned
- [ ] [P3] Batch scoring: batch_size=1, target is 5 per invocation — owner: unassigned
- [ ] [P3] Update CONOP checklist phases with completion status — owner: unassigned

## Blocked

_(none)_

## Completed

- [x] 2026-04-04: Cross-run paper deduplication — SelectionHistory, normalize_paper_id, 30-day cooldown, --no-dedup flag
- [x] 2026-04-04: Adopt decision-scientist agent from upstream (ADAPT), skip MAUT module and team (SKIP)
- [x] 2026-04-04: Apply upstream session-start git sync update
- [x] 2026-03-26: Fix pipeline-feature → feature-development rename to align with utils upstream naming
- [x] 2026-03-25: Apply upstream doctrine update — proposer agent, wave terminology, 5 team templates, /sitrep command, session-start doctrine propagation
- [x] 2026-03-17: Add `--paper-id` flag to `distill` command; `ArxivSourcer.fetch_by_id()`; full test coverage
- [x] 2026-03-12: Make output filename date format configurable (`pipeline.date_format`), default YYMMDD
- [x] 2026-03-11: Integrate `/task` command into session workflows and framework docs
- [x] 2026-03-11: Adapt `/task` command from elephant-graveyard to paperboy domain (agents, teams, examples)
- [x] 2026-03-11: Switch license from Apache 2.0 to GPL v3
- [x] 2026-03-11: Live E2E test fixes — distill timeout and CLI output messaging
- [x] 2026-03-11: Rename default_config.yaml to paperboy.yaml, move tests to tests/
- [x] 2026-03-10: Add `--backend` CLI flag (auto|api|agent|keyword-only)
- [x] 2026-03-10: Implement AgentRunner dual-backend (API + Claude CLI) in `src/agent_runner.py`
- [x] 2026-03-10: CONOP — Claude Code Agent as Pipeline Engine (`docs/plans/20260310_agent_pipeline_conop.md`)

---

## Plans & CONOPs

| Document | Status | Link |
|----------|--------|------|
| Agent Pipeline CONOP | IMPLEMENTED | [docs/plans/20260310_agent_pipeline_conop.md](plans/20260310_agent_pipeline_conop.md) |
