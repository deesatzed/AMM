#!/usr/bin/env python3
"""
MCP API Key Manager Launcher

This script launches the MCP API Key Manager application.
"""

import os
import sys
import logging
from pathlib import Path

import streamlit.web.cli as stcli

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("mcp_key_manager_launcher")

def main():
    """Launch the MCP Key Manager application."""
    # Get the directory of this script
    script_dir = Path(__file__).parent.absolute()
    
    # Path to the app.py file
    app_path = script_dir / "mcp_key_manager" / "app.py"
    
    if not app_path.exists():
        logger.error(f"Application file not found: {app_path}")
        print(f"ERROR: Application file not found: {app_path}")
        sys.exit(1)
    
    # Set up Streamlit arguments
    sys.argv = [
        "streamlit", "run", 
        str(app_path),
        "--server.port=8502",  # Use a different port than the AMM GUI
        "--server.headless=false",
        "--browser.serverAddress=localhost",
        "--browser.gatherUsageStats=false"
    ]
    
    print(f"Starting MCP API Key Manager at http://localhost:8502")
    print(f"Application path: {app_path}")
    
    # Launch Streamlit
    sys.exit(stcli.main())

if __name__ == "__main__":
    main()
