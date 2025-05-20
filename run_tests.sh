#!/bin/bash
# Run all tests for the AMM project

# Set environment and working directory
set -e  # Exit on any error
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Set up environment for testing
echo "Setting up environment for tests..."

# Activate the mcp-env conda environment if available
if command -v conda &> /dev/null; then
    eval "$(conda shell.bash hook)"
    conda activate mcp-env || echo "mcp-env not found, using current environment"
fi

# Set Python path to include project root
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Temporarily unset the GEMINI_API_KEY if it exists (for tests that expect no API key)
if [ -n "$GEMINI_API_KEY" ]; then
    echo "Temporarily unsetting GEMINI_API_KEY for tests..."
    TEMP_GEMINI_API_KEY=$GEMINI_API_KEY
    unset GEMINI_API_KEY
fi

# Create directory for test outputs
mkdir -p test_output

# Enable colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Running AMM Tests ===${NC}"
echo

# First run MCP component tests if available
if [ -f "run_mcp_tests.py" ]; then
    echo -e "${YELLOW}Running MCP Component Tests...${NC}"
    if ./run_mcp_tests.py; then
        echo -e "${GREEN}MCP component tests passed!${NC}"
    else
        echo -e "${RED}MCP component tests failed!${NC}"
        exit 1
    fi
    echo
fi

# Run tests with pytest if available, otherwise use unittest
echo -e "${YELLOW}Running All Unit Tests...${NC}"
if command -v pytest &> /dev/null; then
    # Run the tests with pytest
    echo "Using pytest..."
    if pytest tests/unit -v; then
        echo -e "${GREEN}All unit tests passed!${NC}"
    else
        echo -e "${RED}Unit tests failed!${NC}"
        exit 1
    fi
else
    # Fall back to unittest
    echo "Using unittest..."
    if python -m unittest discover tests; then
        echo -e "${GREEN}All unit tests passed!${NC}"
    else
        echo -e "${RED}Unit tests failed!${NC}"
        exit 1
    fi
fi

# Restore the GEMINI_API_KEY if it was previously set
if [ -n "$TEMP_GEMINI_API_KEY" ]; then
    echo "Restoring GEMINI_API_KEY..."
    export GEMINI_API_KEY=$TEMP_GEMINI_API_KEY
fi

echo

# Show test summary
echo -e "${GREEN}All tests completed successfully!${NC}"
echo "To run specific tests, use:"
echo "  ./run_mcp_tests.py --pattern test_mcp_cli.py"
echo "  python -m unittest tests/unit/test_amm_models.py"
echo
echo "See docs/running_tests_guide.md for more information."