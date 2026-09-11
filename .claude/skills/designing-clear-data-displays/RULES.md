# RULES: The Kernel Expanded

Sidecar to `SKILL.md`. Each rule with the failure it counters, the mechanism, its source, and the test that catches it. The kernel itself is eight lines in `SKILL.md` and CLAUDE.md; this file is the depth behind them. The builder checked each quotation against the sources listed at the end and the gate reviewer re-fetched them; where the book text itself was not fetched, the citation says so.

## 1. Show the Data

The default failure is chartjunk: ink spent on decoration, frames, gradients, and grids that encode no value. Tufte's two erasing principles in *The Visual Display of Quantitative Information* (ch. 4, the data-ink ratio) are "Erase non-data-ink, within reason" and "Erase redundant data-ink, within reason" (secondary source; book text not fetched). Chartjunk is the ink those principles remove (VDQI pp. 106 to 121): "The interior decoration of graphics generates a lot of ink that does not tell the viewer anything new." The hedge is Tufte's own, and it carries weight. Figure-ground fill that makes the data legible is not decoration; it is the ground. The counter-evidence: Bateman et al. (2010) found that some embellishment raises long-term memorability. Few holds that Tufte defined chartjunk too broadly, and Kosara sorts it: a busy background harms, a border is harmless, an annotation helps. So the rule governs data marks and the ink around them, not every pixel on the page. Tufte on graphics that show off the tool: "at least a few computer graphics only evoke the response 'Isn't it remarkable that the computer can be programmed to draw like that?' instead of 'My, what interesting data.'" (VDQI p. 120; primary: the chapter text, 2nd ed.). The library-default application is the skill's.

**Test**: for each mark, name the value it stands for. A mark with no answer goes, unless it is the ground that makes the data legible.

## 2. Label Where the Data Lives

The failure is the code and the darting, not the presence of words beside a figure. A number, a letter, or a color that means nothing until the reader finds it in a key sends the eye away from the data and back for every mark. VDQI p. 180 says to "integrate the caption and legend into the design so that the eye is not required to dart back and forth between textual material and the graphic" (secondary source; book text not fetched) and, on the same page, "Words and pictures belong together." The friendly-graphic table in VDQI puts it as a property of the graphic: "labels are placed on the graphic itself; no legend is required," against the unfriendly graphic where "Obscure codings require going back and forth between legend and graphic." Tufte's list of what is wrong with a default chart names the failure directly: "encoded legends, color without content" (edwardtufte.com, 2003-01-08). The positive form is *Beautiful Evidence* principle 4: "Completely integrate words, numbers, images, diagrams." A caption or list beside the figure that repeats the figure's words is that integration, not a key.

**Test**: cover everything but the figure. Can a reader name every mark without decoding a number, letter, or color?

## 3. The Smallest Effective Difference

The failure is contrast spent where it separates nothing: a black grid behind gray bars, a heavy frame, a thick rule between rows. Tufte's smallest effective difference (*Visual Explanations*, 1997): "Make all visual distinctions as subtle as possible, but still clear and effective" (secondary source; book text not fetched; Tufte names the principle and the book in his 2006-03-06 post). It governs contrast: mute the grid, lighten the frame, thin the rule, so the data marks stand out against a calm ground. It does not govern label size; the legibility floor lives in rule 4's test.

**Test**: for each non-data distinction, lighten it until it just still reads. For each data distinction, ask whether it is the smallest that still separates the two things.

## 4. Two Marks Too Close Make a Third

The failure is two marks, or two labels, set so close that a third shape appears between them: an overprint, a smear, a false object. Tufte cites Albers' "1 + 1 = 3" in *Envisioning Information* ch. 3, Layering and Separation: elements set together interact and create "non-informative patterns and texture simply through their combined presence" (secondary source; book text not fetched). The same chapter states the stance: "Confusion and clutter are failures of design, not attributes of information" (p. 53). The clutter is the designer's, not the data's. For labels on maps the placement rules come from Imhof, "Positioning Names on Maps" (*The American Cartographer*, 1975), whom Tufte cites in *Envisioning Information*; verify that citation against the book, since the journal page and the book's pages were not fetched.

**Test**: compute each label's footprint: anchor, height, and width at 0.55 em per glyph for proportional sans-serif or 0.6 em per glyph for monospace. Any overlap is a placement fault. Fix in this order: flip the anchor; move the baseline; add a leader line; drop the picture label to a caption that carries the same word. Shrink last, and never below what the target screen can read. Shrinking both labels delays the collision and buys nothing.

## 5. The Lie Factor

The failure is a picture whose visual magnitude misstates the data's magnitude: a truncated axis, an area used to encode a length, a decoration that changes apparent size. VDQI p. 57 defines the lie factor as the size of the effect shown in the graphic divided by the size of the effect in the data. Lie factors above 1.05 or below 0.95 indicate substantial distortion (secondary source; book text not fetched). Above 1 exaggerates; below 1 obscures.

**Test**: measure both effects and divide. Outside 0.95 to 1.05 is a finding. If the true difference matters and is small, draw the difference itself in its own panel, labeled as a difference. Then redraw with the whole available series and the baseline at zero (or at the origin the reader assumes). If the effect reverses or vanishes, the finding is the window, not the ratio, and the redraw is that chart (VDQI p. 74, "Compared to what?").

## 6. Compared to What?

The failure is one chart in isolation when the reader's question is a comparison: this period against last, one design against another, six sites against each other. *Envisioning Information* p. 67: "At the heart of quantitative reasoning is a single question: Compared to what? Small multiple designs, multivariate and data bountiful, answer directly by visually enforcing comparisons of changes, of the differences among objects, of the scope of alternatives." *Beautiful Evidence* principle 1: "Show comparisons, contrasts, differences." Making comparisons is also one of the four cognitive tasks Tufte says analytical graphics exist to serve (edwardtufte.com, 2002-11-27).

**Test**: name the comparison the display exists for. If the reader must hold a second page in their head to make it, redesign toward small multiples or a shared axis. One figure per case, side by side, on one scale, already is small multiples; a fix for crowding must not merge them.

## 7. Document the Display

The failure is a figure that cannot be trusted or read on its own: no title, no source, no units, no scale, so the reader guesses at all four. *Beautiful Evidence* principle 5: "Thoroughly describe the evidence. Provide a detailed title, indicate the authors and sponsors, document the data sources, show complete measurement scales, point out relevant issues." Tufte's course teaches "how to assess the credibility of a presentation and its presenter, how to detect cherry-picking, how to reason about alternative explanations" (edwardtufte.com/online-course/). Documentation on the figure is what a reader assesses credibility from.

**Test**: cover the caption and the surrounding page. Can a reader name the units and the scale from the figure alone?

## 8. Content Counts Most

The failure comes in two forms: a design that spends its budget looking sophisticated instead of showing the data, and a design so bare the reader cannot find the point. *Beautiful Evidence* principle 6, under the heading Content Counts Most of All: "Analytical presentations ultimately stand or fall depending on the quality, relevance and integrity of their content." The Feynman-Tufte principle gives the short form, "simple design, intense content" (edwardtufte.com, 2005-03-15; quoted here without the dashes the post sets around it). Tufte's stance on who decides: "Content-driven design requires a radical shift in power and control" (edwardtufte.com, 2002-12-04).

**Test**: name one element you could remove. If none, name one datum you could add.

## Scope Notes

*Beautiful Evidence* principles 2 and 3 are in the source and are not in the kernel. Principle 2: "Show causality, mechanism, explanation, systematic structure." Principle 3: "Show multivariate data; that is show more than 1 or 2 variables." Both apply to analytical charts that make a claim, not to a setup diagram or a single-series chart. A reviewer cites principle 2 only where the display claims a cause, and principle 3 only where it carries more than two variables. VDQI ch. 2 (p. 77) states six principles of graphical integrity, carried so: proportionality is rule 5's lie factor; thorough labeling is rules 2 and 7; data variation, not design variation, is rule 5's changing-scale case; in time-series displays of money, deflated and standardized units, cited only where a display shows money over time; dimensions depicted not exceeding dimensions in the data is rule 5's area-for-length case; and context, which Tufte states as "Compared to what?" (p. 74), is rule 6, with the window test under rule 5 as its check.

## Sources

What each rule rests on, and how each source was read. "Primary" means Tufte's own words: his own site, or the book's text where a chapter was fetched (VDQI ch. 2 and 5, the course PDF at lmscontent.embanet.com). "Secondary" means another page quoting the book; the book text itself was not fetched.

- Rule 1: VDQI ch. 4 (data-ink ratio; the two erasing principles, secondary: holistics.io); chartjunk page ranges (primary: edwardtufte.com/notebook/chartjunk/); the interior-decoration quote, Bateman et al. 2010, Few, Kosara (secondary: en.wikipedia.org/wiki/Chartjunk); "Above all else show the data" (secondary: goodreads.com; qahiccupps.blogspot.com gives p. 92); the p. 120 sentence (primary: the VDQI ch. 5 text, the course PDF; secondary with page: benjaminleroy.github.io, LeRoy's review).
- The pre-question: VDQI p. 56 (primary: the ch. 2 text; LeRoy's review gives pp. 20 and 178, his own, not fetched from the book).
- Rule 2: VDQI p. 180 (secondary: the caption-and-legend sentence appears verbatim in web search results; no fetched page carried it; qahiccupps.blogspot.com gives "Words and pictures belong together" at p. 180); the friendly-graphic table (secondary: en.wikipedia.org, How to create charts for Wikipedia articles); "encoded legends, color without content" (primary: the cancer-survival thread, 2003-01-08); principle 4 (secondary: philogb.github.io/notes/Minard; eyemagazine.com, Barringer, 2012-06-28).
- Rule 3: the smallest effective difference (secondary: blas.com/visual-explanations); its placement in *Visual Explanations* (primary: the analytical-design thread, 2006-03-06); *Envisioning Information* ch. 5 states "Above all, do no harm", Tufte's own sentence, Imhof's color rules following it (secondary: blas.com; the docs.google reading notes, which set Imhof's color rules under their own heading).
- Rule 4: Albers' "1 + 1 = 3" and the combined-presence phrase (secondary: jessepollak's Escaping Flatland post; the chapter 3 placement per reading notes found by search, not fetched); "Confusion and clutter" p. 53 (secondary: robnagler.com book notes); Imhof 1975 (the journal page returned 403; Google Books reports one page of *Envisioning Information* matching "Positioning Names", page not shown; verify the page against the book).
- Rule 5: lie factor formula (secondary: en.wikipedia.org/wiki/Misleading_graph, which does not name Tufte); the 0.95 to 1.05 band and VDQI p. 57 (secondary: infovis-wiki.net/wiki/Lie_Factor); p. 74, "Compared to what?" (primary: the ch. 2 text); p. 178, the pie chart (page: en.wikipedia.org/wiki/Pie_chart, excelcharts.com; wording: verstaresearch.com; Tufte's own, edwardtufte.com/notebook/pie-charts/, 2004-01-21: "the dreaded pie chart", "Worth a try is a table"); dual y-axes: the skill's own reasoning.
- Rule 6: *Envisioning Information* p. 67 (secondary: en.wikipedia.org/wiki/Small_multiple); principle 1 (secondary: philogb); the four cognitive tasks (primary: the analytical-design thread, 2002-11-27).
- Rule 7: principle 5 (secondary: philogb; Barringer paraphrases it as "provide documentation of sources and authority"); the course topic (primary: edwardtufte.com/online-course/).
- Rule 8: principle 6 (secondary: philogb); "simple design, intense content" (primary: the Feynman-Tufte thread, 2005-03-15); content-driven design (primary: the analytical-design thread, 2002-12-04).
- Scope notes: principles 2 and 3 (secondary: philogb; Barringer); the six integrity principles, p. 77 (primary: the ch. 2 text; secondary: guypursey.com for the wording, benjaminleroy.github.io for the page).
- The density guardrail: VDQI p. 168 (secondary: guypursey.com with the page; benjaminleroy.github.io).

## See Also

- `EXAMPLES.md`: every rule above shown in a before/after pair.
- `REVIEWING.md`: how these tests become review findings.
- `SKILL.md`: the kernel, the terms table, and the guardrails (not a persona, not a ban on all non-data ink, not a density rule in either direction, not a sweep).
