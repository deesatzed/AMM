# MCP Server CLI Guide

The MCP Server CLI (`mcp_cli.py`) provides a comprehensive command-line interface for managing MCP servers, including finding, launching, stopping, and testing servers.

## Quick Start

### Interactive Mode

The easiest way to use the CLI is in interactive mode:

```bash
# Launch interactive mode
python mcp_cli.py
```

This provides a menu-driven interface where you can:
- List available MCP servers
- List running servers
- Launch a server
- Stop a server
- Test a server connection
- Fix import issues in server builds

### Command Line Usage

You can also use direct commands:

```bash
# List available MCP servers
python mcp_cli.py --list

# Launch a specific server
python mcp_cli.py --launch /path/to/server --port 8000

# Stop a specific server by PID
python mcp_cli.py --stop 12345

# Stop all running servers
python mcp_cli.py --stop-all

# Test connection to a server
python mcp_cli.py --test http://localhost:8000

# Fix imports in a server build
python mcp_cli.py --fix /path/to/server
```

## Command Reference

### List Servers

```bash
python mcp_cli.py --list
```

Lists all available MCP server builds, showing:
- Directory locations
- Server names and descriptions
- Capabilities (fixed knowledge, adaptive memory)

### List Running Servers

```bash
python mcp_cli.py --running
```

Lists all currently running MCP servers, showing:
- PID (Process ID)
- URL
- Uptime
- Server status

### Launch a Server

```bash
python mcp_cli.py --launch /path/to/server [options]
```

Options:
- `--port PORT`: Port to run the server on (default: 8000)
- `--host HOST`: Host to bind to (default: 0.0.0.0)
- `--api-key KEY`: API key for authentication
- `--api-key-required`: Require API key authentication

### Stop a Server

```bash
# Stop by PID
python mcp_cli.py --stop PID

# Stop all running servers
python mcp_cli.py --stop-all
```

### Test a Server

```bash
python mcp_cli.py --test URL
```

Tests connection to a server by:
- Checking the health endpoint
- Retrieving server information
- Sending a test query

### Fix Imports

```bash
python mcp_cli.py --fix /path/to/server
```

Fixes import issues in an MCP server build by running `fix_imports.py`.

## Integration with Other Tools

The MCP CLI works seamlessly with:

1. **AMM GUI**: The GUI's MCP Server Manager uses the CLI functions
2. **fix_imports.py**: Automatically fixes import issues in server builds
3. **Launch Scripts**: Works alongside `start_mcp.sh` and other launch helpers

## Example Workflows

### Building and Testing a Server

```bash
# Build the server
python build_amm.py designs/my_design.json --output-dir build --build-type mcp_server

# Fix imports if needed
python mcp_cli.py --fix build/my_amm

# Launch the server
python mcp_cli.py --launch build/my_amm

# Test the server
python mcp_cli.py --test http://localhost:8000
```

### Managing Multiple Servers

The CLI makes it easy to manage multiple servers:

1. Launch the interactive mode: `python mcp_cli.py`
2. Select option 1 to list available servers
3. Select option 3 to launch a server (repeating for multiple servers)
4. Use option 2 to see all running servers
5. Use option 6 to test any server

## Troubleshooting

If you encounter issues:

1. **Server won't start**: 
   - Check for port conflicts
   - Try fixing imports with `--fix`
   - Examine server logs

2. **Connection failures**:
   - Verify the server is running (`--running`)
   - Check the host and port are correct
   - Test with cURL: `curl http://localhost:8000/health`

3. **Import errors**:
   - Run the import fix: `--fix /path/to/server`
   - Make sure all required modules are in the build directory

## Advanced Usage

### Custom API Keys

For secure deployments, you can use API key authentication:

```bash
# Generate a random API key
APIKEY=$(python -c "import uuid; print(uuid.uuid4())")

# Launch with API key
python mcp_cli.py --launch /path/to/server --api-key $APIKEY --api-key-required
```

### Server Monitoring

You can set up monitoring scripts using the CLI:

```bash
# Check if servers are running
python mcp_cli.py --running > server_status.log

# Check server health
python mcp_cli.py --test http://localhost:8000 > health_check.log
```