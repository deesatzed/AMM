# MCP Server Connection Fix

## Connection Issues Fixed

We've resolved the "Connection refused" error when connecting to MCP servers from the GUI by fixing the default host binding in the `start_server.py` script.

### Problem

The original script was binding the server to `127.0.0.1` (localhost only), which meant:
- The server was only accessible from the local machine
- Even on the local machine, the host had to match exactly (`127.0.0.1` vs. `localhost`)

### Solution

We've updated the default host binding to `0.0.0.0`, which:
- Makes the server accessible from any network interface
- Works correctly whether you connect via `localhost` or an IP address

## Updated Files

1. **fix_mcp_build.py**
   - Updated the wrapper script template to use `0.0.0.0` as the default host instead of `127.0.0.1`

2. **Existing Built MCP Servers**
   - Updated `start_server.py` to use `0.0.0.0` as the default host

3. **Added start_mcp.sh**
   - Created a simple script that finds and launches the most recently built MCP server
   - Automatically binds to `0.0.0.0` and uses port 8000 by default

## Using the MCP Server

### Option 1: Using start_mcp.sh

The easiest way to start an MCP server is with the new script:

```bash
# Start the server on default port 8000
./start_mcp.sh

# Start the server on a specific port
./start_mcp.sh 8080
```

### Option 2: Using the GUI

You can also use the MCP Server Manager in the GUI Test tab:

1. Go to the Test tab
2. Select "MCP Server Test" mode
3. Under "MCP Server Controls", select your server and click "Launch Server"

### Option 3: Direct Command

To start a specific MCP server directly:

```bash
cd /path/to/your/mcp/server
python start_server.py --port 8000 --host 0.0.0.0
```

## Verifying the Connection

Once the server is running, you can verify the connection:

```bash
# Check health endpoint
curl http://localhost:8000/health

# Get server info
curl http://localhost:8000/info
```

Or use the "Test Connection" button in the GUI's MCP Server Test mode.

## Build Output Review

The build process output you reviewed looks correct and indicates a successful build:

1. Both Python App and MCP Server builds completed successfully
2. All knowledge files were copied correctly
3. All necessary modules were included for standalone operation
4. The wrapper script was created correctly

The built servers are located at:
```
/home/o2satz/MyGit/AFTER_CRASH/May19_AMM/build/amm-prod-bld-20250519/build_news_briefing_agent/news_briefing_agent
```