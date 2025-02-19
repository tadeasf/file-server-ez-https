"""Simple HTTP file server module."""
import os
import socket
import threading
from pathlib import Path
from typing import Optional, Union
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from functools import partial
import mimetypes
from rich.console import Console
from ..utils.config import server as server_config

console = Console()

class EnhancedHTTPRequestHandler(SimpleHTTPRequestHandler):
    """Enhanced request handler with better MIME type support and logging."""
    
    def __init__(self, *args, directory: Optional[str] = None, **kwargs):
        """Initialize the handler with optional root directory."""
        # Ensure proper MIME type detection
        if not mimetypes.inited:
            mimetypes.init()
        # Add common video formats
        mimetypes.add_type('video/mp4', '.mp4')
        mimetypes.add_type('video/webm', '.webm')
        mimetypes.add_type('video/ogg', '.ogv')
        
        super().__init__(*args, directory=directory, **kwargs)
    
    def log_message(self, format: str, *args) -> None:
        """Override logging to use rich console."""
        console.print(f"[dim]{self.address_string()}[/dim] - {format%args}")
    
    def end_headers(self) -> None:
        """Add CORS headers to support access from subdomains."""
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

class FileServer:
    """HTTP file server that can be started and stopped."""
    
    def __init__(
        self,
        directory: Union[str, Path],
        host: str = server_config.default_host,
        port: int = server_config.default_port,
        directory_listing: bool = server_config.directory_listing
    ):
        """Initialize the file server."""
        self.directory = str(Path(directory).resolve())
        self.host = host
        self.port = port
        self.directory_listing = directory_listing
        self._server: Optional[ThreadingHTTPServer] = None
        self._server_thread: Optional[threading.Thread] = None
    
    def _create_handler(self) -> type[SimpleHTTPRequestHandler]:
        """Create a request handler class with our configuration."""
        if not self.directory_listing:
            # Create a subclass that disables directory listing
            class NoListingHTTPRequestHandler(EnhancedHTTPRequestHandler):
                def list_directory(self, path: str) -> None:
                    self.send_error(403, "Directory listing forbidden")
            return partial(NoListingHTTPRequestHandler, directory=self.directory)
        
        return partial(EnhancedHTTPRequestHandler, directory=self.directory)
    
    def start(self) -> None:
        """Start the file server in a background thread."""
        if self._server:
            raise RuntimeError("Server is already running")
        
        # Create and configure the server
        handler = self._create_handler()
        self._server = ThreadingHTTPServer((self.host, self.port), handler)
        
        # Start the server in a background thread
        self._server_thread = threading.Thread(
            target=self._server.serve_forever,
            daemon=True
        )
        self._server_thread.start()
        
        # Get the actual port (in case we used port 0)
        actual_port = self._server.server_port
        
        console.print(
            f"[green]Server started![/green]\n"
            f"Serving directory: [bold]{self.directory}[/bold]\n"
            f"URL: [bold]http://{self.host}:{actual_port}/[/bold]"
        )
    
    def stop(self) -> None:
        """Stop the file server."""
        if self._server:
            self._server.shutdown()
            self._server.server_close()
            self._server = None
            self._server_thread = None
            console.print("[yellow]Server stopped[/yellow]")
    
    @property
    def is_running(self) -> bool:
        """Check if the server is running."""
        return bool(self._server and self._server_thread and self._server_thread.is_alive())
    
    def __enter__(self) -> 'FileServer':
        """Start the server when entering a context."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Stop the server when exiting a context."""
        self.stop()

def find_free_port(start_port: int = 8000, max_tries: int = 100) -> Optional[int]:
    """Find a free port starting from start_port.
    
    Args:
        start_port: Port to start searching from
        max_tries: Maximum number of ports to try
    
    Returns:
        A free port number or None if no free port was found
    """
    for port in range(start_port, start_port + max_tries):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    return None 