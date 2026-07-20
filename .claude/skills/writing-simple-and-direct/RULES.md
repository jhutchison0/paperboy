# RULES — The Kernel Expanded

Sidecar to `SKILL.md`. Each rule with the failure it counters and the test that catches it. The kernel itself is eight lines in `SKILL.md` and CLAUDE.md; this file is the depth behind them.

## 1. Point First

The default failure is throat-clearing: "This document describes...", "In this section we will...". The point of a SITREP is the status. The point of a review is the verdict. Lead with it.

**Test**: delete the first sentence of the draft. If nothing is lost, it was throat-clearing.

## 2. Concrete Words

Abstraction hides failure. "Performance issues exist in the scoring subsystem" reports nothing. "The scorer times out on graphs above 40 nodes" reports a fact someone can act on.

**Test**: if the noun could appear unchanged in any project's document, it is too abstract for this one.

## 3. One Idea Per Sentence

Packed sentences smuggle unexamined links. Trailing participles are the usual vehicle: "..., enabling X, which supports Y." Ask what "enabling" claims. Causes? Permits? Correlates? Write the link as its own sentence with a real verb. Ideas connected in reality need words that state the connection.

**Test**: count the claims in the sentence. More than one claim needs more than one sentence, or a conjunction that names their logic.

## 4. Active Voice

"It was decided" hides the decider, and decisions in this repo have named deciders by design (see Command and Signal in OPORD-FORMAT). Passive is correct when the actor is unknown or irrelevant: "the file was corrupted" needs no agent. Everywhere else, name who did what.

**Test**: ask "by whom?" If the answer matters and the sentence omits it, rewrite.

## 5. Cruft Words

Omnibus words claim much and specify nothing. Starter list in `SKILL.md`; authoritative list in LANGUAGE.md beside the banned ambiguous words. Same mechanism, same maintenance. One exception, stated once: mission statements keep "in order to" because the phrase carries the purpose clause there. Everywhere else, "to" does the work.

**Test**: delete the word. If the sentence loses no meaning, the word was cruft.

## 6. Hedge with Numbers

Stacked qualifiers simulate caution without adding information. "This could potentially cause somewhat significant slowdowns" gives a decision nothing to use. Either quantify ("adds roughly 200 ms per call"), name the unknown ("untested above 10k rows"), or commit. Uncertainty is information. Vagueness is not.

**Test**: could a reader act differently based on the hedge? If not, it carries no information; cut it or replace it with a number.

## 7. The Say-Test

Revision happens by ear. Read the sentence as if reporting it aloud to the lead. Words you would never say (aforementioned, thusly, "per the above") do not belong in writing either. This catches tone drift that no word list can.

**Test**: the rule is the test.

## 8. No Em Dashes

An em dash declares "these thoughts are related" without saying how. This repo bans undeclared relationships in its nouns (LANGUAGE.md bans unqualified "plan"); punctuation gets the same treatment. Choose the mark that states the relationship; the table lives in `SKILL.md`. Two side effects, both wanted: sentences unpack, so rule 3 gets enforced by punctuation; and a well-known tell of machine-generated prose disappears from our artifacts.

The rule governs running prose, where the dash substitutes for stated logic. Typographic uses are outside it: headings and titles, list-index separators, tables, quoted material, and code or specimen text keep their conventions.

**Test**: mechanical. Search the running prose for the character. A match inside a sentence is a finding; a match in a heading, list separator, table, quote, or specimen is not.

## See Also

- `EXAMPLES.md`: every rule above shown in a before/after pair.
- `REVIEWING.md`: how these tests become review findings.
- `SKILL.md`: the kernel, the punctuation table, and the guardrails (not a persona, not a length cap, not retroactive).
