"""Monitoring dashboard — live event stream for active agent pipelines."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from rich.console import Console
from rich.live import Live
from rich.table import Table

from cli_api.broker.broker import get_broker

console = Console()


async def stream_monitor(duration_s: int = 60) -> None:
    """Print live monitoring events from the broker health checks."""
    broker = get_broker()
    end = asyncio.get_event_loop().time() + duration_s

    with Live(console=console, refresh_per_second=1) as live:
        while asyncio.get_event_loop().time() < end:
            health = await broker.health_check_all()
            table = Table(title="cli-api Monitor", show_lines=True)
            table.add_column("Service", style="cyan")
            table.add_column("Status", style="bold")
            table.add_column("Health")
            for service, ok in health.items():
                status_str = "[green]●[/green] online" if ok else "[red]●[/red] offline"
                table.add_row(service, status_str, "✓" if ok else "✗")
            live.update(table)
            await asyncio.sleep(2)


def print_monitor_event(event: dict[str, Any]) -> None:
    """Pretty-print a single monitoring event emitted during chain execution."""
    etype = event.get("event", "")
    chain_id_short = str(event.get("chain_id", ""))[:8]
    step = event.get("step")
    total = event.get("total")
    service = event.get("service", "")

    if etype == "chain_step_start":
        console.print(
            f"[dim]{chain_id_short}…[/dim] [bold cyan]Step {step}/{total}[/bold cyan] "
            f"→ [green]{service}[/green] starting…"
        )
    elif etype == "chain_step_done":
        status = event.get("status", "ok")
        colour = "green" if status == "ok" else "red"
        console.print(
            f"[dim]{chain_id_short}…[/dim] Step {step}/{total} → [{colour}]{service} {status}[/{colour}]"
        )
    else:
        console.print(json.dumps(event))
