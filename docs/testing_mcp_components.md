# Testing MCP Components

This guide explains how to run unit tests for the MCP server components, including the CLI tool, import fix script, and GUI components.

## Overview

The MCP server components include:
1. `mcp_cli.py` - Command-line interface for managing MCP servers
2. `fix_imports.py` - Script to fix import issues in MCP server builds
3. `mcp_server_manager.py` - GUI component for managing MCP servers

Each component has a comprehensive test suite to verify its functionality.

## Running Tests

### Using the Test Runner

The easiest way to run all MCP component tests is with the `run_mcp_tests.py` script:

```bash
# Run all MCP component tests
./run_mcp_tests.py

# Run with verbose output
./run_mcp_tests.py --verbose

# Run tests matching a specific pattern
./run_mcp_tests.py --pattern test_mcp_cli.py

# List available test modules
./run_mcp_tests.py --list
```

### Running Individual Test Modules

You can also run individual test modules directly:

```bash
# Test the MCP CLI
python -m unittest tests/unit/test_mcp_cli.py

# Test the fix_imports script
python -m unittest tests/unit/test_fix_imports.py

# Test the MCP Server Manager component
python -m unittest tests/unit/test_mcp_server_manager.py
```

## Test Coverage

### MCP CLI Tests (`test_mcp_cli.py`)

These tests verify:
- Finding available MCP server builds
- Getting server information
- Launching and stopping servers
- Testing server connections
- CLI main functions and commands

### Fix Imports Tests (`test_fix_imports.py`)

These tests verify:
- Fixing imports in `mcp_server.py`
- Fixing imports in `amm_engine.py`
- Fixing imports in `amm_models.py`
- Fixing imports in `memory_models.py`
- Creating `__init__.py` files
- Command-line interface functionality

### MCP Server Manager Tests (`test_mcp_server_manager.py`)

These tests verify:
- Finding available servers
- Getting server status
- Launching and stopping servers
- UI component behavior
- Session state management

## Writing New Tests

When extending the MCP components, please add corresponding tests:

1. For new CLI features, add tests to `test_mcp_cli.py`
2. For import fix improvements, add tests to `test_fix_imports.py`
3. For GUI component changes, add tests to `test_mcp_server_manager.py`

Follow these guidelines:
- Use descriptive test method names (`test_what_condition_expected_result`)
- Mock external dependencies (filesystem, network, subprocess)
- Test both success and failure cases
- Test edge cases and error handling

## Continuous Integration

The MCP component tests are included in the CI pipeline and will run automatically when:
- Opening a pull request
- Pushing to the main branch
- Merging a pull request

If any tests fail, the CI build will be marked as failed.

## Troubleshooting

### Mock Imports

When testing components that import external modules (like Streamlit), use mocks:

```python
# Example: Mocking Streamlit
sys.modules["streamlit"] = mock_st
```

### File System Operations

For tests that interact with the file system, use `tempfile.TemporaryDirectory()`:

```python
temp_dir = tempfile.TemporaryDirectory()
test_dir = Path(temp_dir.name)
# Create test files in test_dir...
temp_dir.cleanup()  # Clean up after test
```

### Subprocess Calls

For tests that spawn processes, mock `subprocess.Popen`:

```python
@patch("subprocess.Popen")
def test_method(self, mock_popen):
    mock_process = MagicMock()
    mock_process.poll.return_value = None  # Process is running
    mock_popen.return_value = mock_process
    # Test code...
```

## Test Design Philosophy

The MCP component tests follow these principles:

1. **Isolation**: Each test should run independently
2. **Speed**: Tests should run quickly
3. **Coverage**: Tests should cover normal and error cases
4. **Readability**: Tests should be easy to understand