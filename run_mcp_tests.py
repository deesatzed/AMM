#!/usr/bin/env python
"""
Test runner for MCP server components.

This script runs all the unit tests for the MCP server components,
including the CLI, import fixer, and GUI components.
"""

import os
import sys
import unittest
import argparse
from pathlib import Path

def find_tests(pattern=None):
    """Find all test cases matching the given pattern."""
    loader = unittest.TestLoader()
    if pattern:
        suite = loader.discover('tests', pattern=pattern)
    else:
        # Load all the MCP-related tests by default
        suite = unittest.TestSuite()
        
        # Add test_mcp_cli.py
        cli_tests = loader.discover('tests', pattern='test_mcp_cli.py')
        suite.addTests(cli_tests)
        
        # Add test_fix_imports.py
        fix_imports_tests = loader.discover('tests', pattern='test_fix_imports.py')
        suite.addTests(fix_imports_tests)
        
        # Add test_mcp_server_manager.py
        manager_tests = loader.discover('tests', pattern='test_mcp_server_manager.py')
        suite.addTests(manager_tests)
    
    return suite

def run_tests(pattern=None, verbosity=1):
    """Run the specified tests."""
    suite = find_tests(pattern)
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    return result.wasSuccessful()

def list_available_tests():
    """List all available test modules."""
    print("Available test modules:")
    for test_file in Path('tests').glob('**/test_*.py'):
        print(f"  {test_file.relative_to('tests')}")

def main():
    """Parse arguments and run tests."""
    parser = argparse.ArgumentParser(description='Run MCP server tests')
    parser.add_argument('--pattern', '-p', help='Pattern to match test files (e.g., "test_mcp_*.py")')
    parser.add_argument('--verbose', '-v', action='store_true', help='Run with verbose output')
    parser.add_argument('--list', '-l', action='store_true', help='List available test modules')
    args = parser.parse_args()
    
    # Make sure current directory is in path
    sys.path.insert(0, os.getcwd())
    
    if args.list:
        list_available_tests()
        return 0
    
    verbosity = 2 if args.verbose else 1
    success = run_tests(args.pattern, verbosity)
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())