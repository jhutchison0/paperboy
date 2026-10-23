# Paperboy — Task List

## Focus

The order of the campaign, as intent, as of 2026-10-22. A line here says what comes next, never what is true now; `/session-end` rewrites this section when the order changes. Counts and statuses are measured at `/session-start`, not kept here; a step that needs a number names the command that measures it.

1. Close this doctrine cycle at the first `/session-end` under the Claims table (2026-10-22): the `## Claims` rows with both overclaim counts, the disposal annotations in `.claude/upstream-update.md`, then push `main`.
2. Measure the gaps the register opened, cheapest and daily-input first, each recorded in `docs/reviews/`: G6 (the per-feed listing at `/session-start`), G3 (the paired listening test, owner distiller-dev), then G4 and G7 together (the determinism probe and the keyword-gate probe share one saved candidate list). The designs are in `docs/reviews/20261022_gap_register_ds_review.md`, sections 3 and 4.
3. Close Phase 2 by command, not by sentence: `python main.py --help` lists the `--backend` flag, `config.validate` passes on the tracked YAML, and the roster table in `.claude/README.md` matches `ls .claude/agents/`; record the outputs in that session's doc. Then cut v0.3.0 with a CHANGELOG entry (carried since 2026-07-20) and flip the repository public. Before the flip: optionally ask GitHub support to run GC so pre-rewrite objects cannot resolve by URL, and close gap G5 for every rostered clone by each box reporting at `/session-start`.
4. Open Phase 3 with the run-history log (date, status, backend, selected id per run), which is also gap G8's collector; scheduling follows it.
5. The selector findings of the 2026-10-22 decision-science review, as they fit: the dead category sub-criterion (P2 below), failure scoring on the two backends, the threshold that never bites, and the unread config keys; then the standing P3s (batch scoring at the configured target, the CONOP checklist status, the first property test with the Hypothesis plumbing).
6. On the hub's next notification: the verifying-claims entry (adopted here on 2026-10-22 ahead of release; reconcile by its Detect block, revert path in the Completed entry dated 2026-10-22); the hub's correction entries for the register pin and the audit hook's import grep; and the shift-left-testing isolation sidecar with the `--python .venv` install pin, if the hub releases them. All three were held under the hub's CONOP OVERWATCH on 2026-10-22; their headings will appear in `.claude/upstream-update.md` when they ship.
7. Through the KB-traversal window (five sessions from 2026-09-10): a `KB-graph:` line in each session doc for every traversal that informed the work, and the `/pcc` check 5 count recorded.

---

## Active

- [ ] [P3] Agent backend: no temperature control on CLI path (Pillar 4 — idempotency gap); gap G4 in `docs/gaps.md` is the unmeasured half — owner: unassigned
- [ ] [P3] Build gaps G4 and G7's collectors on one fixture: save one `SourceManager.fetch_all()` candidate list to JSON under `output/`; score it ten times per backend (keyword-only as the harness control, API at 0.0, Agent), recording per-paper Claude scores, rank order, top-1 and failed calls in rule 8's two shapes (G4); Claude-score the keyword top 20 once and record the keyword rank of Claude's top-1 (G7). Design: `docs/reviews/20261022_gap_register_ds_review.md` sections 3 and 7. Record in `docs/reviews/`; close or keep each row — owner: python-prototyper
- [ ] [P3] Build gap G6's collector: a feed-only per-feed listing (parsed, total entries, newest entry date, entries in `days_lookback`, warning text) runnable at `/session-start`; `BlogSourcer.health_check()` collapses four feeds into one bit and is not it (DS review F10) — owner: content-curator
- [ ] [P2] Selector: the category sub-criterion is structurally zero (measured 2026-10-22 against the tracked config: no focus keyword matches an arXiv category or feed name; `src/selector.py:184-192`), so the declared 0.50/0.35/0.15 sub-weights act as 0.59/0.41 and the keyword ceiling is 0.85. Drop it and re-normalize, or give it a universe it can hit; move the sub-weights to `config/paperboy.yaml`. DS review F14 — owner: decision-scientist with content-curator
- [ ] [P3] Selector: a failed Claude call keeps the keyword-only score on the API path (`src/selector.py:126`) but injects 0.5 on the Agent path (`:257`), so a failed paper competes on a different scale; score failures the same way on both and count them. DS review F15 — owner: python-prototyper
- [ ] [P3] Selector: `min_score_threshold` never bites on the pipeline's top-1 selection because of the fall-back at `src/selector.py:139-144`; document that or remove the fall-back. DS review F16 — owner: unassigned
- [ ] [P3] Config: `max_papers_to_fetch` and `max_papers_to_score` are read nowhere outside `src/config.py` (DS review F7), and `dedup_cooldown_days: 30` cannot act past `days_lookback: 7` on the arXiv path (`src/sourcer.py:94` queries by submitted date; SME review F4); decide for each whether it is dead or gets wired — owner: decision-scientist
- [ ] [P3] Record the backend in `PipelineResult` and the briefing header (and a config hash if Pillar 4 is to claim one); `docs/design/pillars.md` no longer claims the hash the result never carried (SME review F9) — owner: python-prototyper
- [ ] [P3] When the hub's correction entries land (register pin `_keys`, the audit hook's import grep, `DRIFTING_COUNT` unit word, a renamed state block, `STALE_LATEST` synonyms): reconcile the local pins and run the six COP mutants from agent-eval's 2026-10-06 gate against them — owner: unassigned
- [ ] [P3] Batch scoring: batch_size=1, target is 5 per invocation — owner: unassigned
- [ ] [P3] Update CONOP checklist phases with completion status — owner: unassigned
- [ ] [P3] Evaluate prose-kernel briefings by listening — two NotebookLM episodes per briefing from the kernel-styled (the 2026-07-20 ToolSciVer redistill) and pre-kernel versions of the same paper, order blinded by a sealed coin flip, each scored on the fixed form in `docs/reviews/20261022_gap_register_ds_review.md` section 4 (lost-thread tally, three 1-to-5 ratings, episode length, one forced choice per pair). Text metrics are in gap G3. — owner: distiller-dev

## Blocked

_(none)_

## Completed

- [x] 2026-10-22: Adopt hub entries 2026-09-18 (shift-left-testing 2.1.1, copied from the entry's commit d4ac4e4) and 2026-10-04 picture slices 1 and 2 — gap register `docs/gaps.md` (six rows) with `src/gaps.py` and `tests/test_gaps.py` (test-first); Picture Style kernel; `## Focus` at the head of this file; `/session-start` source tags; CONTEXT.md Current State as pointers; config identity-only (`last_updated`/`updated_by` gone, Nidhogg rostered); counts to commands; `tests/test_state_block.py`; `/pcc` check 5 range `[gate]`. Five sister repos (hallmark, propter, fist, assay, tactics-game) read first by survey agents. Disposals annotated in `.claude/upstream-update.md`. Commits fe719bf, 171b868, 74a14f2, dbed92e.
- [x] 2026-10-22: verifying-claims 1.0.0 adopted ahead of its held entry (hub ff0d8b2; the Picture Style kernel assumes it; propter, tactics-game, hallmark carry it) — all of draft entry B's surfaces and 26 pins (bf037e8); reviewer line alone `[gate]` (e011fef). Revert path: `git revert bf037e8 e011fef` before the merge, `git revert -m 1 <merge>` after; the tests go with them. No heading added to `.claude/doctrine-delivered`; reconcile against entry B's Detect block when the hub releases it.
- [x] 2026-10-22: Audit hook executable bit — mode 100644 in the index since its creation (c06e8ba, 2026-05-22), so it fired only where a box had chmod'ed it locally; this box's log was silent since 2026-07-20 and today's pull rewrote the file at 644. Fixed `[gate]` 11ac109 with `tests/test_audit_hook.py` (written first, red); `/pcc` check 4 now reads hook modes.
- [x] 2026-09-10: Seed hub D10 upward lesson channel — `.claude/upstream-lesson.md` created (mirror of upstream-update.md, append mode) with 3 fleet-scope lessons in the D9 schema: roster-as-config-dimension (backend preference, hub template candidate), the pin-resolve_machine test-hermeticity trap, and second-consumer confirmation of the single-entry propagation gap. Hub harvests on its next visit; nothing written into the hub clone, preserving its OBSERVED-gate provenance.
- [x] 2026-09-10: Machine-keyed backend preference — auto-mode consults `machines.<host>.backend` before the detection chain, so a home box stays on subscription CLI even with an `.env` key present and a work box states API intent explicitly. Advisory (unavailable preference falls through with a logged warning); explicit `--backend` flag wins. Built test-first (8 tests, hermetic against the host roster via autouse pin). Muninn rostered `backend: agent`; live-verified. Suite 172 → 180.
- [x] 2026-09-10: Adopt hub 2026-08 doctrine catch-up (five entries) — uv environments (venv rebuilt on managed 3.12.13, exact 166-test parity, skills refreshed); machine identity (machines: roster, src/machine.py test-first, /session-start Step 1.5; this box is Muninn); audit-hook import-grep fallback (src.-prefixed dotted names for the flat layout, pipe-test verified) + WebSearch/WebFetch on proposer and code-reviewer; KB traversal skill + /pcc checks 5-6 (by-hand first run, 3 findings dispositioned to 0-MISSING baseline); figure style skill + CLAUDE.md kernel + reviewer line; home storage (scope: personal, HOME_* plumbing deferred to first bulk write). SKILLS_FRAMEWORK index caught up (4 unlisted skills). Suite 166 → 172. Disposals annotated in .claude/upstream-update.md.
- [x] 2026-07-20: Prose kernel in distiller prompt — writing-simple-and-direct rules adapted for spoken briefings and embedded in SYSTEM_PROMPT (both backends); em-dash validation warning added. Verified by controlled redistill of the same paper (arXiv:2607.16131): em dashes 49 → 0, cruft words 1 → 0, 8/8 sections intact, 4615 words. Commit c539160.
- [x] 2026-07-20: Relicense GPL v3 → Apache-2.0 ahead of going public — sole author, never distributed, so no copyleft obligations attached; uniform with tacsop (whose template content is Apache-2.0 and lands here every doctrine cycle); explicit patent grant. Canonical LICENSE text; README badge updated. Supersedes the 2026-03-11 GPL switch.
- [x] 2026-07-20: Isolate agent backend from workspace context — AgentRunner now runs `claude -p` with cwd=tempfile.gettempdir() so the CLI cannot load the repo's CLAUDE.md/skills into pipeline prompts. Found via briefing forensics: May briefings had 42-43 em dashes, today's had 0 (the Prose Style kernel had leaked into distillation). Restores distiller prompt as sole style authority (Pillar 1) and removes a hidden output input (Pillar 4). Test-first; 160 tests pass.
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
