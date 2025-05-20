"""
Unit tests for the MCP Server Manager component in the GUI.

These tests verify that the MCP Server Manager component correctly
finds, launches, and manages MCP servers.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import tempfile
from pathlib import Path
import time

# Add project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Mock Streamlit before importing the component
class MockStreamlit:
    """Mock for Streamlit functions."""
    
    def __init__(self):
        self.session_state = {}
        self.calls = []
    
    def __getattr__(self, name):
        """Record all calls to Streamlit functions."""
        def mock_func(*args, **kwargs):
            self.calls.append((name, args, kwargs))
            return MagicMock()
        return mock_func
    
    def reset(self):
        """Reset call history."""
        self.calls = []


# Create mock
mock_st = MockStreamlit()

# Mock the streamlit module
sys.modules["streamlit"] = mock_st

# Now import the component
from amm_gui.components.mcp_server_manager import (
    find_available_servers,
    get_server_status,
    launch_mcp_server,
    stop_mcp_server,
    mcp_server_manager
)

class TestMCPServerManager(unittest.TestCase):
    """Test cases for MCP Server Manager component."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Reset mock
        mock_st.reset()
        mock_st.session_state = {"mcp_servers": {}}
        
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)
        
        # Create a mock MCP server directory structure
        self.server_dir = self.test_dir / "test_server"
        self.server_dir.mkdir()
        
        # Create a start_server.py file
        with open(self.server_dir / "start_server.py", "w") as f:
            f.write("# Mock start_server.py file")
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary directory
        self.temp_dir.cleanup()
    
    @patch("amm_gui.components.mcp_server_manager.find_mcp_builds")
    def test_find_available_servers(self, mock_find_builds):
        """Test finding available MCP servers."""
        # Mock find_mcp_builds to return our test server
        mock_find_builds.return_value = [self.server_dir]
        
        # Call the function
        servers = find_available_servers()
        
        # Check results
        self.assertEqual(len(servers), 1)
        self.assertEqual(servers[0], self.server_dir)
        
        # Test with exception
        mock_find_builds.side_effect = Exception("Test error")
        servers = find_available_servers()
        self.assertEqual(len(servers), 0)
    
    def test_get_server_status(self):
        """Test getting server status."""
        # Mock process that's running
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # Process is running
        
        # Add to session state
        server_id = "test_server_id"
        mock_st.session_state["mcp_servers"] = {
            server_id: {
                "process": mock_process,
                "url": "http://localhost:8000",
                "start_time": time.time()
            }
        }
        
        # Check running server
        status = get_server_status(server_id)
        self.assertTrue(status["running"])
        self.assertEqual(status["url"], "http://localhost:8000")
        
        # Test non-existent server
        status = get_server_status("nonexistent")
        self.assertFalse(status["running"])
        self.assertIsNone(status["url"])
        
        # Test terminated server
        mock_process.poll.return_value = 0  # Process has exited
        status = get_server_status(server_id)
        self.assertFalse(status["running"])
    
    @patch("amm_gui.components.mcp_server_manager.start_server")
    def test_launch_mcp_server(self, mock_start_server):
        """Test launching an MCP server."""
        # Mock successful server start
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # Process is running
        mock_start_server.return_value = mock_process
        
        # Call the function
        result = launch_mcp_server(
            server_dir=self.server_dir,
            port=8000,
            host="0.0.0.0"
        )
        
        # Check results
        self.assertTrue(result["success"])
        self.assertIn("Server started", result["message"])
        self.assertIsNotNone(result["server_id"])
        self.assertIsNotNone(result["url"])
        
        # Check session state was updated
        server_id = result["server_id"]
        self.assertIn(server_id, mock_st.session_state["mcp_servers"])
        self.assertEqual(
            mock_st.session_state["mcp_servers"][server_id]["process"],
            mock_process
        )
        
        # Test already running server
        result = launch_mcp_server(
            server_dir=self.server_dir,
            port=8000,
            host="0.0.0.0"
        )
        self.assertTrue(result["success"])
        self.assertIn("Server already running", result["message"])
        
        # Test failed server start
        mock_start_server.return_value = None
        result = launch_mcp_server(
            server_dir=self.server_dir,
            port=9000,
            host="0.0.0.0"
        )
        self.assertFalse(result["success"])
        self.assertIn("Failed to start server", result["message"])
    
    def test_stop_mcp_server(self):
        """Test stopping an MCP server."""
        # Mock process that's running
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # Process is running
        
        # Add to session state
        server_id = "test_server_id"
        mock_st.session_state["mcp_servers"] = {
            server_id: {
                "process": mock_process,
                "url": "http://localhost:8000",
                "start_time": time.time(),
                "running": True
            }
        }
        
        # Test stopping the server
        result = stop_mcp_server(server_id)
        self.assertTrue(result["success"])
        self.assertIn("Server stopped", result["message"])
        mock_process.terminate.assert_called_once()
        self.assertFalse(mock_st.session_state["mcp_servers"][server_id]["running"])
        
        # Test stopping non-existent server
        result = stop_mcp_server("nonexistent")
        self.assertFalse(result["success"])
        self.assertIn("Server not found", result["message"])
        
        # Test stopping already terminated server
        mock_st.session_state["mcp_servers"][server_id]["process"] = None
        result = stop_mcp_server(server_id)
        self.assertTrue(result["success"])
        self.assertIn("Server was not running", result["message"])


class TestMCPServerManagerUI(unittest.TestCase):
    """Test the UI functions of the MCP Server Manager component."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Reset mock
        mock_st.reset()
        mock_st.session_state = {"mcp_servers": {}}
        
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)
        
        # Create a mock MCP server directory structure
        self.server_dir = self.test_dir / "test_server"
        self.server_dir.mkdir()
        
        # Create a start_server.py file
        with open(self.server_dir / "start_server.py", "w") as f:
            f.write("# Mock start_server.py file")
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary directory
        self.temp_dir.cleanup()
    
    @patch("amm_gui.components.mcp_server_manager.find_available_servers")
    @patch("amm_gui.components.mcp_server_manager.get_server_info")
    def test_mcp_server_manager_no_servers(self, mock_get_info, mock_find_servers):
        """Test MCP Server Manager with no servers."""
        # Mock no servers found
        mock_find_servers.return_value = []
        
        # Call the UI function
        result = mcp_server_manager()
        
        # Check results
        self.assertIsNone(result)
        
        # Verify warning was shown
        warning_calls = [call for call in mock_st.calls if call[0] == "warning"]
        self.assertTrue(any(warning_calls))
        
        # Verify subheader was created
        subheader_calls = [call for call in mock_st.calls if call[0] == "subheader"]
        self.assertTrue(any(subheader_calls))
    
    @patch("amm_gui.components.mcp_server_manager.find_available_servers")
    @patch("amm_gui.components.mcp_server_manager.get_server_info")
    def test_mcp_server_manager_with_servers(self, mock_get_info, mock_find_servers):
        """Test MCP Server Manager with available servers."""
        # Mock servers found
        mock_find_servers.return_value = [self.server_dir]
        
        # Mock server info
        mock_get_info.return_value = {
            "name": "Test Server",
            "description": "Test Description",
            "capabilities": {
                "fixed_knowledge": True,
                "adaptive_memory": True
            }
        }
        
        # Add a running server to session state
        server_id = str(self.server_dir.absolute())
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # Process is running
        mock_st.session_state["mcp_servers"] = {
            server_id: {
                "process": mock_process,
                "url": "http://localhost:8000",
                "start_time": time.time(),
                "running": True,
                "port": 8000,
                "host": "0.0.0.0",
                "dir": self.server_dir
            }
        }
        mock_st.session_state["selected_server_id"] = server_id
        mock_st.session_state["selected_server_url"] = "http://localhost:8000"
        
        # Call the UI function
        result = mcp_server_manager()
        
        # Check results
        self.assertEqual(result, "http://localhost:8000")
        
        # Verify server details were shown
        expander_calls = [call for call in mock_st.calls if call[0] == "expander"]
        self.assertTrue(any(expander_calls))
        
        # Verify selectbox was used
        selectbox_calls = [call for call in mock_st.calls if call[0] == "selectbox"]
        self.assertTrue(any(selectbox_calls))


if __name__ == "__main__":
    unittest.main()