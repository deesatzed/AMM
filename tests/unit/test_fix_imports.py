"""
Unit tests for the fix_imports.py script.

These tests verify that the script correctly fixes import issues
in MCP server builds.
"""

import os
import sys
import unittest
from unittest.mock import patch, mock_open, MagicMock
import tempfile
from pathlib import Path

# Add project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import the functions to test
from fix_imports import (
    fix_mcp_server_imports,
    fix_amm_engine_imports,
    fix_model_imports,
    fix_memory_models_imports,
    create_init_file
)

class TestFixImports(unittest.TestCase):
    """Test cases for fix_imports.py functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary directory
        self.temp_dir.cleanup()
    
    def test_create_init_file(self):
        """Test creating __init__.py file."""
        # Call the function
        create_init_file(self.test_dir)
        
        # Check if file was created
        init_file = self.test_dir / "__init__.py"
        self.assertTrue(init_file.exists())
        
        # Check file content
        with open(init_file, "r") as f:
            content = f.read()
            self.assertIn("# This file makes the directory a Python package", content)
    
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists")
    def test_fix_mcp_server_imports(self, mock_exists, mock_file):
        """Test fixing imports in mcp_server.py."""
        # Setup mocks
        mock_exists.return_value = True
        
        # Set up mock file content
        mock_file.return_value.read.return_value = """
# Try different import paths to handle both direct imports and package imports
try:
    # Direct imports (when files are copied to build dir)
    from amm_engine import AMMEngine
    from amm_models import AMMDesign, AdaptiveMemoryConfig, AgentPrompts
except ImportError:
    try:
        # Package imports (when installed as a package)
        from amm_project.engine.amm_engine import AMMEngine
        from amm_project.models.amm_models import AMMDesign, AdaptiveMemoryConfig, AgentPrompts
    except ImportError as e:
        print(f"Error importing AMM modules: {e}")
        print("Please ensure the AMM modules are available in the Python path.")
        # We'll handle this gracefully when initializing the model server
"""
        
        # Call the function
        result = fix_mcp_server_imports("/path/to/mcp_server.py")
        
        # Check results
        self.assertTrue(result)
        mock_file.assert_called()
        
        # Verify file was written with new imports
        write_calls = mock_file.return_value.write.call_args_list
        self.assertTrue(len(write_calls) > 0)
        
        # Combine all write calls into a single string
        written_content = ""
        for call in write_calls:
            written_content += call[0][0]
        
        # Check for updated imports
        self.assertIn("Direct imports - standalone version", written_content)
        self.assertIn("from memory_models import MemoryRecord", written_content)
    
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists")
    def test_fix_amm_engine_imports(self, mock_exists, mock_file):
        """Test fixing imports in amm_engine.py."""
        # Setup mocks
        mock_exists.return_value = True
        
        # Set up mock file content
        mock_file.return_value.read.return_value = """
from amm_project.models.amm_models import AMMDesign, KnowledgeSourceType
from amm_project.models.memory_models import MemoryRecord
"""
        
        # Call the function
        result = fix_amm_engine_imports("/path/to/amm_engine.py")
        
        # Check results
        self.assertTrue(result)
        mock_file.assert_called()
        
        # Verify file was written with new imports
        write_calls = mock_file.return_value.write.call_args_list
        self.assertTrue(len(write_calls) > 0)
        
        # Combine all write calls into a single string
        written_content = ""
        for call in write_calls:
            written_content += call[0][0]
        
        # Check for updated imports
        self.assertIn("try:", written_content)
        self.assertIn("from amm_models import", written_content)
        self.assertIn("except ImportError:", written_content)
    
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists")
    def test_fix_model_imports(self, mock_exists, mock_file):
        """Test fixing imports in amm_models.py."""
        # Setup mocks
        mock_exists.return_value = True
        
        # Set up mock file content
        mock_file.return_value.read.return_value = """
from amm_project.config.model_config import ModelConfig
"""
        
        # Call the function
        result = fix_model_imports("/path/to/amm_models.py")
        
        # Check results
        self.assertTrue(result)
        mock_file.assert_called()
        
        # Verify file was written with new imports
        write_calls = mock_file.return_value.write.call_args_list
        self.assertTrue(len(write_calls) > 0)
        
        # Combine all write calls into a single string
        written_content = ""
        for call in write_calls:
            written_content += call[0][0]
        
        # Check for updated imports
        self.assertIn("try:", written_content)
        self.assertIn("from model_config import", written_content)
        self.assertIn("except ImportError:", written_content)
    
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists")
    def test_fix_memory_models_imports(self, mock_exists, mock_file):
        """Test fixing imports in memory_models.py."""
        # Setup mocks
        mock_exists.return_value = True
        
        # Set up mock file content
        mock_file.return_value.read.return_value = """
from amm_project.models.amm_models import BaseModel
"""
        
        # Call the function
        result = fix_memory_models_imports("/path/to/memory_models.py")
        
        # Check results
        self.assertTrue(result)
        mock_file.assert_called()
        
        # Verify file was written with new imports
        write_calls = mock_file.return_value.write.call_args_list
        self.assertTrue(len(write_calls) > 0)
        
        # Combine all write calls into a single string
        written_content = ""
        for call in write_calls:
            written_content += call[0][0]
        
        # Check for updated imports
        self.assertIn("try:", written_content)
        self.assertIn("from amm_models import", written_content)
        self.assertIn("except ImportError:", written_content)


class TestFixImportsMain(unittest.TestCase):
    """Test the main function of fix_imports.py."""
    
    @patch("fix_imports.fix_mcp_server_imports")
    @patch("fix_imports.fix_amm_engine_imports")
    @patch("fix_imports.fix_model_imports")
    @patch("fix_imports.fix_memory_models_imports")
    @patch("fix_imports.create_init_file")
    @patch("os.path.abspath")
    @patch("os.path.join")
    @patch("builtins.print")
    def test_main_function(self, mock_print, mock_join, mock_abspath,
                           mock_create_init, mock_fix_memory, mock_fix_models,
                           mock_fix_engine, mock_fix_mcp):
        """Test the main function."""
        # Setup mocks
        mock_abspath.return_value = "/abs/path/to/server"
        mock_join.side_effect = lambda path, file: f"{path}/{file}"
        
        mock_fix_mcp.return_value = True
        mock_fix_engine.return_value = True
        mock_fix_models.return_value = True
        mock_fix_memory.return_value = True
        
        # Mock command line arguments
        with patch("sys.argv", ["fix_imports.py", "/path/to/server"]):
            # Call the main function
            from fix_imports import main
            main()
        
        # Verify all fix functions were called
        mock_fix_mcp.assert_called_once()
        mock_fix_engine.assert_called_once()
        mock_fix_models.assert_called_once()
        mock_fix_memory.assert_called_once()
        mock_create_init.assert_called_once()
    
    @patch("builtins.print")
    def test_help_message(self, mock_print):
        """Test printing help message."""
        from fix_imports import print_help
        
        # Call the function
        print_help()
        
        # Verify help was printed
        mock_print.assert_called()
        
        # Check all expected sections
        calls = [call[0][0] for call in mock_print.call_args_list]
        help_text = "\n".join(calls)
        
        self.assertIn("MCP Server Import Fixer", help_text)
        self.assertIn("Usage:", help_text)
        self.assertIn("Options:", help_text)
        self.assertIn("Examples:", help_text)


if __name__ == "__main__":
    unittest.main()