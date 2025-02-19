"""
File server with automatic HTTPS and Cloudflare DNS management.
"""
from .lib.cloudflare.cloudflare_handler import CloudflareClient, CloudflareConfig, DNSRecord, CloudflareError
from .lib.server.file_server import FileServer
from .lib.utils.ip import find_free_port, get_public_ip, get_local_ip

__all__ = [
    'CloudflareClient',
    'CloudflareConfig',
    'DNSRecord',
    'CloudflareError',
    'FileServer',
    'find_free_port',
    'get_public_ip',
    'get_local_ip'
]
