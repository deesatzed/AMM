# MCP Server Import Fix

## Import Issue Fixed

We've resolved the "No module named 'amm_project'" error and "AMMDesign is not defined" error when running MCP servers by creating a robust import fix solution.

### Problem

When running an MCP server in standalone mode, the imports were failing because:
1. The MCP server was looking for the 'amm_project' module which isn't available in standalone builds
2. The fallback direct import path wasn't properly resolving the AMMDesign class
3. Cross-imports between modules weren't handled correctly in standalone mode

### Solution

We've created a robust fix with multiple components:

1. **fix_imports.py Script**
   - Automatically fixes all import issues in MCP server builds
   - Updates imports to try direct local imports first, then fall back to package imports
   - Fixes imports in all key modules (mcp_server.py, amm_engine.py, amm_models.py)
   - Creates a proper __init__.py file to make the directory a package

2. **Improved Error Handling**
   - Added better error checking and reporting for import failures
   - Checks if critical classes like AMMDesign are available before trying to use them
   - Provides more detailed error messages to help with troubleshooting

3. **Path Handling**
   - Ensures the build directory is properly added to the Python path
   - Uses absolute paths consistently to avoid relative path issues

## Using the Import Fix Script

### Option 1: Fix Existing Builds

To fix import issues in an existing MCP server build:

```bash
# Run the fix_imports.py script on your MCP server build directory
python fix_imports.py /path/to/your/mcp_server_build
```

### Option 2: Future Builds

All future builds will automatically include these fixes in:
- The start_server.py script
- The clean_build_v3.sh script

## Testing the Fixed MCP Server

After fixing the imports, you can test the server:

```bash
cd /path/to/your/mcp_server_build
python start_server.py --port 8000 --host 0.0.0.0
```

Or use the convenient start_mcp.sh script:

```bash
./start_mcp.sh 8000
```

## Troubleshooting

If you still encounter import issues:

1. **Check Python Environment**
   - Make sure you're using the same Python environment that has all the dependencies installed
   - Verify the required packages are installed: `pip install fastapi uvicorn pydantic`

2. **Verify Module Files**
   - Ensure all required module files exist in the build directory:
     - amm_models.py
     - memory_models.py
     - amm_engine.py
     - model_config.py
     - mcp_server.py
     - __init__.py

3. **Run With Debug Output**
   - Run the server with additional logging: `PYTHONVERBOSE=1 python start_server.py`
   - This will show detailed import attempts and paths being searched

4. **Re-run the Fix Script**
   - If you've modified any files, run the fix_imports.py script again
   - This will ensure all import statements are properly updated