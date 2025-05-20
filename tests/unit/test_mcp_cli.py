"""
Unit tests for the MCP CLI tool.

These tests cover the key functionality of the MCP CLI tool,
including server discovery, launching, and management.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import json
from pathlib import Path

# Add project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import the module to test
from mcp_cli import (
    find_mcp_builds,
    get_server_info,
    launch_server,
    stop_server,
    test_server_connection,
    running_servers
)

class TestMCPCLI(unittest.TestCase):
    """Test cases for MCP CLI functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Clear running servers dictionary before each test
        running_servers.clear()
        
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)
        
        # Create a mock MCP server directory structure
        self.server_dir = self.test_dir / "test_server"
        self.server_dir.mkdir()
        
        # Create a start_server.py file
        with open(self.server_dir / "start_server.py", "w") as f:
            f.write("# Mock start_server.py file")
        
        # Create a design.json file
        self.design_data = {
            "name": "Test AMM",
            "description": "Test description",
            "knowledge_sources": [{"id": "test1", "type": "text", "content": "test"}],
            "adaptive_memory": {"enabled": True}
        }
        with open(self.server_dir / "design.json", "w") as f:
            json.dump(self.design_data, f)
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary directory
        self.temp_dir.cleanup()
    
    def test_find_mcp_builds(self):
        """Test finding MCP server builds."""
        # Test with existing directory
        builds = find_mcp_builds(self.test_dir)
        self.assertEqual(len(builds), 1)
        self.assertEqual(builds[0], self.server_dir)
        
        # Test with non-existent directory
        builds = find_mcp_builds(self.test_dir / "nonexistent")
        self.assertEqual(len(builds), 0)
    
    def test_get_server_info(self):
        """Test getting server information."""
        # Test with valid server directory
        info = get_server_info(self.server_dir)
        self.assertIsNotNone(info)
        self.assertEqual(info["name"], "Test AMM")
        self.assertEqual(info["description"], "Test description")
        self.assertTrue(info["capabilities"]["fixed_knowledge"])
        self.assertTrue(info["capabilities"]["adaptive_memory"])
        
        # Test with invalid server directory
        info = get_server_info(self.test_dir / "nonexistent")
        self.assertIsNone(info)
    
    @patch("subprocess.Popen")
    @patch("time.sleep")  # Mock time.sleep to speed up tests
    def test_launch_server(self, mock_sleep, mock_popen):
        """Test launching a server."""
        # Mock the process
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # Process is running
        mock_process.pid = 12345
        mock_popen.return_value = mock_process
        
        # Test launching a server
        pid = launch_server(self.server_dir, port=8000, host="0.0.0.0", wait=False)
        self.assertEqual(pid, 12345)
        self.assertIn(12345, running_servers)
        self.assertEqual(running_servers[12345]["dir"], self.server_dir)
        self.assertEqual(running_servers[12345]["port"], 8000)
        
        # Test launching with non-existent directory
        pid = launch_server(self.test_dir / "nonexistent")
        self.assertIsNone(pid)
    
    @patch("subprocess.Popen")
    def test_stop_server(self, mock_popen):
        """Test stopping a server."""
        # Mock the process
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # Process is running
        mock_process.pid = 12345
        mock_popen.return_value = mock_process
        
        # Add a running server
        running_servers[12345] = {
            "process": mock_process,
            "dir": self.server_dir,
            "port": 8000,
            "host": "0.0.0.0",
            "url": "http://localhost:8000"
        }
        
        # Test stopping a server
        result = stop_server(12345)
        self.assertTrue(result)
        self.assertNotIn(12345, running_servers)
        mock_process.terminate.assert_called_once()
        
        # Test stopping a non-existent server
        result = stop_server(99999)
        self.assertFalse(result)
    
    @patch("requests.get")
    @patch("requests.post")
    def test_test_server_connection(self, mock_post, mock_get):
        """Test server connection testing."""
        # Mock successful health check response
        mock_health_response = MagicMock()
        mock_health_response.status_code = 200
        mock_health_response.json.return_value = {"status": "ok", "timestamp": "2023-01-01T00:00:00Z"}
        
        # Mock successful info check response
        mock_info_response = MagicMock()
        mock_info_response.status_code = 200
        mock_info_response.json.return_value = {
            "name": "Test AMM",
            "description": "Test description",
            "version": "1.0.0",
            "capabilities": {
                "fixed_knowledge": True,
                "adaptive_memory": True
            }
        }
        
        # Mock successful query response
        mock_query_response = MagicMock()
        mock_query_response.status_code = 200
        mock_query_response.json.return_value = {
            "response": "Hello, I'm a test assistant!"
        }
        
        # Configure the mock.get to return different responses based on URL
        def get_side_effect(url, **kwargs):
            if "/health" in url:
                return mock_health_response
            elif "/info" in url:
                return mock_info_response
            return MagicMock(status_code=404)
        
        mock_get.side_effect = get_side_effect
        mock_post.return_value = mock_query_response
        
        # Test successful connection
        result = test_server_connection("http://localhost:8000")
        self.assertTrue(result)
        
        # Test failed connection (exception)
        mock_get.side_effect = Exception("Connection refused")
        result = test_server_connection("http://localhost:9999")
        self.assertFalse(result)


class TestMCPCLIMainFunctions(unittest.TestCase):
    """Test the main functions that orchestrate the CLI operations."""
    
    @patch("mcp_cli.find_mcp_builds")
    def test_list_servers(self, mock_find_builds):
        """Test listing servers."""
        from mcp_cli import list_servers
        
        # Mock find_mcp_builds to return a list of paths
        mock_server1 = MagicMock()
        mock_server1.name = "server1"
        mock_server2 = MagicMock()
        mock_server2.name = "server2"
        mock_find_builds.return_value = [mock_server1, mock_server2]
        
        # Mock get_server_info
        with patch("mcp_cli.get_server_info") as mock_get_info:
            mock_get_info.return_value = {
                "name": "Test Server",
                "description": "Test Description",
                "capabilities": {
                    "fixed_knowledge": True,
                    "adaptive_memory": True
                }
            }
            
            # Test listing servers
            with patch("builtins.print") as mock_print:
                servers = list_servers(show_details=True)
                self.assertEqual(len(servers), 2)
                mock_print.assert_called()
    
    @patch("mcp_cli.running_servers")
    def test_list_running_servers(self, mock_running_servers):
        """Test listing running servers."""
        from mcp_cli import list_running_servers
        
        # Mock running_servers dictionary
        mock_process1 = MagicMock()
        mock_process1.poll.return_value = None  # Process is running
        mock_process2 = MagicMock()
        mock_process2.poll.return_value = 0  # Process has exited
        
        mock_running_servers.items.return_value = [
            (12345, {
                "process": mock_process1,
                "dir": Path("/path/to/server1"),
                "url": "http://localhost:8000",
                "start_time": 1000000000
            }),
            (67890, {
                "process": mock_process2,
                "dir": Path("/path/to/server2"),
                "url": "http://localhost:8001",
                "start_time": 1000000000
            })
        ]
        
        # Test listing running servers
        with patch("builtins.print") as mock_print:
            with patch("time.time", return_value=1000001000):  # 1000 seconds elapsed
                list_running_servers()
                # Should only show the running server
                mock_print.assert_called()
    
    @patch("subprocess.run")
    def test_fix_imports(self, mock_run):
        """Test fixing imports."""
        # We'll test this indirectly through the main function
        from mcp_cli import main
        
        # Mock command line arguments
        with patch("sys.argv", ["mcp_cli.py", "--fix", "/path/to/server"]):
            with patch("pathlib.Path.exists", return_value=True):
                with patch("builtins.print") as mock_print:
                    main()
                    mock_run.assert_called_once()


if __name__ == "__main__":
    unittest.main()