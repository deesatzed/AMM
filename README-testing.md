# AMM Testing (May 19, 2025)

This is a testing environment for the Agno Memory Module (AMM) system.

## Setup and Testing

### Environment Setup

This project uses the `mcp-env` conda environment for development and testing. The environment specifications can be found in `environment.yml`.

```bash
# Create and activate the conda environment
conda env create -f environment.yml
conda activate mcp-env
```

### Running Tests

To run the test suite, use the provided script:

```bash
./run_tests.sh
```

This script:
1. Activates the `mcp-env` conda environment
2. Temporarily unsets any existing GEMINI_API_KEY (to avoid test conflicts)
3. Runs the pytest test suite
4. Restores the original GEMINI_API_KEY

## Key Components

The AMM system consists of:

1. **AMM Engine** (amm_project/engine/amm_engine.py)
   - Core processing logic for queries, knowledge sources, and adaptive memory

2. **AMM Models** (amm_project/models/)
   - Data models for AMM designs, knowledge sources, and memory records

3. **MCP Server** (amm_project/templates/mcp_server.py)
   - FastAPI server for exposing AMMs via standardized API

4. **AMM GUI** (amm_gui/)
   - Streamlit-based interface for designing and testing AMMs

## Recent Fixes

The following issues have been addressed in this version:

1. **API Key Management**: Fixed test dependency on GEMINI_API_KEY environment variable
2. **MagicMock Validation**: Resolved Pydantic validation issues with MagicMock objects
3. **Test Isolation**: Improved test independence by using more comprehensive mocking

## Next Steps

1. Improve test coverage for the MCP server functionality
2. Add integration tests for the AMM builder
3. Develop more comprehensive GUI tests
4. Add documentation and examples for customizing the AMM templates