"""
Command-line interface for the file server with automatic HTTPS.
"""
import typer
from .cmd.cloudflare.generate_dns_record import app as dns_app

app = typer.Typer()
app.add_typer(dns_app, name="dns", help="Manage DNS records")

def main():
    """Entry point for the CLI."""
    app()

if __name__ == "__main__":
    main() 