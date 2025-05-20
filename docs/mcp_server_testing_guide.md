# MCP Server Testing Guide

This guide explains how to test MCP servers using the AMM Design Studio GUI and the new MCP Server Manager component.

## MCP Server Management

The AMM GUI now includes a dedicated MCP Server Manager that helps you:

1. Launch MCP servers directly from the GUI
2. Monitor running server status
3. Stop servers when needed
4. Test connection and send queries

## Testing Workflow

### Option 1: Launch and Test from the GUI

1. **Build an MCP Server**
   - In the GUI, navigate to the "Build" tab
   - Select "MCP Server" as the build type
   - Configure options and build your AMM

2. **Launch the Server**
   - Go to the "Test" tab
   - Select "MCP Server Test" mode
   - Use the "MCP Server Controls" expander
   - Select your server build from the dropdown
   - Configure host/port settings
   - Click "Launch Server"

3. **Test the Server**
   - Once the server is running, click "Test Connection"
   - If successful, you can start sending queries in the chat interface

### Option 2: Connect to an Existing Server

If you have already launched an MCP server outside the GUI:

1. **Go to Test Mode**
   - Navigate to the "Test" tab
   - Select "MCP Server Test" mode

2. **Enter Server Details**
   - Enter the host and port of your running server
   - Click "Test Connection"
   - Start sending queries

## Troubleshooting

### Common Issues

- **Connection Refused**
  - Make sure the server is running
  - Check that the port is correct
  - Verify no firewall is blocking the connection

- **Server Won't Start**
  - Check the logs for error messages
  - Make sure another process isn't using the port

- **API Key Authentication**
  - If using API key authentication, make sure it's correctly configured

### Server Logs

When running servers from the GUI, logs are displayed in the console. Look for:

- Startup messages
- Error messages
- Connection information

## Command Line Alternative

You can also start MCP servers directly from the command line using the `launch_mcp_server.py` script:

```bash
# List available MCP server builds
python launch_mcp_server.py --list

# Launch a specific server
python launch_mcp_server.py --dir /path/to/server --port 8000 --host 0.0.0.0
```

## Example Requests

Once your server is running, you can use tools like curl or Postman to send requests:

```bash
# Check server health
curl http://localhost:8000/health

# Get server info
curl http://localhost:8000/info

# Generate a response
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What can you tell me about AI?",
    "parameters": {},
    "context": {}
  }'
```

## Recommended Workflow

For the best experience, we recommend:

1. **Build the MCP Server** in the Build tab
2. **Launch the Server** using the MCP Server Manager in the Test tab
3. **Test the Connection** to verify it's working
4. **Send Queries** using the chat interface
5. **Stop the Server** when you're done

This workflow ensures you can test your AMM quickly and efficiently without leaving the GUI.