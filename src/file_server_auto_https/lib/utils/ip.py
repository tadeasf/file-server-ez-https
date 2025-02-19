"""IP address utilities."""
import socket
import requests
from typing import Optional

def get_local_ip() -> str:
    """Get the local IP address."""
    # ... (existing implementation)

def get_public_ip() -> Optional[str]:
    """Get the public IP address."""
    # ... (existing implementation)

def find_free_port(start_port: int = 8000, max_tries: int = 100) -> Optional[int]:
    """Find a free port."""
    # ... (moved from file_server.py) 