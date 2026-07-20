# ADOPTION — Installing This Skill in a Repo

Sidecar to `SKILL.md`. Five steps, run once per repo. Downstream repos receiving this skill through propagation start here.

## 1. CLAUDE.md: The Ambient Kernel

Paste this block as a "Prose Style" section so the kernel loads every session:

```markdown
## Prose Style

All prose artifacts follow the writing-simple-and-direct skill. The kernel:

1. Have a point; state it in the first sentence. No throat-clearing.
2. Prefer the concrete word: name the file, the number, the failure.
3. One idea per sentence. Link sentences; do not pack them.
4. Active voice unless the actor is unknown or irrelevant.
5. Cut cruft words. The banned list lives in LANGUAGE.md.
6. Hedge with numbers or not at all.
7. Read it back; if you would not say it, do not write it.
8. No em dashes in running prose. Choose the mark that states the relationship.

Schemas define what a document contains; this defines how the words go.
Never cut a required section to save tokens.
```

The kernel exists in two places by design: CLAUDE.md for ambient load, `SKILL.md` for the sidecar index. Any edit changes both in the same commit.

## 2. LANGUAGE.md: The Cruft List

Add the rule 5 cruft list as a third section beside the banned ambiguous words. Starter content lives in `SKILL.md` Quick Reference. LANGUAGE.md is authoritative from that point on; the skill cites it rather than duplicating it.

## 3. code-reviewer: The Checklist Line

Add one line to the review checklist:

> Prose artifacts: review per writing-simple-and-direct/REVIEWING.md (pass order, finding format, severity mapping).

## 4. Optional, Later: Mechanical Linting

The LANGUAGE.md cruft list and the rule 8 character search compile directly to Vale rules if mechanical prose linting is ever wanted. No dependency today; the seam exists, nothing hangs on it.

## 5. Propagation

This skill propagates as a bundle (all five files) and applies to every downstream repo without adaptation. The propagation entry should restate the two boundary conditions so consumers do not over-apply the rules:

- **Grandfathering**: existing docs, session docs, and reviews are records. The rules apply to new and revised prose only.
- **Schemas outrank style**: never cut a required section to save tokens. A repo's document formats define completeness; this skill only governs wording.

## See Also

- `SKILL.md`: the kernel and guardrails this file installs.
- `REVIEWING.md`: the protocol the step 3 checklist line points to.
