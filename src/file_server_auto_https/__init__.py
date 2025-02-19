"""
File server with automatic HTTPS and Cloudflare DNS management.
"""
import os
from typing import Optional, Dict, List
import shortuuid
import requests
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class CloudflareConfig(BaseModel):
    """Cloudflare API configuration."""
    email: str = Field(..., description="Cloudflare account email")
    api_key: str = Field(..., description="Cloudflare API key")
    zone_id: str = Field(..., description="Zone ID for the domain")
    base_domain: str = Field(..., description="Base domain for subdomains")

class DNSRecord(BaseModel):
    """DNS record model."""
    name: str
    type: str = "A"
    content: str
    proxied: bool = True
    ttl: int = 1  # Auto TTL
    comment: Optional[str] = None

class CloudflareClient:
    """Client for interacting with Cloudflare API."""
    
    def __init__(self, config: CloudflareConfig):
        self.config = config
        self.base_url = "https://api.cloudflare.com/client/v4"
        self.headers = {
            "X-Auth-Email": config.email,
            "X-Auth-Key": config.api_key,
            "Content-Type": "application/json"
        }

    def create_dns_record(self, record: DNSRecord) -> Dict:
        """Create a new DNS record."""
        url = f"{self.base_url}/zones/{self.config.zone_id}/dns_records"
        response = requests.post(url, headers=self.headers, json=record.model_dump(exclude_none=True))
        response.raise_for_status()
        return response.json()

    def list_dns_records(self, params: Optional[Dict] = None) -> List[Dict]:
        """List DNS records for the zone."""
        url = f"{self.base_url}/zones/{self.config.zone_id}/dns_records"
        response = requests.get(url, headers=self.headers, params=params or {})
        response.raise_for_status()
        return response.json()["result"]

def generate_subdomain() -> str:
    """Generate a random subdomain using shortuuid."""
    return shortuuid.uuid()[:8]

def get_cloudflare_config() -> CloudflareConfig:
    """Get Cloudflare configuration from environment variables."""
    required_vars = {
        "email": "CLOUDFLARE_EMAIL",
        "api_key": "CLOUDFLARE_API_KEY",
        "zone_id": "CLOUDFLARE_ZONE_ID",
        "base_domain": "BASE_DOMAIN"
    }
    
    config_data = {}
    missing_vars = []
    
    for key, env_var in required_vars.items():
        value = os.getenv(env_var)
        if not value:
            missing_vars.append(env_var)
        config_data[key] = value
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return CloudflareConfig(**config_data)

def create_subdomain(ip_address: str) -> str:
    """Create a new subdomain pointing to the given IP address."""
    config = get_cloudflare_config()
    client = CloudflareClient(config)
    
    subdomain = generate_subdomain()
    full_domain = f"{subdomain}.{config.base_domain}"
    
    record = DNSRecord(
        name=full_domain,
        content=ip_address,
        comment=f"Auto-generated subdomain for file server"
    )
    
    result = client.create_dns_record(record)
    if not result.get("success"):
        raise RuntimeError(f"Failed to create DNS record: {result.get('errors')}")
    
    return full_domain
