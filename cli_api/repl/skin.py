"""REPL skin with undo/redo — interactive session for CAP services."""

from __future__ import annotations

import asyncio
from typing import Any

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from cli_api.broker.broker import get_broker
from cli_api.cap.protocol import CAPRequest
from cli_api.cap.session import HistoryEntry, Session

console = Console()


class ReplSkin:
    """Interactive REPL with persistent history and undo/redo.

    Commands accepted at the prompt (in addition to free-form text):
    - `undo`   — replay the previous interaction
    - `redo`   — redo an undone interaction
    - `history`— show the interaction history
    - `exit` / `quit` / Ctrl-D — leave the REPL
    """

    def __init__(self, service: str, session: Session, agent_role: str | None = None) -> None:
        self._service = service
        self._session = session
        self._agent_role = agent_role
        self._broker = get_broker()

    def run(self) -> None:
        """Start the synchronous REPL loop (wraps async internals)."""
        asyncio.run(self._loop())

    async def _loop(self) -> None:
        console.print(
            Panel(
                f"[bold cyan]cli-api REPL[/bold cyan]  service=[green]{self._service}[/green]  "
                f"session=[dim]{self._session.session_id[:8]}…[/dim]\n"
                "[dim]Commands: undo | redo | history | exit[/dim]",
                expand=False,
            )
        )

        while True:
            try:
                user_input = Prompt.ask("[bold]>[/bold]").strip()
            except (EOFError, KeyboardInterrupt):
                break

            if not user_input:
                continue

            if user_input.lower() in ("exit", "quit"):
                break

            if user_input.lower() == "undo":
                entry = self._session.undo()
                if entry:
                    console.print(f"[yellow]Undone:[/yellow] {entry.action} → {str(entry.result)[:80]}")
                else:
                    console.print("[dim]Nothing to undo.[/dim]")
                self._session.save()
                continue

            if user_input.lower() == "redo":
                entry = self._session.redo()
                if entry:
                    console.print(f"[green]Redone:[/green] {entry.action} → {str(entry.result)[:80]}")
                else:
                    console.print("[dim]Nothing to redo.[/dim]")
                self._session.save()
                continue

            if user_input.lower() == "history":
                self._show_history()
                continue

            response = await self._dispatch(user_input)
            if response.error:
                console.print(f"[red]Error:[/red] {response.error}")
            else:
                result_str = str(response.result or "")
                try:
                    console.print(Markdown(result_str))
                except Exception:
                    console.print(result_str)

            # Persist
            entry = HistoryEntry(
                request_id=response.request_id,
                service=self._service,
                action="chat",
                args=[user_input],
                kwargs={},
                result=response.result,
                timestamp=response.timestamp,
            )
            self._session.push(entry)
            self._session.save()

        console.print("[dim]Session saved. Goodbye.[/dim]")

    async def _dispatch(self, user_input: str) -> Any:
        request = CAPRequest(
            service=self._service,
            action="chat",
            args=[user_input],
            session_id=self._session.session_id,
            agent_role=self._agent_role,
        )
        return await self._broker.dispatch(request)

    def _show_history(self) -> None:
        if not self._session.history:
            console.print("[dim]No history yet.[/dim]")
            return
        for i, entry in enumerate(self._session.history):
            marker = "→" if i == self._session._cursor else " "
            console.print(
                f" {marker} [{i}] [dim]{entry.service}[/dim] "
                f"{entry.args[0][:60] if entry.args else ''}…"
            )
