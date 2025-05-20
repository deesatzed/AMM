# AMM Clean Build (May 19, 2025)

This is a production-ready version of the Agno Memory Module (AMM) system with all mock and test-only code removed.

## Important Production Guidelines

1. **No Mock Code**: This build contains no mock or placeholder implementations
2. **Real Dependencies**: All dependencies are real and properly implemented
3. **Environment Usage**: Uses the conda `mcp-env` environment exclusively
4. **API Integration**: Directly integrates with Gemini API (requires valid API key)

## Setup

### Environment Setup

```bash
# Create and activate the conda environment
conda env create -f environment.yml
conda activate mcp-env

# Copy example environment file and add your API keys
cp .env.example .env
# Edit .env with your actual API keys
```

### Running the Application

```bash
# Start the AMM GUI
python run_amm_gui.py

# Or run the MCP server demo
python demo_mcp_server.py
```

## Building AMMs

### Using the GUI

1. Open the AMM GUI: `python run_amm_gui.py`
2. Design your AMM or load an existing design
3. Go to the "Build" tab
4. Choose a build type:
   - **Python App**: Standalone Python application
   - **MCP Server**: FastAPI server implementing the Model Control Protocol
5. Configure build options
6. Click "Build AMM"

### Using the Command Line

You can also build directly from the command line:

```bash
python build_amm.py path/to/design.json --output-dir build_dir --build-type mcp_server
```

## Running MCP Server Builds

MCP server builds now include a standalone wrapper script for easy startup:

```bash
cd path/to/mcp_build
python start_server.py --host 0.0.0.0 --port 8000 --api-key your_key
```

Options:
- `--host`: Host address (default: 127.0.0.1, use 0.0.0.0 for all interfaces)
- `--port`: Port number (default: 8000)
- `--api-key`: Optional API key for authentication
- `--api-key-required`: Enable API key authentication

See `docs/MCP_SERVER_GUIDE.md` for complete details on using the MCP server.

## Development Guidelines

1. **Real Testing**: Always test with real dependencies and API keys
2. **No Placeholder Code**: Don't add mock implementations or placeholder code
3. **Environment Consistency**: Maintain compatibility with mcp-env
4. **Proper Error Handling**: Use robust error handling for API failures
5. **Documentation**: Keep documentation up-to-date with implementation

## Production Components

1. **AMM Engine**: Core processing engine with real Gemini API integration
2. **MCP Server**: Production-ready FastAPI server for client integration
   - Now supports standalone deployment with self-contained modules
   - Includes wrapper script for easy startup and configuration
3. **Key Manager**: Secure API key management for production deployments
4. **GUI Interface**: User-friendly interface for AMM design and testing

## Upgrading Existing MCP Builds

If you have existing MCP server builds created before the standalone mode fixes, you can upgrade them:

```bash
./upgrade_mcp_build.sh /path/to/mcp/build/directory
```

## Releasing to Production

Before releasing to production:

1. Run all tests with real API keys
2. Verify memory usage and performance
3. Check API rate limit compliance
4. Validate security measures
5. Update documentation for any changes

## Additional Documentation

- `docs/MCP_SERVER_GUIDE.md`: Complete guide for building and using MCP servers
- `docs/running_mcp_server.md`: Detailed runtime options for MCP servers
- `docs/FIXED_ISSUES.md`: Documentation of fixed issues and improvements