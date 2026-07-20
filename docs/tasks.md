# Paperboy — Task List

**Last Updated**: 2026-07-20

---

## Active

- [ ] [P3] Agent backend: no temperature control on CLI path (Pillar 4 — idempotency gap) — owner: unassigned
- [ ] [P3] Batch scoring: batch_size=1, target is 5 per invocation — owner: unassigned
- [ ] [P3] Update CONOP checklist phases with completion status — owner: unassigned

## Blocked

_(none)_

## Completed

- [x] 2026-07-20: Blog feed audit (closed P3 from 2026-05-19) — Anthropic feed is a 404 with no official replacement (commented out with re-enable note); Google feedburner feed went stale in 2024, replaced with research.google/blog/rss; OpenAI URL updated to post-redirect openai.com/news/rss.xml; Distill.pub archived since 2021, commented out; Lilian Weng and The Gradient healthy. Live run: 82 papers + 10 articles, no feed warnings.
- [x] 2026-07-20: Privatize distiller user_context (P1, pre-public gate) — USER_CONTEXT env override in config.py (test-first, 3 tests), generic persona in tracked YAML, .env.example documented, real context migrated to local .env and verified end-to-end. History scrubbed: role/division text replaced in all historical config blobs via git-filter-repo replace-text; typo email jhustchion@anl.gov fixed via mailmap the same day. All commit hashes rewritten.
- [x] 2026-07-20: Public-repo prose sweep — README, CONTEXT, LANGUAGE, CLAUDE, CHANGELOG, docs/adr, docs/design, config swept per writing-simple-and-direct on topic/docs-public-prose-sweep; code-reviewer audit gate APPROVE WITH FIXES (4 Minor, applied); factual corrections verified against code/config (Eight-Section Structure, BlogSourcer feeds, episode length); merged 1d66fdd, branch deleted
- [x] 2026-07-20: Adopt upstream tacsop 2026-07-20 doctrine cycle — Part 1 hub rename verified (utils → tacsop); Part 2 planning doctrine (CONOP/OPORD format templates, task.md proword + promote wiring, deep-modules sentence); Part 3 writing-simple-and-direct skill + ADOPTION.md run, shift-left-testing 2.1.0 (4 new sidecars). Property-test plumbing deferred to first property test. 156 tests pass.
- [x] 2026-05-22: Adopt upstream utils 2026-05-19 doctrine cycle — LANGUAGE.md, CONTEXT.md, ADR system, SKILLS_FRAMEWORK v2 (5 legacy single-file skills → directory form), PostToolUse shift-left audit hook (glob adapted for flat src/), Python 3.11 min, test-first python-prototyper. Audited by pipeline-sme + code-reviewer; 7 fixes applied. Commit c06e8ba (hash post-2026-07-20 history rewrite).
- [x] 2026-05-21: Honest success/failure reporting — PipelineResult.partial status, no dedup poisoning on distill failure, CLI exits 2 on partial
- [x] 2026-05-21: AgentRunner timeout diagnostics — Popen+communicate captures partial stdout, 1.5x backoff on distill timeout retry, distill_timeout default 300→600
- [x] 2026-05-21: Failure-reason propagation — AgentRunner.last_error (timeout/validation/subprocess) flows through distiller into PipelineResult.error
- [x] 2026-05-21: Closed P3 distiller-raises-on-agent-failure task — verified distiller already returns None gracefully (no longer raises RuntimeError)
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
