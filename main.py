#!/usr/bin/env python3
"""
Research Podcast Pipeline — CLI Entry Point

Usage:
    python main.py run                          # Run the full pipeline
    python main.py run --date 2026-03-10        # Run for a specific date
    python main.py run --config my_config.yaml  # Use custom config
    python main.py run --output-dir ./my_output # Override output directory
    python main.py source                       # Source papers only
    python main.py select                       # Score and select only
    python main.py distill                      # Distill briefing only
    python main.py health                       # Check service connectivity
    python main.py info                         # Show current configuration
"""

import sys
from datetime import date, datetime
from pathlib import Path

import click

# Add project root to path so `src` is importable
sys.path.insert(0, str(Path(__file__).parent))

from src.config import PipelineConfig
from src.pipeline import DailyPipeline


def _load_and_validate(config_path):
    """Load config and handle validation errors/warnings."""
    cfg = PipelineConfig.load(config_path=config_path)
    errors, warnings = cfg.validate()
    for warn in warnings:
        click.echo(f"Note: {warn}", err=True)
    if errors:
        for err in errors:
            click.echo(f"Config error: {err}", err=True)
        sys.exit(1)
    return cfg


def _apply_date_overrides(cfg, target_date, days_back):
    """Apply --date and --days-back overrides to config. Exits on error."""
    if target_date and days_back:
        click.echo("Config error: --date and --days-back are mutually exclusive.", err=True)
        sys.exit(1)
    if target_date:
        try:
            parsed = datetime.strptime(target_date, "%Y-%m-%d").date()
        except ValueError:
            click.echo(f"Config error: Invalid date format '{target_date}'. Use YYYY-MM-DD.", err=True)
            sys.exit(1)
        delta = (date.today() - parsed).days
        if delta < 0:
            click.echo(f"Config error: --date {target_date} is in the future.", err=True)
            sys.exit(1)
        cfg.days_lookback = max(delta + 1, 1)  # +1 to include the target date
        click.echo(f"Targeting papers from {parsed} (days_lookback={cfg.days_lookback})")
    if days_back:
        cfg.days_lookback = days_back


@click.group()
def cli():
    """Research Podcast Pipeline — Daily AI research briefings for your workout."""
    pass


@cli.command()
@click.option("--config", type=click.Path(exists=True), default=None, help="Path to config YAML file")
@click.option("--output-dir", type=click.Path(), default=None, help="Override output directory")
@click.option("--days-back", type=int, default=None, help="Override days lookback for paper search")
@click.option("--date", "target_date", type=str, default=None, help="Target date (YYYY-MM-DD). Computes days-back from today.")
@click.option(
    "--backend",
    type=click.Choice(["auto", "api", "agent", "keyword-only"], case_sensitive=False),
    default="auto",
    help="Claude backend: auto (detect), api (SDK), agent (CLI), keyword-only (no Claude)",
)
def run(config, output_dir, days_back, target_date, backend):
    """Run the full pipeline: source -> select -> distill -> save."""
    cfg = _load_and_validate(config)

    if output_dir:
        cfg.output_dir = output_dir
    _apply_date_overrides(cfg, target_date, days_back)

    pipeline = DailyPipeline(cfg, backend=backend)
    result = pipeline.run()

    if result.success:
        click.echo(f"\n{'=' * 60}")
        click.echo(f"SUCCESS!")
        click.echo(f"{'=' * 60}")
        click.echo(f"Paper:    {result.selected_paper.paper.title[:80]}")
        click.echo(f"Score:    {result.selected_paper.score:.2f}")
        if result.briefing:
            click.echo(f"Words:    {result.briefing.word_count}")
            click.echo(f"Saved to: {result.briefing_path}")
            click.echo(f"\nUpload this file to NotebookLM to generate your podcast!")
        elif pipeline.distiller is None:
            click.echo(f"\nNo briefing generated (keyword-only mode).")
        else:
            click.echo(f"\nWarning: Briefing generation failed. Paper was selected but no briefing was produced.")
            click.echo(f"Try re-running or check logs for details.")
    else:
        click.echo(f"\nPipeline failed: {result.error}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--config", type=click.Path(exists=True), default=None, help="Path to config YAML file")
@click.option("--days-back", type=int, default=None, help="Override days lookback")
@click.option("--date", "target_date", type=str, default=None, help="Target date (YYYY-MM-DD)")
def source(config, days_back, target_date):
    """Source papers and articles only (no scoring or distillation)."""
    cfg = _load_and_validate(config)
    _apply_date_overrides(cfg, target_date, days_back)

    from src.sourcer import SourceManager
    sm = SourceManager(cfg)
    papers, articles = sm.fetch_all()

    click.echo(f"\nSourced {len(papers)} papers and {len(articles)} articles")
    for p in papers[:10]:
        click.echo(f"  [{p.source}] {p.title[:80]}")
    if len(papers) > 10:
        click.echo(f"  ... and {len(papers) - 10} more")
    for a in articles[:5]:
        click.echo(f"  [blog] {a.title[:80]}")
    if len(articles) > 5:
        click.echo(f"  ... and {len(articles) - 5} more")


@cli.command()
@click.option("--config", type=click.Path(exists=True), default=None, help="Path to config YAML file")
@click.option("--days-back", type=int, default=None, help="Override days lookback")
@click.option("--date", "target_date", type=str, default=None, help="Target date (YYYY-MM-DD)")
@click.option(
    "--backend",
    type=click.Choice(["auto", "api", "agent", "keyword-only"], case_sensitive=False),
    default="keyword-only",
    help="Claude backend for scoring (default: keyword-only)",
)
def select(config, days_back, target_date, backend):
    """Source papers and score/select the best candidate."""
    cfg = _load_and_validate(config)
    _apply_date_overrides(cfg, target_date, days_back)

    from src.sourcer import SourceManager
    from src.pipeline import DailyPipeline

    # Source
    sm = SourceManager(cfg)
    papers, articles = sm.fetch_all()
    if not papers and not articles:
        click.echo("No papers or articles found. Check your network and config.", err=True)
        sys.exit(1)

    click.echo(f"Sourced {len(papers)} papers and {len(articles)} articles")

    # Select
    pipeline = DailyPipeline(cfg, backend=backend)
    scored = pipeline.selector.select_best(papers, articles, top_k=5)

    click.echo(f"\nTop {len(scored)} candidates:")
    for i, sp in enumerate(scored, 1):
        click.echo(f"  {i}. [{sp.score:.3f}] {sp.paper.title[:70]}")
        click.echo(f"     {sp.reasoning[:100]}")


@cli.command()
@click.option("--config", type=click.Path(exists=True), default=None, help="Path to config YAML file")
@click.option(
    "--backend",
    type=click.Choice(["auto", "api", "agent"], case_sensitive=False),
    default="auto",
    help="Claude backend for distillation (required — no keyword-only mode)",
)
@click.option("--output-dir", type=click.Path(), default=None, help="Override output directory")
@click.option("--paper-id", type=str, default=None, help="ArXiv paper ID to distill directly (e.g., 1904.12787)")
def distill(config, backend, output_dir, paper_id):
    """Source, select, and distill a briefing (full pipeline, explicit distillation focus)."""
    cfg = _load_and_validate(config)

    if output_dir:
        cfg.output_dir = output_dir

    pipeline = DailyPipeline(cfg, backend=backend)
    if pipeline.distiller is None:
        click.echo("Distillation requires a Claude backend (api or agent). Set ANTHROPIC_API_KEY or install Claude CLI.", err=True)
        sys.exit(1)

    # Fetch specific paper by ArXiv ID if provided
    paper_override = None
    if paper_id:
        from src.sourcer import ArxivSourcer
        click.echo(f"Fetching ArXiv paper: {paper_id}")
        try:
            sourcer = ArxivSourcer(cfg)
            paper_override = sourcer.fetch_by_id(paper_id)
            click.echo(f"Found: {paper_override.title[:80]}")
        except Exception as e:
            click.echo(f"Error fetching paper {paper_id}: {e}", err=True)
            sys.exit(1)

    result = pipeline.run(paper_override=paper_override)

    if result.success and result.briefing:
        click.echo(f"\nBriefing distilled: {result.briefing.word_count} words")
        click.echo(f"Saved to: {result.briefing_path}")
    elif result.success:
        click.echo("\nPaper selected but briefing generation failed.", err=True)
        sys.exit(1)
    else:
        click.echo(f"\nPipeline failed: {result.error}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--config", type=click.Path(exists=True), default=None, help="Path to config YAML file")
def health(config):
    """Check connectivity to ArXiv, blog feeds, Claude API, and Claude CLI."""
    cfg = PipelineConfig.load(config_path=config)

    if not cfg.anthropic_api_key:
        click.echo("Note: ANTHROPIC_API_KEY not set — Claude API check will be skipped.")

    pipeline = DailyPipeline(cfg, backend="keyword-only")
    results = pipeline.health_check()

    click.echo(f"\nHealth Check Results:")
    click.echo(f"{'=' * 40}")
    all_ok = True
    for service, healthy in results.items():
        status = click.style("OK", fg="green") if healthy else click.style("FAILED", fg="red")
        click.echo(f"  {service:.<30} {status}")
        if not healthy:
            all_ok = False

    if all_ok:
        click.echo(f"\nAll services healthy!")
    else:
        click.echo(f"\nSome services are unhealthy. Check logs for details.")
        sys.exit(1)


@cli.command()
@click.option("--config", type=click.Path(exists=True), default=None, help="Path to config YAML file")
def info(config):
    """Display current pipeline configuration."""
    cfg = PipelineConfig.load(config_path=config)

    click.echo(f"\nResearch Podcast Pipeline — Configuration")
    click.echo(f"{'=' * 50}")
    click.echo(f"Output dir:     {cfg.output_dir}")
    click.echo(f"Days lookback:  {cfg.days_lookback}")
    click.echo(f"ArXiv categories: {', '.join(cfg.arxiv.categories)}")
    click.echo(f"Blog feeds:     {len(cfg.blogs.feeds)}")
    for feed in cfg.blogs.feeds:
        click.echo(f"  - {feed.name}")
    click.echo(f"Focus keywords: {len(cfg.focus_areas.keywords)}")
    click.echo(f"Claude model:   {cfg.claude.model}")
    click.echo(f"Scoring model:  {cfg.claude.scoring_model}")
    click.echo(f"Claude scoring: {'enabled' if cfg.selector.use_claude_scoring else 'disabled'}")
    click.echo(f"Target words:   {cfg.distiller.target_word_count}")
    click.echo(f"API key set:    {'yes' if cfg.anthropic_api_key else 'NO'}")
    click.echo(f"Agent runner:   {'enabled' if cfg.agent_runner.enabled else 'disabled'}")


if __name__ == "__main__":
    cli()
