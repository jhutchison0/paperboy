# ADR-0001: Directory Form Mandatory for All New Skills

**Status**: Accepted
**Date**: 2026-05-22
**Decision-maker(s)**: jhutchison (lead). Decision adopted from upstream `utils` as part of the 2026-05-19 doctrine cycle; paperboy applies the same rule going forward.

---

## Triple-Filter Check

- [x] **Hard to reverse** — once skill authoring conventions are entrenched and agents are reading sidecar files via progressive disclosure, reverting to single-file form requires either rewriting every directory-form skill back to a monolith or maintaining a mixed-form codebase. Both regress on the original problem.
- [x] **Surprising without context** — a contributor writing a 50-line skill might reasonably ask: "Why am I creating a directory for this?" The default intuition is that single-file is simpler for small things.
- [x] **Result of a real trade-off** — single-file is genuinely simpler per-skill and was paperboy's historical pattern (the five skills deleted in this cycle were all single-file). Directory form carries structural overhead. The trade-off chose prevention of the 1500-line monolith over per-skill ergonomics.

All three filter conditions pass. ADR is warranted.

---

## Context

Before the 2026-05-22 doctrine adoption, paperboy held five single-file skills inherited from upstream `utils` v1: `SKILLS_FRAMEWORK.md`, `configuration-management.md` (1533 lines), `python-venv-management.md` (623 lines), `shift-left-testing.md` (1242 lines), and `session-end.md`. Three of those crossed any reasonable line-count threshold for monolith concerns; none of them had been audited or refactored locally.

Anthropic's December 2025 open skills standard had codified a directory form (`SKILL.md` plus sidecar files, progressive disclosure) explicitly to prevent skills from outgrowing their context budget. Matt Pocock's skills repo had been using the pattern in production for months.

The upstream `utils` 2026-05-19 doctrine cycle made this decision for its own repo (utils' [ADR-0001](https://github.com/jhutchison0/utils/blob/main/docs/adr/0001-directory-form-mandatory-for-new-skills.md)) and propagated SKILLS_FRAMEWORK v2 plus three legacy single-file skills refactored to directory form. Paperboy adopted that bundle on 2026-05-22.

The question this ADR resolves is: **does paperboy keep the same rule, or does it diverge?**

A numeric trigger ("migrate at >500 lines") was considered and rejected by the same reasoning as upstream — every legacy skill in this repo had silently crossed that threshold without action. The rule self-violated.

---

## Decision

**All new skills MUST be authored in directory form** (`.claude/skills/<name>/SKILL.md` + optional sidecars), regardless of expected size. The single-file form (`.claude/skills/<name>.md`) is **not used** for any new skill. The five legacy single-file skills inherited from upstream v1 were deleted on 2026-05-22 and replaced by their directory-form counterparts. No further single-file skills are added to this repo.

Concretely:

- A new skill starts at `.claude/skills/<name>/SKILL.md` with the standard YAML frontmatter (`name`, `description`, `version`, optional `allowed-tools`).
- Sidecars are added when topical separation warrants them, not at a line-count threshold. A 30-line skill is a directory with one file; that is correct.
- `SKILLS_FRAMEWORK.md` v2 documents the layout spec; this ADR records the mandatory-not-optional nature of the rule.

---

## Alternatives Considered

### Alternative A: Numeric trigger ("migrate at >N lines")

A line-count threshold that mandates directory form only past that point. Smaller skills stay single-file. Appealing because it preserves zero-overhead for genuinely small skills.

Rejected because:
- Every legacy single-file skill paperboy inherited crossed 500 lines without anyone noticing or acting on it. The rule self-violated.
- Authors do not reliably predict how a skill will grow; the threshold debate would recur at every PR.
- The cost of "premature" directory form is one extra directory and one extra file — trivial. The cost of "delayed" directory form is a 1500-line monolith refactor — non-trivial.

### Alternative B: Diverge from upstream — keep single-file as the default

Paperboy has fewer skills than utils and skill bloat is less acute. Keeping single-file would minimize per-skill overhead.

Rejected because:
- Aligning with upstream simplifies future doctrine adoption — any new skill that lands upstream in directory form lands here unchanged.
- The five legacy skills had already drifted past size thresholds without local action; predicting better self-discipline this time is unwarranted.
- Aligns with Anthropic's December 2025 open standard regardless of upstream.

### Alternative C: Mandatory directory form for all (this ADR)

Adopt upstream's rule. Slight per-skill overhead: even a 30-line skill is a directory with one file. Eliminates the "when to migrate" debate. Aligns with the Anthropic Dec 2025 open standard. Makes future sidecar additions (ENFORCEMENT.md, HOW-TO.md, etc.) natural to add without restructuring.

---

## Consequences

### Positive

- New skills are structurally ready for sidecars from day one.
- Aligns with Anthropic's December 2025 skills open standard.
- Aligns with upstream `utils` — incoming doctrine artifacts land unchanged.
- Progressive disclosure is the default frame when authoring a new skill, even when the first version is small.
- Eliminates a recurring debate ("is this skill big enough to warrant a directory?").

### Negative

- Per-skill overhead: a 30-line skill is a directory with one file instead of a single file. Slightly more typing; slightly more `ls` output.
- Contributors new to paperboy may find the convention surprising at first. `SKILLS_FRAMEWORK.md` and this ADR carry the explanation.
- Single-file skills authored externally cannot be dropped in unchanged; they require minimal wrapping into a directory.

### Neutral

- No legacy single-file skills remain after the 2026-05-22 adoption. This ADR codifies the existing state of the repo, it does not change current files.

---

## References

- [`.claude/skills/SKILLS_FRAMEWORK.md`](../../.claude/skills/SKILLS_FRAMEWORK.md) v2 — the layout spec this ADR enforces.
- [`.claude/upstream-update.md`](../../.claude/upstream-update.md) — 2026-05-19 entry: doctrine cycle that brought this decision downstream.
- `.claude/skills/shift-left-testing/ENFORCEMENT.md` — sidecar example demonstrating the value of directory form.
- Anthropic, Skills Open Standard (December 2025) — directory form with frontmatter.
- Matt Pocock, [`mattpocock/skills`](https://github.com/mattpocock/skills) — the prior-art that established directory-form as production-tested.
