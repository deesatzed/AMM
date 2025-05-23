#!/bin/bash

# Improved clean build script to create a production-ready AMM build with no mock code
# Version 3: Fixes metadata-related issues when building MCP server

# Usage: ./clean_build_v3.sh [output_directory]
# If output_directory is not specified, the build will be created in May19_AMM/build/amm-prod-bld-YYYYMMDD

# Set environment and working directory
set -e  # Exit on any error

if [[ "$(uname)" == "Darwin" ]]; then
  SED_I_ARG="-i ''" # macOS requires an argument for -i (empty string for no backup)
else
  SED_I_ARG="-i"    # Linux sed -i
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Handle custom output directory if provided
if [ $# -eq 1 ]; then
    # Use the provided output directory
    CUSTOM_OUTPUT_DIR="$1"
    
    # Check if it's an absolute path
    if [[ "$CUSTOM_OUTPUT_DIR" = /* ]]; then
        # Absolute path - use as is
        BUILD_DIR="$CUSTOM_OUTPUT_DIR"
    else
        # Relative path - make it relative to the current directory
        BUILD_DIR="$SCRIPT_DIR/$CUSTOM_OUTPUT_DIR"
    fi
    
    # Create a specific build name based on date
    BUILD_NAME="amm-prod-$(date +%Y%m%d)"
else
    # Default configuration if no output directory is provided
    BUILD_DIR="$SCRIPT_DIR/build"
    BUILD_NAME="amm-production-bld-$(date +%Y%m%d)"
fi

SOURCE_DIR="$SCRIPT_DIR"
FINAL_BUILD_DIR="$BUILD_DIR/$BUILD_NAME"

echo "Creating production build in: $FINAL_BUILD_DIR"

# Clean previous build if it exists
if [ -d "$FINAL_BUILD_DIR" ]; then
    echo "Removing previous build..."
    rm -rf "$FINAL_BUILD_DIR"
fi

# Create fresh build directory
mkdir -p "$FINAL_BUILD_DIR"

# First, set up the minimal necessary directory structure
echo "Setting up directory structure..."
mkdir -p "$FINAL_BUILD_DIR/amm_project/config"
mkdir -p "$FINAL_BUILD_DIR/amm_project/engine"
mkdir -p "$FINAL_BUILD_DIR/amm_project/models"
mkdir -p "$FINAL_BUILD_DIR/amm_project/templates"
mkdir -p "$FINAL_BUILD_DIR/amm_gui/components"
mkdir -p "$FINAL_BUILD_DIR/amm_gui/utils"
mkdir -p "$FINAL_BUILD_DIR/mcp_key_manager"
mkdir -p "$FINAL_BUILD_DIR/designs"
mkdir -p "$FINAL_BUILD_DIR/knowledge_files"
mkdir -p "$FINAL_BUILD_DIR/tests/unit"
mkdir -p "$FINAL_BUILD_DIR/docs"

# Copy only the necessary files for production
echo "Copying core production files..."

# Core AMM project
cp "$SOURCE_DIR/amm_project/__init__.py" "$FINAL_BUILD_DIR/amm_project/"
cp "$SOURCE_DIR/amm_project/config/__init__.py" "$FINAL_BUILD_DIR/amm_project/config/"
cp "$SOURCE_DIR/amm_project/config/model_config.py" "$FINAL_BUILD_DIR/amm_project/config/"
cp "$SOURCE_DIR/amm_project/engine/__init__.py" "$FINAL_BUILD_DIR/amm_project/engine/"
cp "$SOURCE_DIR/amm_project/engine/amm_engine.py" "$FINAL_BUILD_DIR/amm_project/engine/"
cp "$SOURCE_DIR/amm_project/models/__init__.py" "$FINAL_BUILD_DIR/amm_project/models/"
cp "$SOURCE_DIR/amm_project/models/amm_models.py" "$FINAL_BUILD_DIR/amm_project/models/"
cp "$SOURCE_DIR/amm_project/models/memory_models.py" "$FINAL_BUILD_DIR/amm_project/models/"
cp "$SOURCE_DIR/amm_project/templates/__init__.py" "$FINAL_BUILD_DIR/amm_project/templates/"
cp "$SOURCE_DIR/amm_project/templates/mcp_server.py" "$FINAL_BUILD_DIR/amm_project/templates/"
cp "$SOURCE_DIR/amm_project/templates/run_mcp_server.py" "$FINAL_BUILD_DIR/amm_project/templates/"

# AMM GUI
cp "$SOURCE_DIR/amm_gui/__init__.py" "$FINAL_BUILD_DIR/amm_gui/"
cp "$SOURCE_DIR/amm_gui/app.py" "$FINAL_BUILD_DIR/amm_gui/"
cp "$SOURCE_DIR/amm_gui/components/__init__.py" "$FINAL_BUILD_DIR/amm_gui/components/"
cp "$SOURCE_DIR/amm_gui/components/knowledge_source_manager.py" "$FINAL_BUILD_DIR/amm_gui/components/"
cp "$SOURCE_DIR/amm_gui/components/memory_manager.py" "$FINAL_BUILD_DIR/amm_gui/components/"
cp "$SOURCE_DIR/amm_gui/components/mcp_server_manager.py" "$FINAL_BUILD_DIR/amm_gui/components/"
cp "$SOURCE_DIR/amm_gui/utils/__init__.py" "$FINAL_BUILD_DIR/amm_gui/utils/"
cp "$SOURCE_DIR/amm_gui/utils/amm_integration.py" "$FINAL_BUILD_DIR/amm_gui/utils/"
cp "$SOURCE_DIR/amm_gui/utils/file_handling.py" "$FINAL_BUILD_DIR/amm_gui/utils/"
cp "$SOURCE_DIR/amm_gui/utils/temp_manager.py" "$FINAL_BUILD_DIR/amm_gui/utils/"

# MCP Key Manager
cp "$SOURCE_DIR/mcp_key_manager/__init__.py" "$FINAL_BUILD_DIR/mcp_key_manager/"
cp "$SOURCE_DIR/mcp_key_manager/app.py" "$FINAL_BUILD_DIR/mcp_key_manager/"
cp "$SOURCE_DIR/mcp_key_manager/cli.py" "$FINAL_BUILD_DIR/mcp_key_manager/"

# Main scripts and configuration files
cp "$SOURCE_DIR/build_amm.py" "$FINAL_BUILD_DIR/"
cp "$SOURCE_DIR/build_news_agent.py" "$FINAL_BUILD_DIR/"
cp "$SOURCE_DIR/demo_mcp_server.py" "$FINAL_BUILD_DIR/"
cp "$SOURCE_DIR/launch_mcp_server.py" "$FINAL_BUILD_DIR/"
cp "$SOURCE_DIR/fix_imports.py" "$FINAL_BUILD_DIR/"
cp "$SOURCE_DIR/start_mcp.sh" "$FINAL_BUILD_DIR/"
cp "$SOURCE_DIR/mcp_cli.py" "$FINAL_BUILD_DIR/"
cp "$SOURCE_DIR/run_mcp_tests.py" "$FINAL_BUILD_DIR/"
cp "$SOURCE_DIR/run_tests.sh" "$FINAL_BUILD_DIR/"
chmod +x "$FINAL_BUILD_DIR/start_mcp.sh"
chmod +x "$FINAL_BUILD_DIR/fix_imports.py"
chmod +x "$FINAL_BUILD_DIR/mcp_cli.py"
chmod +x "$FINAL_BUILD_DIR/run_mcp_tests.py"
chmod +x "$FINAL_BUILD_DIR/run_tests.sh"
cp "$SOURCE_DIR/run_amm_gui.py" "$FINAL_BUILD_DIR/"
cp "$SOURCE_DIR/run_mcp_key_manager.py" "$FINAL_BUILD_DIR/"
cp "$SOURCE_DIR/setup.py" "$FINAL_BUILD_DIR/"
cp "$SOURCE_DIR/requirements.txt" "$FINAL_BUILD_DIR/"
cp "$SOURCE_DIR/environment.yml" "$FINAL_BUILD_DIR/"
cp "$SOURCE_DIR/DEPLOYMENT_GUIDE.md" "$FINAL_BUILD_DIR/"

# Create a simple test script to verify MCP builds work
cat > "$FINAL_BUILD_DIR/test_mcp_build.py" << 'EOF'
#!/usr/bin/env python
"""
Test script to verify the MCP server build works correctly.
"""

import os
import sys
import json
from pathlib import Path
from build_amm import build_amm, BuildType

def main():
    # Create a minimal test design
    print("Creating test design...")
    test_design = {
        "id": "test_mcp_build",
        "name": "Test MCP Build",
        "description": "Test design for MCP server build",
        "knowledge_sources": [],
        "adaptive_memory": {
            "enabled": True,
            "db_name_prefix": "test_amm_memory",
            "retrieval_limit": 10
        },
        "agent_prompts": {
            "system_instruction": "You are a helpful assistant.",
            "welcome_message": "Hello, how can I help you?"
        },
        "metadata": {}  # Ensure metadata is included
    }
    
    test_design_path = Path("./test_mcp_design.json")
    with open(test_design_path, "w") as f:
        json.dump(test_design, f, indent=2)
        
    print(f"Using design file: {test_design_path}")
    
    # Create a test build output directory
    output_dir = Path("./test_build")
    output_dir.mkdir(exist_ok=True)
    
    try:
        # Attempt to build with MCP server build type
        print("Building AMM with MCP server build type...")
        build_path = build_amm(
            design_json_path=str(test_design_path),
            output_root_dir=str(output_dir),
            build_type=BuildType.MCP_SERVER
        )
        
        print(f"Build succeeded! Output at: {build_path}")
        return True
    except Exception as e:
        print(f"Build failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
EOF

# Make the test script executable
chmod +x "$FINAL_BUILD_DIR/test_mcp_build.py"

# Copy documentation
cp -r "$SOURCE_DIR/docs"/* "$FINAL_BUILD_DIR/docs/"

# Add MCP server documentation
cp "$SOURCE_DIR/docs/MCP_SERVER_GUIDE.md" "$FINAL_BUILD_DIR/docs/"
cp "$SOURCE_DIR/docs/running_mcp_server.md" "$FINAL_BUILD_DIR/docs/"
cp "$SOURCE_DIR/docs/FIXED_ISSUES.md" "$FINAL_BUILD_DIR/docs/"
cp "$SOURCE_DIR/docs/mcp_server_testing_guide.md" "$FINAL_BUILD_DIR/docs/"
cp "$SOURCE_DIR/docs/mcp_gui_integration_summary.md" "$FINAL_BUILD_DIR/docs/"
cp "$SOURCE_DIR/docs/mcp_cli_guide.md" "$FINAL_BUILD_DIR/docs/"
cp "$SOURCE_DIR/docs/mcp_connection_fix.md" "$FINAL_BUILD_DIR/docs/"
cp "$SOURCE_DIR/docs/mcp_import_fix.md" "$FINAL_BUILD_DIR/docs/"
cp "$SOURCE_DIR/docs/amm_engine_fix_summary.md" "$FINAL_BUILD_DIR/docs/"
cp "$SOURCE_DIR/docs/mcp_improvements_summary.md" "$FINAL_BUILD_DIR/docs/"
cp "$SOURCE_DIR/docs/testing_mcp_components.md" "$FINAL_BUILD_DIR/docs/"
cp "$SOURCE_DIR/docs/running_tests_guide.md" "$FINAL_BUILD_DIR/docs/"

# Create an additional README file specific to MCP servers
cat > "$FINAL_BUILD_DIR/docs/README-MCP-SERVER.md" << 'EOF'
# MCP Server Quick Reference

MCP (Model Control Protocol) server builds now include these improvements:

1. **Standalone Operation**: No need for amm_project package, all required modules are included
2. **Easier Startup**: New wrapper script handles paths and configuration automatically
3. **Robust Error Handling**: Better error recovery and logging
4. **Metadata Support**: Properly handles optional metadata field
5. **Complete Documentation**: Detailed guides on usage and troubleshooting
6. **GUI Integration**: Launch and manage MCP servers directly from the GUI
7. **Import Fix**: Automatic import fixing script for standalone MCP servers
8. **Network Access**: Binds to 0.0.0.0 by default for better accessibility

## Quick Start

### Option 1: Easy Server Start

```bash
# Start the most recently built MCP server on port 8000
./start_mcp.sh

# Start on a specific port
./start_mcp.sh 9000
```

### Option 2: Manual Start

```bash
cd /path/to/mcp/build
python start_server.py --host 0.0.0.0 --port 8000
```

### Fixing Import Issues

If you encounter import errors:

```bash
# Fix imports in a specific MCP server build
python fix_imports.py /path/to/mcp/build
```

## Testing the API

Basic health check:
```bash
curl -X GET http://localhost:8000/health
```

Send a query:
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Hello, how are you?",
    "parameters": {},
    "context": {}
  }'
```

## For Complete Documentation

See the following guide files:
- MCP_SERVER_GUIDE.md - Complete guide for MCP server usage
- running_mcp_server.md - Detailed runtime options and examples
- FIXED_ISSUES.md - Documentation of fixes and improvements
EOF

# Copy designs and knowledge files (sample data)
cp -r "$SOURCE_DIR/designs"/* "$FINAL_BUILD_DIR/designs/"
cp -r "$SOURCE_DIR/knowledge_files"/* "$FINAL_BUILD_DIR/knowledge_files/"

# Copy test files
cp "$SOURCE_DIR/tests/unit/test_mcp_cli.py" "$FINAL_BUILD_DIR/tests/unit/"
cp "$SOURCE_DIR/tests/unit/test_fix_imports.py" "$FINAL_BUILD_DIR/tests/unit/"
cp "$SOURCE_DIR/tests/unit/test_mcp_server_manager.py" "$FINAL_BUILD_DIR/tests/unit/"
cp "$SOURCE_DIR/tests/__init__.py" "$FINAL_BUILD_DIR/tests/" 2>/dev/null || touch "$FINAL_BUILD_DIR/tests/__init__.py"
cp "$SOURCE_DIR/tests/unit/__init__.py" "$FINAL_BUILD_DIR/tests/unit/" 2>/dev/null || touch "$FINAL_BUILD_DIR/tests/unit/__init__.py"

# Add final README and configuration
cp "$SOURCE_DIR/README-clean.md" "$FINAL_BUILD_DIR/README.md"
cp "$SOURCE_DIR/.env.example" "$FINAL_BUILD_DIR/.env.example"

# Remove any remaining mock code from Python files
echo "Cleaning Python files of any test/mock code..."
find "$FINAL_BUILD_DIR" -name "*.py" | while read file; do
    # Remove unittest.mock imports
    sed $SED_I_ARG '/from unittest.mock import/d' "$file"
    sed $SED_I_ARG '/import unittest.mock/d' "$file"
    sed $SED_I_ARG '/from unittest import mock/d' "$file"
    
    # Remove pytest imports
    sed $SED_I_ARG '/import pytest/d' "$file"
    sed $SED_I_ARG '/from pytest import/d' "$file"
    
    # Remove MagicMock references
    sed $SED_I_ARG '/MagicMock/d' "$file"
    
    # Remove patch decorators
    sed $SED_I_ARG '/@patch/d' "$file"
    sed $SED_I_ARG '/@mock/d' "$file"
    
    # Remove any lines with explicit mock references
    sed $SED_I_ARG '/mock_/d' "$file"
done

# Create production environment file
echo "# Production configuration - ADD YOUR API KEYS
GEMINI_API_KEY=your_gemini_api_key_here

# Model Configuration
MODEL=gemini-1.5-flash
MODEL2=gemini-1.5-pro
EMBEDDING_MODEL=models/text-embedding-004

# MCP Server Configuration
MCP_SERVER_PORT=8000 
MCP_SERVER_HOST=0.0.0.0
MCP_API_KEY=your_mcp_api_key_here

# Production Settings
DEBUG=false
LOG_LEVEL=INFO
LANCEDB_CACHE_DIR=./lancedb_cache" > "$FINAL_BUILD_DIR/.env.production"

# Document the fixed metadata issue
echo "# Fixed Issues

## MCP Server Build Errors

### Metadata Field Error
- **Issue**: When building an AMM with the MCP server build type, it would fail with a 'metadata' error.
- **Fix**: Added proper handling for the metadata field in:
  - The AMMDesign model now initializes metadata with default empty dictionary
  - The app.py GUI checks for existence of metadata before accessing it 
  - The mcp_server.py template properly handles missing metadata

### Import Errors
- Fixed the import paths in MCP server template to properly import required classes
- Added graceful error handling for import failures
- Added fix_imports.py script to fix import issues in standalone MCP server builds
- Updated import statements to work in both package and standalone contexts

### MCP Server Connection Issues
- **Issue**: When testing MCP servers via the GUI, connection errors occurred
- **Fix**: Created integrated MCP server manager in the GUI
  - Added launch_mcp_server.py script for easier server management
  - Created mcp_server_manager.py component for the GUI
  - Integrated server management directly into the Test tab
  - Fixed connection handling between GUI and server
- **Host Binding Fix**: Updated default host binding from 127.0.0.1 to 0.0.0.0
  - Ensures the server is accessible from both localhost and network interfaces
  - Prevents "Connection refused" errors when testing

## AMMDesign Model Errors

### ID Field Compatibility
- Added support for both 'id' and 'design_id' fields for backward compatibility
- Created helper methods to consistently access the ID regardless of which field is used

### Optional Fields
- Made metadata and ui_metadata fields optional with default empty dictionaries
- Improved validation to handle missing fields gracefully" > "$FINAL_BUILD_DIR/docs/FIXED_ISSUES.md"

# Generate a file list for verification
echo "Generating file list..."
find "$FINAL_BUILD_DIR" -type f | sort > "$FINAL_BUILD_DIR/production_files.txt"

echo "Build completed successfully!"
echo "Production build location: $FINAL_BUILD_DIR"
echo ""
echo "To use this build:"
echo "1. cd $FINAL_BUILD_DIR"
echo "2. cp .env.production .env"
echo "3. Edit .env to add your API keys"
echo "4. conda activate mcp-env"
echo "5. python run_amm_gui.py"
echo ""
echo "To test MCP server builds:"
echo "  cd $FINAL_BUILD_DIR && python test_mcp_build.py"
echo ""
echo "To build an MCP server directly:"
echo "  cd $FINAL_BUILD_DIR && python build_amm.py path/to/design.json --output-dir build --build-type mcp_server"
echo ""
echo "To manage MCP servers:"
echo "  cd $FINAL_BUILD_DIR && python mcp_cli.py --interactive     # Interactive mode"
echo "  cd $FINAL_BUILD_DIR && python mcp_cli.py --list           # List available servers"
echo "  cd $FINAL_BUILD_DIR && python mcp_cli.py --launch PATH    # Launch a server"
echo ""
echo "To run unit tests for MCP components:"
echo "  cd $FINAL_BUILD_DIR && python run_mcp_tests.py            # Run all MCP tests"
echo "  cd $FINAL_BUILD_DIR && python run_mcp_tests.py --verbose  # Run with verbose output"
echo "  cd $FINAL_BUILD_DIR && ./run_tests.sh                   # Run all tests in the project"
echo ""
echo "For full MCP server documentation:"
echo "  See $FINAL_BUILD_DIR/docs/MCP_SERVER_GUIDE.md"
echo "  See $FINAL_BUILD_DIR/docs/mcp_cli_guide.md"
