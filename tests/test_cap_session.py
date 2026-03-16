"""Tests for the CAP session (state + undo/redo)."""

from __future__ import annotations

import time

from cli_api.cap.session import HistoryEntry, Session


def _make_entry(service: str = "openai", action: str = "chat", result: str = "ok") -> HistoryEntry:
    return HistoryEntry(
        request_id="req-1",
        service=service,
        action=action,
        args=["hello"],
        kwargs={},
        result=result,
        timestamp=time.time(),
    )


class TestSession:
    def test_push_increments_cursor(self):
        s = Session()
        assert s._cursor == -1
        s.push(_make_entry(result="r1"))
        assert s._cursor == 0
        s.push(_make_entry(result="r2"))
        assert s._cursor == 1

    def test_undo(self):
        s = Session()
        e1 = _make_entry(result="r1")
        e2 = _make_entry(result="r2")
        s.push(e1)
        s.push(e2)

        undone = s.undo()
        assert undone is e2
        assert s._cursor == 0

    def test_undo_at_start_returns_none(self):
        s = Session()
        assert s.undo() is None

    def test_redo_after_undo(self):
        s = Session()
        e1 = _make_entry(result="r1")
        e2 = _make_entry(result="r2")
        s.push(e1)
        s.push(e2)
        s.undo()

        redone = s.redo()
        assert redone is e2
        assert s._cursor == 1

    def test_redo_without_undo_returns_none(self):
        s = Session()
        s.push(_make_entry())
        assert s.redo() is None

    def test_push_after_undo_discards_redo_tail(self):
        s = Session()
        s.push(_make_entry(result="r1"))
        s.push(_make_entry(result="r2"))
        s.undo()
        s.push(_make_entry(result="r3"))

        assert len(s.history) == 2
        assert s.history[-1].result == "r3"
        assert not s.can_redo()

    def test_can_undo_can_redo(self):
        s = Session()
        assert not s.can_undo()
        assert not s.can_redo()
        s.push(_make_entry())
        assert s.can_undo()
        assert not s.can_redo()

    def test_current_entry(self):
        s = Session()
        e = _make_entry(result="latest")
        s.push(e)
        assert s.current_entry() is e

    def test_get_or_create_new(self):
        s = Session.get_or_create(None)
        assert s.session_id

    def test_save_and_load(self, tmp_path, monkeypatch):
        import cli_api.cap.session as sess_mod

        monkeypatch.setattr(sess_mod, "_SESSIONS_DIR", tmp_path)
        s = Session()
        s.push(_make_entry(result="saved"))
        s.save()

        loaded = Session.load(s.session_id)
        assert loaded.session_id == s.session_id
        assert len(loaded.history) == 1
        assert loaded.history[0].result == "saved"
        assert loaded._cursor == 0
