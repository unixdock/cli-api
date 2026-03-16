"""CAP Session — stateful conversation tracking with undo/redo history."""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_SESSIONS_DIR = Path.home() / ".cli-api" / "sessions"


@dataclass
class HistoryEntry:
    """One reversible command in the session history."""

    request_id: str
    service: str
    action: str
    args: list[str]
    kwargs: dict[str, Any]
    result: Any
    timestamp: float


@dataclass
class Session:
    """Persistent, stateful CAP session."""

    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    history: list[HistoryEntry] = field(default_factory=list)
    # pointer for undo/redo — index of the *last applied* entry (−1 = nothing)
    _cursor: int = field(default=-1, repr=False)
    metadata: dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # History helpers
    # ------------------------------------------------------------------

    def push(self, entry: HistoryEntry) -> None:
        """Append *entry* and advance cursor (discards any redo tail)."""
        # Drop any entries after current cursor (they were undone)
        self.history = self.history[: self._cursor + 1]
        self.history.append(entry)
        self._cursor = len(self.history) - 1
        self.updated_at = time.time()

    def can_undo(self) -> bool:
        return self._cursor >= 0

    def can_redo(self) -> bool:
        return self._cursor < len(self.history) - 1

    def undo(self) -> HistoryEntry | None:
        if not self.can_undo():
            return None
        entry = self.history[self._cursor]
        self._cursor -= 1
        self.updated_at = time.time()
        return entry

    def redo(self) -> HistoryEntry | None:
        if not self.can_redo():
            return None
        self._cursor += 1
        entry = self.history[self._cursor]
        self.updated_at = time.time()
        return entry

    def current_entry(self) -> HistoryEntry | None:
        if self._cursor < 0 or not self.history:
            return None
        return self.history[self._cursor]

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _path(self) -> Path:
        return _SESSIONS_DIR / f"{self.session_id}.json"

    def save(self) -> None:
        _SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
        data = {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "cursor": self._cursor,
            "metadata": self.metadata,
            "history": [
                {
                    "request_id": e.request_id,
                    "service": e.service,
                    "action": e.action,
                    "args": e.args,
                    "kwargs": e.kwargs,
                    "result": e.result,
                    "timestamp": e.timestamp,
                }
                for e in self.history
            ],
        }
        self._path().write_text(json.dumps(data, ensure_ascii=False, indent=2))

    @classmethod
    def load(cls, session_id: str) -> Session:
        path = _SESSIONS_DIR / f"{session_id}.json"
        if not path.exists():
            raise FileNotFoundError(f"Session '{session_id}' not found.")
        data = json.loads(path.read_text())
        session = cls(
            session_id=data["session_id"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            metadata=data.get("metadata", {}),
        )
        session.history = [
            HistoryEntry(**e) for e in data.get("history", [])
        ]
        session._cursor = data.get("cursor", len(session.history) - 1)
        return session

    @classmethod
    def get_or_create(cls, session_id: str | None) -> Session:
        if session_id:
            try:
                return cls.load(session_id)
            except FileNotFoundError:
                pass
        return cls(session_id=session_id or str(uuid.uuid4()))

    @classmethod
    def list_sessions(cls) -> list[dict[str, Any]]:
        if not _SESSIONS_DIR.exists():
            return []
        sessions = []
        for path in sorted(_SESSIONS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
            try:
                data = json.loads(path.read_text())
                sessions.append(
                    {
                        "session_id": data["session_id"],
                        "created_at": data["created_at"],
                        "updated_at": data["updated_at"],
                        "history_len": len(data.get("history", [])),
                    }
                )
            except Exception:
                continue
        return sessions
