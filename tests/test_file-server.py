"""Tests for the file server functionality."""
import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from file_server_auto_https.lib.server.file_server import FileServer, find_free_port

def test_find_free_port():
    """Test finding a free port."""
    # Test successful port finding
    with patch('socket.socket') as mock_socket:
        mock_socket.return_value.__enter__.return_value.bind.return_value = None
        port = find_free_port(8000)
        assert port == 8000

    # Test when first port is taken
    with patch('socket.socket') as mock_socket:
        mock_socket.return_value.__enter__.return_value.bind.side_effect = [OSError, None]
        port = find_free_port(8000)
        assert port == 8001

    # Test when no ports are available
    with patch('socket.socket') as mock_socket:
        mock_socket.return_value.__enter__.return_value.bind.side_effect = OSError
        port = find_free_port(8000, max_tries=1)
        assert port is None

def test_file_server_init():
    """Test FileServer initialization."""
    server = FileServer("./")
    assert server.directory == Path("./").resolve()
    assert server.host == "0.0.0.0"
    assert server.port == 8000
    assert server.directory_listing is True
    assert server._server is None
    assert server._server_thread is None

def test_file_server_context_manager():
    """Test FileServer context manager."""
    with patch('threading.Thread'):
        with FileServer("./") as server:
            assert server.is_running
        assert not server.is_running

@pytest.mark.asyncio
async def test_file_server_start_stop():
    """Test starting and stopping the file server."""
    with patch('threading.Thread') as mock_thread:
        server = FileServer("./")
        
        # Test start
        server.start()
        assert server.is_running
        mock_thread.assert_called_once()
        
        # Test stop
        server.stop()
        assert not server.is_running
        assert server._server is None
        assert server._server_thread is None

def test_file_server_url():
    """Test server URL generation."""
    server = FileServer("./", host="localhost", port=8000)
    assert server.url == "http://localhost:8000"