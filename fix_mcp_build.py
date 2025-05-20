#!/usr/bin/env python
"""
Fix script for MCP server builds.

This script copies necessary AMM modules into the MCP server build directory
so they can be imported directly without relying on external packages.
"""

import sys
import os
import shutil
from pathlib import Path
import argparse

def fix_mcp_build(build_dir):
    """
    Fix an MCP server build by copying necessary modules.
    
    Args:
        build_dir: Path to the MCP server build directory
    """
    build_path = Path(build_dir)
    
    # Ensure the build directory exists
    if not build_path.exists() or not build_path.is_dir():
        print(f"Error: Build directory not found: {build_path}")
        return False
    
    # Check if it's an MCP server build
    if not (build_path / "mcp_server.py").exists():
        print(f"Error: This doesn't appear to be an MCP server build (missing mcp_server.py)")
        return False
    
    # Get the source directory (project root)
    source_dir = Path(__file__).parent
    
    print(f"Fixing MCP server build in: {build_path}")
    print(f"Source directory: {source_dir}")
    
    # Step 1: Create necessary directories
    print("Creating module directories...")
    (build_path / "amm_models.py").unlink(missing_ok=True)  # Remove existing files if any
    (build_path / "amm_engine.py").unlink(missing_ok=True)
    
    # Step 2: Copy essential files for direct imports
    print("Copying essential modules...")
    
    # Copy core models
    try:
        shutil.copy(source_dir / "amm_project" / "models" / "amm_models.py", build_path / "amm_models.py")
        shutil.copy(source_dir / "amm_project" / "models" / "memory_models.py", build_path / "memory_models.py")
        shutil.copy(source_dir / "amm_project" / "engine" / "amm_engine.py", build_path / "amm_engine.py")
        shutil.copy(source_dir / "amm_project" / "config" / "model_config.py", build_path / "model_config.py")
        print("✓ Core modules copied successfully")
    except Exception as e:
        print(f"Error copying core modules: {e}")
        return False
    
    # Step 3: Update mcp_server.py imports to use local modules
    print("Updating mcp_server.py imports...")
    
    mcp_server_path = build_path / "mcp_server.py"
    try:
        with open(mcp_server_path, 'r') as f:
            content = f.read()
        
        # Update imports to use local modules
        content = content.replace(
            '# Direct imports (when files are copied to build dir)\n    from amm_engine import AMMEngine\n    from amm_models import AMMDesign, AdaptiveMemoryConfig, AgentPrompts',
            '# Direct imports (from local modules)\n    from amm_engine import AMMEngine\n    from amm_models import AMMDesign, AdaptiveMemoryConfig, AgentPrompts\n    from memory_models import MemoryRecord\n    from model_config import ModelConfig'
        )
        
        with open(mcp_server_path, 'w') as f:
            f.write(content)
        
        print("✓ MCP server imports updated")
    except Exception as e:
        print(f"Error updating MCP server imports: {e}")
        return False
    
    # Step 4: Create a simple wrapper script to help with imports and testing
    print("Creating wrapper script...")
    
    wrapper_script = """#!/usr/bin/env python
\"\"\"
MCP Server Wrapper Script

This script ensures proper imports and starts the MCP server.
\"\"\"

import os
import sys
from pathlib import Path

# Add current directory to Python path for imports
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

# Set environment variables
os.environ["AMM_DESIGN_PATH"] = str(current_dir / "design.json")
os.environ["AMM_BUILD_DIR"] = str(current_dir)

# Run the server
if __name__ == "__main__":
    import uvicorn
    
    # Import only after path setup
    from mcp_server import app
    
    # Get port from arguments or use default
    port = 8000
    host = "0.0.0.0"
    
    if len(sys.argv) > 1:
        for i, arg in enumerate(sys.argv):
            if arg == "--port" and i + 1 < len(sys.argv):
                port = int(sys.argv[i + 1])
            elif arg == "--host" and i + 1 < len(sys.argv):
                host = sys.argv[i + 1]
    
    print(f"Starting MCP server on {host}:{port}")
    print(f"Design path: {os.environ['AMM_DESIGN_PATH']}")
    print(f"Build directory: {os.environ['AMM_BUILD_DIR']}")
    
    uvicorn.run(app, host=host, port=port)
"""
    
    try:
        with open(build_path / "start_server.py", 'w') as f:
            f.write(wrapper_script)
        
        # Make executable
        os.chmod(build_path / "start_server.py", 0o755)
        print("✓ Wrapper script created")
    except Exception as e:
        print(f"Error creating wrapper script: {e}")
        return False
    
    print("\n✅ MCP server build fixed successfully!")
    print(f"To start the server, run: python {build_path}/start_server.py --port 8000 --host 0.0.0.0")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fix MCP server build")
    parser.add_argument("build_dir", help="Path to the MCP server build directory")
    
    args = parser.parse_args()
    success = fix_mcp_build(args.build_dir)
    sys.exit(0 if success else 1)