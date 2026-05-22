# Session: Honest Pipeline Status + AgentRunner Timeout Diagnostics

**Date**: 2026-05-21
**Branch**: main
**Tags**: #session #pipeline #fix #complete #pillar-2 #pillar-4

**Documents**: [pillars.md](../design/pillars.md) — Pillar 2 (Source Diversity & Resilience), Pillar 4 (Pipeline Idempotency)
**Follows**: [20260407_distill_prompt_clarity.md](20260407_distill_prompt_clarity.md)

---

## Summary

A real run today (2026-05-19) declared `Pipeline SUCCESS` while producing no briefing — distillation timed out twice and the pipeline cheerfully recorded the paper into the dedup history anyway, blocking future retries for 30 days. The user spotted it. We fixed three independent reliability problems in one session.

## The bug we hit

```
09:00:09 [WARNING] AgentRunner: invocation timed out after 300s
09:05:09 [WARNING] AgentRunner: distill_paper failed after 2 attempt(s) — returning None
09:05:09 [INFO]    src.pipeline: Recorded selection: 2605.18747v1
09:05:09 [INFO]    Pipeline SUCCESS
                     Briefing: None
                     Saved to: None
```

Pipeline status determined by "did an exception get raised?" — not "did we produce anything?". And the failed selection got recorded, poisoning dedup.

## What changed

### 1. Honest success/failure reporting

`PipelineResult` gains a third status: `partial` — distinct from `success` (briefing produced, or keyword-only intentional skip) and `error` (exception). The pipeline now:

- Returns `partial` when a Claude backend was configured but no briefing was produced
- **Does NOT record** the selection in history on partial — paper stays available for retry
- Surfaces a `PARTIAL` block on stderr from `main.py run` and exits with code 2 (cron-visible)
- Distiller is None (keyword-only) still returns `success` since no briefing was expected

**Files**: [src/pipeline.py:189-238](../../src/pipeline.py#L189-L238), [src/pipeline.py:336-378](../../src/pipeline.py#L336-L378), [main.py:93-117](../../main.py#L93-L117)

### 2. AgentRunner timeout diagnostics + smarter retry

`_invoke` migrated from `subprocess.run` to `Popen + communicate(timeout=...)`. Why: on Linux, `subprocess.run`'s `TimeoutExpired` discards stdout. With Popen, after killing the process we call `communicate()` again to drain whatever was buffered before the kill — giving us diagnostic data about whether Claude was actively generating ("partial stdout head: '# Briefing...'") or stuck producing nothing.

Other reliability changes:
- `distill_paper` retries with **1.5× extended timeout** after a timeout (retrying with the same timeout that just failed was theater)
- `score_paper` keeps a **fixed timeout** — 30s scoring failures signal a sick CLI more often than a budget shortfall
- `distill_timeout` default: **300s → 600s** (4500-word target needs headroom; back-of-envelope: 6000 output tokens / ~40 tok/s + CLI overhead + variance)

**Files**: [src/agent_runner.py:208-303](../../src/agent_runner.py#L208-L303), [src/agent_runner.py:360-407](../../src/agent_runner.py#L360-L407), [config/paperboy.yaml:117](../../config/paperboy.yaml#L117)

### 3. Failure-reason propagation end-to-end

Specific failure kinds now flow from CLI invocation up to user-facing message:

```
AgentRunner._invoke → outcome.timed_out flag
  ↓
AgentRunner.{score,distill}_paper → self.last_error = "distill_paper timed out after 2 attempt(s); final timeout was 900s"
  ↓
BriefingDistiller.distill → self.last_error (forwards AgentRunner's, or sets its own for SDK errors)
  ↓
DailyPipeline.run → PipelineResult.error = distiller.last_error
  ↓
main.py run → "Reason: distill_paper timed out after 2 attempt(s); final timeout was 900s"
```

User no longer reads the generic `distillation returned no content` — they read what actually happened.

**Files**: [src/agent_runner.py:77](../../src/agent_runner.py#L77), [src/distiller.py:255-281](../../src/distiller.py#L255-L281), [src/pipeline.py:367-373](../../src/pipeline.py#L367-L373)

## Decisions worth recording

- **Status semantics**: `partial` exits **2** from the CLI (distinct from `1`-on-error) so automation can distinguish "pipeline crashed" from "pipeline ran but didn't produce output". Cron jobs can branch on it.
- **No backoff for `score_paper`**: parallel symmetry with `distill_paper` was rejected. Scoring failures at 30s are diagnostic signals, not budget problems — extending the timeout would slow failure detection without buying real headroom.
- **`_InvocationOutcome` over tuple return**: two named fields cost 7 lines and pay back at every call site (`outcome.text is None` reads cleaner than `text is None` after destructuring).
- **Duplication between `score_paper` and `distill_paper` left intact**: structural parallelism is real (~25 lines) but the differences (validator, cleaner, backoff policy, validation-error tracking) are load-bearing. An abstraction would need 4+ callables and obscure exactly the parts that differ.

## Tests

- **159 passing** (138 baseline → 159 = +21 new tests across the three fixes)
- New file: `tests/test_pipeline_outcomes.py` — status transitions, history non-recording on partial, distiller forwarding
- Migrated `tests/test_agent_runner.py` from `subprocess.run` mocks to `Popen` mocks
- New tests for partial-output capture, timeout backoff, no-backoff for scoring, `last_error` reasons

## Commits

```
1e8620a [fix][pipeline][agent] Honest failure reporting + timeout diagnostics
358c521 [config][test] Detect .env.example placeholder API key and treat as unset
```

The second was a pre-existing change from a prior session that hadn't been committed; split out cleanly with `git apply --cached` so the two commits stay semantically distinct.

## What today's failed run would now look like

```
[WARNING] AgentRunner: invocation timed out after 600s
          (captured 14283 bytes / ~2100 words of partial stdout)
[WARNING] AgentRunner: partial stdout head: '# Research Briefing\n\n## Why Should You Care...'
[INFO]    AgentRunner: distill_paper retry will use extended timeout 900s
[WARNING] AgentRunner: invocation timed out after 900s ...
[WARNING] AgentRunner: distill_paper failed after 2 attempt(s) — distill_paper timed out
                       after 2 attempt(s); final timeout was 900s

============================================================
PARTIAL — paper selected but briefing failed
============================================================
Paper:    Code as Agent Harness
Score:    0.70
Reason:   distill_paper timed out after 2 attempt(s); final timeout was 900s

Paper was NOT recorded for dedup — re-run to retry.
(exit code 2)
```

## Outstanding

- **Blog feed audit** (added to tasks.md): 5 of 6 feeds returned 0 articles on 2026-05-19. Anthropic Research had an XML parse error; Lilian Weng / The Gradient / Distill.pub are likely dormant. Pillar 2 says source diversity — we currently have one working blog. Worth triage in a future session.
- Pre-existing P3s still standing: temperature control on CLI path (idempotency), batch scoring (still batch_size=1 vs target 5), CONOP checklist completion updates.
