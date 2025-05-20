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
