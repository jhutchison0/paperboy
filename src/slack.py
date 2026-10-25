"""Slack delivery: one summary post per run, stdlib HTTP only (CONOP COURIER D4, D10)."""

import json
import os
import re
import socket
import time
import urllib.error
import urllib.request
from typing import Any

API = "https://slack.com/api/"
TIMEOUT_S = 10

_sleep = time.sleep


class SlackError(RuntimeError):
    """Slack refused or failed to take a call."""


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _call(method: str, payload: dict[str, Any]) -> dict[str, Any]:
    """POST one Slack Web API call; retry once on HTTP 429, never on timeout."""
    token = os.environ.get("SLACK_BOT_TOKEN")
    if not token:
        raise RuntimeError("SLACK_BOT_TOKEN is not set; the token lives in .env")
    for attempt in (1, 2):
        req = urllib.request.Request(
            API + method,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json; charset=utf-8",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt == 1:
                _sleep(int(e.headers.get("Retry-After", "1")))
                continue
            raise SlackError(f"{method}: HTTP {e.code}") from e
        except (socket.timeout, TimeoutError) as e:
            raise SlackError(f"{method}: timed out after {TIMEOUT_S}s") from e
        except urllib.error.URLError as e:
            raise SlackError(f"{method}: {e.reason}") from e
        if not body.get("ok"):
            raise SlackError(f"{method}: {body.get('error', 'unknown_error')}")
        return body
    raise SlackError(f"{method}: HTTP 429")  # unreachable; keeps the type checker honest


def post_message(text: str, channel: str, thread_ts: str | None = None) -> str:
    """Post one message and return its ``ts``.

    Args:
        text: Message text; ``& < >`` are escaped for mrkdwn.
        channel: Channel id.
        thread_ts: Parent ``ts`` to reply in a thread.

    Returns:
        The posted message's ``ts``.

    Raises:
        RuntimeError: ``SLACK_BOT_TOKEN`` is unset.
        SlackError: Slack returned ``ok: false``, a non-2xx status, or timed out.
    """
    payload: dict[str, Any] = {"channel": channel, "text": _escape(text)}
    if thread_ts:
        payload["thread_ts"] = thread_ts
    return _call("chat.postMessage", payload)["ts"]


def auth_test() -> dict[str, Any]:
    """Call ``auth.test`` and return the parsed body.

    Raises:
        RuntimeError: ``SLACK_BOT_TOKEN`` is unset.
        SlackError: Slack rejected the token or the call failed.
    """
    return _call("auth.test", {})


MAX_TEXT = 4000
ABSTRACT_SENTENCES = 3
ABSTRACT_CHARS = 600
ERROR_CHARS = 500
LEGEND = (
    "Reactions on this message: :white_check_mark: agree, :one: to :five: the rank "
    "you would have picked, :headphones: heard"
)


def _trim_abstract(abstract: str, max_chars: int = ABSTRACT_CHARS) -> str:
    """Keep three sentences or ``max_chars``, whichever is shorter; mark a cut with an ellipsis."""
    flat = " ".join(abstract.split())
    sentences = re.split(r"(?<=[.!?])\s+", flat)
    out = " ".join(sentences[:ABSTRACT_SENTENCES])
    cut = len(sentences) > ABSTRACT_SENTENCES
    if len(out) > max_chars:
        head = out[: max(max_chars - 1, 0)]
        space = head.rfind(" ")
        out, cut = (head[:space] if space > 0 else head).rstrip(), True
    return out.rstrip(".,;:") + "…" if cut else out


def _success(result: Any, max_abstract: int) -> str:
    sel = result.selected_paper
    top = [
        f"{i}. {c.paper.title} ({c.score:.2f})"
        for i, c in enumerate(result.top_candidates[:5], 1)
    ]
    words = result.briefing.word_count if result.briefing else 0
    tele = (
        f"{result.status} | {result.backend} | {result.distill_model or 'cli-default'}"
        f" | {round(result.duration_s)}s | {words} words"
    )
    if result.briefing_path is not None:
        briefing_line = f"Briefing: {result.briefing_path.name} on the home share"
    else:
        briefing_line = "No briefing this run (no Claude backend); the selection is recorded"
    return "\n".join(
        [
            f"*{sel.paper.title}*",
            sel.paper.url,
            sel.reasoning,
            _trim_abstract(sel.paper.abstract, max_abstract),
            "Top five today:",
            *top,
            briefing_line,
            LEGEND,
            tele,
        ]
    )


def build_message(result: Any) -> str:
    """Render a run result as the one Slack post (CONOP COURIER D4).

    Args:
        result: Run result with ``status`` of success, partial or error.

    Returns:
        The message text, under 4,000 characters for a success.

    Raises:
        ValueError: ``result.status`` is none of the three.
    """
    if result.status == "success":
        budget = ABSTRACT_CHARS
        text = _success(result, budget)
        while len(text) >= MAX_TEXT and budget > 0:
            budget = max(budget - (len(text) - MAX_TEXT + 1), 0)
            text = _success(result, budget)
        return text[: MAX_TEXT - 1]
    if result.status == "partial":
        sel = result.selected_paper
        return "\n".join(
            [
                ":warning: Paperboy ran partially.",
                f"*{sel.paper.title}* ({sel.score:.2f})",
                f"Error: {(result.error or 'unknown error')[:ERROR_CHARS]}",
                "Briefing not recorded for dedup; the next run retries.",
            ]
        )
    if result.status == "error":
        return f":x: Paperboy run failed.\n{(result.error or 'unknown error')[:ERROR_CHARS]}"
    raise ValueError(f"unknown status: {result.status!r}")
