# Session: Project Identity, API Access, and Agent Deployment Exploration

**Date**: 2026-03-10
**Branch**: main
**Tags**: #session #doc #config #pipeline #in-progress

**Documents**: [pillars.md](../design/pillars.md) — Reviewed all docs against design pillars for mission alignment
**Follows**: [20260310_project_bootstrap.md](20260310_project_bootstrap.md) — Continues from bootstrap session
**Requires**: API access (Anthropic API key, Bedrock, or Vertex) to enable Claude-dependent pipeline stages

---

## Summary

Established project naming identity, reviewed all primary documentation for mission alignment via pipeline-sme agent, explored the code to understand what's needed for a live run, and discovered the API access gap. Session ended with a strategic discussion about alternative approaches to powering the Claude-dependent pipeline stages, including a novel idea to deploy a local Claude Code agent on a constrained git workflow.

## Changes Made

### Documentation
- **`README.md`** — Added "Why Paperboy?" section with origin story: *"You're literally on a bike, getting papers delivered. It's the 1985 arcade game but instead of throwing newspapers at houses, you're absorbing ArXiv papers on an exercise bike."* Anchored with identity sentence: *"the repo's real job is straightforward: source, score, and deliver a daily academic briefing — like a real paperboy, rain or shine."*
- **`CLAUDE.md`** — Added "About the Name" section establishing the flavor boundary: arcade/fitness is a nod, not the focus. Explicit guardrail: *"Don't theme things around arcades, bikes, or fitness."*

### Code
- **`requirements.txt`** — Added `pytest>=8.0` as explicit dependency
- **`test_pipeline.py`** — Fixed `test_selection` fixture issue: added `import pytest`, proper `@pytest.fixture` for `config`, removed return values from test functions, updated `__main__` block

### Infrastructure
- **`.gitignore`** — Added `output/` and `.claude/agent-memory/` entries

## Pipeline-SME Doc Review

Ran the pipeline-sme agent across all 6 primary docs (CLAUDE.md, README.md, project.yaml, default_config.yaml, pillars.md, roadmap.md). **All aligned.** Key findings:

- Flavor contained to exactly two sections (README "Why Paperboy?" + CLAUDE.md "About the Name"), zero leakage into technical docs
- `pillars.md` is the strongest doc — consumption context appears once in Pillar 1 as a functional design constraint, not flavor
- `default_config.yaml` `distiller.style: "3blue1brown"` is a legit style reference, not a tangent

## API Access Gap

### The Problem

The pipeline's Claude-dependent stages (semantic scoring in `selector.py`, briefing generation in `distiller.py`) use the `anthropic` Python SDK, which requires an API key:

```python
# src/pipeline.py:79
self.claude = Anthropic(api_key=config.anthropic_api_key)
```

The user has a Max20 subscription with OAuth credentials, but **Max subscription OAuth tokens cannot be used with the `anthropic` Python SDK**. This is a policy restriction — OAuth is licensed for Claude.ai and Claude Code CLI only, not programmatic API access.

The user attempted to obtain an API key from console.anthropic.com but Anthropic is experiencing email delivery issues: *"We are experiencing delivery issues with some email providers and are working to resolve this."*

### What Works Without an API Key

| Pipeline Stage | Claude Required? | Status |
|----------------|-----------------|--------|
| ArXiv sourcing | No | Ready to run |
| RSS blog sourcing | No | Ready to run |
| Keyword scoring | No | Ready to run |
| Claude semantic scoring | **Yes** | Blocked |
| Briefing distillation | **Yes** | Blocked |
| Markdown save | No | Ready to run |

### Four Options Discussed

1. **Get the API key** — Resolve the email delivery issue with Anthropic support. Cleanest path but blocked on Anthropic's infrastructure.

2. **Cloud provider (Bedrock/Vertex)** — Swap `anthropic.Anthropic()` for Bedrock or Vertex client. Requires AWS or GCP account. User has a Gemini subscription but doubts it includes Vertex API access.

3. **Shell out to Claude Code CLI** — Replace `anthropic.Anthropic().messages.create()` calls with `subprocess.run(["claude", "-p", "..."])`, piping prompts through the CLI which authenticates via Max subscription. Unconventional but technically works with existing credentials. Trades SDK ergonomics for immediate functionality.

4. **Deploy a local Claude Code agent on a constrained git workflow** — The most ambitious option. Use Claude Code (authenticated via Max subscription) as an autonomous agent operating on a dedicated branch or worktree, given a defined workflow to execute. Rather than the pipeline calling the API directly, the pipeline delegates Claude-dependent work to a Claude Code agent with limited scope.

### On Option 4: Local Agent Deployment (User Context)

The user has significant experience with coding agent evaluation from work (GitLab workspace, may mirror to GitHub). Key details:

- **Agent comparison study**: Compared Claude Code agent vs. Aider agent vs. OpenCode agent
- **Multi-model evaluation**: OpenCode and Aider agents were powered by both GPT-5.2 and Gemini Pro
- **Kahneman-inspired agent profiles**: Agents were given System 1 (fast/intuitive) and System 2 (slow/deliberative) profiles, inspired by *Thinking, Fast and Slow*
- **Escalating difficulty challenges**: Agents were tasked with progressively harder problems, culminating in challenges requiring them to detect confirmation bias and selection bias in data — agents had to recognize gaps and change their problem-solving approach to earn full credit
- **Bottom line**: Deploying a local agent on a limited git workflow is a known-viable pattern from this research. The paperboy pipeline could benefit from this approach, particularly for the Claude-dependent stages where an agent could be given a focused mandate (e.g., "score these papers" or "distill this paper into a briefing") on a dedicated worktree.

This work lives in the user's GitLab workspace and may be mirrored to GitHub for reference.

## CLI Mismatch Finding

Documentation (CLAUDE.md, project.yaml) references `source`, `select`, and `distill` as individual CLI subcommands, but only `run`, `health`, and `info` are implemented in `main.py`. The individual stage commands are a Phase 2 deliverable.

## Design Decisions

1. **Flavor boundary** — Arcade/fitness imagery is confined to two dedicated sections. All technical docs, config, and design docs stay grounded in the research pipeline domain.

2. **Identity sentence** — *"source, score, and deliver a daily academic briefing — like a real paperboy, rain or shine"* — names the three pipeline actions, states the output, anchors the name to reliability.

## Pillar Compliance

No deviations. Documentation changes reinforce mission clarity. Test fixture fix improves reproducibility (Pillar 4).

## Follow-Up Items

### Immediate (Next Session)
- [ ] Resolve API access — try Anthropic support, check Vertex/Bedrock availability
- [ ] Implement `source` subcommand — runs sourcing stage independently, no API key needed
- [ ] Run live sourcing to validate ArXiv + RSS fetch against real endpoints
- [ ] Push commits to origin

### Phase 2 Backlog
- [ ] Implement `select` and `distill` subcommands (once API access resolved)
- [ ] Fix CLI doc mismatch — align CLAUDE.md/project.yaml with actual commands
- [ ] Create team templates (source-development.md, pipeline-feature.md, briefing-quality.md)

### Exploration
- [ ] Prototype local Claude Code agent for pipeline stages (Option 4)
- [ ] Mirror agent comparison study from GitLab to GitHub for reference
- [ ] Evaluate System 1/System 2 agent profiles for paperboy-specific workflows
