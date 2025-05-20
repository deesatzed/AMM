# Running Tests Guide

This guide explains how to run tests for the AMM project, including the MCP server components and core AMM functionality.

## Quick Start

For a quick test run, use one of these commands:

```bash
# Run MCP component tests
./run_mcp_tests.py

# Run all tests in the project
python -m unittest discover tests

# Run a specific test module
python -m unittest tests/unit/test_mcp_cli.py
```

## Test Types

The AMM project includes several types of tests:

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test interactions between components
3. **Functional Tests**: Test end-to-end functionality

## Running MCP Component Tests

The MCP components (CLI, import fixer, GUI integration) have dedicated tests and a test runner:

```bash
# Run all MCP tests
./run_mcp_tests.py

# Run with verbose output
./run_mcp_tests.py --verbose

# Run specific MCP tests
./run_mcp_tests.py --pattern test_mcp_cli.py

# List available test modules
./run_mcp_tests.py --list
```

## Running Specific Tests

You can run specific tests by module, class, or method:

```bash
# Run a specific test module
python -m unittest tests/unit/test_mcp_cli.py

# Run a specific test class
python -m unittest tests.unit.test_mcp_cli.TestMCPCLI

# Run a specific test method
python -m unittest tests.unit.test_mcp_cli.TestMCPCLI.test_find_mcp_builds
```

## Running with Pytest

If you have pytest installed, you can use it for more advanced testing features:

```bash
# Install pytest if needed
pip install pytest pytest-cov

# Run all tests
pytest tests/

# Run with coverage report
pytest --cov=amm_project tests/

# Run specific tests
pytest tests/unit/test_mcp_cli.py

# Run tests matching a pattern
pytest -k "mcp"
```

## Test Environment Setup

Before running tests, make sure your environment is set up correctly:

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your test configuration
   ```

3. **Create Test Directories**:
   ```bash
   mkdir -p build  # For MCP server build tests
   ```

## Troubleshooting Tests

If tests are failing, check these common issues:

1. **Import Errors**: Make sure the project root is in your Python path
   ```bash
   export PYTHONPATH=$PYTHONPATH:$(pwd)
   ```

2. **Missing Dependencies**: Make sure all dependencies are installed
   ```bash
   pip install -r requirements/dev.txt
   ```

3. **File Permissions**: Make sure script files are executable
   ```bash
   chmod +x run_mcp_tests.py
   ```

4. **Environment Variables**: Check if required environment variables are set
   ```bash
   source .env
   ```

## Adding New Tests

When adding new features, please add corresponding tests:

1. **Create a New Test Module**:
   ```python
   # tests/unit/test_my_feature.py
   import unittest
   
   class TestMyFeature(unittest.TestCase):
       def test_new_functionality(self):
           # Test code here
           self.assertTrue(True)
   ```

2. **Add Test Documentation**:
   Update the test documentation to include your new tests.

3. **Run Your Tests**:
   Make sure your tests pass before submitting changes.

## Test Directories

The test structure is organized as follows:

```
tests/                     # Root test directory
├── __init__.py            # Makes tests a proper package
├── unit/                  # Unit tests
│   ├── __init__.py
│   ├── test_amm_engine.py # Core AMM tests
│   ├── test_amm_models.py # Model tests
│   ├── test_mcp_cli.py    # MCP CLI tests
│   ├── test_fix_imports.py# Import fixer tests
│   └── test_mcp_server_manager.py # GUI component tests
└── integration/           # Integration tests
    └── __init__.py
```

## Test Documentation

Each test module includes docstrings that explain:
- What functionality is being tested
- What test fixtures are used
- What mocks or patches are applied

Review these docstrings to understand test purpose and behavior.

## Continuous Integration

Tests are automatically run in the CI pipeline when code is pushed or a PR is created. The CI configuration runs all tests and reports any failures.

To see the same results locally that CI will see:

```bash
# Run tests the way CI does
./run_tests.sh
```

## Conclusion

Testing is an essential part of maintaining code quality. By running tests regularly and adding tests for new features, we ensure the AMM project remains stable and reliable.