# EXAMPLES — Before and After

Sidecar to `SKILL.md`. Domain-native pairs, written for this repo. Each shows the kernel rules at work with word counts for the quoted text only. Note pair 3: direct is not always shorter. Cruft shrinks; fog grows into facts.

---

## 1. SITREP opener

**Before** (41 words):
> This SITREP provides a comprehensive overview of the current status of the ongoing work related to the velocity scoring engine, including progress that has been made, issues that have been encountered, and next steps that are planned for the upcoming session.

**After** (16 words):
> Wave 2 is blocked. The scorer times out on graphs above 40 nodes; fix proposed below.

**Rules applied**: 1 (point first), 2 (concrete), 5 (cruft).
The before sentence is a table of contents for itself. The after sentence is the report.

---

## 2. Review finding

**Before** (25 words):
> It was observed that there could potentially be some performance concerns with the approach that was selected, which might possibly impact scalability in certain scenarios.

**After** (18 words):
> Major: score_graph() is O(n²) in node count. At 10k nodes it takes 40 seconds against a 5-second budget.

**Rules applied**: 2 (concrete), 4 (active), 6 (numbers).
Five hedges became two measurements and a severity. A reviewer who cannot name the function and the number has not finished reviewing.

---

## 3. ADR consequence (the growing pair)

**Before** (15 words):
> We chose append-only doctrine updates — this preserves history and avoids merge conflicts — which supports auditability.

**After** (25 words):
> We chose append-only doctrine updates. Appending preserves history, so every past notification remains auditable. It also avoids merge conflicts because no line is ever rewritten.

**Rules applied**: 3 (one idea per sentence), 8 (no em dashes).
The revision is longer because the em dashes were hiding two causal claims. Writing "so" and "because" forced them into the open. Longer and truer beats shorter and smudged.

---

## 4. Backbrief

**Before** (19 words):
> Significant progress was made on the testing infrastructure, with various improvements implemented across multiple components to enhance overall reliability.

**After** (20 words):
> Added 14 tests for wave_loader.py and fixed the flaky fixture in conftest.py. Suite: 212 passing, zero flaky over 20 runs.

**Rules applied**: 2 (concrete), 4 (active).
Same length, opposite information density. The before could describe any week of any project ever; the after can be verified.

---

## 5. Proposal recommendation

**Before** (20 words):
> This approach leverages a robust, comprehensive framework to seamlessly facilitate the integration of the scoring module, streamlining the overall workflow.

**After** (14 words):
> This approach connects the scoring module through one adapter file. Callers do not change.

**Rules applied**: 5 (cruft), 2 (concrete).
Six banned words removed; two facts remain. If removing the cruft leaves nothing, the proposal had nothing.

---

## 6. Commit message

**Before** (17 words):
> Made some updates to potentially improve how the config loading might handle certain edge cases somewhat better

**After** (19 words):
> Fix config loader crash on empty YAML files. Empty files now return the default config. Add a regression test.

**Rules applied**: 1 (point first), 2 (concrete), 6 (numbers or nothing).
A commit message is a claim about what changed. Hedged claims cannot be reverted, bisected, or trusted.

---

## See Also

- `RULES.md`: the tests behind each rule applied above.
- `REVIEWING.md`: turning a before-sentence into a finding with a rewrite.
