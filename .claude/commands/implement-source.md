# Implement Source Workflow

You are guiding the implementation of a new content source for the research podcast pipeline. Follow each stage carefully, confirming completion before moving to the next.

## Pre-Flight Check

First, understand what we're building:
1. Read the user's request carefully
2. Identify the source type: **RSS feed**, **API**, or **web scraper**?
3. Check if a similar source already exists in `src/sourcer.py`
4. Read `src/models.py` to understand the Paper and Article dataclasses

## Stage 1: Design

**Goal**: Define the source behavior before coding.

- [ ] What data source are we connecting to? (ArXiv, HuggingFace, blog RSS, etc.)
- [ ] What data does it provide? (title, abstract, authors, date, URL, etc.)
- [ ] How does the raw data map to the `Paper` or `Article` model?
- [ ] What authentication is needed? (API key, none, OAuth?)
- [ ] What rate limiting applies? (ArXiv requires 3s delay, etc.)
- [ ] How do we handle failures? (timeout, empty response, malformed data)
- [ ] Check `docs/design/pillars.md` for principles:
  - **Content Quality First**: Does this source provide high-quality research content?
  - **Source Diversity & Resilience**: Does it add diversity? What's the fallback if it's down?
  - **Extensibility by Design**: Does it follow the ContentSourcer ABC pattern?

**Output**: Summary of the source, its data format, model mapping, and error strategy.

---

## Stage 2: Implement Source Class

**Goal**: Extend the ContentSourcer ABC in `src/sourcer.py`.

### Add the new source class:

```python
class {SourceName}Sourcer(ContentSourcer):
    """Fetches content from {source description}.

    Config keys:
        {config_section}.{key}: {description}
    """

    def __init__(self, config: dict):
        self.config = config
        # Extract source-specific config

    def fetch(self) -> list[Paper | Article]:
        """Fetch papers/articles from {source}.

        Returns list of Paper/Article objects.
        Handles network errors gracefully — returns empty list on failure.
        """
        ...

    def health_check(self) -> bool:
        """Verify {source} is reachable and responding."""
        ...
```

**Critical checks**:
- [ ] Implements `ContentSourcer` ABC (`fetch()` and `health_check()`)
- [ ] `fetch()` returns `list[Paper]` or `list[Article]` — correctly typed
- [ ] Network errors caught and logged, never crash the pipeline
- [ ] Rate limiting respected (sleep between requests if required)
- [ ] Deduplication: checks for duplicate titles/URLs before returning
- [ ] Config-driven: URLs, limits, timeouts come from `config/paperboy.yaml`
- [ ] No API keys hardcoded — all from environment variables

**Output**: Source class implemented and importable.

---

## Stage 3: Write Tests

**Goal**: Prove correctness and resilience.

### Add tests (in `tests/` or `tests/test_pipeline.py`):

```python
class Test{SourceName}Sourcer:
    def test_fetch_returns_papers(self):
        """fetch() returns list of Paper/Article objects."""
        ...

    def test_fetch_handles_network_error(self):
        """fetch() returns empty list on network failure, doesn't crash."""
        ...

    def test_fetch_handles_empty_response(self):
        """fetch() handles source returning no results."""
        ...

    def test_fetch_deduplicates(self):
        """Duplicate papers/articles are filtered out."""
        ...

    def test_model_mapping(self):
        """Raw source data maps correctly to Paper/Article fields."""
        ...

    def test_health_check_success(self):
        """health_check() returns True when source is reachable."""
        ...

    def test_health_check_failure(self):
        """health_check() returns False when source is down."""
        ...

    def test_rate_limiting(self):
        """Respects configured rate limits between requests."""
        ...
```

### Run tests:
```bash
pytest -k {source_name}   # New source tests
pytest                     # Full suite
```

**Critical checks**:
- [ ] All external HTTP calls mocked (no real network in tests)
- [ ] Both success and failure paths tested
- [ ] Paper/Article model fields validated
- [ ] No flaky tests (no timing dependencies)

**Output**: All tests pass, error handling verified.

---

## Stage 4: Configure

**Goal**: Wire the source into the pipeline configuration.

- [ ] Add source config section to `config/paperboy.yaml`:
  ```yaml
  {source_name}:
    enabled: true
    # Source-specific settings...
  ```
- [ ] Add any new environment variables to `.env.example`
- [ ] Verify `src/config.py` can load the new config section
- [ ] Ensure defaults are sensible if config keys are missing

---

## Stage 5: Integrate

**Goal**: Register the source and verify end-to-end.

- [ ] Register the new sourcer in the pipeline (either in `src/sourcer.py` SourceManager or `src/pipeline.py`)
- [ ] Verify the pipeline runs end-to-end with the new source:
  ```bash
  python main.py          # Full pipeline run
  ```
- [ ] Check that papers from the new source:
  - Appear in the sourcing output
  - Flow through selection/scoring
  - Appear in the final briefing (if scored high enough)
- [ ] Run full test suite: `pytest`
- [ ] If substantial work, create session doc in `docs/sessions/`

---

## Ready to Start?

Tell me what content source you'd like to add. Describe where the data comes from (URL, API, RSS feed) and what kind of content it provides, and I'll guide you through each stage.
