# MCP Server Guide

This guide explains how to build, run, and troubleshoot the MCP (Model Control Protocol) server for Agno Memory Module (AMM).

## Overview

The MCP server provides a standardized API for interacting with your AMM, allowing client applications to send queries and receive responses via HTTP, similar to other LLM APIs.

## Building an MCP Server

### Using the GUI

1. Open the AMM GUI:
   ```bash
   python run_amm_gui.py
   ```

2. Design your AMM (or load an existing design)

3. Go to the "Build" tab

4. Select "MCP Server" as the build type

5. Set your build options (directory, port, API key, etc.)

6. Click "Build AMM"

### Using the Command Line

You can also build an MCP server directly from the command line:

```bash
python build_amm.py path/to/design.json --output-dir build --build-type mcp_server
```

## Running the MCP Server

### Method 1: Using the Wrapper Script (Recommended)

Each MCP server build now includes a standalone wrapper script:

```bash
cd /path/to/build_directory
python start_server.py --host 0.0.0.0 --port 8000 --api-key your_api_key
```

Options:
- `--host`: Host address (default: 127.0.0.1, use 0.0.0.0 for all IPs)
- `--port`: Port number (default: 8000)
- `--api-key`: Optional API key
- `--api-key-required`: Enable API key authentication

### Method 2: Using run_mcp_server.py (Legacy)

The original method is still supported:

```bash
cd /path/to/build_directory
export AMM_DESIGN_PATH="$(pwd)/design.json"
export AMM_BUILD_DIR="$(pwd)"
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python run_mcp_server.py --port 8000 --host 0.0.0.0
```

## Using the MCP API

### Health Check

```bash
curl -X GET http://localhost:8000/health
```

### Get AMM Information

```bash
curl -X GET http://localhost:8000/info
```

### Generate a Response

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What can you tell me about these tech headlines?",
    "parameters": {},
    "context": {}
  }'
```

When API key authentication is enabled:

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "query": "What can you tell me about these tech headlines?",
    "parameters": {},
    "context": {}
  }'
```

## Upgrading Existing MCP Builds

If you have existing MCP server builds created before the standalone mode fixes, you can upgrade them:

```bash
./upgrade_mcp_build.sh /path/to/mcp/build/directory
```

This script:
1. Copies necessary module files into the build directory
2. Creates the standalone wrapper script
3. Adds README documentation

## Troubleshooting

### Import Errors

If you see errors like "No module named 'amm_project'", use the `start_server.py` wrapper script which is now included with all MCP server builds.

### Knowledge File Errors

If knowledge files aren't being found:
1. Check that the paths in your design.json file are correct
2. Ensure that the knowledge files exist in the specified locations
3. If using relative paths, make sure they are relative to the build directory

### API Key Authentication

If you're getting 401 Unauthorized errors:
1. Check that you're providing the correct API key in the X-API-Key header
2. Alternatively, include the key in the Authorization header as "Bearer YOUR_KEY"
3. Make sure API_KEY_REQUIRED is set to "true" in your environment

## Version Compatibility

The MCP server template has been updated to be fully self-contained and no longer requires the amm_project package to be installed. This makes it easier to deploy as a standalone service.

## Environment Variables

The MCP server uses the following environment variables:
- `AMM_DESIGN_PATH`: Path to the design.json file
- `AMM_BUILD_DIR`: Path to the build directory
- `MCP_API_KEY`: API key for authentication
- `API_KEY_REQUIRED`: Set to "true" to enable API key authentication
- `MCP_HOST`: Default host address
- `MCP_PORT`: Default port number