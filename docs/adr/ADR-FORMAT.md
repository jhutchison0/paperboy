# ADR Format

This is the template for Architecture Decision Records in this repo. ADRs live in `docs/adr/NNNN-slug.md`. See the [`recording-architecture-decisions`](../../.claude/skills/recording-architecture-decisions/SKILL.md) skill for when to write one.

The triple filter at the top of every ADR is the **gate**, not a formality. If any of the three boxes is unchecked, the decision does not warrant an ADR; document it elsewhere (commit message, session doc, design doc, inline comment).

---

## When to Write an ADR

Adopt verbatim from Matt Pocock's `ADR-FORMAT.md` (mattpocock/skills):

> Write an ADR only when the decision is:
>
> - **Hard to reverse** — the cost of changing your mind later is meaningful.
> - **Surprising without context** — a future reader will wonder "why did they do it this way?"
> - **The result of a real trade-off** — there were genuine alternatives and you picked one for specific reasons.
>
> If any one is missing, skip the ADR.

---

## Template

Copy this template into a new file at `docs/adr/NNNN-slug.md`, then fill it in. Use the next unused four-digit sequential number.

```markdown
# ADR-NNNN: <Short, Descriptive Title>

**Status**: Proposed | Accepted | Superseded by ADR-MMMM
**Date**: YYYY-MM-DD
**Decision-maker(s)**: <name(s)>

---

## Triple-Filter Check

Before writing this ADR, confirm:

- [ ] **Hard to reverse** — changing this later carries meaningful cost.
- [ ] **Surprising without context** — a future reader will wonder why.
- [ ] **Result of a real trade-off** — genuine alternatives existed and were considered.

If any box is unchecked, this is not an ADR-worthy decision. Document it elsewhere.

---

## Context

What forces are at play? What constraints? What was being optimized? What problem brought us here? Be specific: a future reader needs to understand the situation that made this decision necessary.

---

## Decision

What was chosen. Be specific: name files, commands, configurations, or behaviors. Avoid vague phrasing.

---

## Alternatives Considered

The real options that were on the table. For each, one paragraph: what it was, what made it appealing, why it was rejected.

### Alternative A: <Name>
<Description. Why considered. Why rejected.>

### Alternative B: <Name>
<Description. Why considered. Why rejected.>

(Add as many as were real candidates. Do not pad; list only alternatives that were genuinely considered.)

---

## Consequences

### Positive
- <What this enables. What problem it solves. What capability it adds.>

### Negative
- <What this forecloses. What costs it introduces. What risks it creates.>

### Neutral
- <Changes that are neither clearly positive nor negative — operational shifts, new dependencies, etc.>

Honesty matters in this section. If an ADR has only positive consequences, the rigor is missing: every real trade-off carries cost.

---

## References

- Related ADRs (link by number and title).
- External sources (papers, blog posts, prior art) that informed the decision.
- Code or config locations most affected.
- Session docs or design docs that preceded this decision.
```

---

## Status Values

- **Proposed** — drafted but not yet committed to.
- **Accepted** — committed to and in effect.
- **Superseded by ADR-MMMM** — replaced by a later decision. The original ADR is kept for historical context; the new ADR explains the reversal.

ADRs are **append-only**. Once accepted, do not edit content. To change a decision, write a new ADR that supersedes the old one. Update the old ADR's Status field only, never its body.

---

## Numbering

- Sequential, four-digit, zero-padded: `0001`, `0002`, `0003`, ...
- Never reuse a number, even if an ADR is superseded.
- Find the next number with `ls docs/adr/ | tail -1` (excluding `.gitkeep` and this format file).

---

## Sources

- Matt Pocock, [`mattpocock/skills/skills/engineering/grill-with-docs/ADR-FORMAT.md`](https://github.com/mattpocock/skills) — the triple filter, adopted verbatim.
- Michael Nygard, "Documenting Architecture Decisions" (2011) — the original ADR pattern.
- This project's [`recording-architecture-decisions` skill](../../.claude/skills/recording-architecture-decisions/SKILL.md) — when to invoke.
