# Upstream Doctrine Update

**Source**: [utils](/home/jhutchison/projects/github/utils) — shared workflow template
**Action**: Review changes below and selectively merge into your project's command files.
**Cleanup**: Delete this file after reviewing.

---

## 2026-03-26: Decision Science Module — Partially Adopted

**Reviewed**: 2026-04-04.
- `decision_science` Python module: **SKIP** — Paperboy's scoring is a 2-criteria weighted sum (~30 lines). The MAUT framework is overkill. Revisit if scoring grows to 5+ criteria.
- `decision-scientist` agent: **ADAPT** — Adopted as advisory auditor for weight validity, scoring fairness, and statistical soundness. Adapted with paperboy-specific context (selector weights, keyword scoring, thresholds).
- `decision-science` team template: **SKIP** — No dedicated team needed. Agent joins existing teams as a reviewer alongside code-reviewer when DS concerns arise.

---

## 2026-03-31: Session-Start — Add Git Sync — APPLIED

**Applied**: 2026-04-04. Added `git fetch && git pull` to session-start Step 4.

---

---

## 2026-05-19: Doctrine Artifact Buildout + Skills Framework v2 + TDD Enforcement Hook

**Processed**: 2026-05-22. Adopted via `scripts/adopt_doctrine.py` (mechanical) + hand-merge (judgment-required). Disposal:

- §1 LANGUAGE.md — **CUSTOMIZE** ✓ (paperboy domains: pipeline data model, sources, backends, escalation, governance)
- §2 CONTEXT.md — **CUSTOMIZE** ✓ (paperboy identity/mission/state/constraints with 5 pillars)
- §3 ADR system — **TEMPLATE-COPY + ADR-0001 re-attributed** ✓
- §4 propagation-protocol — **SKIP** (paperboy is downstream, not a hub)
- §5 SKILLS_FRAMEWORK v2 + 3 directory-form skills — **TEMPLATE-COPY** ✓ (5 legacy single-files deleted: shift-left-testing, configuration-management, python-venv-management, session-end, SKILLS_FRAMEWORK)
- §6 VERTICAL-SLICING — **TEMPLATE-COPY** ✓ (included in shift-left-testing directory)
- §7 PostToolUse hook + ENFORCEMENT.md — **CUSTOMIZE** ✓ (glob hand-edited to `*/src/*.py` for paperboy's flat src/ layout; ENFORCEMENT.md myproject refs replaced with `src/`)
- §8 session-end skill deletion + docs/session-doc-format.md — **CONDITIONAL + TEMPLATE-COPY** ✓ (skill deleted; format spec adopted; command slimmed)
- §9 python-prototyper agent test-first inversion — **CUSTOMIZE** ✓ (workflow inverted; flat-src/ adapted; dataclass-additions carve-out added per pipeline-sme audit)
- §10 CLAUDE.md test-first wording — **CUSTOMIZE** ✓
- §11 Python 3.10 → 3.11 bump — **TEMPLATE-COPY** ✓ (config/project.yaml + CLAUDE.md; local env is 3.12.4)
- §12 .gitignore additions — **TEMPLATE-COPY** ✓
- §13 settings.local.json → settings.json rename — **TEMPLATE-COPY** ✓ (pre-existed as untracked; plain mv)
- §17 slimmed session-end command — **CUSTOMIZE** ✓ (paperboy commit tags preserved)
- §23 scripts/adopt_doctrine.py helper — **invoked from upstream clone**, not copied into paperboy/scripts/

**Local additions** (not in upstream):
- `.claude/skills/configuration-management/PAPERBOY-NOTES.md` — carves out skill sections (profiles, ConfigLoader, ${ENV_VAR} substitution) that don't apply to paperboy's single-file YAML + hand-rolled loader pattern. Per code-reviewer audit.

**Audits**: pipeline-sme (4 fixes applied) + code-reviewer (3 fixes applied). All 161 tests pass. PostToolUse audit hook verified firing.

---

This is the largest propagation cycle to date. It bundles work from three sessions:
the doctrine-artifact buildout (LANGUAGE.md, CONTEXT.md, ADR system, propagation protocol),
the Wave 2 refactor of three legacy single-file skills into Anthropic's December 2025 open-standard directory form,
and the Pass 4 enforcement-layer build — a deterministic PostToolUse hook that audits shift-left-testing discipline on every Write/Edit to production code.

The cycle also catches up on the **Python 3.11 minimum bump** that was committed 2026-04-21 but never propagated.

Read this entry in full before merging anything — adoption mode varies per artifact.

### Files added (utils)

```
LANGUAGE.md
CONTEXT.md
docs/propagation-protocol.md
docs/session-doc-format.md
docs/adr/ADR-FORMAT.md
docs/adr/.gitkeep
docs/adr/0001-directory-form-mandatory-for-new-skills.md
.claude/skills/maintaining-ubiquitous-language/SKILL.md
.claude/skills/maintaining-project-context/SKILL.md
.claude/skills/recording-architecture-decisions/SKILL.md
.claude/skills/shift-left-testing/                       (directory replaces former single-file)
  SKILL.md
  TIERS.md
  PATTERNS.md
  MOCKS.md
  FIXTURES.md
  VERTICAL-SLICING.md
  ENFORCEMENT.md
  CI.md
  ANTIPATTERNS.md
.claude/skills/configuration-management/                 (directory replaces former single-file)
  SKILL.md + 5 sidecars
.claude/skills/python-venv-management/                   (directory replaces former single-file)
  SKILL.md + 2 sidecars
.claude/hooks/post-tool-shift-left-audit.sh              (executable; A5 PostToolUse audit)
scripts/adopt_doctrine.py                                (optional downstream-side adoption helper; see §23)
tests/unit/test_adopt_doctrine.py                        (35 tests for the helper)
```

### Files changed (utils)

```
CLAUDE.md                                                (Shift-Left Testing principle strengthened to test-first vertical-slice; hook reference)
.claude/agents/python-prototyper.md                      (workflow inverted to test-first; stale pillars.md ref repointed)
.claude/skills/SKILLS_FRAMEWORK.md                       (v2 — Anthropic Dec 18 open standard; YAML frontmatter; directory form; progressive disclosure)
.claude/README.md                                        (skills tree refreshed)
.claude/commands/session-end.md                          (Step 5 slimmed to reference docs/session-doc-format.md)
.claude/settings.json                                    (PostToolUse hook block added)
.gitignore                                               (added docs/design/hold/ and .claude/audits/)
pyproject.toml                                           (Python 3.11 min — bumped 2026-04-21)
config/project.yaml                                      (python.min_version 3.11 — bumped 2026-04-21)
```

### Files deleted (utils)

```
.claude/skills/session-end.md                            (reference content demoted to docs/session-doc-format.md)
.claude/skills/shift-left-testing.md                     (replaced by directory form)
.claude/skills/configuration-management.md               (replaced by directory form)
.claude/skills/python-venv-management.md                 (replaced by directory form)
```

### Files renamed (utils)

```
.claude/settings.local.json → .claude/settings.json      (Anthropic convention; settings.local.json now per-user override only, gitignored)
```

---

### Adoption-Mode Table (master)

Each artifact in this propagation has one of four adoption modes. Downstream maintainers — **read this table before merging anything**.

| # | Artifact | Mode | Notes |
|---|---|---|---|
| 1 | `LANGUAGE.md` (repo root) | **CUSTOMIZE** | Copy as starter template, then rewrite per your project's domains. Our terms (decision-science, escalation ladder, governance) likely do not apply verbatim. |
| 2 | `.claude/skills/maintaining-ubiquitous-language/` | **TEMPLATE-COPY** | Skill mechanics are universal. |
| 3 | `CONTEXT.md` (repo root) | **CUSTOMIZE** | Copy as starter template, then rewrite per your project's identity, mission, and constraints. The structure stays; the content is yours. |
| 4 | `.claude/skills/maintaining-project-context/` | **TEMPLATE-COPY** | Skill mechanics are universal. |
| 5 | `docs/adr/ADR-FORMAT.md` + `.gitkeep` | **TEMPLATE-COPY** | Format spec is universal. |
| 6 | `.claude/skills/recording-architecture-decisions/` | **TEMPLATE-COPY** | Skill mechanics are universal. |
| 7 | `docs/adr/0001-directory-form-mandatory-for-new-skills.md` | **TEMPLATE-COPY-WITH-NOTE** | The decision applies downstream because you're adopting the same SKILLS_FRAMEWORK v2. Copy it as your own ADR-0001 (or as ADR-NNNN if you already have ADRs). Update Decision-maker(s) field to attribute the local adoption. |
| 8 | `.claude/skills/SKILLS_FRAMEWORK.md` v2 | **TEMPLATE-COPY** | Universal. The military/civilian vocab crosswalk section stays as-is; you choose which side to use locally. |
| 9 | `.claude/skills/shift-left-testing/` (entire directory) | **TEMPLATE-COPY** | Replaces any prior single-file `shift-left-testing.md`. Discipline universal; sidecar paths reference `src/myproject/` only inside the hook script (see #12). |
| 10 | `.claude/skills/configuration-management/` | **TEMPLATE-COPY** | Replaces any prior single-file `configuration-management.md`. |
| 11 | `.claude/skills/python-venv-management/` | **TEMPLATE-COPY** | Replaces any prior single-file `python-venv-management.md`. |
| 12 | `.claude/hooks/post-tool-shift-left-audit.sh` | **CUSTOMIZE** | Copy script, **substitute the package path glob** `*/src/myproject/*.py` to match your repo's package (e.g., `*/src/yourpkg/*.py`). Everything else is portable. Run `chmod +x` after copying. |
| 13 | `.claude/settings.json` `hooks.PostToolUse` block | **TEMPLATE-COPY** | Merge into your existing settings.json (do not replace; preserve your env/permissions). Uses `$CLAUDE_PROJECT_DIR` so the path is portable. |
| 14 | `.gitignore` lines: `.claude/audits/` and `docs/design/hold/` | **TEMPLATE-COPY** | Append to your existing `.gitignore`. |
| 15 | `docs/session-doc-format.md` | **TEMPLATE-COPY** | Universal session-doc format spec. |
| 16 | `.claude/skills/session-end.md` **deletion** | **CONDITIONAL** | Only if your repo currently has it. Move the reference content out first (we put it in `docs/session-doc-format.md`); then delete. |
| 17 | `.claude/commands/session-end.md` (slimmed) | **TEMPLATE-COPY** | Replaces your existing one; Step 5 now references `docs/session-doc-format.md` instead of duplicating the body. |
| 18 | `docs/propagation-protocol.md` | **SKIP-OR-CUSTOMIZE** | Only relevant to **propagation hubs** (currently `utils` only). Skip unless your repo also serves doctrine to other repos. |
| 19 | Python 3.11 min bump (`pyproject.toml`, `config/project.yaml`, CLAUDE.md) | **TEMPLATE-COPY** | This is the catch-up from 2026-04-21. Verify your CI/local env supports 3.11 before merging. |
| 20 | `.claude/agents/python-prototyper.md` (test-first workflow + pillars ref fix) | **CUSTOMIZE** | Workflow change is universal, but the agent file contains hard-coded `src/myproject/` references in the Project Layout and Scope sections. Substitute to your package name. If you've previously customized this agent locally, diff first — see §9. |
| 21 | `CLAUDE.md` Development Principles strengthening (test-first vertical-slice) | **CUSTOMIZE** | Copy the wording template; adapt path references to your repo's package layout. |
| 22 | `.claude/settings.local.json` → `.claude/settings.json` rename | **TEMPLATE-COPY** | Anthropic convention. Your existing settings.local.json (if any) becomes per-user-override-only, gitignored. |
| 23 | `scripts/adopt_doctrine.py` + tests | **TEMPLATE-COPY** | Optional adoption helper. Automates the mechanical parts of this bundle (verbatim copies, hook substitution, settings.json merge, .gitignore append). See §23 for the action and the explicit non-goals. |

---

### 1. LANGUAGE.md and the `maintaining-ubiquitous-language` skill

A glossary of project-specific terms lives at the repo root. One-line definitions, no synonyms. Companion to `CONTEXT.md` (narrative) and `config/project.yaml` (structured state).

**Pattern source**: Matt Pocock's `grill-with-docs` skill (`CONTEXT-FORMAT.md`). Adopted as a pattern, **not adopted verbatim** — Pocock's vocabulary disambiguates TypeScript-ecosystem overloads. Yours needs to disambiguate the terms your project actually uses.

**Skill**: `.claude/skills/maintaining-ubiquitous-language/` is invoked when a new term emerges, when a definition becomes stale, or when an agent uses two words for the same thing.

**Action required**:
1. Copy `.claude/skills/maintaining-ubiquitous-language/` verbatim into your repo.
2. Copy `LANGUAGE.md` as a **starter template**. Replace the example sections (Decision Science, Agent Framework, Escalation Ladder, Governance & Propagation, Workflow Artifacts, Vocabulary Crosswalk, Anti-Glossary) with your project's actual domains. Keep the meta-structure: bold term, one-line definition, `_Avoid:_` synonyms when ambiguity exists.
3. Add LANGUAGE.md to your CONTEXT.md reading order (see §2) once both exist.

---

### 2. CONTEXT.md and the `maintaining-project-context` skill

A one-page narrative of the project's identity, mission, current state, and key constraints. Uses terms defined in LANGUAGE.md. For machine-readable state, defers to `config/project.yaml`.

**Pattern source**: Pocock's `CONTEXT-FORMAT.md`. Same adoption stance as LANGUAGE.md — pattern only, content yours.

**Skill**: `.claude/skills/maintaining-project-context/` — invoked at the start of significant new work, when the project mission changes, or when an agent needs to orient quickly.

**Action required**:
1. Copy `.claude/skills/maintaining-project-context/` verbatim.
2. Copy `CONTEXT.md` as a **starter template**. Replace Identity/Mission/Current State/Constraints/Key Relationships/Reading Order with your project's. Preserve the "Distinguishing This File from Adjacent Artifacts" table at the bottom — it prevents content from drifting into the wrong file.
3. Wire CONTEXT.md into onboarding: it should be the first file agents and humans read. Update your README (or equivalent) to point at it.

---

### 3. ADR System

Architecture Decision Records live at `docs/adr/NNNN-slug.md`. The triple-filter gate is the central discipline: write an ADR **only when** the decision is (1) hard to reverse, (2) surprising without context, and (3) the result of a real trade-off between genuine alternatives. If any one filter fails, document it elsewhere (commit message, session doc, inline comment).

**Pattern source**: Pocock's `ADR-FORMAT.md`. The triple filter is adopted verbatim.

**Files**:
- `docs/adr/ADR-FORMAT.md` — the template and the gate.
- `docs/adr/.gitkeep` — preserves the empty directory.
- `docs/adr/0001-directory-form-mandatory-for-new-skills.md` — first ADR, exercises the format. Captures the same decision you adopt when you adopt SKILLS_FRAMEWORK v2 (§5), so propagating it gives downstream a worked example and a real anchoring decision.
- `.claude/skills/recording-architecture-decisions/SKILL.md` — invocation rules; refuses to write an ADR when any filter fails.

**Action required**:
1. `mkdir -p docs/adr` and copy `docs/adr/ADR-FORMAT.md`. (Once ADR-FORMAT.md is in the directory it preserves itself in git — no `.gitkeep` needed. Copy `.gitkeep` only if you intend to leave the directory empty for a while.)
2. Copy `.claude/skills/recording-architecture-decisions/` verbatim.
3. Copy `docs/adr/0001-directory-form-mandatory-for-new-skills.md` as your own ADR-0001 (or as ADR-NNNN if you already have ADRs). Edit the Decision-maker(s) field to attribute local adoption. The decision applies in your repo because you're adopting SKILLS_FRAMEWORK v2 — so this is genuinely your decision too.
4. Add `docs/adr/` to your CONTEXT.md reading order (between propagation-protocol.md and docs/sessions/).

---

### 4. Propagation Protocol (`docs/propagation-protocol.md`)

Formalizes the doctrine-propagation governance: what counts as doctrine, the 5-question evaluation gate, batching rules, the cycle anatomy, downstream discovery, append mode, and rollback.

**Adoption mode: SKIP-OR-CUSTOMIZE.** This file is relevant only to repos that serve doctrine to other repos. Currently only `utils` does this. Most downstream repos can ignore it.

If your repo is also a hub (you propagate doctrine to other repos), copy `docs/propagation-protocol.md` and customize the "Discoverable Roster" section to match your downstream set.

---

### 5. SKILLS_FRAMEWORK v2 + Directory-Form Mandate

`.claude/skills/SKILLS_FRAMEWORK.md` is rewritten to v2. The substantive changes:

- **YAML frontmatter spec** — every SKILL.md starts with `name`, `description`, `version` (and optional `allowed-tools`, `model`, `memory`). Aligns with Anthropic's Dec 2025 open standard.
- **Directory form is now the default and mandatory for all new skills** — see ADR-0001. A skill is a directory containing `SKILL.md` and optional sidecar files. Single-file form is retained only for skills already migrated.
- **Progressive disclosure rule** — SKILL.md is the entry point and stays small (target <150 lines). Topical content moves into sidecar files (`PATTERNS.md`, `MOCKS.md`, etc.) loaded on demand. This protects the context budget when many skills exist.
- **Military/civilian vocabulary crosswalk** — for content that crosses to external audiences, substitute the civilian terms (PCC → pre-commit-check, OPORD → operations-order, etc.). Internal files keep military terms. Crosswalk lives in LANGUAGE.md.

Three legacy single-file skills were refactored to directory form in this cycle:

| Skill | Before | After | Sidecars |
|---|---|---|---|
| `shift-left-testing` | 1242 lines, single file | 9 files total: SKILL.md (103 lines) + 8 sidecars | TIERS, PATTERNS, MOCKS, FIXTURES, **VERTICAL-SLICING**, **ENFORCEMENT**, CI, ANTIPATTERNS |
| `configuration-management` | 1533 lines, single file | 6 files total: SKILL.md (88 lines) + 5 sidecars | STRUCTURE-AND-FILES, LOADER, SECRETS, VALIDATION, TESTING-AND-PATTERNS |
| `python-venv-management` | 623 lines, single file | 3 files total: SKILL.md (105 lines) + 2 sidecars | SETUP, TROUBLESHOOTING |

**Action required**:
1. Copy `.claude/skills/SKILLS_FRAMEWORK.md` verbatim — this is the spec for everything else in this section.
2. For each of the three legacy skills above, if your repo has the single-file version: **diff your local file against `utils` first** to surface customizations:
   ```bash
   diff .claude/skills/<name>.md <utils-path>/.claude/skills/<name>/SKILL.md
   diff .claude/skills/<name>.md <utils-path>/.claude/skills/<name>/PATTERNS.md     # repeat per sidecar
   ```
   If you find local-only content (project-specific examples, repo-customized commands, embedded fixture paths), copy it into the appropriate sidecar of the new directory form before deleting your single-file. Then: delete the old `.claude/skills/<name>.md`; copy the entire `.claude/skills/<name>/` directory in its place.
3. Copy ADR-0001 (§3) as your local record of the mandatory-directory-form decision.

---

### 6. Shift-Left-Testing Discipline: Vertical Slicing (`VERTICAL-SLICING.md`)

A new sidecar in the shift-left-testing skill encodes the **tracer-bullet TDD** discipline: write a failing test, then the minimum implementation that passes it, then move to the next slice. Adapted from Pocock's `tdd` skill; the rules are quoted verbatim where attributed.

The failure mode this prevents is the "horizontal slice" — writing all tests first, then all implementation — which looks productive but produces brittle code shaped by what the author *thought* the tests would need, not by what each test actually required.

**Rules** (verbatim from Pocock):
- One test at a time. Only enough code to pass the current test.
- Don't anticipate future tests.
- Never refactor while RED. Get to GREEN first. Refactor only when all tests pass.

**Action required**:
1. Already included if you adopt the new `.claude/skills/shift-left-testing/` directory (§5 step 2).
2. Surface the discipline in agent instructions — the `python-prototyper` agent update (§9) does this; mirror similar changes in any other code-writing agents you have.

---

### 7. Shift-Left-Testing Enforcement Layer (`ENFORCEMENT.md` + PostToolUse Hook)

**This is the most novel artifact in the cycle.** The skill alone is *probabilistic* — an agent may or may not invoke it on any given turn. The enforcement layer adds *deterministic* mechanisms so the discipline survives contact with agents that don't read the skill.

The enforcement gradient (documented in `.claude/skills/shift-left-testing/ENFORCEMENT.md`):

| Layer | Determinism | Blocking? | Mechanism |
|---|---|---|---|
| 1. The skill itself | Probabilistic | No | Agent reads when relevant |
| 2. CLAUDE.md Development Principle | Probabilistic | No | Agent reads at session start |
| 3. `python-prototyper.md` workflow | Probabilistic | No | Agent definition prescribes order |
| 4. **PostToolUse audit hook** | **Deterministic** | **No (logs + warns)** | Harness runs after every Write/Edit |
| 5. Stop hook diff audit | Deterministic | No | Not configured (next iteration) |
| 6. PreToolUse block hook | Deterministic | Yes | **Intentionally not configured** — see ENFORCEMENT.md |

Layers 1–4 are what this propagation ships. Layer 6 (hard-block) was MAUT-evaluated and rejected because false-positive risk on legitimate refactors / config edits outweighs the determinism gain. See `docs/reviews/20260519_pass4_enforcement_maut.md` if you want the analysis.

**What the hook does** (`.claude/hooks/post-tool-shift-left-audit.sh`):
- Fires after every `Write` or `Edit`.
- Exits silently for tools that aren't Write/Edit, paths outside `src/myproject/**/*.py`, and `__init__.py` / `conftest.py` / `test_*.py`.
- For everything else: looks for a `tests/**/test_<basename>.py` partner via `find`.
- If no partner: appends `MISSING_TEST` to `.claude/audits/shift-left-violations.log` and emits a one-line stderr warning the agent sees.
- If partner: appends `OK_TEST_EXISTS` log line.
- **Never blocks**. `set -uo pipefail` (not `-e`); always exits 0.

**Action required**:
1. Create `.claude/hooks/` directory in your repo.
2. Copy `.claude/hooks/post-tool-shift-left-audit.sh`.
3. **Substitute the path glob** — find this block in the script:
   ```bash
   case "$file_path" in
       */src/myproject/*.py) ;;
       *) exit 0 ;;
   esac
   ```
   Replace `myproject` with your repo's package name. **Bash `case` syntax notes**:
   - Single package: `*/src/yourpkg/*.py)`
   - Wildcard (any package under `src/`): `*/src/*/*.py)`
   - Multi-package alternation: list the full patterns joined by `|` — **not** parentheses. Correct: `*/src/pkg1/*.py|*/src/pkg2/*.py)`. **Wrong**: `*/src/(pkg1|pkg2)/*.py)` — that is regex/extglob syntax and is invalid in a plain bash `case` pattern. The script does not enable `extglob`, so the wrong form silently never matches and the hook does nothing (it still `exit 0`s, so you get no error — just empty audit logs).
4. `chmod +x .claude/hooks/post-tool-shift-left-audit.sh`
5. **Merge the hook block into your `.claude/settings.json`** — DO NOT REPLACE the whole file. Preserve your existing `env`, `permissions`, and any other top-level keys.

   **Case A — your settings.json has no `hooks` block**: add this as a new top-level key alongside `env` / `permissions`:
   ```json
   "hooks": {
     "PostToolUse": [
       {
         "matcher": "Write|Edit",
         "hooks": [
           {
             "type": "command",
             "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/post-tool-shift-left-audit.sh",
             "timeout": 10
           }
         ]
       }
     ]
   }
   ```

   **Case B — your settings.json already has a `hooks` block** (e.g., you already configured a formatter or logger):

   - If your existing `hooks.PostToolUse` array does NOT include a `"matcher": "Write|Edit"` entry: append the entry object above (the inner object containing `matcher` and `hooks`) to the existing PostToolUse array.
   - If your existing `hooks.PostToolUse` ALREADY has a `"matcher": "Write|Edit"` entry: append the `{ "type": "command", "command": "$CLAUDE_PROJECT_DIR/...", "timeout": 10 }` object to that matcher's inner `hooks` array. Multiple commands run sequentially under the same matcher.
   - Validate after editing with `jq -e '.hooks.PostToolUse[] | select(.matcher == "Write|Edit") | .hooks[] | select(.command | endswith("post-tool-shift-left-audit.sh"))' .claude/settings.json` — exit 0 + prints your command = correct merge.
6. Add `.claude/audits/` to your `.gitignore` (the log file lives there).
7. Copy `.claude/skills/shift-left-testing/ENFORCEMENT.md` (included if you copy the whole directory in §5).
8. **Verify the hook is installed and fires**:
   ```bash
   # (a) jq is required by the hook script — verify it's available:
   command -v jq || echo "INSTALL JQ: the hook script needs it to parse stdin"

   # (b) The script must be executable. Windows / git config core.fileMode=false can lose this:
   test -x .claude/hooks/post-tool-shift-left-audit.sh || chmod +x .claude/hooks/post-tool-shift-left-audit.sh

   # (c) Pipe-test the script directly (simulates what the harness will send):
   echo '{"tool_name":"Edit","tool_input":{"file_path":"'"$PWD"'/src/<yourpkg>/<some_existing_file>.py"}}' \
     | .claude/hooks/post-tool-shift-left-audit.sh; echo "exit=$?"
   # Expected: exit=0; if the test partner exists, no stderr; if not, a [shift-left-audit] warning.

   # (d) End-to-end: Edit a real file in src/<yourpkg>/ via Claude Code, then:
   tail -1 .claude/audits/shift-left-violations.log
   # Expected: a fresh entry timestamped within the last minute.
   ```
   If (d) shows no fresh entry but (c) worked, the settings watcher hasn't reloaded — open the `/hooks` menu in Claude Code to refresh, or restart the session.
9. **Per-developer override**: anyone who wants to disable the hook can override in `.claude/settings.local.json` (gitignored). The shipped `.claude/settings.json` is team-wide.

**What the hook does NOT catch** (be honest with your team):
- Temporal vertical-slicing violations (all tests first, then all impl — both have test partners).
- Empty test stubs that exist but contain no assertions.
- Tests in non-standard locations (the inference is strictly `tests/**/test_<basename>.py`).
- Commits made outside Claude Code.

The skill is for what hooks can't catch.

---

### 8. Session-End Skill/Command Deduplication

`.claude/commands/session-end.md` and `.claude/skills/session-end.md` previously duplicated each other. We **removed the skill** and **slimmed the command** to reference a new doc:

- `.claude/skills/session-end.md` — **deleted**. The reference content (knowledge-graph edge types, body template, diagram guidelines) moved out.
- `docs/session-doc-format.md` — **new**. Holds the reference content.
- `.claude/commands/session-end.md` — Step 5 now reads "see `docs/session-doc-format.md`" instead of duplicating the body.

Rationale: session-end is user-invoked (it has side effects — commits files). Skills with side effects that auto-trigger are wrong by construction. Per Anthropic's own docs, command and skill with the same name are equivalent — keeping both is redundant.

**Action required**:
1. Copy `docs/session-doc-format.md` verbatim.
2. **Before deleting `.claude/skills/session-end.md`**, diff it against ours to surface any local customizations:
   ```bash
   diff .claude/skills/session-end.md <utils-path>/.claude/skills/session-end.md  # before utils deleted it; compare against the prior tagged commit if needed: git -C <utils-path> show cf946b5:.claude/skills/session-end.md
   ```
   If your file has local-only content (e.g., custom edge types, repo-specific body templates, embedded checklists), copy that content into `docs/session-doc-format.md` first. Only delete the skill file once nothing of value is lost.
3. Replace `.claude/commands/session-end.md` with the slimmed version that references `docs/session-doc-format.md`. If your command had local customizations, merge them in rather than overwriting.

---

### 9. `python-prototyper` Agent Workflow Inverted to Test-First

Previous workflow:
```
3. Implement the code
4. Write tests alongside the code in tests/
```

This was code-first-tests-second; the agent definition itself was actively undermining shift-left at the enforcement surface. Now:

```
3. Plan the vertical slices (list behaviors to test in priority order)
4. For each slice, in order:
   a. Write the next failing test in tests/ — confirm RED
   b. Write minimum code in src/ that passes it — confirm GREEN
   c. Do not refactor while RED; refactor only when all tests pass
5. Run full pytest
```

Also fixed: stale reference to `docs/design/pillars.md` (which doesn't exist in `utils`); now points to `CONTEXT.md` + `config/project.yaml`.

**Adoption mode: CUSTOMIZE** (master table row 20). The file contains hard-coded `src/myproject/` references in the **Project Layout** and **Scope** sections — substitute to your package name. There is also a reference to the audit-hook log path in the Design Principles section that mentions `src/myproject/`.

**Action required**:
1. **If you have not customized this agent locally**: copy `.claude/agents/python-prototyper.md` from `utils`, then find/replace every occurrence of `myproject` with your package name. Three sections contain it: Project Layout, Scope, and the Shift-Left Testing design principle.
2. **If you have customized this agent locally**: diff first.
   ```bash
   diff .claude/agents/python-prototyper.md <utils-path>/.claude/agents/python-prototyper.md
   ```
   Merge in: (a) the workflow inversion (steps 3–5 are now test-first vertical-slice), (b) the pillars-ref fix (CONTEXT.md + config/project.yaml instead of docs/design/pillars.md), (c) the strengthened Shift-Left Testing design principle (including the hook reference). Preserve your local customizations.
3. Verify after merging: the workflow section MUST list "write failing test" before "write minimum code." If any of your local edits restore code-first ordering, the agent will undermine the rest of this propagation.

---

### 10. CLAUDE.md — Test-First Development Principle

The Shift-Left Testing principle in CLAUDE.md is strengthened from "write tests alongside code" to a mandate for test-first vertical-slice with explicit reference to the hook.

**Action required**:
1. Update your CLAUDE.md Development Principles section. Wording template:

```markdown
### Shift-Left Testing (test-first, vertical-slice)
Every new behavior in `src/<yourpkg>/` is driven by a **failing test written first**, followed by the **minimum implementation** that makes it pass, then the next slice. This is vertical-slice (tracer-bullet) TDD; see [`.claude/skills/shift-left-testing/VERTICAL-SLICING.md`](.claude/skills/shift-left-testing/VERTICAL-SLICING.md).

Do not write a horizontal slice (all tests first, then all impl). Do not write production code without a failing test driving it.

A `PostToolUse` audit hook (`.claude/hooks/post-tool-shift-left-audit.sh`) fires after every `Write`/`Edit` to `src/<yourpkg>/**/*.py` and logs evidence to `.claude/audits/shift-left-violations.log`. The hook does not block; it produces an audit trail. See [`.claude/skills/shift-left-testing/ENFORCEMENT.md`](.claude/skills/shift-left-testing/ENFORCEMENT.md) for the full enforcement gradient.
```

Substitute `<yourpkg>` to match your package name.

---

### 11. Python 3.11 Minimum (catch-up from 2026-04-21)

Bumped from 3.10 in `utils` on 2026-04-21 but the propagation cycle that day was scoped to the docs/reviews convention and didn't carry this. Catching up now.

**Files affected**:
- `pyproject.toml` — `requires-python = ">=3.11"` (utils' pyproject does not declare a classifiers table; if yours does, update the `Programming Language :: Python :: 3.X` entries to remove 3.10 and add 3.11+)
- `config/project.yaml` — `python.min_version: "3.11"`, `python_requires: ">=3.11"`
- `CLAUDE.md` — "Language: Python (3.11+)"

Rationale: `zoneinfo` is in stdlib at 3.9+, `match` is 3.10+, but 3.11 brings tomllib (stdlib TOML parsing), Exception Groups, faster startup. Most CI images and local environments are at 3.11+ already.

**Action required**:
1. Verify your local environment and CI use Python 3.11+. `python --version`.
2. If yes: update your `pyproject.toml`, `config/project.yaml`, and CLAUDE.md to declare 3.11 minimum.
3. If no: defer this part of the propagation until your environment is upgraded. The other artifacts in this cycle do not depend on Python 3.11.

---

### 12. `.gitignore` Additions

```
# Scratch / hold area (per-repo thinking workspace)
docs/design/hold/

# Claude Code
.claude/audits/
```

`docs/design/hold/` is a per-repo workspace for strategic memos, attached docs, and scratch — tracked locally on the filesystem, gitignored. `.claude/audits/` is where the shift-left audit log lives.

**Action required**: append both to your `.gitignore` (after the existing `.claude/agent-memory/` and `.claude/settings.local.json` lines if you have them).

---

### 13. `settings.local.json` → `settings.json` Rename

Anthropic's convention: `.claude/settings.json` is the team-wide checked-in file, `.claude/settings.local.json` is the per-user override (gitignored). The previous filename used `settings.local.json` for team-wide content — backwards.

**Action required**:
1. If your repo has `.claude/settings.local.json` with team-wide content: `git mv .claude/settings.local.json .claude/settings.json` so the rename is tracked. (Plain `mv` won't work cleanly if `.claude/settings.local.json` was previously gitignored — the rename needs to enter git's tracking; verify with `git status` afterward.)
2. Confirm `.claude/settings.local.json` is listed in `.gitignore` going forward. Anything in it is now per-developer-override and not committed.
3. The hook configuration from §7 lives in `.claude/settings.json` (team-wide, checked in). Per-developer disable goes in `.claude/settings.local.json` (gitignored).

---

### 23. Optional Adoption Helper (`scripts/adopt_doctrine.py`)

A downstream-side helper that applies the **mechanical** parts of this bundle for you: the 10 verbatim copies, the hook-script `myproject` → `<yourpkg>` substitution, the `.claude/settings.json` `PostToolUse` merge, and the `.gitignore` append. Everything that requires human judgment (LANGUAGE.md content, CONTEXT.md content, CLAUDE.md merge, ADR-0001 attribution, python-prototyper customization, Python 3.11 bump, hub-only propagation-protocol, legacy single-file skill deletions, `settings.local.json` rename) is **deliberately left for you** — the script prints a checklist of those items with section references back to this entry.

**Explicit non-goals**: the helper does not delete anything, does not edit `LANGUAGE.md` / `CONTEXT.md` / `CLAUDE.md` / `pyproject.toml`, does not rename `settings.local.json`, and does not overwrite existing target files (any pre-existing target is skipped with a "review by hand" status). The settings.json merge preserves all existing top-level keys and any existing `PostToolUse` matchers; it appends ours as an additional entry and is idempotent on re-run.

**Action required**:
1. Copy `scripts/adopt_doctrine.py` into your repo's `scripts/` directory. (You can also run it from a local utils clone without copying — `python ~/projects/github/utils/scripts/adopt_doctrine.py` from your repo root.)
2. Optionally copy `tests/unit/test_adopt_doctrine.py` if you want the test partner local; otherwise the upstream tests are authoritative.
3. From your repo root, dry-run first: `python scripts/adopt_doctrine.py --dry-run`. Review the printed plan and the "MANUAL ATTENTION REQUIRED" checklist.
4. Re-run without `--dry-run` to apply: `python scripts/adopt_doctrine.py`. You will be prompted `Apply changes? [y/N]` unless you pass `--yes`.
5. Apply the manual-attention items by hand using this doctrine entry as your reference.

**Flags**:
- `--upstream PATH` — local utils clone (default `~/projects/github/utils/`).
- `--package NAME` — your downstream package name (default: auto-detect from `src/<pkg>/` if exactly one subdirectory exists).
- `--dry-run` — print the plan, write nothing.
- `--yes` — skip the confirmation prompt.

**Operational safety**: dry-run is the default mental model — the explicit prompt before any write is non-negotiable in the interactive path. The helper is idempotent: re-running after a partial adoption skips already-applied items.

**The risk of using the helper vs. by-hand adoption**: the helper itself is a single point of failure — a bug in the script applies the bug to every repo that runs it. Mitigations: (a) 35 tests covering all 9 functions including settings-merge edge cases (empty / other-matcher / our-matcher-already-present); (b) skip-don't-overwrite semantics on every target; (c) the helper deliberately refuses CUSTOMIZE artifacts so the human still applies the judgment-heavy ones. If you are uncomfortable with the helper, the manual adoption path below remains fully supported.

---

### Suggested Adoption Order

**Fast path (helper-assisted, see §23)**: dry-run `scripts/adopt_doctrine.py` from your repo root, review the plan and the manual-attention checklist, re-run to apply the mechanical 13 artifacts in one step, then work through the printed checklist for the 10 judgment-required items by hand.

**Slow path (fully by hand)** — within one merge session per repo:

1. **First — the framework spec**: copy SKILLS_FRAMEWORK.md v2 (§5). Everything else makes sense against it.
2. **Refactor the three legacy skills to directory form**: shift-left-testing, configuration-management, python-venv-management (§5).
3. **Add the ADR system**: ADR-FORMAT.md, .gitkeep, the skill, ADR-0001 (§3).
4. **Add the doctrine artifacts**: LANGUAGE.md + skill (§1), CONTEXT.md + skill (§2). Customize the content as you go.
5. **Resolve session-end dedup**: docs/session-doc-format.md, delete the skill, slim the command (§8).
6. **Update python-prototyper agent**: test-first workflow + pillars ref fix (§9).
7. **Update CLAUDE.md** Development Principles (§10).
8. **Wire the enforcement layer**: copy the hook script with path substitution, merge the settings.json block, update .gitignore (§7, §12, §13).
9. **Verify**: run your test suite (should be unaffected); edit any src/ file and check `.claude/audits/shift-left-violations.log` for a fresh entry.
10. **Python 3.11 bump** (§11) — only if your environment supports it.

---

### Rollback

If anything in this cycle breaks your repo, each artifact reverts independently:

- The **PostToolUse hook** never blocks tool calls — at worst it produces noisy stderr. Disable by removing the `hooks` block from `.claude/settings.json` (or override in `.claude/settings.local.json` with `"hooks": {}`).
- The **hook script** at `.claude/hooks/post-tool-shift-left-audit.sh` is referenced only by `.claude/settings.json`. After the settings-block removal above, the script file is inert. Delete or leave it; either is fine.
- The **directory-form skill refactors** are functionally equivalent to the single-file versions — Claude Code's skill discovery picks up both forms. If a refactored skill misbehaves, revert by restoring the prior single-file from git history and removing the new directory.
- **LANGUAGE.md / CONTEXT.md** are docs only — no code consumes them. Delete the files if they're not useful yet; the skills will simply not find a glossary/context to maintain.
- **ADR system** is docs only. Delete `docs/adr/` and `.claude/skills/recording-architecture-decisions/` if not useful.
- **`.gitignore` additions** (`docs/design/hold/`, `.claude/audits/`) — remove the lines if you want either path tracked. The `.claude/audits/` line is load-bearing for the hook (without it, the audit log would be committed and noisy); only remove if you've also removed the hook.
- **`settings.local.json` → `settings.json` rename** — `git mv` back if needed. Confirm `.gitignore` matches the choice.
- **Python 3.11 bump** is in `pyproject.toml`, `config/project.yaml`, CLAUDE.md — revert these three files to restore 3.10 minimum.
- **`python-prototyper.md` workflow inversion** — `git revert` the agent file; the previous code-first workflow returns. The Pass 4 audit notes that the previous workflow was actively undermining shift-left, so revert only if you've decided not to adopt the enforcement layer at all.
- **CLAUDE.md test-first principle** — revert that section if you've decided not to adopt the enforcement layer.

---

### Source Material and Attribution

- **Matt Pocock's [`mattpocock/skills`](https://github.com/mattpocock/skills)** — pattern source for `LANGUAGE.md` (CONTEXT-FORMAT.md adapted), `CONTEXT.md` (CONTEXT-FORMAT.md adapted), `ADR-FORMAT.md` (triple filter adopted verbatim), and `VERTICAL-SLICING.md` (tracer-bullet rules adopted verbatim where attributed). **Patterns adopted, vocabulary not** — Pocock's vocab is TypeScript-ecosystem-specific.
- **Anthropic's December 2025 skills open standard** — directory form with YAML frontmatter, progressive disclosure.
- **Pass 4 reviews** — `docs/reviews/20260519_pass4_doctrine_audit.md` (code-reviewer), `docs/reviews/20260519_pass4_enforcement_maut.md` (decision-scientist), `docs/reviews/20260519_pass4_enforcement_grill.md` (proposer). Read these if you want to understand why the enforcement layer is soft-deterministic rather than hard-block.
- **utils sessions** — `docs/sessions/20260519_doctrine_artifact_buildout.md` documents the original build; the current session doc (the one in this propagation's commit) documents the Pass 4 + enforcement-layer additions.

---