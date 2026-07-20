# REVIEWING — The Review Protocol for Prose

Sidecar to `SKILL.md`. How code-reviewer (or a human) reviews a prose artifact against the kernel. Writing and reviewing are different activities: the writer applies rules; the reviewer produces findings someone else can act on. This file governs the second.

## Pass Order

Review in four passes, largest defect class first. Stopping early is allowed: a document that fails pass 1 gets that finding first, because fixing the point usually rewrites the sentences that would have been flagged later.

1. **Point.** Apply the rule 1 test to the document and to each section: delete the first sentence; was anything lost? A SITREP whose status appears in paragraph three fails here regardless of how clean the sentences are.
2. **Structure.** Scan for packed sentences (rule 3): trailing participles, comma chains, stacked clauses. Check that stated links (so, because, therefore) match the logic they claim.
3. **Words.** Sweep for cruft (rule 5, against the LANGUAGE.md list), hedges (rule 6), and agentless passives where the actor matters (rule 4).
4. **Punctuation.** Mechanical em dash search (rule 8). Zero matches expected in running prose; headings, list separators, tables, quotes, and specimens are exempt (RULES.md 8).

## Finding Format

A finding without a rewrite is a complaint. Every finding carries three parts:

```
[Minor] Rule 6: "could potentially cause somewhat significant slowdowns"
        (docs/plans/conop_compass_scoring.md, Approaches Considered)
Rewrite: "adds roughly 200 ms per call at 10k nodes (measured, n=5)"
```

Quote the sentence, name the rule, propose the replacement. The rewrite requirement keeps the reviewer honest: a rule violation you cannot rewrite may not be a violation (see What Not to Flag).

## Severity Mapping

- **Minor** (default): a kernel violation whose meaning still comes through. Cruft, isolated passives, a fixable em dash.
- **Major**: the violation obscures meaning or blocks action. A SITREP with no discernible status. A review finding so hedged it cannot be acted on. A packed sentence whose causal claim cannot be recovered by the reader.
- **Critical**: never issued for style. Critical stays reserved for its existing definition (secrets, security). Prose style cannot reach it.

Severity attaches to the effect on the reader, not to the rule number. Ten Minor cruft findings do not add up to a Major; one unrecoverable causal claim does.

## What Not to Flag

- **Grandfathered documents.** Session docs, reviews, and any doc predating adoption are records. No findings against history.
- **Quoted material.** Quotes reproduce their source, dashes and all. The specimen text in `EXAMPLES.md` pair 3 is the standing example.
- **Mission statements using "in order to."** The stated exception in rule 5; the phrase is load-bearing there.
- **Documents that grew.** Longer and truer follows this skill (see the Token Economy section of `SKILL.md` and `EXAMPLES.md` pair 3). Length alone is never a finding; a missing point is.
- **Required schema sections.** A section that exists because CONOP-FORMAT requires it is never "unnecessary." Schemas outrank style; take the completeness question to the format doc, not the style review.

## The Reviewer's Own Prose

Findings are prose artifacts. A hedged, passive, cruft-laden finding about hedging fails its own review. The finding format above is short on purpose: severity, rule, quote, rewrite. Nothing in it needs a paragraph.

## See Also

- `RULES.md`: the per-rule tests the passes apply.
- `EXAMPLES.md`: rewrites to pattern findings on.
- `ADOPTION.md`: the one-line addition that puts this protocol in code-reviewer's checklist.
