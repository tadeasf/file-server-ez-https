"""Module for detecting machine's IP addresses."""
import socket
import requests
import json
from typing import Optional

def get_local_ip() -> str:
    """Get the local IP address of the machine."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't need to be reachable
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def get_public_ip() -> Optional[str]:
    """Get the public IP address of the machine using external services."""
    services = [
        ("https://api.ipify.org", lambda r: r.text.strip()),
        ("https://api.myip.com", lambda r: json.loads(r.text)["ip"]),
        ("https://ifconfig.me/ip", lambda r: r.text.strip())
    ]
    
    for url, parser in services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return parser(response)
        except (requests.RequestException, json.JSONDecodeError, KeyError):
            continue
    
    return None

def get_ip(use_public: bool = True) -> str:
    """Get IP address based on preference.
    
    Args:
        use_public: If True, tries to get public IP first, falls back to local IP.
                   If False, returns local IP.
    """
    if use_public:
        public_ip = get_public_ip()
        if public_ip:
            return public_ip
    
    return get_local_ip()
