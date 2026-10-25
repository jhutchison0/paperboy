"""Slack delivery: the HTTP layer against a fake urlopen, and the message texts."""

import io
import json
import re
import socket
import urllib.error
from pathlib import Path
from types import SimpleNamespace

import pytest

from src import slack


class FakeResponse:
    def __init__(self, body: dict | str, status: int = 200):
        self._raw = (body if isinstance(body, str) else json.dumps(body)).encode()
        self.status = status

    def read(self) -> bytes:
        return self._raw

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def fake_urlopen(monkeypatch, *outcomes):
    """Replace urlopen; each call pops one outcome (response or exception)."""
    calls = []
    queue = list(outcomes)

    def _urlopen(req, timeout=None):
        calls.append(SimpleNamespace(req=req, timeout=timeout))
        out = queue.pop(0)
        if isinstance(out, BaseException):
            raise out
        return out

    monkeypatch.setattr(slack.urllib.request, "urlopen", _urlopen)
    return calls


@pytest.fixture(autouse=True)
def token(monkeypatch):
    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test")
    monkeypatch.setattr(slack, "_sleep", lambda s: None)


def http_error(code: int, headers: dict | None = None) -> urllib.error.HTTPError:
    return urllib.error.HTTPError(
        "https://slack.com/api/x", code, "err", headers or {}, io.BytesIO(b"")
    )


# --- post_message -----------------------------------------------------------


def test_post_message_returns_ts_and_sends_bearer_json(monkeypatch):
    calls = fake_urlopen(monkeypatch, FakeResponse({"ok": True, "ts": "1700.01"}))
    ts = slack.post_message("hello", "C123")
    assert ts == "1700.01"
    req = calls[0].req
    assert req.full_url == "https://slack.com/api/chat.postMessage"
    assert req.get_header("Authorization") == "Bearer xoxb-test"
    assert json.loads(req.data) == {"channel": "C123", "text": "hello"}
    assert calls[0].timeout == 10


def test_post_message_sends_thread_ts_when_given(monkeypatch):
    calls = fake_urlopen(monkeypatch, FakeResponse({"ok": True, "ts": "2"}))
    slack.post_message("hi", "C1", thread_ts="1.0")
    assert json.loads(calls[0].req.data)["thread_ts"] == "1.0"


def test_post_message_escapes_mrkdwn_characters(monkeypatch):
    calls = fake_urlopen(monkeypatch, FakeResponse({"ok": True, "ts": "1"}))
    slack.post_message("a & b <c> d", "C1")
    assert json.loads(calls[0].req.data)["text"] == "a &amp; b &lt;c&gt; d"


def test_missing_token_names_dotenv(monkeypatch):
    monkeypatch.delenv("SLACK_BOT_TOKEN")
    with pytest.raises(RuntimeError, match=r"\.env"):
        slack.post_message("x", "C1")


def test_ok_false_raises_slack_error_with_slack_string(monkeypatch):
    fake_urlopen(monkeypatch, FakeResponse({"ok": False, "error": "not_in_channel"}))
    with pytest.raises(slack.SlackError, match="not_in_channel"):
        slack.post_message("x", "C1")


def test_429_sleeps_retry_after_then_retries_once(monkeypatch):
    slept = []
    monkeypatch.setattr(slack, "_sleep", slept.append)
    calls = fake_urlopen(
        monkeypatch,
        http_error(429, {"Retry-After": "3"}),
        FakeResponse({"ok": True, "ts": "9"}),
    )
    assert slack.post_message("x", "C1") == "9"
    assert slept == [3]
    assert len(calls) == 2


def test_429_twice_raises(monkeypatch):
    calls = fake_urlopen(
        monkeypatch, http_error(429, {"Retry-After": "1"}), http_error(429, {"Retry-After": "1"})
    )
    with pytest.raises(slack.SlackError, match="429"):
        slack.post_message("x", "C1")
    assert len(calls) == 2


@pytest.mark.parametrize("exc", [socket.timeout("t"), TimeoutError("t")])
def test_timeout_raises_without_retry(monkeypatch, exc):
    calls = fake_urlopen(monkeypatch, exc, FakeResponse({"ok": True, "ts": "1"}))
    with pytest.raises(slack.SlackError, match="timed out"):
        slack.post_message("x", "C1")
    assert len(calls) == 1


def test_other_http_status_raises_with_status(monkeypatch):
    fake_urlopen(monkeypatch, http_error(500))
    with pytest.raises(slack.SlackError, match="500"):
        slack.post_message("x", "C1")


# --- auth_test --------------------------------------------------------------


def test_auth_test_returns_parsed_body(monkeypatch):
    body = {"ok": True, "user": "paperboy", "team": "t"}
    calls = fake_urlopen(monkeypatch, FakeResponse(body))
    assert slack.auth_test() == body
    assert calls[0].req.full_url == "https://slack.com/api/auth.test"


def test_auth_test_ok_false_raises(monkeypatch):
    fake_urlopen(monkeypatch, FakeResponse({"ok": False, "error": "invalid_auth"}))
    with pytest.raises(slack.SlackError, match="invalid_auth"):
        slack.auth_test()


# --- build_message ----------------------------------------------------------


def cand(n: int, score: float = 0.82, abstract: str = "One. Two. Three. Four."):
    paper = SimpleNamespace(
        title=f"Paper {n}",
        authors=["A. Author"],
        url=f"https://arxiv.org/abs/2610.0000{n}",
        abstract=abstract,
        id=f"2610.0000{n}",
    )
    return SimpleNamespace(paper=paper, score=score, reasoning=f"Why paper {n}.")


def result(status="success", **over):
    top = [cand(i, 0.9 - i / 10) for i in range(1, 6)]
    base = dict(
        status=status,
        selected_paper=top[0],
        briefing=SimpleNamespace(word_count=2450),
        briefing_path=Path("/x/2026-10-24_paper-1.md"),
        error=None,
        backend="agent",
        distill_model=None,
        duration_s=187.4,
        top_candidates=top,
    )
    base.update(over)
    return SimpleNamespace(**base)


def test_success_sections_appear_in_order():
    text = slack.build_message(result())
    marks = [
        "*Paper 1*",
        "https://arxiv.org/abs/2610.00001",
        "Why paper 1.",
        "One. Two. Three…",
        "1. Paper 1 (0.80)",
        "5. Paper 5 (0.40)",
        "Briefing: 2026-10-24_paper-1.md on the home share",
        ":white_check_mark:",
        "success",
    ]
    positions = [text.index(m) for m in marks]
    assert positions == sorted(positions)


def test_success_legend_and_telemetry_lines():
    lines = slack.build_message(result()).splitlines()
    legend = next(x for x in lines if ":headphones:" in x)
    assert ":one:" in legend and ":five:" in legend
    tele = lines[-1]
    for part in ("success", "agent", "cli-default", "187", "2450"):
        assert part in tele


def test_success_telemetry_names_model_when_set():
    assert "claude-x" in slack.build_message(result(distill_model="claude-x")).splitlines()[-1]


def test_abstract_trimmed_to_three_sentences_with_ellipsis():
    text = slack.build_message(result())
    assert "Three…" in text and "Four." not in text
    assert "Three.…" not in text


def test_abstract_trimmed_to_600_characters():
    long = "word " * 400
    r = result()
    r.selected_paper.paper.abstract = long
    r.top_candidates[0] = r.selected_paper
    text = slack.build_message(r)
    block = next(x for x in text.splitlines() if x.startswith("word"))
    assert len(block) <= 600
    assert block.endswith("…")


def test_short_abstract_has_no_ellipsis():
    r = result()
    r.selected_paper.paper.abstract = "Only one sentence."
    text = slack.build_message(r)
    assert "Only one sentence." in text and "Only one sentence.…" not in text


def test_success_text_stays_under_4000_characters():
    r = result()
    r.selected_paper.paper.abstract = "x" * 20000
    r.selected_paper.reasoning = "r" * 1500
    for c in r.top_candidates:
        c.paper.title = "T" * 400
    assert len(slack.build_message(r)) < 4000


def test_partial_message():
    text = slack.build_message(
        result("partial", error="distill failed", briefing=None, briefing_path=None)
    )
    assert ":warning:" in text
    assert "Paper 1" in text and "0.80" in text
    assert "distill failed" in text
    assert "not recorded for dedup; the next run retries" in text


def test_error_message_cuts_error_to_500_characters():
    text = slack.build_message(
        result("error", error="e" * 900, selected_paper=None, briefing=None,
               briefing_path=None, top_candidates=[])
    )
    assert "e" * 500 in text and "e" * 501 not in text
    assert text.count("\n") <= 2


def test_unknown_status_raises():
    with pytest.raises(ValueError):
        slack.build_message(result("weird"))


def test_module_source_has_no_em_dash():
    assert chr(0x2014) not in Path(slack.__file__).read_text(encoding="utf-8")


def test_success_without_briefing_still_renders():
    """Keyword-only success: no briefing, no path; the post must still render (COURIER gate MA1)."""
    r = result(briefing=None, briefing_path=None, distill_model=None)
    text = slack.build_message(r)
    assert "*Paper 1*" in text
    assert "No briefing" in text
    assert "0 words" in text


def test_abstract_cut_falls_on_a_word_boundary():
    words = [f"w{i}" for i in range(400)]
    r = result()
    r.selected_paper.paper.abstract = " ".join(words)
    r.top_candidates[0] = r.selected_paper
    text = slack.build_message(r)
    block = next(x for x in text.splitlines() if x.startswith("w0 "))
    last = block.rstrip("…").split()[-1]
    assert last in words


def test_legend_names_this_message():
    text = slack.build_message(result())
    assert "Reactions on this message:" in text


def test_partial_error_is_cut_to_500_chars():
    r = result("partial", error="e" * 900, briefing=None, briefing_path=None)
    line = next(x for x in slack.build_message(r).splitlines() if x.startswith("Error:"))
    assert len(line) <= len("Error: ") + 500
