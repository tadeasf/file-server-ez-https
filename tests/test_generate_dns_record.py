"""Tests for DNS record generation functionality."""
import pytest
from unittest.mock import patch, MagicMock
import re

from file_server_auto_https.lib.cloudflare.cloudflare_handler import (
    CloudflareClient,
    CloudflareConfig,
    DNSRecord,
    CloudflareError,
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
def mock_success_response():
    """Fixture for successful API response."""
    return {
        "success": True,
        "result": {
            "id": "test-id",
            "name": "test.example.com",
            "type": "A",
            "content": "1.1.1.1",
            "proxied": True,
            "ttl": 1
        }
    }

@pytest.fixture
def mock_client(mock_config, mock_success_response):
    """Fixture for mock Cloudflare client."""
    with patch('requests.post') as mock_post, \
         patch('requests.get') as mock_get, \
         patch('requests.delete') as mock_delete:
        
        # Configure mock responses
        mock_response = MagicMock()
        mock_response.json.return_value = mock_success_response
        mock_response.ok = True
        
        mock_post.return_value = mock_response
        mock_get.return_value = mock_response
        mock_delete.return_value = mock_response
        
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

def test_create_dns_record(mock_client, mock_success_response):
    """Test creating a DNS record."""
    record = DNSRecord(
        name="test.example.com",
        content="1.1.1.1",
        comment="Test record"
    )
    
    result = mock_client.create_dns_record(record)
    assert result == mock_success_response
    assert result["success"] is True
    assert "result" in result

def test_create_dns_record_error(mock_client):
    """Test error handling when creating a DNS record."""
    with patch('requests.post') as mock_post:
        # Configure mock to return an error response
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 400
        mock_response.reason = "Bad Request"
        mock_response.json.return_value = {
            "success": False,
            "errors": [{"code": 1000, "message": "API Error"}]
        }
        mock_post.return_value = mock_response
        
        record = DNSRecord(
            name="test.example.com",
            content="1.1.1.1"
        )
        
        with pytest.raises(CloudflareError) as exc_info:
            mock_client.create_dns_record(record)
        
        assert "400 Bad Request" in str(exc_info.value)

def test_list_dns_records(mock_client, mock_success_response):
    """Test listing DNS records."""
    with patch('requests.get') as mock_get:
        # Configure mock to return a list of records
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "success": True,
            "result": [mock_success_response["result"]]
        }
        mock_get.return_value = mock_response
        
        records = mock_client.list_dns_records()
        assert isinstance(records, list)
        assert len(records) == 1
        assert records[0]["id"] == "test-id"

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
    
    # Test TTL validation
    with pytest.raises(ValueError):
        DNSRecord(
            name="test.example.com",
            content="1.1.1.1",
            ttl=30  # Too low
        )
    
    # Test empty name validation
    with pytest.raises(ValueError):
        DNSRecord(
            name="",
            content="1.1.1.1"
        )
    
    # Test empty content validation
    with pytest.raises(ValueError):
        DNSRecord(
            name="test.example.com",
            content=""
        )
