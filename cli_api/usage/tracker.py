"""Usage tracker — per-service token and latency accounting."""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

_USAGE_PATH = Path.home() / ".cli-api" / "usage.json"


@dataclass
class UsageRecord:
    """One usage entry."""

    service: str
    action: str
    tokens_in: int = 0
    tokens_out: int = 0
    latency_ms: int = 0
    status: str = "ok"
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ServiceSummary:
    """Aggregated stats for a single service."""

    service: str
    calls: int = 0
    tokens_in: int = 0
    tokens_out: int = 0
    errors: int = 0
    avg_latency_ms: float = 0.0
    total_latency_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class UsageTracker:
    """Records and summarises token/credit usage across services."""

    _MAX_RECORDS = 10_000

    def __init__(self) -> None:
        self._records: list[UsageRecord] = []
        self._load()

    def record(
        self,
        service: str,
        action: str,
        tokens_in: int = 0,
        tokens_out: int = 0,
        latency_ms: int = 0,
        status: str = "ok",
    ) -> None:
        rec = UsageRecord(
            service=service,
            action=action,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            latency_ms=latency_ms,
            status=status,
        )
        self._records.append(rec)
        if len(self._records) > self._MAX_RECORDS:
            self._records = self._records[-self._MAX_RECORDS :]
        self._save()

    def summaries(self) -> list[ServiceSummary]:
        by_service: dict[str, ServiceSummary] = {}
        for rec in self._records:
            s = by_service.setdefault(rec.service, ServiceSummary(service=rec.service))
            s.calls += 1
            s.tokens_in += rec.tokens_in
            s.tokens_out += rec.tokens_out
            s.total_latency_ms += rec.latency_ms
            if rec.status != "ok":
                s.errors += 1
        for s in by_service.values():
            if s.calls:
                s.avg_latency_ms = round(s.total_latency_ms / s.calls, 1)
        return sorted(by_service.values(), key=lambda x: x.calls, reverse=True)

    def recent(self, n: int = 20) -> list[UsageRecord]:
        return self._records[-n:]

    def clear(self) -> None:
        self._records = []
        self._save()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load(self) -> None:
        if not _USAGE_PATH.exists():
            return
        try:
            raw = json.loads(_USAGE_PATH.read_text())
            self._records = [UsageRecord(**r) for r in raw]
        except Exception:
            self._records = []

    def _save(self) -> None:
        _USAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
        _USAGE_PATH.write_text(
            json.dumps([r.to_dict() for r in self._records], ensure_ascii=False, indent=2)
        )


_tracker: UsageTracker | None = None


def get_tracker() -> UsageTracker:
    global _tracker
    if _tracker is None:
        _tracker = UsageTracker()
    return _tracker
