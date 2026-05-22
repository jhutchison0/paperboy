"""
Configuration management for the Research Podcast Pipeline.

Loads settings from YAML config files and environment variables.
Secrets (API keys) come from env vars or .env files.
Everything else lives in the YAML config.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml
from dotenv import load_dotenv


_PLACEHOLDER_API_KEY = "sk-ant-your-key-here"


@dataclass
class ArxivConfig:
    categories: list[str] = field(default_factory=lambda: ["cs.AI", "cs.LG", "cs.CL", "stat.ML"])
    max_results_per_category: int = 25
    sort_by: str = "submittedDate"
    rate_limit_seconds: int = 3


@dataclass
class BlogFeed:
    name: str
    url: str
    category: str = "general"


@dataclass
class BlogConfig:
    feeds: list[BlogFeed] = field(default_factory=list)
    timeout_seconds: int = 15


@dataclass
class FocusAreas:
    primary: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)


@dataclass
class ClaudeConfig:
    model: str = "claude-sonnet-4-20250514"
    scoring_model: str = "claude-haiku-4-5-20251001"
    max_tokens: int = 8000
    temperature: float = 0.7


@dataclass
class SelectorConfig:
    use_claude_scoring: bool = True
    keyword_weight: float = 0.4
    claude_weight: float = 0.6
    min_score_threshold: float = 0.3
    top_k_for_claude: int = 5


@dataclass
class DistillerConfig:
    target_word_count: int = 4500
    style: str = "3blue1brown"
    include_challenger_sections: bool = True
    user_context: str = ""


@dataclass
class AgentRunnerConfig:
    enabled: bool = True
    score_timeout: int = 30          # seconds per scoring invocation
    distill_timeout: int = 600       # seconds for briefing generation (4500-word target needs headroom)
    max_retries: int = 1
    max_output_bytes: int = 51200    # 50KB output cap
    batch_size: int = 1              # papers per scoring invocation (target: 5)


@dataclass
class PipelineConfig:
    """Top-level configuration container."""
    output_dir: str = "./output/briefings"
    date_format: str = "%y%m%d"
    max_papers_to_fetch: int = 50
    max_papers_to_score: int = 20
    days_lookback: int = 7
    dedup_cooldown_days: int = 30
    log_level: str = "INFO"

    # Sub-configs
    arxiv: ArxivConfig = field(default_factory=ArxivConfig)
    blogs: BlogConfig = field(default_factory=BlogConfig)
    focus_areas: FocusAreas = field(default_factory=FocusAreas)
    claude: ClaudeConfig = field(default_factory=ClaudeConfig)
    selector: SelectorConfig = field(default_factory=SelectorConfig)
    distiller: DistillerConfig = field(default_factory=DistillerConfig)
    agent_runner: AgentRunnerConfig = field(default_factory=AgentRunnerConfig)

    # Secrets (loaded from environment)
    anthropic_api_key: str = ""

    @classmethod
    def load(cls, config_path: Optional[str] = None, env_path: Optional[str] = None) -> "PipelineConfig":
        """
        Load configuration from YAML file and environment variables.

        Priority: env vars > .env file > YAML config > defaults

        Args:
            config_path: Path to YAML config file. Defaults to config/paperboy.yaml.
            env_path: Path to .env file. Defaults to .env in project root.
        """
        # Load .env file if it exists
        if env_path:
            load_dotenv(env_path)
        else:
            load_dotenv()  # Looks for .env in current directory

        # Determine config file path
        if config_path is None:
            # Look relative to this file's parent's parent (project root)
            project_root = Path(__file__).parent.parent
            config_path = str(project_root / "config" / "paperboy.yaml")

        # Load YAML
        raw = {}
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file, "r") as f:
                raw = yaml.safe_load(f) or {}

        # Build config object
        config = cls()

        # Pipeline settings
        pipeline_raw = raw.get("pipeline", {})
        config.output_dir = pipeline_raw.get("output_dir", config.output_dir)
        config.date_format = pipeline_raw.get("date_format", config.date_format)
        config.max_papers_to_fetch = pipeline_raw.get("max_papers_to_fetch", config.max_papers_to_fetch)
        config.max_papers_to_score = pipeline_raw.get("max_papers_to_score", config.max_papers_to_score)
        config.days_lookback = pipeline_raw.get("days_lookback", config.days_lookback)
        config.dedup_cooldown_days = pipeline_raw.get("dedup_cooldown_days", config.dedup_cooldown_days)
        config.log_level = pipeline_raw.get("log_level", config.log_level)

        # ArXiv settings
        arxiv_raw = raw.get("arxiv", {})
        config.arxiv = ArxivConfig(
            categories=arxiv_raw.get("categories", config.arxiv.categories),
            max_results_per_category=arxiv_raw.get("max_results_per_category", config.arxiv.max_results_per_category),
            sort_by=arxiv_raw.get("sort_by", config.arxiv.sort_by),
            rate_limit_seconds=arxiv_raw.get("rate_limit_seconds", config.arxiv.rate_limit_seconds),
        )

        # Blog feeds
        blogs_raw = raw.get("blogs", {})
        feeds = []
        for feed_raw in blogs_raw.get("feeds", []):
            feeds.append(BlogFeed(
                name=feed_raw["name"],
                url=feed_raw["url"],
                category=feed_raw.get("category", "general"),
            ))
        config.blogs = BlogConfig(
            feeds=feeds,
            timeout_seconds=blogs_raw.get("timeout_seconds", 15),
        )

        # Focus areas
        focus_raw = raw.get("focus_areas", {})
        config.focus_areas = FocusAreas(
            primary=focus_raw.get("primary", []),
            keywords=focus_raw.get("keywords", []),
        )

        # Claude settings
        claude_raw = raw.get("claude", {})
        config.claude = ClaudeConfig(
            model=claude_raw.get("model", config.claude.model),
            scoring_model=claude_raw.get("scoring_model", config.claude.scoring_model),
            max_tokens=claude_raw.get("max_tokens", config.claude.max_tokens),
            temperature=claude_raw.get("temperature", config.claude.temperature),
        )

        # Selector settings
        selector_raw = raw.get("selector", {})
        config.selector = SelectorConfig(
            use_claude_scoring=selector_raw.get("use_claude_scoring", config.selector.use_claude_scoring),
            keyword_weight=selector_raw.get("keyword_weight", config.selector.keyword_weight),
            claude_weight=selector_raw.get("claude_weight", config.selector.claude_weight),
            min_score_threshold=selector_raw.get("min_score_threshold", config.selector.min_score_threshold),
            top_k_for_claude=selector_raw.get("top_k_for_claude", config.selector.top_k_for_claude),
        )

        # Distiller settings
        distiller_raw = raw.get("distiller", {})
        config.distiller = DistillerConfig(
            target_word_count=distiller_raw.get("target_word_count", config.distiller.target_word_count),
            style=distiller_raw.get("style", config.distiller.style),
            include_challenger_sections=distiller_raw.get("include_challenger_sections", config.distiller.include_challenger_sections),
            user_context=distiller_raw.get("user_context", config.distiller.user_context),
        )

        # Agent runner settings
        ar_raw = raw.get("agent_runner", {})
        config.agent_runner = AgentRunnerConfig(
            enabled=ar_raw.get("enabled", config.agent_runner.enabled),
            score_timeout=ar_raw.get("score_timeout", config.agent_runner.score_timeout),
            distill_timeout=ar_raw.get("distill_timeout", config.agent_runner.distill_timeout),
            max_retries=ar_raw.get("max_retries", config.agent_runner.max_retries),
            max_output_bytes=ar_raw.get("max_output_bytes", config.agent_runner.max_output_bytes),
            batch_size=ar_raw.get("batch_size", config.agent_runner.batch_size),
        )

        # Secrets from environment
        config.anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY", "")

        return config

    def validate(self) -> tuple[list[str], list[str]]:
        """
        Validate configuration and return (errors, warnings).

        Errors are fatal — the pipeline should not start.
        Warnings are informational — the pipeline can proceed.

        Returns:
            Tuple of (errors, warnings). Empty errors list means config is valid.
        """
        errors = []
        warnings = []

        if self.anthropic_api_key == _PLACEHOLDER_API_KEY:
            warnings.append(
                "ANTHROPIC_API_KEY is the placeholder from .env.example — treating as unset. "
                "Replace it with your real key in .env, or delete .env to use the Claude CLI subscription."
            )
            self.anthropic_api_key = ""
        elif not self.anthropic_api_key:
            warnings.append(
                "ANTHROPIC_API_KEY not set. Claude scoring/distillation will use the "
                "AgentRunner (Claude Code CLI) backend if available, or keyword-only scoring."
            )

        # Required content
        if not self.arxiv.categories:
            errors.append("No ArXiv categories configured.")
        if not self.focus_areas.keywords:
            errors.append("No focus area keywords configured.")

        # Claude settings
        if not (0.0 <= self.claude.temperature <= 1.0):
            errors.append(f"claude.temperature must be 0.0-1.0, got {self.claude.temperature}.")
        if self.claude.max_tokens <= 0:
            errors.append("claude.max_tokens must be positive.")

        # Selector settings
        if not (0.0 <= self.selector.min_score_threshold <= 1.0):
            errors.append(f"selector.min_score_threshold must be 0.0-1.0, got {self.selector.min_score_threshold}.")
        if self.selector.top_k_for_claude <= 0:
            errors.append("selector.top_k_for_claude must be positive.")
        weight_sum = self.selector.keyword_weight + self.selector.claude_weight
        if abs(weight_sum - 1.0) > 0.01:
            warnings.append(
                f"selector.keyword_weight + claude_weight = {weight_sum:.2f} (expected ~1.0). "
                f"Scores may not be normalized."
            )

        # Distiller settings
        if self.distiller.target_word_count <= 0:
            errors.append("distiller.target_word_count must be positive.")

        # Pipeline settings
        if self.days_lookback <= 0:
            errors.append("days_lookback must be positive.")

        # AgentRunner bounds
        if self.agent_runner.score_timeout <= 0:
            errors.append("agent_runner.score_timeout must be positive.")
        if self.agent_runner.distill_timeout <= 0:
            errors.append("agent_runner.distill_timeout must be positive.")
        if self.agent_runner.max_output_bytes <= 0:
            errors.append("agent_runner.max_output_bytes must be positive.")
        if self.agent_runner.max_retries < 0:
            errors.append("agent_runner.max_retries must be non-negative.")

        return errors, warnings
