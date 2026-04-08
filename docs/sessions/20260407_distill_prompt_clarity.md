# Session: Reframe Distiller Style Guidance — Clarity Over Feelings

**Date**: 2026-04-07
**Branch**: main
**Tags**: #session #distill #complete #pillar-1

**Documents**: [pillars.md](../design/pillars.md) — Pillar 1 (Content Quality First)
**Follows**: [20260404_dedup_and_upstream_doctrine.md](20260404_dedup_and_upstream_doctrine.md)

---

## Summary

Reviewed all 3Blue1Brown-inspired style guidance across prompts, README, and agent definitions. Replaced language that optimized for how the listener *feels* ("feel smarter, not intimidated/lectured at") with language that optimizes for how well they *understand* ("prioritize clarity over completeness").

The distinction: 3Blue1Brown is effective because he teaches clearly, not because he engineers emotional states. Our prompts should reflect that.

## Changes

| File | Before | After |
|------|--------|-------|
| `src/distiller.py` SYSTEM_PROMPT | "Make the reader feel smarter, not intimidated." | "Prioritize clarity over completeness — a listener who understands one idea deeply learns more than one who's been shown five ideas superficially." |
| `README.md` NotebookLM style table | "Make the listener feel smarter, not lectured at." | "Prioritize clarity — one idea understood deeply is worth more than five skimmed." |
| `.claude/agents/distiller-dev.md` | "Make the reader feel smarter, not intimidated" | "Prioritize clarity over completeness — One idea understood deeply beats five skimmed." |

## Left Untouched

Two lines reviewed and kept as-is:
- `src/distiller.py:118-119` — "someone listening on an exercise bike should nod and think 'oh, THAT'S what they mean'" — describes genuine understanding, not a manufactured feeling.
- `src/distiller.py:214` — "Include moments of genuine surprise or delight" — about calling out what's actually clever in the paper, not engineering emotion.

## Test Results

134 tests pass (no changes to logic).
