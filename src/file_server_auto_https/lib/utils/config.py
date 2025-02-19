"""Configuration management module."""
import os
from typing import Dict
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

    @classmethod
    def from_env(cls) -> 'CloudflareConfig':
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
        
        return cls(**config_data)

class ServerConfig(BaseModel):
    """File server configuration."""
    default_host: str = "0.0.0.0"
    default_port: int = 8000
    max_port_tries: int = 100
    directory_listing: bool = True

# Global config instances
cloudflare = CloudflareConfig.from_env()
server = ServerConfig() 