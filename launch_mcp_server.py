#!/usr/bin/env python
"""
MCP Server Launcher Script

This script helps launch an MCP server for testing purposes.
It provides a simple command-line interface to start a server
from a built MCP server package.
"""

import os
import sys
import argparse
import subprocess
import time
import signal
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mcp_launcher")

def find_mcp_builds(search_dir=None):
    """Find all MCP server builds in the given directory."""
    if search_dir is None:
        search_dir = Path.cwd() / "build"
    
    search_dir = Path(search_dir)
    if not search_dir.exists():
        return []
    
    # Look for directories containing start_server.py
    mcp_builds = []
    for path in search_dir.glob("**/start_server.py"):
        mcp_builds.append(path.parent)
    
    return sorted(mcp_builds)

def start_server(server_dir, port=8000, host="0.0.0.0", api_key=None, api_key_required=False):
    """Start an MCP server from the given directory."""
    server_dir = Path(server_dir)
    if not server_dir.exists():
        logger.error(f"Server directory does not exist: {server_dir}")
        return None
    
    # Check for start_server.py script
    start_script = server_dir / "start_server.py"
    if not start_script.exists():
        logger.error(f"start_server.py not found in {server_dir}")
        return None
    
    # Build command
    cmd = [sys.executable, str(start_script), "--port", str(port), "--host", host]
    if api_key_required and api_key:
        cmd.extend(["--api-key", api_key, "--api-key-required"])
    elif api_key_required:
        cmd.append("--api-key-required")
    elif api_key:
        cmd.extend(["--api-key", api_key])
    
    # Start server process
    logger.info(f"Starting MCP server from {server_dir} on {host}:{port}")
    
    try:
        process = subprocess.Popen(
            cmd,
            cwd=server_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment for the server to start
        time.sleep(2)
        
        if process.poll() is not None:
            # Process has already terminated
            returncode = process.poll()
            stdout, stderr = process.communicate()
            logger.error(f"Server failed to start (exit code {returncode})")
            logger.error(f"stdout: {stdout}")
            logger.error(f"stderr: {stderr}")
            return None
        
        logger.info(f"Server started with PID {process.pid}")
        return process
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        return None

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Launch an MCP server for testing")
    parser.add_argument("--dir", help="Path to MCP server build directory")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument("--api-key", help="API key for authentication")
    parser.add_argument("--api-key-required", action="store_true", help="Require API key authentication")
    parser.add_argument("--list", action="store_true", help="List available MCP server builds")
    args = parser.parse_args()
    
    # List available builds if requested
    if args.list:
        builds = find_mcp_builds()
        if not builds:
            print("No MCP server builds found.")
            return
        
        print("Available MCP server builds:")
        for i, build in enumerate(builds):
            print(f"{i+1}. {build}")
        
        # Prompt user to select a build
        try:
            selection = input("Enter build number to launch (or q to quit): ")
            if selection.lower() == 'q':
                return
            
            selection = int(selection) - 1
            if 0 <= selection < len(builds):
                args.dir = builds[selection]
            else:
                print("Invalid selection.")
                return
        except (ValueError, IndexError):
            print("Invalid selection.")
            return
    
    # If no directory specified and not listing, search for builds
    if args.dir is None:
        builds = find_mcp_builds()
        if not builds:
            print("No MCP server builds found. Please specify a build directory.")
            return
        
        # Use the most recent build
        args.dir = builds[0]
        print(f"Using most recent MCP server build: {args.dir}")
    
    # Start the server
    server_process = start_server(
        server_dir=args.dir,
        port=args.port,
        host=args.host,
        api_key=args.api_key,
        api_key_required=args.api_key_required
    )
    
    if server_process is None:
        print("Failed to start server. See logs for details.")
        return
    
    print(f"MCP server running at http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop the server...")
    
    try:
        # Monitor server process
        while server_process.poll() is None:
            time.sleep(1)
        
        # Server process terminated
        returncode = server_process.poll()
        stdout, stderr = server_process.communicate()
        logger.error(f"Server terminated unexpectedly (exit code {returncode})")
        logger.error(f"stdout: {stdout}")
        logger.error(f"stderr: {stderr}")
    except KeyboardInterrupt:
        print("\nStopping server...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print("Server did not terminate gracefully, forcing...")
            server_process.kill()
    
    print("Server stopped.")

if __name__ == "__main__":
    main()