#!/usr/bin/env python
"""
MCP Server CLI Manager

A command-line interface for managing MCP servers - finding, launching, and stopping them.
Provides a unified interface for all MCP server operations.
"""

import os
import sys
import argparse
import time
import subprocess
import signal
import logging
import json
import re
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mcp_cli")

# Import launch_mcp_server functions if available
try:
    from launch_mcp_server import find_mcp_builds, start_server
except ImportError:
    # Define them here if not available
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

# Running servers tracker - dictionary of PID -> server info
running_servers = {}

def list_servers(search_dirs=None, show_details=False):
    """List all available MCP server builds."""
    if search_dirs is None:
        search_dirs = [Path.cwd() / "build"]
        # Also check parent directories
        parent = Path.cwd().parent
        if "build" in os.listdir(parent):
            search_dirs.append(parent / "build")
    
    all_servers = []
    for search_dir in search_dirs:
        servers = find_mcp_builds(search_dir)
        all_servers.extend(servers)
    
    if not all_servers:
        print("No MCP server builds found.")
        return
    
    print(f"\n{len(all_servers)} MCP Server Builds Found:\n")
    for i, server in enumerate(all_servers):
        # Extract metadata if possible
        design_info = get_server_info(server)
        if design_info and show_details:
            print(f"{i+1}. {server.name} - {design_info.get('name', 'Unknown')}")
            print(f"   Path: {server}")
            print(f"   Description: {design_info.get('description', 'No description')}")
            capabilities = design_info.get('capabilities', {})
            print(f"   Capabilities:")
            print(f"     Fixed Knowledge: {'✓' if capabilities.get('fixed_knowledge', False) else '✗'}")
            print(f"     Adaptive Memory: {'✓' if capabilities.get('adaptive_memory', False) else '✗'}\n")
        else:
            print(f"{i+1}. {server.name} - {server}")
    
    return all_servers

def get_server_info(server_dir):
    """Get information about a server build by reading its design.json."""
    design_path = Path(server_dir) / "design.json"
    if not design_path.exists():
        return None
    
    try:
        with open(design_path, "r") as f:
            design = json.load(f)
        
        # Extract relevant information
        info = {
            "name": design.get("name", "Unknown"),
            "description": design.get("description", "No description"),
            "capabilities": {
                "fixed_knowledge": bool(design.get("knowledge_sources")),
                "adaptive_memory": design.get("adaptive_memory", {}).get("enabled", False)
            }
        }
        return info
    except Exception as e:
        logger.error(f"Error reading design.json: {e}")
        return None

def launch_server(server_dir, port=8000, host="0.0.0.0", api_key=None, api_key_required=False, wait=True):
    """Launch an MCP server and add it to the running servers list."""
    server_dir = Path(server_dir)
    if not server_dir.exists():
        print(f"Error: Server directory does not exist: {server_dir}")
        return None
    
    # Check if already running on this port
    for pid, info in running_servers.items():
        if info["port"] == port:
            print(f"Warning: A server is already running on port {port} (PID: {pid})")
            if input("Stop this server and start a new one? (y/n): ").lower() == 'y':
                stop_server(pid)
            else:
                return None
    
    # Start the server
    print(f"Starting MCP server from {server_dir.name}...")
    process = start_server(
        server_dir=server_dir,
        port=port,
        host=host,
        api_key=api_key,
        api_key_required=api_key_required
    )
    
    if process is None:
        print("Failed to start server. See logs for details.")
        return None
    
    # Store the server process
    running_servers[process.pid] = {
        "process": process,
        "dir": server_dir,
        "port": port,
        "host": host,
        "api_key": api_key,
        "api_key_required": api_key_required,
        "start_time": time.time(),
        "url": f"http://{host if host != '0.0.0.0' else 'localhost'}:{port}"
    }
    
    url = f"http://{host if host != '0.0.0.0' else 'localhost'}:{port}"
    print(f"Server started with PID {process.pid}")
    print(f"Server URL: {url}")
    
    # Test connection
    if wait:
        print("Testing connection...", end="", flush=True)
        max_retries = 5
        retry_count = 0
        while retry_count < max_retries:
            try:
                response = requests.get(f"{url}/health", timeout=1)
                if response.status_code == 200:
                    print(" ✓ Connected!")
                    # Get server info
                    try:
                        info_response = requests.get(f"{url}/info", timeout=1)
                        if info_response.status_code == 200:
                            info = info_response.json()
                            print(f"Server Name: {info.get('name', 'Unknown')}")
                            print(f"Description: {info.get('description', 'No description')}")
                        else:
                            print("Could not fetch server info.")
                    except Exception:
                        pass
                    break
                else:
                    print(".", end="", flush=True)
            except Exception:
                print(".", end="", flush=True)
            
            retry_count += 1
            time.sleep(1)
        
        if retry_count == max_retries:
            print(" ✗ Failed to connect! Server may still be starting...")
    
    return process.pid

def stop_server(pid):
    """Stop a running MCP server by PID."""
    if pid not in running_servers:
        print(f"No server found with PID {pid}")
        return False
    
    server_info = running_servers[pid]
    process = server_info["process"]
    
    if process.poll() is not None:
        # Process already terminated
        print(f"Server with PID {pid} is not running.")
        del running_servers[pid]
        return True
    
    print(f"Stopping server with PID {pid}...")
    try:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print("Server did not terminate gracefully, forcing...")
            process.kill()
        
        print(f"Server stopped: {pid}")
        del running_servers[pid]
        return True
    except Exception as e:
        print(f"Error stopping server: {e}")
        return False

def stop_all_servers():
    """Stop all running MCP servers."""
    if not running_servers:
        print("No running servers to stop.")
        return
    
    print(f"Stopping {len(running_servers)} servers...")
    failed = []
    
    # Get a copy of the keys to avoid dictionary size changing during iteration
    pids = list(running_servers.keys())
    for pid in pids:
        if not stop_server(pid):
            failed.append(pid)
    
    if failed:
        print(f"Failed to stop {len(failed)} servers: {failed}")
    else:
        print("All servers stopped successfully.")

def list_running_servers():
    """List all running MCP servers."""
    # Update status of all running servers
    to_remove = []
    for pid, info in running_servers.items():
        process = info["process"]
        if process.poll() is not None:
            to_remove.append(pid)
    
    # Remove any terminated servers
    for pid in to_remove:
        del running_servers[pid]
    
    if not running_servers:
        print("No running MCP servers.")
        return
    
    print("\nRunning MCP Servers:")
    for pid, info in running_servers.items():
        uptime = int(time.time() - info["start_time"])
        url = info["url"]
        print(f" - PID {pid}: {info['dir'].name}")
        print(f"   URL: {url}")
        print(f"   Uptime: {uptime} seconds")
        
        # Check status
        try:
            response = requests.get(f"{url}/health", timeout=1)
            if response.status_code == 200:
                print(f"   Status: ✓ Running")
            else:
                print(f"   Status: ! Unhealthy (Status {response.status_code})")
        except Exception:
            print(f"   Status: ? Not responding")
        
        print()

def test_server_connection(url=None, pid=None):
    """Test connection to a running MCP server."""
    if pid is not None:
        if pid not in running_servers:
            print(f"No server found with PID {pid}")
            return False
        url = running_servers[pid]["url"]
    
    if url is None:
        print("Error: No URL or PID provided.")
        return False
    
    print(f"Testing connection to MCP server at {url}...")
    
    try:
        # Health check
        health_response = requests.get(f"{url}/health", timeout=5)
        if health_response.status_code == 200:
            print("✓ Health check: OK")
            health_data = health_response.json()
            print(f"  Status: {health_data.get('status', 'Unknown')}")
            print(f"  Timestamp: {health_data.get('timestamp', 'Unknown')}")
        else:
            print(f"✗ Health check failed: {health_response.status_code}")
            return False
        
        # Info check
        info_response = requests.get(f"{url}/info", timeout=5)
        if info_response.status_code == 200:
            print("✓ Info check: OK")
            info_data = info_response.json()
            print("\nServer Information:")
            print(f"  Name: {info_data.get('name', 'Unknown')}")
            print(f"  Description: {info_data.get('description', 'No description')}")
            print(f"  Version: {info_data.get('version', 'Unknown')}")
            
            capabilities = info_data.get('capabilities', {})
            print("\nCapabilities:")
            for name, enabled in capabilities.items():
                print(f"  {name}: {'✓' if enabled else '✗'}")
        else:
            print(f"✗ Info check failed: {info_response.status_code}")
        
        # Example query
        print("\nSending test query...")
        query_response = requests.post(
            f"{url}/generate",
            json={
                "query": "Hello, what's your purpose?",
                "parameters": {},
                "context": {}
            },
            timeout=10
        )
        
        if query_response.status_code == 200:
            print("✓ Query test: OK")
            result = query_response.json()
            print("\nQuery Response:")
            print(f"{result.get('response', 'No response')}\n")
        else:
            print(f"✗ Query test failed: {query_response.status_code}")
        
        return True
    except Exception as e:
        print(f"✗ Connection test failed: {e}")
        return False

def run_interactive_mode():
    """Run an interactive CLI for managing MCP servers."""
    print("\n=== MCP Server Management CLI ===\n")
    
    while True:
        print("\nAvailable commands:")
        print("  1. List available MCP servers")
        print("  2. List running servers")
        print("  3. Launch a server")
        print("  4. Stop a server")
        print("  5. Stop all servers")
        print("  6. Test a server")
        print("  7. Fix imports in a server build")
        print("  8. Exit")
        
        choice = input("\nEnter your choice (1-8): ")
        
        if choice == '1':
            # List servers
            all_servers = list_servers(show_details=True)
        
        elif choice == '2':
            # List running servers
            list_running_servers()
        
        elif choice == '3':
            # Launch a server
            all_servers = list_servers()
            if not all_servers:
                continue
            
            try:
                idx = int(input("\nEnter server number to launch: ")) - 1
                if 0 <= idx < len(all_servers):
                    server_dir = all_servers[idx]
                    port = int(input("Enter port (default: 8000): ") or "8000")
                    host = input("Enter host (default: 0.0.0.0): ") or "0.0.0.0"
                    api_key_required = input("Require API key? (y/n, default: n): ").lower() == 'y'
                    
                    api_key = None
                    if api_key_required:
                        api_key = input("Enter API key (leave empty to generate): ")
                        if not api_key:
                            import uuid
                            api_key = str(uuid.uuid4())
                            print(f"Generated API key: {api_key}")
                    
                    launch_server(server_dir, port, host, api_key, api_key_required)
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Invalid input.")
        
        elif choice == '4':
            # Stop a server
            list_running_servers()
            if not running_servers:
                continue
            
            try:
                pid = int(input("\nEnter PID of server to stop: "))
                stop_server(pid)
            except ValueError:
                print("Invalid PID.")
        
        elif choice == '5':
            # Stop all servers
            stop_all_servers()
        
        elif choice == '6':
            # Test a server
            if running_servers:
                list_running_servers()
                try:
                    pid = int(input("\nEnter PID of server to test (or 0 for custom URL): "))
                    if pid == 0:
                        url = input("Enter server URL: ")
                        test_server_connection(url=url)
                    else:
                        test_server_connection(pid=pid)
                except ValueError:
                    print("Invalid PID.")
            else:
                url = input("Enter server URL to test: ")
                test_server_connection(url=url)
        
        elif choice == '7':
            # Fix imports
            all_servers = list_servers()
            if not all_servers:
                continue
            
            try:
                idx = int(input("\nEnter server number to fix imports: ")) - 1
                if 0 <= idx < len(all_servers):
                    server_dir = all_servers[idx]
                    print(f"Fixing imports in {server_dir}...")
                    
                    # Use fix_imports.py if available
                    fix_script = Path(__file__).parent / "fix_imports.py"
                    if fix_script.exists():
                        subprocess.run([sys.executable, str(fix_script), str(server_dir)])
                    else:
                        print("fix_imports.py not found. Please run it manually.")
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Invalid input.")
        
        elif choice == '8':
            # Exit
            if running_servers:
                stop = input("There are still running servers. Stop them before exiting? (y/n): ")
                if stop.lower() == 'y':
                    stop_all_servers()
            
            print("Exiting...")
            break
        
        else:
            print("Invalid choice. Please try again.")

def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="MCP Server CLI")
    parser.add_argument("--list", action="store_true", help="List available MCP server builds")
    parser.add_argument("--running", action="store_true", help="List running MCP servers")
    parser.add_argument("--launch", metavar="PATH", help="Launch an MCP server from the given path")
    parser.add_argument("--stop", metavar="PID", type=int, help="Stop a running MCP server by PID")
    parser.add_argument("--stop-all", action="store_true", help="Stop all running MCP servers")
    parser.add_argument("--test", metavar="URL", help="Test connection to an MCP server")
    parser.add_argument("--fix", metavar="PATH", help="Fix imports in an MCP server build")
    parser.add_argument("--port", type=int, default=8000, help="Port to use when launching a server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to use when launching a server")
    parser.add_argument("--api-key", help="API key for authentication")
    parser.add_argument("--api-key-required", action="store_true", help="Require API key authentication")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    # No arguments provided, run interactive mode
    if len(sys.argv) == 1:
        run_interactive_mode()
        return
    
    # Process the command line arguments
    if args.interactive:
        run_interactive_mode()
    elif args.list:
        list_servers(show_details=True)
    elif args.running:
        list_running_servers()
    elif args.launch:
        launch_server(
            server_dir=args.launch,
            port=args.port,
            host=args.host,
            api_key=args.api_key,
            api_key_required=args.api_key_required
        )
    elif args.stop:
        stop_server(args.stop)
    elif args.stop_all:
        stop_all_servers()
    elif args.test:
        test_server_connection(url=args.test)
    elif args.fix:
        # Use fix_imports.py if available
        fix_script = Path(__file__).parent / "fix_imports.py"
        if fix_script.exists():
            subprocess.run([sys.executable, str(fix_script), args.fix])
        else:
            print("fix_imports.py not found. Please run it manually.")

if __name__ == "__main__":
    main()