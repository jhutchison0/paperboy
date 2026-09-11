# ADOPTION: Installing This Skill in a Repo

Sidecar to `SKILL.md`. Five steps, run once per repo. Downstream repos receiving this skill through propagation start here.

## 1. CLAUDE.md: The Ambient Kernel

Paste this block as a "Figure Style" section beside "Prose Style" so the kernel loads every session:

```markdown
## Figure Style

All data displays follow the designing-clear-data-displays skill. The kernel:

1. Show the data; erase ink that carries none, within reason.
2. Label the data where it lives; a key the eye must decode fails.
3. Make every distinction as subtle as it can be and still be seen.
4. Two marks too close make a third; move one, do not shrink both.
5. Show the effect at its true size: lie factor between 0.95 and 1.05.
6. Answer "compared to what?"; small multiples over one lonely chart.
7. Document the display: title, source, units, scale on the figure.
8. Content counts most: simple design, intense content.

Schemas and a repo's UX rules define what a display must contain; this defines how the ink goes.
Before the eight: could a table or a sentence carry these numbers? Under about twenty, a table usually does (VDQI p. 56).
A UX rule that asks for a less dense display wins; state the override.
```

The kernel exists in two places by design: CLAUDE.md for ambient load, `SKILL.md` for the sidecar index. Any edit changes both in the same commit.

## 2. code-reviewer: The Checklist Line

Add one line to the review checklist, beside the prose line:

> Figures, charts, maps, and data-bearing layouts: review per designing-clear-data-displays/REVIEWING.md (pass order, finding format, severity mapping).

## 3. The Skills Index and the README Tree

List the skill in the repo's skills framework file (path, focus, use when) and add the directory to the skills tree in the `.claude/` README. Skills self-trigger by description; no team template needs to name this one.

## 4. Optional, Later: A Layout Probe

Label footprints are measurable in a headless browser: render the page, read each label's bounding box, fail the check on any overlap. That probe can sit at the gate of any change that draws. No dependency today; the seam exists, nothing hangs on it. Until then, `REVIEWING.md` gives the estimate to use.

## 5. Propagation

This skill propagates as a bundle (all five files) and applies to every downstream repo without adaptation. The propagation entry should restate the two boundary conditions so consumers do not over-apply the rules:

- **Grandfathering**: adoption triggers no sweep. A figure a change touches, or a queued task names, gets the full pass order; a display the app still renders is not a record.
- **UX rules outrank style**: a repo's own UX or accessibility rules can require a less dense display, a larger label, or a sentence in place of a table. State the override; do not ignore the rule. This skill governs only how the ink goes.

## See Also

- `SKILL.md`: the kernel and guardrails this file installs.
- `REVIEWING.md`: the protocol the step 2 checklist line points to.
