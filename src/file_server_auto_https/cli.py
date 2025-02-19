"""
Command-line interface for the file server with automatic HTTPS.
"""
import typer
from .cmd.cloudflare.generate_dns_record import app as dns_app
from .cmd.server.serve import app as server_app

app = typer.Typer()
app.add_typer(dns_app, name="dns", help="Manage DNS records")
app.add_typer(server_app, name="serve", help="Start file server with HTTPS")

def main():
    """Entry point for the CLI."""
    app()

if __name__ == "__main__":
    main() 