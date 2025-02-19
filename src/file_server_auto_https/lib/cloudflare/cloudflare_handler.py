"""Cloudflare API handler module."""
import os
from typing import Optional, Dict, List, Any
import string
import random
import requests
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class CloudflareError(Exception):
    """Custom exception for Cloudflare API errors."""
    def __init__(self, message: str, errors: Optional[List[Dict[str, Any]]] = None):
        super().__init__(message)
        self.errors = errors or []

class CloudflareConfig(BaseModel):
    """Cloudflare API configuration."""
    email: str = Field(..., description="Cloudflare account email")
    api_key: str = Field(..., description="Cloudflare API key")
    zone_id: str = Field(..., description="Zone ID for the domain")
    base_domain: str = Field(..., description="Base domain for subdomains")

    @field_validator('zone_id')
    def validate_zone_id(cls, v):
        """Validate zone_id length."""
        if len(v) > 32:
            raise ValueError("zone_id must not exceed 32 characters")
        return v

class DNSRecordSettings(BaseModel):
    """DNS record settings."""
    ipv4_only: bool = False
    ipv6_only: bool = False

class DNSRecord(BaseModel):
    """DNS record model."""
    name: str
    type: str = "A"
    content: str
    proxied: bool = True
    ttl: int = 1  # Auto TTL
    comment: Optional[str] = None
    settings: Optional[DNSRecordSettings] = None
    tags: Optional[List[str]] = None

    @field_validator('name')
    def validate_name(cls, v):
        """Validate record name."""
        if not v:
            raise ValueError("name cannot be empty")
        return v

    @field_validator('content')
    def validate_content(cls, v):
        """Validate record content."""
        if not v:
            raise ValueError("content cannot be empty")
        return v

    @field_validator('ttl')
    def validate_ttl(cls, v):
        """Validate TTL value."""
        if v != 1 and (v < 60 or v > 86400):
            raise ValueError("ttl must be 1 (automatic) or between 60 and 86400 seconds")
        return v

class CloudflareClient:
    """Client for interacting with Cloudflare API."""
    
    def __init__(self, config: Optional[CloudflareConfig] = None):
        """Initialize the client with config or load from environment."""
        self.config = config or self._load_config()
        self.base_url = "https://api.cloudflare.com/client/v4"
        self.headers = {
            "X-Auth-Email": self.config.email,
            "X-Auth-Key": self.config.api_key,
            "Content-Type": "application/json"
        }

    @staticmethod
    def _load_config() -> CloudflareConfig:
        """Load configuration from environment variables."""
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

    def _handle_response(self, response: requests.Response) -> Dict:
        """Handle API response and raise appropriate errors."""
        try:
            data = response.json()
        except ValueError:
            raise CloudflareError(f"Invalid JSON response: {response.text}")

        if not response.ok:
            message = f"{response.status_code} {response.reason}"
            if data.get("errors"):
                message = f"{message}: {data['errors']}"
            raise CloudflareError(message, data.get("errors"))

        if not data.get("success"):
            raise CloudflareError("API request was not successful", data.get("errors"))

        return data

    def create_dns_record(self, record: DNSRecord) -> Dict:
        """Create a new DNS record."""
        url = f"{self.base_url}/zones/{self.config.zone_id}/dns_records"
        
        # Prepare the record data
        record_data = record.model_dump(exclude_none=True)
        
        # Add default settings if not provided
        if "settings" not in record_data:
            record_data["settings"] = {"ipv4_only": False, "ipv6_only": False}
            
        response = requests.post(url, headers=self.headers, json=record_data)
        return self._handle_response(response)

    def list_dns_records(self, params: Optional[Dict] = None) -> List[Dict]:
        """List DNS records for the zone."""
        url = f"{self.base_url}/zones/{self.config.zone_id}/dns_records"
        response = requests.get(url, headers=self.headers, params=params or {})
        data = self._handle_response(response)
        return data["result"]

    def delete_dns_record(self, record_id: str) -> Dict:
        """Delete a DNS record by ID."""
        if len(record_id) > 32:
            raise ValueError("record_id must not exceed 32 characters")
            
        url = f"{self.base_url}/zones/{self.config.zone_id}/dns_records/{record_id}"
        response = requests.delete(url, headers=self.headers)
        return self._handle_response(response)

def generate_subdomain(length: int = 8) -> str:
    """Generate a random subdomain with mixed case letters and numbers.
    
    Args:
        length: Length of the subdomain to generate.
    
    Returns:
        A random string of specified length containing mixed case letters and numbers.
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))
