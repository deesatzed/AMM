# MCP Server GUI Integration

## Implementation Summary

We've integrated the MCP server manager functionality directly into the AMM GUI, making it easy to launch, manage, and test MCP servers without leaving the interface. This addresses the connection issues encountered when testing MCP servers from the GUI.

### Key Components

1. **MCP Server Manager Component**
   - Created a new Streamlit component in `amm_gui/components/mcp_server_manager.py`
   - Provides UI for selecting, launching, and stopping MCP servers
   - Monitors server status and provides diagnostics

2. **GUI Integration**
   - Updated the Test tab in `amm_gui/app.py` to include the MCP Server Manager
   - Made the manager accessible via an expander in the MCP Server Test mode
   - Auto-detects and uses server URL if launched from the manager

3. **Documentation**
   - Added a new guide in `docs/mcp_server_testing_guide.md`
   - Updated the README with information about the new feature

## How It Works

1. The MCP Server Manager finds available server builds by searching for directories containing `start_server.py`
2. Users can select a server, configure options (port, host, API key), and launch it
3. The component keeps track of running servers and their status
4. The Test tab automatically uses the URL of the launched server for testing

## Benefits

- **Simplified Workflow**: Users can now build, launch, and test MCP servers without leaving the GUI
- **Better Diagnostics**: The manager provides status information and troubleshooting guidance
- **Reduced Errors**: Eliminates manual steps that were causing connection issues
- **Improved UX**: Clearer workflow and more intuitive testing process

## Technical Details

- Uses the `launch_mcp_server.py` script in the background to start server processes
- Maintains server processes in the Streamlit session state
- Provides proper cleanup when servers are stopped or the session ends
- Supports API key authentication for secure server testing

## Next Steps

1. **Persistent Server Management**
   - Consider adding a way to save server configurations for quick re-launching
   - Add support for managing multiple servers simultaneously

2. **Extended Testing Capabilities**
   - Add performance testing features (load testing, response time measurements)
   - Support for batch testing with predefined query sets

3. **Logging Improvements**
   - Capture and display server logs directly in the GUI
   - Add log level filtering and search capabilities

4. **Deployment Automation**
   - Integrate with deployment pipelines for production servers
   - Add support for containerization (Docker) of MCP servers

## Known Limitations

- Server processes are tied to the Streamlit session - if the GUI is restarted, they need to be launched again
- Limited visibility into server process details (e.g., memory usage, detailed performance metrics)
- No direct integration with cloud deployment options yet