# PCI - Pre-Code Inspection

Context-aware code inspection based on what you changed. The inspection adapts to your commit.

**Military origin**: Pre-Combat Inspection - the leader's check based on the specific mission. Going to the mountains? Check cold weather gear. Night mission? Check NVGs and IR. The inspection fits the operation.

## Philosophy

PCI is **contextual and intelligent**. It answers: "What should I look closely at given these changes?"

- Analyzes your actual diff
- Applies relevant checks based on files touched
- Catches issues PCC can't (architectural, design principle violations)
- Run before merge/PR, or when PCC passes but you want confidence

For the quick standardized checklist, use `/pcc` first.

## Workflow

### Step 1: Analyze the Change Set

```bash
# Get changed files (staged + unstaged, or branch diff)
git diff --name-only HEAD~1  # Last commit
git diff --name-only main    # Branch diff from main
git diff --cached --name-only  # Staged only
```

Categorize files into domains:

| Domain | Paths |
|--------|-------|
| **Sources** | `src/sourcer.py` |
| **Selection** | `src/selector.py` |
| **Distillation** | `src/distiller.py` |
| **Pipeline** | `src/pipeline.py`, `main.py` |
| **Config** | `src/config.py`, `config/*.yaml` |
| **Models** | `src/models.py` |
| **TTS** | `src/tts_interface.py` |
| **Tests** | `tests/**/*.py`, `test_*.py` |
| **Documentation** | `docs/**/*.md` |

### Step 2: Apply Domain-Specific Checks

---

#### Source Changes (`src/sourcer.py`)

- [ ] **Graceful degradation**: Does it handle network failures, timeouts, and empty responses without crashing?
- [ ] **Rate limiting**: Respects ArXiv 3-second delay? Blog feed timeouts configured?
- [ ] **Deduplication**: Are duplicate papers/articles detected and filtered?
- [ ] **ABC compliance**: New source implements ContentSourcer ABC with `fetch()` and `health_check()`?
- [ ] **Model mapping**: Data correctly maps to Paper/Article dataclass fields?
- [ ] **Config-driven**: Source parameters (URLs, categories, limits) come from config, not hardcoded?

---

#### Selection Changes (`src/selector.py`)

- [ ] **Keyword weights**: Do weights sum correctly? Are they configurable via config?
- [ ] **Threshold configurable**: `min_score_threshold` loaded from config, not hardcoded?
- [ ] **Claude scoring prompt**: Clear, focused prompt? Produces consistent 0-1 scores?
- [ ] **Top-K logic**: Only the top-K keyword matches get Claude-scored (cost control)?
- [ ] **Hybrid scoring**: `keyword_weight` + `claude_weight` applied correctly?
- [ ] **Edge cases**: Handles zero papers, all-tied scores, missing abstracts?

---

#### Distillation Changes (`src/distiller.py`)

- [ ] **All 8 sections present**: Briefing structure complete per spec?
- [ ] **Word count targets**: Approximately 4500 words? Not truncated?
- [ ] **YAML frontmatter**: Valid frontmatter with date, paper count, sources?
- [ ] **Prompt quality**: Follows 3Blue1Brown explanatory style? Accessible tone?
- [ ] **Error handling**: Graceful fallback if Claude API fails mid-generation?
- [ ] **Context window**: Total prompt + papers fit within model context limits?

---

#### Pipeline Changes (`src/pipeline.py`, `main.py`)

- [ ] **Stage ordering**: Source -> Select -> Distill -> Export? No skipped stages?
- [ ] **Error handling**: Each stage fails gracefully without corrupting previous stage output?
- [ ] **Health checks**: Pipeline verifies API keys, network, config before starting?
- [ ] **Date-stamping**: Output files use correct date format? No overwrites of previous days?
- [ ] **Idempotency**: Running the same day twice produces consistent results, not duplicates?
- [ ] **CLI correct**: Click commands and options properly defined? Help text accurate?

---

#### Config Changes (`src/config.py`, `config/*.yaml`)

- [ ] **YAML valid**: Config files parse without errors?
- [ ] **Defaults sensible**: Missing keys fall back to reasonable defaults?
- [ ] **Environment variable overrides**: `.env` values take precedence over YAML?
- [ ] **API keys not hardcoded**: All secrets come from environment variables, never config files?
- [ ] **New fields documented**: Any new config keys have comments explaining their purpose?

---

#### Model Changes (`src/models.py`)

- [ ] **Dataclass fields typed**: All fields have type annotations?
- [ ] **Conversion methods correct**: `Article -> Paper` mapping preserves all needed data?
- [ ] **Defaults sensible**: Optional fields have reasonable defaults?
- [ ] **Serialization**: Models can be serialized to/from dict/JSON if needed?
- [ ] **Backward compatible**: Existing code using these models still works?

---

#### TTS Changes (`src/tts_interface.py`)

- [ ] **ABC defined**: Interface is abstract, not tied to a specific TTS provider?
- [ ] **Audio format**: Output format specified (MP3, WAV)?
- [ ] **Error handling**: Graceful fallback if TTS service unavailable?
- [ ] **Text chunking**: Long briefings split appropriately for TTS limits?

---

#### Test Changes (`tests/**/*.py`, `test_*.py`)

- [ ] **Coverage for new code**: New functions/classes have corresponding tests?
- [ ] **No flaky tests**: Tests don't depend on network, timing, or execution order?
- [ ] **Mocking external APIs**: ArXiv, RSS feeds, Claude API all mocked in tests?
- [ ] **Assertions match intent**: Tests check the right thing, not just "no exception"?
- [ ] **Edge cases covered**: Empty input, malformed data, API errors tested?

---

#### Test Infrastructure Safeguards

- [ ] **pytest timeout configured**: Check for timeout settings
- [ ] **Slow tests marked**: Long tests have `@pytest.mark.slow` or `@pytest.mark.timeout`?
- [ ] **Background processes tracked**: Any `run_in_background` commands have cleanup?

---

### Step 3: Report Findings

```
PCI Report - Branch: feature-huggingface-source (vs main)
=========================================================

Changes Analyzed:
  4 files changed, 95 insertions(+), 12 deletions(-)

Domains Touched:
  [Sources] src/sourcer.py
  [Config] config/paperboy.yaml
  [Tests] tests/test_pipeline.py
  [Models] src/models.py

Inspection Results:

[Source Compliance] src/sourcer.py
  [OK] Implements ContentSourcer ABC
  [OK] fetch() handles network timeouts
  [OK] health_check() verifies endpoint reachable
  [WARN] Line 78: No deduplication against existing papers

[Config Validation]
  [OK] New feed entry has name, url, category
  [OK] No API keys in config file

[Tests]
  [OK] Fetch mocked with unittest.mock
  [MISS] No test for rate limiting behavior

Summary:
  0 blocking issues
  1 warning
  1 missing test

Recommendations:
  1. Add deduplication check in HuggingFaceSourcer.fetch()
  2. Add test for rate limiting between API calls
```

### Step 4: Recommend Follow-Up Actions

Based on changes, PCI may suggest:

| Trigger | Recommendation |
|---------|----------------|
| New source added | Verify ABC compliance, test error handling, check deduplication |
| Scoring logic changed | Verify weights sum correctly, test edge cases, check cost control |
| Distiller modified | Verify all 8 sections, check word count, test prompt quality |
| Pipeline changed | Run end-to-end test, verify idempotency, check stage ordering |
| Config changed | Validate YAML, check no secrets hardcoded, verify defaults |
| Model changed | Check backward compatibility, verify serialization, test conversions |

## Output Levels

### Quick Mode (default)
Just the summary and action items:
```
/pci
```

### Verbose Mode
Full inspection details for each file:
```
/pci --verbose
```

### Focus Mode
Inspect specific domain only:
```
/pci --focus sources
/pci --focus selection
/pci --focus distillation
/pci --focus pipeline
/pci --focus tests
```

## Integration with PCC

Typical workflow:
```
1. /pcc              # Quick check - am I safe to push?
2. [fix any failures]
3. /pci              # Deep inspection - what should I review?
4. [address findings]
5. git push
```

## Key Files to Reference

| Purpose | File |
|---------|------|
| Project status & phases | `config/project.yaml` |
| Design principles | `docs/design/pillars.md` |
| Pipeline configuration | `config/paperboy.yaml` |
| Project roadmap | `docs/design/roadmap.md` |
