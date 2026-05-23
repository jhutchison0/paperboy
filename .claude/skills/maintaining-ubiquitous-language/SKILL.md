---
name: maintaining-ubiquitous-language
description: Maintain a project-specific glossary of domain terms in LANGUAGE.md at the repo root. Use when a new domain term emerges in conversation, when reviewing code that uses inconsistent terminology, when onboarding a new contributor or agent, or when an existing definition becomes stale.
version: "1.0.0"
---

# Maintaining Ubiquitous Language

Adapted from Matt Pocock's `grill-with-docs/CONTEXT-FORMAT.md` and Eric Evans's *Domain-Driven Design*. The pattern is general; the vocabulary is project-specific. This project's LANGUAGE.md covers decision science, the agent framework, the military escalation ladder, and governance — **not** TypeScript ecosystem overloads.

## When to Use

Invoke this skill when any of the following occur:

- A new domain term enters the conversation that risks being defined two different ways by two different people or two different agents.
- Code review surfaces inconsistent terminology — different files using different words for the same concept, or the same word for different concepts.
- A new contributor or agent is onboarded and needs to know what words mean here.
- An existing LANGUAGE.md entry becomes stale (the concept changed; the synonyms list is incomplete; the entry conflicts with how the term is actually used).

Do **not** invoke this skill for:
- Terms that have appeared exactly once and may not recur.
- General-purpose programming vocabulary that has no project-specific meaning.
- Synonyms or aliases handled adequately by a comment or docstring.

## Core Rules

These rules come from Pocock's CONTEXT-FORMAT.md, verbatim where strong. They are not negotiable — the discipline is the point.

- **Keep definitions tight. One sentence max.**
- **Define what it IS, not what it does.**
- **Each term gets a bold name, one-line definition, and `_Avoid:_` list of synonyms** (when ambiguity exists).
- **It is a glossary and nothing else. Not a spec, not a scratch pad.**

If you find yourself writing a multi-sentence definition, the term probably belongs in CONTEXT.md, in a design doc, or in code documentation — not in LANGUAGE.md.

## Entry Format

```markdown
**TermName**: One-sentence definition stating what the term IS, not what it does. _Avoid:_ synonym1, synonym2, synonym3.
```

Real examples from this project's LANGUAGE.md:

```markdown
**Criterion**: A dimension along which alternatives are compared. _Avoid:_ factor, attribute, measure, metric.

**Wave**: A tactical parallel-execution unit inside a CONOP or OPORD where agent teams deploy. _Avoid:_ sprint, batch.

**Skill**: A self-loading capability defined in `.claude/skills/<name>/SKILL.md` (directory form, preferred) or `.claude/skills/<name>.md` (single-file, legacy), invoked by name or auto-triggered by Claude when the description matches. _Avoid:_ procedure (too generic), playbook (already taken by team templates).
```

The `_Avoid:_` list is **only included when ambiguity exists**. A term with no plausible synonyms doesn't need one.

## Workflow

When a candidate term emerges:

1. **Notice the moment.** A term is candidate-worthy when (a) two participants in the conversation appear to mean different things by it, OR (b) the same concept has been referred to by two different names in the last few exchanges.
2. **Propose the entry inline.** Draft the entry following the format. Keep it under one sentence. Identify the `_Avoid:_` list.
3. **Confirm with the user.** Do not commit to LANGUAGE.md without the user's nod — definitions are policy-level, not implementation-level.
4. **Update LANGUAGE.md.** Add the entry to the correct topical section (Decision Science, Agent Framework, Escalation Ladder, Governance, Workflow Artifacts, or a new section if the term doesn't fit).
5. **Propagate the rename.** If the new entry conflicts with existing prose or code (e.g., LANGUAGE.md now says use "criterion" but several files say "factor"), surface the inconsistency. Do not silently rewrite — flag it for the user to decide whether to fix now or track as a separate task.

## What LANGUAGE.md Is Not

To prevent scope creep, LANGUAGE.md is **not**:

- A specification of behavior. (That's CONTEXT.md or design docs.)
- A scratch pad for exploratory thinking. (That's `docs/design/hold/` or session notes.)
- A list of every term in the codebase. (Only project-specific terms with ambiguity risk belong.)
- A versioned API surface. (Definitions can change; consumers don't depend on stability.)
- Documentation of one-off jargon. (Recurrence + ambiguity is the bar.)

## Sources

- Eric Evans, *Domain-Driven Design* — the original "ubiquitous language" pattern.
- Matt Pocock, [`mattpocock/skills/skills/engineering/grill-with-docs/CONTEXT-FORMAT.md`](https://github.com/mattpocock/skills) — the format and discipline adopted here.
- This project's [LANGUAGE.md](../../../LANGUAGE.md) — the artifact this skill maintains.
