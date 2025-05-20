"""
MCP Server Manager Component
---------------------------
Component for managing MCP server instances from the GUI
"""
import os
import sys
import time
import streamlit as st
import subprocess
import requests
from pathlib import Path
import logging
import threading
import json
from typing import Optional, Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mcp_server_manager")

# Add project root to path to access our modules
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Try to import from either CLI or direct modules
try:
    # First try to use the CLI functions
    from mcp_cli import find_mcp_builds, start_server, get_server_info, test_server_connection
    logger.info("Using mcp_cli module for server management")
except ImportError:
    try:
        # Fall back to launch_mcp_server 
        from launch_mcp_server import find_mcp_builds, start_server
        logger.info("Using launch_mcp_server module")
        
        # Define missing functions
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
        
        def test_server_connection(url):
            """Test connection to an MCP server."""
            try:
                # Health check
                response = requests.get(f"{url}/health", timeout=5)
                if response.status_code == 200:
                    return {"success": True, "health": response.json()}
                return {"success": False, "error": f"Health check failed: {response.status_code}"}
            except Exception as e:
                return {"success": False, "error": str(e)}
    except ImportError:
        logger.error("Could not import launch_mcp_server or mcp_cli modules")
        
        # Define stub functions to avoid errors
        def find_mcp_builds(search_dir=None):
            logger.error("find_mcp_builds not available")
            return []
            
        def start_server(*args, **kwargs):
            logger.error("start_server not available")
            return None
            
        def get_server_info(server_dir):
            logger.error("get_server_info not available")
            return None
            
        def test_server_connection(url):
            logger.error("test_server_connection not available")
            return {"success": False, "error": "Function not available"}

# Dict to store running server processes
if "mcp_servers" not in st.session_state:
    st.session_state.mcp_servers = {}

def find_available_servers() -> List[Path]:
    """Find available MCP server builds."""
    try:
        # Define search directories
        project_root = Path(__file__).parent.parent.parent
        search_dirs = [
            project_root / "build",  # Main build directory
            project_root  # Project root for custom builds
        ]
        
        # Look for any directories with start_server.py
        servers = []
        for search_dir in search_dirs:
            if search_dir.exists():
                # Use find_mcp_builds for standard locations
                found_servers = find_mcp_builds(search_dir)
                for server in found_servers:
                    if server not in servers:
                        servers.append(server)
        
        # Special case: check if we're in an MCP build directory now
        current_dir = Path.cwd()
        start_script = current_dir / "start_server.py"
        if start_script.exists() and current_dir not in servers:
            servers.append(current_dir)
        
        return servers
    except Exception as e:
        logger.error(f"Error finding MCP servers: {e}")
        return []

def get_server_status(server_id: str) -> Dict[str, Any]:
    """Get the status of a server by its ID."""
    if server_id not in st.session_state.mcp_servers:
        return {
            "running": False,
            "url": None,
            "pid": None,
            "start_time": None
        }
    
    server_info = st.session_state.mcp_servers[server_id]
    process = server_info.get("process")
    
    if process is None:
        return {
            "running": False,
            "url": None,
            "pid": None,
            "start_time": None
        }
    
    # Check if process is still running
    is_running = process.poll() is None
    
    if not is_running:
        # Process has stopped, clean up
        st.session_state.mcp_servers[server_id]["process"] = None
        st.session_state.mcp_servers[server_id]["running"] = False
    
    return {
        "running": is_running,
        "url": server_info.get("url"),
        "pid": process.pid if is_running else None,
        "start_time": server_info.get("start_time")
    }

def launch_mcp_server(server_dir: Path, port: int = 8000, host: str = "0.0.0.0",
                      api_key: Optional[str] = None, api_key_required: bool = False) -> Dict[str, Any]:
    """Launch an MCP server and return its information."""
    try:
        server_id = str(server_dir.absolute())
        
        # Check if server is already running
        status = get_server_status(server_id)
        if status["running"]:
            return {
                "success": True,
                "message": f"Server already running at {status['url']}",
                "server_id": server_id,
                "url": status["url"]
            }
        
        # Start the server
        process = start_server(
            server_dir=server_dir,
            port=port,
            host=host,
            api_key=api_key,
            api_key_required=api_key_required
        )
        
        if process is None:
            return {
                "success": False,
                "message": "Failed to start server. See logs for details.",
                "server_id": server_id,
                "url": None
            }
        
        # Store server process
        st.session_state.mcp_servers[server_id] = {
            "process": process,
            "url": f"http://{host if host != '0.0.0.0' else 'localhost'}:{port}",
            "host": host,
            "port": port,
            "api_key": api_key,
            "api_key_required": api_key_required,
            "dir": server_dir,
            "running": True,
            "start_time": time.time()
        }
        
        return {
            "success": True,
            "message": f"Server started at http://{host if host != '0.0.0.0' else 'localhost'}:{port}",
            "server_id": server_id,
            "url": f"http://{host if host != '0.0.0.0' else 'localhost'}:{port}"
        }
    except Exception as e:
        logger.error(f"Error launching MCP server: {e}")
        return {
            "success": False,
            "message": f"Error launching server: {str(e)}",
            "server_id": server_id if 'server_id' in locals() else None,
            "url": None
        }

def stop_mcp_server(server_id: str) -> Dict[str, Any]:
    """Stop a running MCP server."""
    if server_id not in st.session_state.mcp_servers:
        return {
            "success": False,
            "message": "Server not found"
        }
    
    server_info = st.session_state.mcp_servers[server_id]
    process = server_info.get("process")
    
    if process is None or process.poll() is not None:
        # Process is not running
        st.session_state.mcp_servers[server_id]["running"] = False
        return {
            "success": True,
            "message": "Server was not running"
        }
    
    try:
        # Terminate the process
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        
        st.session_state.mcp_servers[server_id]["running"] = False
        st.session_state.mcp_servers[server_id]["process"] = None
        
        return {
            "success": True,
            "message": "Server stopped"
        }
    except Exception as e:
        logger.error(f"Error stopping MCP server: {e}")
        return {
            "success": False,
            "message": f"Error stopping server: {str(e)}"
        }

def mcp_server_manager():
    """MCP Server Manager UI component."""
    st.subheader("MCP Server Manager", help="Manage MCP server instances")
    
    # Find available servers
    if st.button("🔄 Refresh Server List", help="Refresh the list of available MCP servers"):
        st.session_state.refresh_servers = True
        st.success("Server list refreshed!")
    
    available_servers = find_available_servers()
    
    if not available_servers:
        st.warning("No MCP server builds found. Build an AMM with the MCP server build type first.")
        return None
    
    # Server selection with more info
    server_paths = {str(s): s for s in available_servers}
    selected_server = st.selectbox(
        "Select MCP Server",
        options=list(server_paths.keys()),
        format_func=lambda x: Path(x).name,
        help="Select a built MCP server to launch"
    )
    
    # Show server details if available
    server_info = get_server_info(server_paths[selected_server])
    if server_info:
        with st.expander("Server Details", expanded=False):
            st.write(f"**Name:** {server_info.get('name', 'Unknown')}")
            st.write(f"**Description:** {server_info.get('description', 'No description')}")
            capabilities = server_info.get('capabilities', {})
            st.write("**Capabilities:**")
            st.write(f"- Fixed Knowledge: {'✓' if capabilities.get('fixed_knowledge', False) else '✗'}")
            st.write(f"- Adaptive Memory: {'✓' if capabilities.get('adaptive_memory', False) else '✗'}")
            
            # Fix imports button
            fix_imports_script = Path(__file__).parent.parent.parent / "fix_imports.py"
            if fix_imports_script.exists():
                if st.button("Fix Imports", help="Fix any import issues in this MCP server build"):
                    with st.spinner("Fixing imports..."):
                        result = subprocess.run(
                            [sys.executable, str(fix_imports_script), str(server_paths[selected_server])],
                            capture_output=True,
                            text=True
                        )
                        if result.returncode == 0:
                            st.success("Imports fixed successfully!")
                        else:
                            st.error(f"Error fixing imports: {result.stderr}")
                            st.code(result.stdout)
    
    # Server configuration
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        server_host = st.text_input("Host", value="0.0.0.0", help="Host to bind the server to")
    
    with col2:
        server_port = st.number_input("Port", value=8000, min_value=1, max_value=65535, help="Port to run the server on")
    
    with col3:
        api_key_required = st.checkbox("Require API Key", value=False, help="Require API key authentication")
    
    if api_key_required:
        api_key = st.text_input("API Key", type="password", help="API key for authentication (leave blank to generate)")
        if not api_key:
            import uuid
            api_key = str(uuid.uuid4())
            st.info(f"Generated API key: {api_key}")
    else:
        api_key = None
    
    # Server control buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Launch Server", type="primary"):
            with st.spinner("Starting MCP server..."):
                result = launch_mcp_server(
                    server_dir=server_paths[selected_server],
                    port=server_port,
                    host=server_host,
                    api_key=api_key,
                    api_key_required=api_key_required
                )
                
                if result["success"]:
                    st.success(result["message"])
                    st.session_state.selected_server_id = result["server_id"]
                    st.session_state.selected_server_url = result["url"]
                else:
                    st.error(result["message"])
    
    # Only show stop button if we have a selected server
    with col2:
        if "selected_server_id" in st.session_state:
            server_id = st.session_state.selected_server_id
            status = get_server_status(server_id)
            
            if status["running"]:
                if st.button("Stop Server", type="secondary"):
                    with st.spinner("Stopping MCP server..."):
                        result = stop_mcp_server(server_id)
                        
                        if result["success"]:
                            st.success(result["message"])
                        else:
                            st.error(result["message"])
            else:
                st.button("Stop Server", type="secondary", disabled=True)
    
    # Running servers section
    st.subheader("Running Servers")
    
    # Check all servers
    running_servers = []
    for server_id, server_info in st.session_state.mcp_servers.items():
        status = get_server_status(server_id)
        if status["running"]:
            running_servers.append({
                "id": server_id,
                "name": Path(server_id).name,
                "url": server_info.get("url"),
                "uptime": time.time() - server_info.get("start_time", time.time()),
                "port": server_info.get("port", 8000),
                "host": server_info.get("host", "0.0.0.0")
            })
    
    if running_servers:
        # Add a "Stop All Servers" button
        if st.button("🛑 Stop All Servers", type="secondary"):
            with st.spinner("Stopping all servers..."):
                for server in running_servers:
                    stop_mcp_server(server['id'])
                st.success("All servers stopped!")
                st.rerun()
        
        for server in running_servers:
            with st.expander(f"{server['name']} - {server['url']}", expanded=True):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Server info
                    st.write(f"**Server:** {Path(server['id']).name}")
                    st.write(f"**URL:** {server['url']}")
                    st.write(f"**Uptime:** {int(server['uptime'])} seconds")
                    
                    # Show connection status
                    test_button_key = f"test_connection_{server['id']}"
                    if st.button(f"Test Connection", key=test_button_key):
                        with st.spinner("Testing connection..."):
                            test_result = test_server_connection(server['url'])
                            if test_result.get("success", False):
                                st.success("✓ Connection successful!")
                                if "health" in test_result:
                                    st.json(test_result["health"])
                            else:
                                st.error(f"✗ Connection failed: {test_result.get('error', 'Unknown error')}")
                
                with col2:
                    # Server actions
                    if st.button(f"Open URL", key=f"open_{server['id']}"):
                        import webbrowser
                        webbrowser.open(server['url'])
                    
                    if st.button(f"Stop Server", key=f"stop_{server['id']}", type="secondary"):
                        with st.spinner(f"Stopping {server['name']}..."):
                            result = stop_mcp_server(server['id'])
                            if result["success"]:
                                st.success(result["message"])
                                time.sleep(1)  # Brief pause
                                st.rerun()
                            else:
                                st.error(result["message"])
                
                # API endpoints section
                st.write("**API Endpoints:**")
                endpoint_cols = st.columns(3)
                with endpoint_cols[0]:
                    st.markdown(f"🔗 [Health Check]({server['url']}/health)")
                with endpoint_cols[1]:
                    st.markdown(f"🔗 [Server Info]({server['url']}/info)")
                with endpoint_cols[2]:
                    st.markdown(f"🔗 [Generate API]({server['url']}/docs)")
                
                # Test query section
                with st.form(key=f"query_form_{server['id']}"):
                    st.subheader("Test Query")
                    test_query = st.text_area("Enter a query to test:", value="Hello, what can you tell me about yourself?")
                    send_query = st.form_submit_button("Send Query")
                    
                    if send_query:
                        with st.spinner("Processing query..."):
                            try:
                                import requests
                                
                                # Get server details for API key
                                server_details = st.session_state.mcp_servers.get(server['id'])
                                headers = {}
                                if server_details and server_details.get("api_key_required") and server_details.get("api_key"):
                                    headers = {"X-API-Key": server_details["api_key"]}
                                
                                response = requests.post(
                                    f"{server['url']}/generate",
                                    json={
                                        "query": test_query,
                                        "parameters": {},
                                        "context": {}
                                    },
                                    headers=headers,
                                    timeout=30
                                )
                                
                                if response.status_code == 200:
                                    result = response.json()
                                    st.write("**Response:**")
                                    st.write(result.get("response", "No response"))
                                    
                                    # Show metadata if present
                                    metadata = result.get("metadata", {})
                                    if metadata:
                                        with st.expander("Response Metadata"):
                                            st.json(metadata)
                                else:
                                    st.error(f"Error from MCP server: Status code {response.status_code}")
                            except Exception as e:
                                st.error(f"Error querying MCP server: {str(e)}")
    else:
        st.info("No running MCP servers.")
        
        # Show CLI option when no servers are running
        st.write("""
        You can also manage servers from the command line:
        ```bash
        python mcp_cli.py --interactive
        ```
        """)
    
    # Information section
    with st.expander("Troubleshooting & Information"):
        st.markdown("""
        ### MCP Server Information
        
        The Model Control Protocol (MCP) server allows applications to connect to your AMM over HTTP.
        
        **Common issues:**
        - **Connection refused**: Check that the server is running and the port is correct
        - **API key errors**: Ensure you're including the API key in requests if required
        - **Server not starting**: Check the logs for errors
        
        **API Endpoints:**
        - `GET /health` - Check if the server is running
        - `GET /info` - Get information about the AMM
        - `POST /generate` - Generate a response from the AMM
        
        **Example request:**
        ```python
        import requests
        
        response = requests.post(
            "http://localhost:8000/generate",
            json={
                "query": "What can you tell me about AI?",
                "parameters": {},
                "context": {}
            }
        )
        
        result = response.json()
        print(result["response"])
        ```
        """)
    
    # Return the current server URL if one is running
    if "selected_server_url" in st.session_state and running_servers:
        return st.session_state.selected_server_url
    
    return None