---
name: recording-architecture-decisions
description: Record significant architectural decisions in docs/adr/NNNN-slug.md only after a decision satisfies all three of Pocock's triple-filter gates — hard to reverse, surprising without context, and the result of a real trade-off between genuine alternatives. If any one filter fails, do not write an ADR.
version: "1.0.0"
---

# Recording Architecture Decisions

Architecture Decision Records (ADRs) capture decisions that future readers will need context for — decisions that are hard to undo, that look strange without explanation, and that came from a real choice between competing options. They are not a log of all decisions. They are a log of decisions that justify the cost of being written down.

The format and discipline are adapted from Matt Pocock's `mattpocock/skills/skills/engineering/grill-with-docs/ADR-FORMAT.md`, verbatim on the triple filter because it is the part that prevents ADR sprawl.

## When to Use

Invoke this skill **after** a decision is made that satisfies **all three** of the following gates:

1. **Hard to reverse** — the cost of changing your mind later is meaningful (rewriting many files, breaking downstream consumers, losing data, requiring coordinated migration).
2. **Surprising without context** — a future reader looking at the code will wonder "why did they do it this way?" with no obvious answer.
3. **Result of a real trade-off** — there were genuine alternatives on the table, and one was picked for specific reasons over others that also had merit.

**If any one of these three is missing, do not write an ADR.** Document the decision in:
- A commit message (for code-level choices).
- A session doc (for project-level choices that are easily reversible).
- A design doc (for in-progress thinking that isn't yet a decision).
- An inline comment (for surprising choices that are easy to reverse).

## The Triple Filter as a Gate

Examples of decisions that **pass** the filter and warrant an ADR:

- Adopting append-mode in the doctrine propagation script over overwrite-mode (hard to reverse — appended notifications accumulate; surprising — append is unusual for notification systems; real trade-off — debt visibility vs notification volume).
- Choosing single-process SQLite over Postgres for a CLI tool (hard to reverse — schema migration to multi-user; surprising — most apps default to Postgres; real trade-off — operational simplicity vs concurrency).
- Splitting a monolithic agent into proposer + code-reviewer with explicit debate (hard to reverse — agent definitions and team templates change; surprising — debate is an unusual pattern; real trade-off — single-perspective speed vs multi-perspective rigor).

Examples that **fail** the filter (do not write ADRs for these):

- Picking pytest over unittest (reversible by config change; not surprising; routine choice).
- Using `pathlib` over `os.path` (reversible per-file; not surprising in modern Python; not a real trade-off, pathlib wins).
- Renaming a file (reversible, contextual, not architectural).
- Adopting a coding-style rule (reversible by re-linting, documented in linter config).

## File Naming

ADRs live in `docs/adr/NNNN-slug.md` where:

- `NNNN` is a zero-padded four-digit sequential number (`0001`, `0002`, `0003`, ...). Use the next unused number. Never reuse a number.
- `slug` is a short kebab-case identifier for the decision (`0001-doctrine-propagation-append-mode.md`, `0007-skills-directory-form.md`).

## Format

See [`docs/adr/ADR-FORMAT.md`](../../../docs/adr/ADR-FORMAT.md) for the canonical template.

Briefly: every ADR has Status, Date, the triple-filter check, Context, Decision, Alternatives Considered, Consequences, and References.

## Workflow

When a decision lands that you believe is ADR-worthy:

1. **Run the triple filter explicitly.** Out loud or in a comment, state which way each of the three gates falls. If any fails, stop — document the decision elsewhere.
2. **Find the next ADR number.** `ls docs/adr/ | tail -1` shows the most recent. Increment.
3. **Draft the file** following `docs/adr/ADR-FORMAT.md`. Fill the triple-filter checkboxes at the top. Be specific about the alternatives — naming what was rejected matters as much as naming what was chosen.
4. **Confirm with the user.** ADRs become permanent project history. Always confirm before committing.
5. **Cross-link.** If the decision references prior ADRs, link them. If it supersedes a prior decision, mark the prior ADR's status as "Superseded by ADR-NNNN".
6. **Commit and propagate.** ADR additions are doctrine candidates — consider whether the decision affects downstream repos. If so, draft a `docs/doctrine-updates.md` entry. If not, just commit.

## Anti-Patterns to Avoid

- **ADR sprawl** — writing ADRs for every choice. The filter exists to prevent this.
- **Retroactive ADRs without alternatives** — if you cannot remember what the alternatives were, you cannot honestly write the "Alternatives Considered" section. Skip the ADR.
- **ADRs as planning docs** — ADRs record decisions that have been made. Use design docs or plans for in-progress thinking.
- **ADRs as advocacy** — the Consequences section should include negative consequences honestly. If an ADR reads like marketing, the rigor is missing.
- **Editing past ADRs** — once accepted, ADRs are append-only. To change a decision, write a new ADR that supersedes the old one.

## Sources

- Matt Pocock, [`mattpocock/skills/skills/engineering/grill-with-docs/ADR-FORMAT.md`](https://github.com/mattpocock/skills) — the triple filter, adopted verbatim.
- Michael Nygard's original ADR pattern (2011) — the format ancestor.
- This project's [`docs/adr/ADR-FORMAT.md`](../../../docs/adr/ADR-FORMAT.md) — the template this skill uses.
