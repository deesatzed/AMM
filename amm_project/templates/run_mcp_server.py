#!/usr/bin/env python
"""
Run script for the AMM MCP Server.
This script starts the MCP server with the appropriate configuration.
"""

import os
import sys
from pathlib import Path

# Set environment variables for the MCP server
current_dir = Path(__file__).parent.absolute()
os.environ["AMM_DESIGN_PATH"] = str(current_dir / "design.json")
os.environ["AMM_BUILD_DIR"] = str(current_dir)

# Import the MCP server app
import uvicorn

def print_help():
    """Print help information."""
    print("AMM MCP Server")
    print("Usage: python run_mcp_server.py [options]")
    print("")
    print("Options:")
    print("  --port PORT         Port to run the server on (default: 8000)")
    print("  --host HOST         Host to bind the server to (default: 127.0.0.1)")
    print("  --api-key KEY       API key for authentication")
    print("  --api-key-required  Require API key for authentication")
    print("  --help              Show this help message")
    print("")
    print("Environment variables:")
    print("  MCP_PORT            Port to run the server on")
    print("  MCP_HOST            Host to bind the server to")
    print("  MCP_API_KEY         API key for authentication")
    print("  API_KEY_REQUIRED    Set to 'true' to require API key")
    print("")
    print("Examples:")
    print("  python run_mcp_server.py --port 8080 --host 0.0.0.0")
    print("  python run_mcp_server.py --api-key my-secret-key --api-key-required")
    sys.exit(0)

if __name__ == "__main__":
    import argparse
    import socket
    
    parser = argparse.ArgumentParser(description="Run AMM MCP Server")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind the server to")
    parser.add_argument("--api-key", type=str, help="API key for authentication (optional)")
    parser.add_argument("--api-key-required", action="store_true", help="Require API key for authentication")
    args = parser.parse_args()
    
    # Set environment variables based on arguments
    port = args.port or int(os.environ.get("MCP_PORT", "8000"))
    host = args.host or os.environ.get("MCP_HOST", "127.0.0.1")
    
    if args.api_key:
        os.environ["MCP_API_KEY"] = args.api_key
    
    if args.api_key_required:
        os.environ["API_KEY_REQUIRED"] = "true"
    
    # Check if port is already in use
    def is_port_in_use(port, host='127.0.0.1'):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, port))
                return False
            except socket.error:
                return True
    
    # Find an available port if the specified one is in use
    original_port = port
    max_attempts = 10
    attempt = 0
    
    while is_port_in_use(port, host) and attempt < max_attempts:
        port += 1
        attempt += 1
    
    if attempt > 0:
        if attempt >= max_attempts:
            print(f"ERROR: Could not find an available port after {max_attempts} attempts.")
            sys.exit(1)
        else:
            print(f"Port {original_port} is already in use. Using port {port} instead.")
    
    # Print startup information
    print(f"Starting AMM MCP Server on {host}:{port}")
    print(f"Design: {os.environ['AMM_DESIGN_PATH']}")
    print(f"Build directory: {os.environ['AMM_BUILD_DIR']}")
    if os.environ.get("API_KEY_REQUIRED", "").lower() == "true":
        print("API key authentication is enabled")
    
    # Start the server
    try:
        uvicorn.run("mcp_server:app", host=host, port=port, reload=False)
    except Exception as e:
        print(f"ERROR: Failed to start server: {e}")
        sys.exit(1)
