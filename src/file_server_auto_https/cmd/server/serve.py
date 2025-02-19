"""
Command module for starting the file server with automatic HTTPS.
"""
import os
import signal
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ...cloudflare.client import CloudflareClient
from ...cloudflare.exceptions import CloudflareError
from ...server.file_server import FileServer, find_free_port

app = typer.Typer()
console = Console()

@app.command()
def start(
    directory: Path = typer.Argument(
        Path("."),
        help="Directory to serve files from",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    port: int = typer.Option(
        8000,
        "--port",
        "-p",
        help="Port to listen on (0 for auto-selection)",
    ),
    host: str = typer.Option(
        "0.0.0.0",
        "--host",
        "-h",
        help="Host to bind to",
    ),
    no_directory_listing: bool = typer.Option(
        False,
        "--no-directory-listing",
        "-n",
        help="Disable directory listing",
    ),
    subdomain: Optional[str] = typer.Option(
        None,
        "--subdomain",
        "-s",
        help="Specific subdomain to use (default: auto-generated)",
    ),
    no_dns: bool = typer.Option(
        False,
        "--no-dns",
        help="Skip DNS record creation (for local testing)",
    ),
    no_proxy: bool = typer.Option(
        False,
        "--no-proxy",
        help="Don't proxy through Cloudflare (for local testing)",
    ),
):
    """Start a file server with automatic HTTPS."""
    # Handle Ctrl+C gracefully
    def signal_handler(signum, frame):
        console.print("\n[yellow]Shutting down server...[/]")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Auto-select port if requested
    if port == 0:
        port = find_free_port()
        console.print(f"[green]Selected port: {port}[/]")

    # Create DNS record if needed
    dns_record = None
    if not no_dns:
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                progress.add_task(description="Creating DNS record...", total=None)
                client = CloudflareClient()
                dns_record = client.create_dns_record(subdomain)
                console.print(f"[green]Created DNS record: {dns_record['name']}[/]")
        except CloudflareError as e:
            console.print(f"[red]Failed to create DNS record: {e}[/]")
            if not no_proxy:
                console.print("[yellow]Running without Cloudflare proxy...[/]")
                no_proxy = True

    # Start the server
    server = FileServer(
        directory=directory,
        port=port,
        host=host,
        enable_directory_listing=not no_directory_listing,
    )

    # Print server info
    console.print("\n[bold]Server Configuration:[/]")
    console.print(f"  Directory: {directory}")
    console.print(f"  Internal URL: http://{host}:{port}")
    if dns_record and not no_proxy:
        console.print(f"  Public URL: https://{dns_record['name']}")
    console.print("\nPress Ctrl+C to stop the server\n")

    try:
        with server:
            # Keep main thread alive
            signal.pause()
    except KeyboardInterrupt:
        pass
    finally:
        if dns_record and not no_dns:
            try:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    progress.add_task(description="Cleaning up DNS record...", total=None)
                    client.delete_dns_record(dns_record["id"])
                    console.print("[green]Cleaned up DNS record[/]")
            except CloudflareError as e:
                console.print(f"[red]Failed to clean up DNS record: {e}[/]")

if __name__ == "__main__":
    app() 