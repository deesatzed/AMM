#!/bin/bash

# Script to upgrade an existing MCP server build with the standalone mode fixes
# Usage: ./upgrade_mcp_build.sh /path/to/mcp/build/directory

set -e  # Exit on any error

if [ $# -ne 1 ]; then
    echo "Usage: $0 /path/to/mcp/build/directory"
    exit 1
fi

BUILD_DIR="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -d "$BUILD_DIR" ]; then
    echo "Error: Build directory does not exist: $BUILD_DIR"
    exit 1
fi

if [ ! -f "$BUILD_DIR/mcp_server.py" ]; then
    echo "Error: Not an MCP server build (missing mcp_server.py): $BUILD_DIR"
    exit 1
fi

echo "Upgrading MCP server build: $BUILD_DIR"

# Copy required modules to the build directory
echo "Copying core modules..."
cp "$SCRIPT_DIR/amm_project/models/amm_models.py" "$BUILD_DIR/amm_models.py"
cp "$SCRIPT_DIR/amm_project/models/memory_models.py" "$BUILD_DIR/memory_models.py"
cp "$SCRIPT_DIR/amm_project/engine/amm_engine.py" "$BUILD_DIR/amm_engine.py"
cp "$SCRIPT_DIR/amm_project/config/model_config.py" "$BUILD_DIR/model_config.py"

# Create the wrapper script
echo "Creating wrapper script..."
cat > "$BUILD_DIR/start_server.py" << 'EOF'
#!/usr/bin/env python
"""
MCP Server Wrapper Script

This script ensures proper imports and starts the MCP server.
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path for imports
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

# Set environment variables
os.environ["AMM_DESIGN_PATH"] = str(current_dir / "design.json")
os.environ["AMM_BUILD_DIR"] = str(current_dir)

# Run the server
if __name__ == "__main__":
    import uvicorn
    import argparse
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="Run the AMM MCP Server")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind the server to")
    parser.add_argument("--api-key", type=str, help="API key for authentication (optional)")
    parser.add_argument("--api-key-required", action="store_true", help="Require API key for authentication")
    args = parser.parse_args()
    
    # Set environment variables based on arguments
    if args.api_key:
        os.environ["MCP_API_KEY"] = args.api_key
    
    if args.api_key_required:
        os.environ["API_KEY_REQUIRED"] = "true"
    
    print(f"Starting MCP server on {args.host}:{args.port}")
    print(f"Design path: {os.environ['AMM_DESIGN_PATH']}")
    print(f"Build directory: {os.environ['AMM_BUILD_DIR']}")
    
    # Import only after path setup
    from mcp_server import app
    
    # Run the server
    uvicorn.run(app, host=args.host, port=args.port)
EOF

# Make the wrapper script executable
chmod +x "$BUILD_DIR/start_server.py"

# Add usage documentation
cat > "$BUILD_DIR/README.md" << 'EOF'
# AMM MCP Server

This is a standalone MCP (Model Control Protocol) server build of an Adaptive Memory Module (AMM).

## Quick Start

To run the MCP server, use the `start_server.py` script:

```bash
python start_server.py --host 0.0.0.0 --port 8000
```

Command-line options:
- `--host`: The host address to bind to (default: 127.0.0.1, use 0.0.0.0 to accept connections from any IP)
- `--port`: The port to listen on (default: 8000)
- `--api-key`: Optional API key for authentication
- `--api-key-required`: Flag to require API key authentication

## Testing the Server

Once the server is running, you can test it with a simple health check:

```bash
curl -X GET http://localhost:8000/health
```

To send a query to the AMM:

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What can you tell me about this project?",
    "parameters": {},
    "context": {}
  }'
```

## API Endpoints

- `GET /health` - Health check endpoint
- `GET /info` - Get information about the AMM
- `POST /generate` - Generate a response from the AMM
EOF

echo "✅ MCP server build upgraded successfully!"
echo "To run the server, use: python $BUILD_DIR/start_server.py --host 0.0.0.0 --port 8000"