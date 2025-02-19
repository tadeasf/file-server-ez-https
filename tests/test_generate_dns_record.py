"""Tests for DNS record generation functionality."""
import pytest
from unittest.mock import patch, MagicMock
import re

from file_server_auto_https.lib.cloudflare.cloudflare_handler import (
    CloudflareClient,
    CloudflareConfig,
    DNSRecord,
    generate_subdomain
)

@pytest.fixture
def mock_config():
    """Fixture for mock Cloudflare configuration."""
    return CloudflareConfig(
        email="test@example.com",
        api_key="test-key",
        zone_id="test-zone",
        base_domain="example.com"
    )

@pytest.fixture
def mock_client(mock_config):
    """Fixture for mock Cloudflare client."""
    with patch('requests.post') as mock_post, \
         patch('requests.get') as mock_get:
        
        mock_post.return_value.json.return_value = {"success": True, "result": {"id": "test-id"}}
        mock_get.return_value.json.return_value = {"result": []}
        
        client = CloudflareClient(mock_config)
        yield client

def test_generate_subdomain_length():
    """Test that generated subdomains have correct length."""
    length = 8
    subdomain = generate_subdomain(length)
    assert len(subdomain) == length

def test_generate_subdomain_characters():
    """Test that generated subdomains contain valid characters."""
    subdomain = generate_subdomain()
    # Should only contain letters and numbers
    assert re.match(r'^[a-zA-Z0-9]+$', subdomain) is not None

def test_generate_subdomain_uniqueness():
    """Test that generated subdomains are unique."""
    subdomains = [generate_subdomain() for _ in range(100)]
    # Convert to set to remove duplicates
    unique_subdomains = set(subdomains)
    # Should have same length if all are unique
    assert len(subdomains) == len(unique_subdomains)

def test_create_dns_record(mock_client):
    """Test creating a DNS record."""
    record = DNSRecord(
        name="test.example.com",
        content="1.1.1.1",
        comment="Test record"
    )
    
    result = mock_client.create_dns_record(record)
    assert result["success"] is True
    assert "result" in result

def test_create_dns_record_error(mock_client):
    """Test error handling when creating a DNS record."""
    with patch('requests.post') as mock_post:
        mock_post.return_value = MagicMock()
        mock_post.return_value.raise_for_status.side_effect = Exception("API Error")
        
        record = DNSRecord(
            name="test.example.com",
            content="1.1.1.1"
        )
        
        with pytest.raises(Exception):
            mock_client.create_dns_record(record)

def test_list_dns_records(mock_client):
    """Test listing DNS records."""
    records = mock_client.list_dns_records()
    assert isinstance(records, list)

def test_dns_record_validation():
    """Test DNS record validation."""
    # Test required fields
    with pytest.raises(ValueError):
        DNSRecord()  # Missing required fields
    
    # Test valid record
    record = DNSRecord(
        name="test.example.com",
        content="1.1.1.1"
    )
    assert record.type == "A"  # Default value
    assert record.proxied is True  # Default value
    assert record.ttl == 1  # Default value
