"""Tests for IP address detection functionality."""
import socket
import pytest
from unittest.mock import patch, MagicMock
from file_server_auto_https.lib.grab_ip import get_local_ip, get_public_ip, get_ip

def test_get_local_ip():
    """Test local IP detection."""
    with patch('socket.socket') as mock_socket:
        mock_socket.return_value.getsockname.return_value = ('192.168.1.100', 0)
        ip = get_local_ip()
        assert ip == '192.168.1.100'

def test_get_public_ip():
    """Test public IP detection."""
    # Test successful API call
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = {'ip': '1.2.3.4'}
        ip = get_public_ip()
        assert ip == '1.2.3.4'

    # Test failed API call
    with patch('requests.get') as mock_get:
        mock_get.side_effect = Exception("API error")
        ip = get_public_ip()
        assert ip is None

def test_get_ip():
    """Test IP address selection logic."""
    with patch('file_server_auto_https.lib.grab_ip.get_public_ip') as mock_public_ip, \
         patch('file_server_auto_https.lib.grab_ip.get_local_ip') as mock_local_ip:
        
        # Test public IP preference
        mock_public_ip.return_value = '1.2.3.4'
        mock_local_ip.return_value = '192.168.1.100'
        assert get_ip(use_public=True) == '1.2.3.4'
        
        # Test fallback to local IP
        mock_public_ip.return_value = None
        assert get_ip(use_public=True) == '192.168.1.100'
        
        # Test local IP only
        assert get_ip(use_public=False) == '192.168.1.100'