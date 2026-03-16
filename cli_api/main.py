"""cli-api — CLI-First Universal Protocol (CAP) entry point.

Usage:
    cli-api <service> <action> [args…]   [--json] [--session ID]
                                          [--agent-role ROLE] [--monitor]
    cli-api chain "svc1 -> svc2 -> svc3" "initial prompt"
    cli-api list
    cli-api register <name> [--adapter TYPE] [--url URL] [--model M]
    cli-api usage
    cli-api repl <service>
    cli-api bridge <protocol> <payload-json>
    cli-api monitor
"""

from __future__ import annotations

import asyncio
import json
from typing import Annotated

import typer
from rich.console import Console
from rich.json import JSON
from rich.panel import Panel
from rich.table import Table

from cli_api import __version__
from cli_api.cap.schema import build_capability_manifest
from cli_api.cap.session import Session

app = typer.Typer(
    name="cli-api",
    help="CLI-First Universal Protocol (CAP) — one command to unify AI agents.",
    add_completion=False,
    no_args_is_help=False,
)
console = Console()
err_console = Console(stderr=True)


# ---------------------------------------------------------------------------
# Version / global help
# ---------------------------------------------------------------------------


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"cli-api {__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Annotated[
        bool,
        typer.Option("--version", "-V", callback=_version_callback, is_eager=True),
    ] = False,
    json_output: Annotated[bool, typer.Option("--json", help="Output JSON")] = False,
) -> None:
    """cli-api: CLI-First Universal Protocol (CAP).

    Run 'cli-api --help' for the full capability manifest (JSON Schema).
    """
    if ctx.invoked_subcommand is None:
        # Print CAP capability manifest
        manifest = build_capability_manifest()
        if json_output:
            typer.echo(json.dumps(manifest, ensure_ascii=False, indent=2))
        else:
            console.print(Panel(JSON(json.dumps(manifest, ensure_ascii=False, indent=2)),
                                title="[bold cyan]cli-api Capability Manifest (CAP v1.0)[/bold cyan]",
                                expand=False))


# ---------------------------------------------------------------------------
# cli-api call <service> <action> [args…]
# ---------------------------------------------------------------------------


@app.command("call")
def call_service(
    service: Annotated[str, typer.Argument(help="Target service name (e.g. openai, ollama)")],
    action: Annotated[str, typer.Argument(help="Action to invoke (e.g. chat, complete)")],
    args: Annotated[list[str] | None, typer.Argument(help="Positional arguments")] = None,
    json_output: Annotated[bool, typer.Option("--json")] = False,
    session_id: Annotated[str | None, typer.Option("--session")] = None,
    agent_role: Annotated[str | None, typer.Option("--agent-role")] = None,
    monitor: Annotated[bool, typer.Option("--monitor")] = False,
    local: Annotated[bool, typer.Option("--local", help="Prefer local (Ollama/LM Studio)")] = False,
) -> None:
    """Invoke <action> on <service> with optional positional args."""
    from cli_api.broker.broker import RoutingHint, get_broker
    from cli_api.cap.protocol import CAPRequest

    request = CAPRequest(
        service=service,
        action=action,
        args=args or [],
        session_id=session_id,
        agent_role=agent_role,
    )

    hint = RoutingHint(prefer_local=local)

    async def _run() -> None:
        broker = get_broker()
        if monitor:
            console.print(f"[dim]Dispatching to[/dim] [green]{service}[/green][dim]…[/dim]")

        response = await broker.dispatch(request, hint)

        if json_output:
            typer.echo(response.to_json())
        else:
            if response.error:
                err_console.print(f"[red]Error:[/red] {response.error}")
                raise typer.Exit(1)
            result = response.result
            if isinstance(result, (dict, list)):
                console.print(JSON(json.dumps(result, ensure_ascii=False, indent=2)))
            else:
                console.print(str(result))
            if monitor:
                console.print(
                    f"[dim]latency={response.metadata.get('latency_ms')}ms  "
                    f"model={response.metadata.get('model', 'n/a')}[/dim]"
                )

        # Persist session
        if session_id or request.session_id:
            session = Session.get_or_create(request.session_id)
            from cli_api.cap.session import HistoryEntry
            session.push(HistoryEntry(
                request_id=response.request_id,
                service=service,
                action=action,
                args=args or [],
                kwargs={},
                result=response.result,
                timestamp=response.timestamp,
            ))
            session.save()

    asyncio.run(_run())


# ---------------------------------------------------------------------------
# cli-api chain "svc1 -> svc2 -> svc3" "<prompt>"
# ---------------------------------------------------------------------------


@app.command("chain")
def chain_command(
    pipeline: Annotated[str, typer.Argument(help="Pipeline spec: 'svc1 -> svc2 -> svc3'")],
    prompt: Annotated[str, typer.Argument(help="Initial input passed to the first service")],
    action: Annotated[str, typer.Option("--action")] = "chat",
    session_id: Annotated[str | None, typer.Option("--session")] = None,
    agent_roles: Annotated[str | None, typer.Option(
        "--agent-roles", help="Comma-separated roles matching pipeline stages"
    )] = None,
    monitor: Annotated[bool, typer.Option("--monitor")] = False,
    json_output: Annotated[bool, typer.Option("--json")] = False,
) -> None:
    """Run a multi-step agent pipeline.

    Example:
        cli-api chain "grok-researcher -> claude-writer -> grok-reviewer" "Write about AI agents"
    """
    from cli_api.chain.executor import ChainExecutor, parse_pipeline
    from cli_api.monitor.dashboard import print_monitor_event

    steps = parse_pipeline(pipeline)
    if not steps:
        err_console.print("[red]Error:[/red] Empty pipeline spec.")
        raise typer.Exit(1)

    roles = [r.strip() for r in agent_roles.split(",")] if agent_roles else None

    async def _run() -> None:
        executor = ChainExecutor()

        async def _on_event(ev: dict) -> None:
            if monitor:
                print_monitor_event(ev)

        result = await executor.execute(
            pipeline=steps,
            initial_input=prompt,
            action=action,
            session_id=session_id,
            agent_roles=roles,
            monitor_callback=_on_event,
        )

        if json_output:
            out = {
                "chain_id": result.chain_id,
                "pipeline": result.pipeline,
                "success": result.success,
                "final_result": result.final_result,
                "error": result.error,
                "steps": [s.to_dict() for s in result.steps],
            }
            typer.echo(json.dumps(out, ensure_ascii=False, indent=2))
        else:
            if result.success:
                console.print(
                    Panel(
                        str(result.final_result),
                        title=f"[bold green]Chain complete[/bold green] "
                              f"([dim]{' → '.join(steps)}[/dim])",
                        expand=False,
                    )
                )
            else:
                err_console.print(f"[red]Chain failed:[/red] {result.error}")
                raise typer.Exit(1)

    asyncio.run(_run())


# ---------------------------------------------------------------------------
# cli-api list
# ---------------------------------------------------------------------------


@app.command("list")
def list_services(
    json_output: Annotated[bool, typer.Option("--json")] = False,
) -> None:
    """List all registered agent services."""
    from cli_api.adapters.registry import get_registry

    registry = get_registry()
    entries = registry.list_services()

    if json_output:
        typer.echo(json.dumps([e.to_dict() for e in entries], ensure_ascii=False, indent=2))
        return

    table = Table(title="Registered Services", show_lines=True)
    table.add_column("Name", style="cyan")
    table.add_column("Adapter")
    table.add_column("Local")
    table.add_column("Description")
    for e in entries:
        table.add_row(
            e.name,
            e.adapter_type,
            "✓" if e.local_only else "—",
            e.description[:60],
        )
    console.print(table)


# ---------------------------------------------------------------------------
# cli-api register <name>
# ---------------------------------------------------------------------------


@app.command("register")
def register_service(
    name: Annotated[str, typer.Argument(help="Service name to register")],
    adapter_type: Annotated[str, typer.Option("--adapter")] = "openai",
    url: Annotated[str | None, typer.Option("--url")] = None,
    model: Annotated[str | None, typer.Option("--model")] = None,
    api_key_env: Annotated[str | None, typer.Option("--api-key-env")] = None,
    description: Annotated[str, typer.Option("--description")] = "",
    local: Annotated[bool, typer.Option("--local")] = False,
    json_output: Annotated[bool, typer.Option("--json")] = False,
) -> None:
    """Register a new agent service in the local registry.

    Example:
        cli-api register my-gpt --adapter openai --model gpt-4o
    """
    from cli_api.adapters.registry import ServiceEntry, get_registry

    entry = ServiceEntry(
        name=name,
        adapter_type=adapter_type,
        description=description or f"{adapter_type} service",
        base_url=url,
        model=model,
        api_key_env=api_key_env,
        local_only=local,
    )
    get_registry().register(entry)

    if json_output:
        typer.echo(json.dumps(entry.to_dict(), ensure_ascii=False, indent=2))
    else:
        console.print(f"[green]✓[/green] Registered service [cyan]{name}[/cyan] "
                      f"([dim]{adapter_type}[/dim])")


# ---------------------------------------------------------------------------
# cli-api usage
# ---------------------------------------------------------------------------


@app.command("usage")
def usage(
    json_output: Annotated[bool, typer.Option("--json")] = False,
    recent: Annotated[int, typer.Option("--recent", help="Show N recent calls")] = 0,
) -> None:
    """Display real-time cross-service token/credit consumption."""
    from cli_api.usage.tracker import get_tracker

    tracker = get_tracker()

    if recent:
        records = tracker.recent(recent)
        if json_output:
            typer.echo(json.dumps([r.to_dict() for r in records], ensure_ascii=False, indent=2))
        else:
            table = Table(title=f"Recent {recent} Calls", show_lines=True)
            table.add_column("Service", style="cyan")
            table.add_column("Action")
            table.add_column("In", justify="right")
            table.add_column("Out", justify="right")
            table.add_column("Latency")
            table.add_column("Status")
            for r in records:
                table.add_row(
                    r.service, r.action,
                    str(r.tokens_in), str(r.tokens_out),
                    f"{r.latency_ms}ms",
                    r.status,
                )
            console.print(table)
        return

    summaries = tracker.summaries()

    if json_output:
        typer.echo(json.dumps([s.to_dict() for s in summaries], ensure_ascii=False, indent=2))
        return

    table = Table(title="Usage Summary", show_lines=True)
    table.add_column("Service", style="cyan")
    table.add_column("Calls", justify="right")
    table.add_column("Tokens In", justify="right")
    table.add_column("Tokens Out", justify="right")
    table.add_column("Avg Latency")
    table.add_column("Errors", justify="right")
    for s in summaries:
        table.add_row(
            s.service,
            str(s.calls),
            str(s.tokens_in),
            str(s.tokens_out),
            f"{s.avg_latency_ms}ms",
            str(s.errors),
        )
    if not summaries:
        console.print("[dim]No usage data yet. Run some commands first.[/dim]")
    else:
        console.print(table)


# ---------------------------------------------------------------------------
# cli-api repl <service>
# ---------------------------------------------------------------------------


@app.command("repl")
def repl(
    service: Annotated[str, typer.Argument(help="Service to interact with")] = "openai",
    session_id: Annotated[str | None, typer.Option("--session")] = None,
    agent_role: Annotated[str | None, typer.Option("--agent-role")] = None,
) -> None:
    """Launch an interactive REPL with undo/redo for the given service."""
    from cli_api.repl.skin import ReplSkin

    session = Session.get_or_create(session_id)
    skin = ReplSkin(service=service, session=session, agent_role=agent_role)
    skin.run()


# ---------------------------------------------------------------------------
# cli-api monitor
# ---------------------------------------------------------------------------


@app.command("monitor")
def monitor_cmd(
    duration: Annotated[int, typer.Option("--duration", "-d")] = 30,
) -> None:
    """Stream live health monitoring for all registered services."""
    from cli_api.monitor.dashboard import stream_monitor

    console.print(f"[bold]Monitoring for {duration}s…[/bold]  (Ctrl-C to stop)")
    try:
        asyncio.run(stream_monitor(duration))
    except KeyboardInterrupt:
        pass


# ---------------------------------------------------------------------------
# cli-api bridge <protocol> <payload>
# ---------------------------------------------------------------------------


@app.command("bridge")
def bridge(
    protocol: Annotated[str, typer.Argument(help="Source protocol: mcp | a2a | acp")],
    payload: Annotated[str, typer.Argument(help="JSON payload from the source protocol")],
    service: Annotated[str | None, typer.Option("--service")] = None,
    json_output: Annotated[bool, typer.Option("--json")] = False,
    execute: Annotated[bool, typer.Option("--execute", help="Also dispatch the translated request")] = False,
) -> None:
    """Translate a foreign protocol payload (MCP/A2A/ACP) into a CAP request."""
    from cli_api.bridge.translators import translate_to_cap

    try:
        request = translate_to_cap(protocol, payload, service)
    except ValueError as exc:
        err_console.print(f"[red]Bridge error:[/red] {exc}")
        raise typer.Exit(1)

    if json_output or not execute:
        typer.echo(request.to_json())

    if execute:
        from cli_api.broker.broker import get_broker

        async def _run() -> None:
            broker = get_broker()
            response = await broker.dispatch(request)
            if json_output:
                typer.echo(response.to_json())
            else:
                console.print(str(response.result or response.error or ""))

        asyncio.run(_run())


# ---------------------------------------------------------------------------
# cli-api sessions
# ---------------------------------------------------------------------------


@app.command("sessions")
def sessions(
    json_output: Annotated[bool, typer.Option("--json")] = False,
) -> None:
    """List all saved sessions."""
    all_sessions = Session.list_sessions()
    if json_output:
        typer.echo(json.dumps(all_sessions, ensure_ascii=False, indent=2))
        return

    if not all_sessions:
        console.print("[dim]No sessions found.[/dim]")
        return

    table = Table(title="Saved Sessions", show_lines=True)
    table.add_column("Session ID", style="cyan")
    table.add_column("History", justify="right")
    for s in all_sessions:
        table.add_row(s["session_id"], str(s["history_len"]))
    console.print(table)


if __name__ == "__main__":
    app()
