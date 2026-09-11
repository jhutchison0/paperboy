---
name: designing-clear-data-displays
description: House figure style distilled from Edward Tufte's books and course. Eight kernel rules with tests, before/after pairs, and a review protocol for every chart, figure, map, table, or data-bearing layout. Use when drawing or reviewing any data display.
version: "1.1.0"
---

# Designing Clear Data Displays

House style for data displays. Three goals: figures a reader can use without decoding, ink spent on data rather than decoration, and effects shown at their true size. This SKILL.md is the entry point; expansions, examples, and the review protocol live in sidecar files loaded on demand.

Scope, stated once: a repo's UX rules and document schemas define **what** a display must contain. This skill defines **how** the ink goes. Never drop a required element to save ink. Before the eight: could a table or a sentence carry these numbers? Under about twenty, a table usually does (VDQI p. 56).

**Philosophy**: *Show the data. Spend ink on nothing else, within reason.*

## When to Use

- Drawing any data display: chart, figure, map, diagram, table, sparkline, or a page layout that carries data
- Reviewing a data display (the code reviewer loads `REVIEWING.md`)
- Writing the code that places marks and labels (apply the rule 4 test before the first render)
- Adopting this skill in a downstream repo (`ADOPTION.md`, once)

## The Kernel

Eight rules. The ambient copy lives in CLAUDE.md (see `ADOPTION.md`); `RULES.md` expands each one with its source and its test.

1. Show the data; erase ink that carries none, within reason.
2. Label the data where it lives; a key the eye must decode fails.
3. Make every distinction as subtle as it can be and still be seen.
4. Two marks too close make a third; move one, do not shrink both.
5. Show the effect at its true size: lie factor between 0.95 and 1.05.
6. Answer "compared to what?"; small multiples over one lonely chart.
7. Document the display: title, source, units, scale on the figure.
8. Content counts most: simple design, intense content.

## Quick Reference

### Tufte's Terms

| Term | Plain description | Rule |
|---|---|---|
| Data-ink | Ink that changes when the data changes. The rest is non-data-ink. | 1 |
| Chartjunk | Non-data-ink and redundant data-ink spent on decoration. | 1 |
| Smallest effective difference | The lightest contrast that still separates two things. | 3 |
| Layering and separation | Stratifying a display so each layer reads alone and the layers read together. | 4 |
| 1 + 1 = 3 | Two marks set close create a third shape between them. Albers' phrase, used by Tufte. | 4 |
| Lie factor | Size of the effect in the graphic divided by size of the effect in the data. | 5 |
| Small multiples | The same design repeated, one panel per case, on one scale. | 6 |
| Sparkline | A word-sized line chart with no axes, set in the sentence it belongs to. | 2, 6 |
| Six principles of analytical design | Comparisons; causality; multivariate data; integration of words and images; documentation; content counts most. | 2, 6, 7, 8 |

### Chartjunk Starter List (rule 1)

Heavy grids; encoded keys; gratuitous 3-D; gradients and shadows on data marks; decorative icons inside marks; moiré fills (hatching that vibrates). Each is ink that changes when the designer's taste changes, not when the data does. Library defaults are not neutral: a plotting library draws a legend and a grid unasked, and both are chartjunk or an encoded key until a rule above approves them.

### Named Failures

- **Pie chart** (rules 6, 8). Tufte's reason: no order along a visual dimension, low density. A table beats it almost always; more than one pie is worse, since the reader compares wedges across pies in spatial disarray (VDQI p. 178). Use a table or an ordered bar.
- **Dual y-axes** (rules 5, 6). Two independent scales are two free parameters the designer picks; the crossing point and the slopes can be tuned to tell either story, and no single lie factor catches it. This is the skill's own reasoning, not Tufte's. Use a shared axis or two small multiples instead.

## Ink Economy

Show-the-data usually means less ink, and the exceptions are instructive. In `EXAMPLES.md`, pairs 4 and 6 erase ink, pair 1 moves ink without adding any, and pairs 2, 3, and 5 add it. Every addition answers a question the reader had. Decoration shrinks; missing documentation grows into facts. A display that gained ink and gained meaning followed this skill.

## What This Skill Is Not

- **Not a persona.** "Draw like Tufte" is the roleplay that design principle 5 forbids. These are named rules with sources and tests, applied like any other schema.
- **Not a ban on all ink that carries no datum.** Rule 1 keeps Tufte's "within reason". Figure-ground fill that makes the data legible (a panel under light labels on a dark page) is exempt. A caption beside a figure that repeats the figure's words is words and pictures together (Beautiful Evidence, principle 4), not a key.
- **Not a density rule in either direction.** Tufte's "maximize data density ... within reason" (VDQI p. 168) and his shrink principle in the same chapter are not adopted as a floor; a repo's own UX rules can require a less dense display for its readers. Either way: state the override in the review; do not ignore the rule.
- **Not a sweep.** Adoption re-reviews nothing. A figure a change touches, or a task names, is in scope in full; a display the app still renders is not a record.

## Sidecar Files

Loaded on demand when this SKILL.md cites them. Read only the ones relevant to the task at hand.

- [RULES.md](RULES.md): each kernel rule expanded with the failure it counters, the mechanism, its source, and the test that catches it. Read before drawing anything larger than a sparkline.
- [EXAMPLES.md](EXAMPLES.md): six generic before/after pairs as specs and sketches, including the pair that grows. Read when a rule feels abstract.
- [REVIEWING.md](REVIEWING.md): the review protocol for displays: pass order, finding format, severity mapping, what not to flag, mechanical checks. Read by the code reviewer before reviewing any figure.
- [ADOPTION.md](ADOPTION.md): the CLAUDE.md kernel block, the reviewer checklist line, the index entries, the optional layout probe, and propagation notes. Read once per repo.

## References

- Edward R. Tufte, *The Visual Display of Quantitative Information* (1983; 2nd ed. 2001). Data-ink, chartjunk, the lie factor, friendly graphics.
- Edward R. Tufte, *Envisioning Information* (1990). Layering and separation, small multiples, "compared to what?".
- Edward R. Tufte, *Visual Explanations* (1997). The smallest effective difference.
- Edward R. Tufte, *Beautiful Evidence* (2006). The six fundamental principles of analytical design; sparklines.
- Edward R. Tufte, *Seeing with Fresh Eyes* (2020).
- Edward Tufte's online course (edwardtufte.com/online-course/): fundamental design strategies for all information displays; credibility of a presentation and its presenter; standards of comparison.
- Distilled here, not transcribed. `RULES.md` lists what each rule rests on and which sources were read.
- The writing-simple-and-direct skill: the prose-side twin of this skill. Findings about figures are prose and follow its kernel.

---

**Maintained by**: Designing Clear Data Displays Skill
**Version**: 1.1.0, the external feedback round: the pre-question, Named Failures, the window test, the density guardrail (2026-08-27). 1.0.0, first committed version: directory form with four sidecars and the review protocol (2026-08-27)
