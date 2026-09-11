# REVIEWING: The Review Protocol for Data Displays

Sidecar to `SKILL.md`. How the code reviewer (or a human) reviews a chart, figure, map, table, or data-bearing layout against the kernel. Drawing and reviewing are different activities: the designer applies rules; the reviewer produces findings someone else can act on. This file governs the second.

## Pass Order

Review in five passes, largest defect class first. Stopping early is allowed: a display that fails pass 1 gets that finding first, because fixing the comparison usually redraws the marks that would have been flagged later.

1. **Content and comparison** (rules 6 and 8). First, the pre-question: could a table or a sentence carry these numbers as well? Under about twenty numbers a table usually does (VDQI p. 56). If a sentence: the finding is "a sentence, not a chart", the redraw is the sentence, and the rest of the review is the prose kernel's. If a table: the finding is "a table, not a chart", and passes 2 and 3 run on the table. Otherwise name the comparison the display exists for. If there is none, the finding is "no comparison shown"; if the reader must hold a second page in their head to make it, the finding is "redesign toward small multiples or a shared axis". Then rule 8: name one element to remove; if none, name one datum to add.
2. **Documentation** (rule 7). Cover the caption and the surrounding page. Title, source, units, scale: which are missing from the figure itself?
3. **Data-ink** (rules 1 and 3). For each mark, name the value it stands for. For each non-data distinction, ask whether it could be lighter and still read. Figure-ground fill that makes the data legible passes.
4. **Labeling and placement** (rules 2 and 4). Cover everything but the figure: can a reader name every mark without decoding a number, letter, or color? Compute each label's footprint: does any two overlap?
5. **Integrity** (rule 5). Measure the effect shown and the effect in the data; divide. Outside 0.95 to 1.05 is a finding.

## Finding Format

A finding without a redraw is a complaint. Every finding carries three parts: severity and rule, the offending element (by coordinate, selector, or quote), and a concrete redraw.

```
[Major] Rule 4: "Block A" (x 55.0 to 78.1, y 98) and "Block B" (x 46.9 to 70.0, y 98) overlap by 15 units
        (templates/setup.svg, the second <text>)
Redraw: anchor "Block B" start at x=80; it spans 80.0 to 103.1; no overlap; font unchanged
```

Name the element the way the author can find it: an SVG coordinate, a CSS selector, a table cell, a quoted label. The redraw requirement keeps the reviewer honest: a rule violation you cannot redraw may not be a violation (see What Not to Flag).

## Severity Mapping

- **Minor** (default): a kernel violation the reader can read through. A gradient on a bar; a grid darker than it needs to be; a unit stated in the caption but not on the figure; a lie factor outside the band on a step the reader does not compare.
- **Major**: a violation that blocks the reader's task. Two labels overprinting so a name cannot be read. A key the reader must decode to use the figure at all. A lie factor outside 0.95 to 1.05 on the comparison the display exists for. A comparison the display exists for and does not show.
- **Critical**: never issued for display style. Critical stays reserved for the reviewer's own checklist definition (secrets, security). Style cannot reach it.

Severity attaches to the effect on the reader, not to the rule number. Ten Minor decoration findings do not add up to a Major; one unreadable label does.

## What Not to Flag

- **Figures nobody is changing.** Adoption triggers no sweep. A figure a change touches, or a queued task names, gets the full pass order.
- **What the repo's own UX rules decided.** A repo can require a less dense display for its readers, a sentence where a table would be denser, or a larger label than the smallest effective difference allows. When the override is stated, it is not a finding. When it is not stated, the finding asks for the statement, not for the redraw. An override is stated when it appears in the repo's ambient rules (CLAUDE.md), its pillars, or the decision table of the plan that drew the figure. Cite the line.
- **Print, appendix, or role-restricted tables** where the repo permits them. A dense table on a page built for it is content, not chartjunk.
- **A caption that repeats the figure's words.** That is words and pictures together (rule 2; Beautiful Evidence, principle 4), not a key.
- **Figure-ground fill.** A panel that makes the labels legible is exempt under rule 1's "within reason".
- **Displays that grew.** Ink that answers a reader's question is data-ink (`EXAMPLES.md` pair 5). Ink count alone is never a finding; ink that stands for nothing is.

## Mechanical Checks

Label footprints and lie factors are measurable; measure them. A footprint is anchor, height, and estimated width: 0.55 em per glyph for proportional sans-serif or 0.6 em per glyph for monospace (0.56 to 0.60 across common faces; the estimate errs wide, the safe side). A lie factor is two ratios and a division. Where a headless browser is available, render the page and read the bounding boxes from it rather than estimating; the estimate is for the case where no browser can run.

## The Reviewer's Own Prose

Findings are prose artifacts and follow the prose kernel. A finding that says "cluttered" without a coordinate fails its own review. The format above is short on purpose: severity, rule, element, redraw.

## See Also

- `RULES.md`: the per-rule tests the passes apply.
- `EXAMPLES.md`: redraws to pattern findings on.
- `ADOPTION.md`: the one-line addition that puts this protocol in the code reviewer's checklist.
