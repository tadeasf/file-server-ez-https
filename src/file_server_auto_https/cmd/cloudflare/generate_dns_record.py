"""Command for generating DNS records."""
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

from ...lib.cloudflare.cloudflare_handler import (
    CloudflareClient,
    DNSRecord,
    DNSRecordSettings,
    CloudflareError,
    generate_subdomain
)
from ...lib.grab_ip import get_ip

app = typer.Typer()
console = Console()

def format_error(error: CloudflareError) -> str:
    """Format CloudflareError for display."""
    message = str(error)
    if error.errors:
        message += "\nDetails:"
        for err in error.errors:
            if isinstance(err, dict):
                message += f"\n- Code {err.get('code', 'N/A')}: {err.get('message', 'Unknown error')}"
            else:
                message += f"\n- {err}"
    return message

@app.command()
def create(
    ip: Optional[str] = typer.Option(None, help="IP address to use. If not provided, will auto-detect."),
    use_public_ip: bool = typer.Option(True, help="Use public IP instead of local IP when auto-detecting."),
    subdomain: Optional[str] = typer.Option(None, help="Specific subdomain to use. If not provided, will generate random."),
    length: int = typer.Option(8, help="Length of random subdomain if generated."),
    proxied: bool = typer.Option(True, help="Whether to proxy through Cloudflare."),
    ttl: int = typer.Option(1, help="TTL in seconds. Use 1 for automatic.")
) -> None:
    """Create a new DNS record for the file server."""
    try:
        # Get IP address
        ip_address = ip or get_ip(use_public=use_public_ip)
        console.print(Panel(f"Using IP address: {ip_address}", title="Setup"))
        
        # Get or generate subdomain
        sub = subdomain or generate_subdomain(length)
        
        # Initialize client
        client = CloudflareClient()
        
        # Create record
        record = DNSRecord(
            name=f"{sub}.{client.config.base_domain}",
            content=ip_address,
            proxied=proxied,
            ttl=ttl,
            comment="Auto-generated subdomain for file server",
            settings=DNSRecordSettings(ipv4_only=False, ipv6_only=False)
        )
        
        # Show the record we're about to create
        console.print("\nCreating DNS record:")
        console.print(Syntax(record.model_dump_json(indent=2), "json"))
        
        result = client.create_dns_record(record)
        
        if result.get("success"):
            console.print(Panel(
                f"[green]Successfully created DNS record![/green]\n\n"
                f"Domain: [bold]{record.name}[/bold]\n"
                f"IP: [bold]{ip_address}[/bold]\n"
                f"Proxied: [bold]{'Yes' if proxied else 'No'}[/bold]\n"
                f"TTL: [bold]{'Auto' if ttl == 1 else ttl}[/bold]\n"
                f"Record ID: [bold]{result['result']['id']}[/bold]",
                title="Success"
            ))
        else:
            raise CloudflareError("Failed to create DNS record", result.get("errors"))
            
    except CloudflareError as e:
        console.print(Panel(f"[red]Cloudflare Error:[/red]\n{format_error(e)}", title="Error"))
        raise typer.Exit(1)
    except Exception as e:
        console.print(Panel(f"[red]Error:[/red] {str(e)}", title="Error"))
        raise typer.Exit(1)

@app.command()
def list_records(
    show_all: bool = typer.Option(False, help="Show all records, not just those created by this tool")
) -> None:
    """List DNS records in the zone."""
    try:
        client = CloudflareClient()
        records = client.list_dns_records()
        
        table = Table(title=f"DNS Records for {client.config.base_domain}")
        table.add_column("ID", style="dim")
        table.add_column("Name", style="bold")
        table.add_column("Type")
        table.add_column("Content")
        table.add_column("Proxied", justify="center")
        table.add_column("TTL", justify="right")
        table.add_column("Comment", style="dim")
        
        for record in records:
            if show_all or (record.get("comment", "").startswith("Auto-generated subdomain")):
                table.add_row(
                    record["id"],
                    record["name"],
                    record["type"],
                    record["content"],
                    "✓" if record["proxied"] else "✗",
                    "Auto" if record["ttl"] == 1 else str(record["ttl"]),
                    record.get("comment", "")
                )
        
        console.print(table)
        
    except CloudflareError as e:
        console.print(Panel(f"[red]Cloudflare Error:[/red]\n{format_error(e)}", title="Error"))
        raise typer.Exit(1)
    except Exception as e:
        console.print(Panel(f"[red]Error:[/red] {str(e)}", title="Error"))
        raise typer.Exit(1)

@app.command()
def delete(
    record_id: str = typer.Argument(..., help="ID of the DNS record to delete")
) -> None:
    """Delete a DNS record by ID."""
    try:
        client = CloudflareClient()
        result = client.delete_dns_record(record_id)
        
        if result.get("success"):
            console.print(Panel(
                f"[green]Successfully deleted DNS record![/green]\n"
                f"Record ID: [bold]{record_id}[/bold]",
                title="Success"
            ))
        else:
            raise CloudflareError("Failed to delete DNS record", result.get("errors"))
            
    except CloudflareError as e:
        console.print(Panel(f"[red]Cloudflare Error:[/red]\n{format_error(e)}", title="Error"))
        raise typer.Exit(1)
    except Exception as e:
        console.print(Panel(f"[red]Error:[/red] {str(e)}", title="Error"))
        raise typer.Exit(1)

if __name__ == "__main__":
    app()
