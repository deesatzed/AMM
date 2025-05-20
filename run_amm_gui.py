#!/usr/bin/env python3
"""
AMM Design Studio Launcher
-------------------------
Script to launch the AMM Design Studio Streamlit application.
"""
import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import streamlit
        print("✓ Streamlit is installed")
    except ImportError:
        print("✗ Streamlit is not installed. Please install it with: pip install streamlit")
        return False
        
    try:
        import dotenv
        print("✓ python-dotenv is installed")
    except ImportError:
        print("✗ python-dotenv is not installed. Please install it with: pip install python-dotenv")
        return False
        
    return True

def main():
    """Launch the AMM Design Studio Streamlit application."""
    # Check dependencies
    if not check_dependencies():
        print("Please install the required dependencies and try again.")
        return 1
        
    # Get the directory of this script
    script_dir = Path(__file__).parent.absolute()
    
    # Path to the Streamlit app
    app_path = script_dir / "amm_gui" / "app.py"
    
    # Check if the app exists
    if not app_path.exists():
        print(f"Error: Could not find the AMM Design Studio app at {app_path}")
        return 1
    
    # Create temp directory if it doesn't exist
    temp_dir = script_dir / "temp"
    temp_dir.mkdir(exist_ok=True)
    
    # Create designs directory if it doesn't exist
    designs_dir = script_dir / "designs"
    designs_dir.mkdir(exist_ok=True)
    
    print("Launching AMM Design Studio...")
    print(f"App path: {app_path}")
    
    # Check if GEMINI_API_KEY is set
    if not os.environ.get("GEMINI_API_KEY"):
        print("Warning: GEMINI_API_KEY environment variable is not set.")
        print("Some features like testing AMMs may not work correctly.")
    
    # Launch Streamlit
    try:
        # Use subprocess to run streamlit
        cmd = [sys.executable, "-m", "streamlit", "run", str(app_path), "--server.port=8501"]
        
        # Print the command for debugging
        print(f"Running command: {' '.join(cmd)}")
        
        # Run the command
        process = subprocess.run(cmd)
        return process.returncode
    except Exception as e:
        print(f"Error launching Streamlit: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
