---
name: writing-simple-and-direct
description: House prose style distilled from Barzun's Simple and Direct. Eight kernel rules with expansions, before/after patterns, and a review protocol for every prose artifact (SITREPs, reviews, proposals, ADRs, session docs, backbriefs, commit messages). Use when writing or reviewing any prose artifact.
version: "1.0.0"
---

# Writing Simple and Direct

House style for prose. Three goals: clearer communication for humans, fewer tokens per artifact, and removal of machine-prose defaults from our output. This SKILL.md is the entry point; expansions, examples, and the review protocol live in sidecar files loaded on demand.

Scope, stated once: document schemas (TCS, CONOP-FORMAT, OPORD-FORMAT) define **what** a document contains. This skill defines **how** the words go. Never cut a required section to save tokens.

**Philosophy**: *Have a point. Make it in the fewest words that keep it true.*

## When to Use

- Writing any prose artifact: SITREP, review, proposal, ADR, session doc, backbrief, commit message, PR text
- Reviewing prose artifacts (code-reviewer loads `REVIEWING.md` for document reviews)
- Writing docstrings and comments (apply the rules; enforcement stays on artifacts)
- Adopting this skill in a downstream repo (`ADOPTION.md`, once)

## The Kernel

Eight rules. The ambient copy lives in CLAUDE.md (see `ADOPTION.md`); `RULES.md` expands each one with its test.

1. Have a point; state it in the first sentence. No throat-clearing.
2. Prefer the concrete word: name the file, the number, the failure.
3. One idea per sentence. Link sentences; do not pack them.
4. Active voice unless the actor is unknown or irrelevant.
5. Cut cruft words. The banned list lives in LANGUAGE.md.
6. Hedge with numbers or not at all.
7. Read it back; if you would not say it, do not write it.
8. No em dashes in running prose. Choose the mark that states the relationship.

## Quick Reference

### The Punctuation Table (rule 8)

| Relationship | Mark |
|---|---|
| Announces or expands | Colon |
| Balances two complete thoughts | Semicolon |
| Separate ideas | Period |
| Stated logic (and, but, because, so) | Conjunction |
| True aside | Parentheses |

### Cruft Starter List (rule 5)

leverage, utilize, robust, seamless, comprehensive, facilitate, streamline, delve, crucial, holistic; "it should be noted that"; "in order to" outside mission statements. Authoritative list: LANGUAGE.md.

## Token Economy

Simple and direct is usually cheap, and the exception is instructive. In `EXAMPLES.md`, cruft-heavy prose shrinks by half or more after revision. Under-specified prose grows, because facts cost more words than fog. Both are correct outcomes. Model output skews toward cruft, so net savings are real; but a document that got longer and truer also followed this skill. Expect the largest savings in written artifacts. Effects on reasoning traces are second-order; do not count on them.

## What This Skill Is Not

- **Not a persona.** "Write like Barzun" is the roleplay that design principle 5 forbids. These are named rules with tests, applied like any other schema.
- **Not a length cap.** Completeness comes from the document schemas. Cut words, never required fields. A short OPORD missing its exit criteria is not simple; it is malformed.
- **Not retroactive.** Existing docs are grandfathered, and session docs and reviews are records; leave them. The rules apply to new and revised prose.

## Sidecar Files

Loaded on demand when this SKILL.md cites them. Read only the ones relevant to the task at hand.

- [RULES.md](RULES.md): each kernel rule expanded with the failure it counters and the test that catches it. Read when writing any artifact longer than a commit message.
- [EXAMPLES.md](EXAMPLES.md): six domain-native before/after pairs with word counts, including the pair that grows. Read when a rule feels abstract.
- [REVIEWING.md](REVIEWING.md): the review protocol for prose: pass order, finding format, severity mapping, what not to flag. Read by code-reviewer before reviewing any prose artifact.
- [ADOPTION.md](ADOPTION.md): the CLAUDE.md kernel block, LANGUAGE.md additions, reviewer checklist line, the optional Vale seam, and propagation notes. Read once per repo.

## References

- Jacques Barzun, *Simple and Direct: A Rhetoric for Writers* (1975; 4th ed. 2001). Six parts (diction, linking, tone, meaning, composition, revision) and twenty numbered principles. Distilled here, not transcribed.
- LANGUAGE.md: the banned-word mechanism this skill extends.
- CLAUDE.md "Simplicity First": the code-side twin of this skill.

---

**Maintained by**: Writing Simple and Direct Skill
**Version**: 1.0.0, first committed version: directory form with four sidecars and the review protocol (2026-07-20)
