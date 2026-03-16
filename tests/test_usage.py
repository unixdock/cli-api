"""Tests for the usage tracker."""

from __future__ import annotations

from cli_api.usage.tracker import UsageTracker


def _fresh_tracker() -> UsageTracker:
    t = UsageTracker.__new__(UsageTracker)
    t._records = []
    return t


class TestUsageTracker:
    def test_record_increments_list(self):
        t = _fresh_tracker()
        t.record("openai", "chat", tokens_in=10, tokens_out=20, latency_ms=50)
        assert len(t._records) == 1

    def test_summary_aggregates(self):
        t = _fresh_tracker()
        t.record("openai", "chat", tokens_in=10, tokens_out=20, latency_ms=100)
        t.record("openai", "chat", tokens_in=5, tokens_out=10, latency_ms=200)
        t.record("ollama", "chat", tokens_in=3, tokens_out=6, latency_ms=50)

        summaries = {s.service: s for s in t.summaries()}
        assert summaries["openai"].calls == 2
        assert summaries["openai"].tokens_in == 15
        assert summaries["openai"].tokens_out == 30
        assert summaries["openai"].avg_latency_ms == 150.0
        assert summaries["ollama"].calls == 1

    def test_recent(self):
        t = _fresh_tracker()
        for i in range(5):
            t.record("svc", "chat", tokens_in=i)
        recent = t.recent(3)
        assert len(recent) == 3
        assert recent[-1].tokens_in == 4

    def test_error_counted(self):
        t = _fresh_tracker()
        t.record("svc", "chat", status="ok")
        t.record("svc", "chat", status="error")
        summaries = {s.service: s for s in t.summaries()}
        assert summaries["svc"].errors == 1

    def test_clear(self):
        t = _fresh_tracker()
        t.record("svc", "chat")
        t.clear()
        assert len(t._records) == 0
        assert t.summaries() == []

    def test_max_records_trimmed(self):
        t = _fresh_tracker()
        t._MAX_RECORDS = 5
        for i in range(10):
            t.record("svc", "chat")
        assert len(t._records) == 5
