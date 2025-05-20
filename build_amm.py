import shutil
import os
import json
from pathlib import Path
from enum import Enum
from amm_project.models.amm_models import AMMDesign, KnowledgeSourceType

# --- CONFIGURABLE ---
KNOWLEDGE_DIR_NAME = 'knowledge'
DESIGN_FILENAME = 'design.json'  # Changed from AMMDesign.json for MCP compatibility
REQUIREMENTS_FILENAME = 'requirements.txt'
RUN_SCRIPT_FILENAME = 'run_amm.py'
MCP_SERVER_FILENAME = 'mcp_server.py'
RUN_MCP_SERVER_FILENAME = 'run_mcp_server.py'

# Default requirements file to use if none provided
DEFAULT_REQUIREMENTS = """google-generativeai>=0.8.5
lancedb>=0.22.0
pydantic>=2.11.0
python-dotenv>=1.0.0
SQLAlchemy>=2.0.0
"""

class BuildType(str, Enum):
    """Build type for AMM packages."""
    PYTHON_APP = "python_app"
    MCP_SERVER = "mcp_server"


def build_amm(design_json_path, output_root_dir, requirements_path=None, build_type=BuildType.PYTHON_APP):
    """
    Build a runnable AMM package from a design JSON and its referenced knowledge sources.
    - design_json_path: Path to AMMDesign JSON file
    - output_root_dir: Directory to create the build in (will create <design_id>/ inside this)
    - requirements_path: Path to requirements.txt to copy (optional)
    """
    # Load and validate design (Pydantic v2 compliant)
    with open(design_json_path, "r", encoding="utf-8") as f:
        design_json_str = f.read()
    design = AMMDesign.model_validate_json(design_json_str)
    
    # Create build directory with design ID
    design_id = design.id if design.id is not None else design.design_id
    build_dir = Path(output_root_dir) / design_id
    build_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Building AMM package for '{design.name}' (ID: {design_id})")
    print(f"Build type: {build_type}")

    # Create knowledge directory for source files
    knowledge_dir = build_dir / KNOWLEDGE_DIR_NAME
    knowledge_dir.mkdir(exist_ok=True)
    
    # Process knowledge sources: copy files and update paths in the design
    for ks in design.knowledge_sources:
        if ks.type == KnowledgeSourceType.FILE and hasattr(ks, "path") and ks.path:
            source_path = Path(ks.path)
            if source_path.exists() and source_path.is_file():
                # Copy the file to knowledge directory
                target_path = knowledge_dir / source_path.name
                shutil.copy2(source_path, target_path)
                # Update the path in the design to point to the knowledge directory
                ks.path = f"knowledge/{source_path.name}"
                print(f"Copied knowledge file: {source_path} -> {target_path}")
            else:
                print(f"WARNING: Knowledge source file not found: {ks.path}")

    # Write the updated design JSON with modified paths
    with open(build_dir / DESIGN_FILENAME, "w", encoding="utf-8") as f:
        f.write(design.model_dump_json(indent=2))

    # Handle requirements.txt
    if requirements_path and Path(requirements_path).exists():
        # Copy requirements.txt if path provided and file exists
        shutil.copy(requirements_path, build_dir / REQUIREMENTS_FILENAME)
    else:
        # Create a default requirements.txt if path not provided or file doesn't exist
        print("Using default requirements file (requirements_path not provided or file not found)")
        with open(build_dir / REQUIREMENTS_FILENAME, "w", encoding="utf-8") as f:
            f.write(DEFAULT_REQUIREMENTS)
    
    # Add additional requirements based on build type
    if build_type == BuildType.MCP_SERVER:
        with open(build_dir / REQUIREMENTS_FILENAME, "a") as f:
            f.write("\n# MCP Server Requirements\nfastapi>=0.95.0\nuvicorn>=0.22.0\npython-multipart>=0.0.6\n")
    
    # Write run scripts based on build type
    if build_type == BuildType.PYTHON_APP or build_type == BuildType.MCP_SERVER:
        # Always include the Python app for CLI usage
        write_run_amm(build_dir / RUN_SCRIPT_FILENAME)
    
    if build_type == BuildType.MCP_SERVER:
        # Copy MCP server template files
        mcp_template_dir = Path(__file__).parent / "amm_project" / "templates"
        
        # Copy mcp_server.py
        try:
            shutil.copy(mcp_template_dir / MCP_SERVER_FILENAME, build_dir / MCP_SERVER_FILENAME)
            print(f"Added MCP server file: {MCP_SERVER_FILENAME}")
        except FileNotFoundError:
            print(f"ERROR: MCP server template file not found: {mcp_template_dir / MCP_SERVER_FILENAME}")
            print("Please ensure the template files are in the correct location.")
        
        # Copy run_mcp_server.py
        try:
            shutil.copy(mcp_template_dir / RUN_MCP_SERVER_FILENAME, build_dir / RUN_MCP_SERVER_FILENAME)
            print(f"Added MCP server run script: {RUN_MCP_SERVER_FILENAME}")
        except FileNotFoundError:
            print(f"ERROR: MCP server run script template not found: {mcp_template_dir / RUN_MCP_SERVER_FILENAME}")
            
        # Copy required AMM modules directly to the build directory for self-contained use
        print("Adding required AMM modules for standalone operation...")
        try:
            # Copy core modules
            source_dir = Path(__file__).parent
            shutil.copy(source_dir / "amm_project" / "models" / "amm_models.py", build_dir / "amm_models.py")
            shutil.copy(source_dir / "amm_project" / "models" / "memory_models.py", build_dir / "memory_models.py")
            shutil.copy(source_dir / "amm_project" / "engine" / "amm_engine.py", build_dir / "amm_engine.py")
            shutil.copy(source_dir / "amm_project" / "config" / "model_config.py", build_dir / "model_config.py")
            
            # Create a standalone wrapper script
            start_script = """#!/usr/bin/env python
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
    import argparse
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="Run the AMM MCP Server")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument("--api-key", type=str, help="API key for authentication (optional)")
    parser.add_argument("--api-key-required", action="store_true", help="Require API key for authentication")
    args = parser.parse_args()
    
    # Set environment variables based on arguments
    if args.api_key:
        os.environ["MCP_API_KEY"] = args.api_key
    
    if args.api_key_required:
        os.environ["API_KEY_REQUIRED"] = "true"
    
    print(f"Starting MCP server on {args.host}:{args.port}")
    print(f"Design path: {os.environ['AMM_DESIGN_PATH']}")
    print(f"Build directory: {os.environ['AMM_BUILD_DIR']}")
    
    # Import only after path setup
    from mcp_server import app
    
    # Run the server
    uvicorn.run(app, host=args.host, port=args.port)
"""
            with open(build_dir / "start_server.py", 'w') as f:
                f.write(start_script)
            
            # Make executable
            os.chmod(build_dir / "start_server.py", 0o755)
            print("Added standalone MCP server wrapper script: start_server.py")
        except Exception as e:
            print(f"WARNING: Error adding standalone modules: {e}")
            print("The MCP server may require additional setup to run correctly.")
    
    print(f'AMM build complete at: {build_dir}')
    
    # Return the build directory path as a string
    return str(build_dir)


def write_run_amm(target_path):
    """
    Write a production-ready run_amm.py script for running the AMM CLI.
    """
    code = '''#!/usr/bin/env python
import json
from pathlib import Path
import sys
import argparse

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run the AMM CLI.")
    parser.add_argument("--query", help="Process a single query and exit")
    args = parser.parse_args()
    
    try:
        from amm_project.engine.amm_engine import AMMEngine
        from amm_project.models.amm_models import AMMDesign
    except ImportError as e:
        print(f"Error: Could not import AMMEngine or AMMDesign: {e}", file=sys.stderr)
        sys.exit(1)
        
    design_path = Path(__file__).parent / "design.json"
    try:
        with open(design_path, "r", encoding="utf-8") as f:
            design_json = f.read()
        design = AMMDesign.model_validate_json(design_json)
    except Exception as e:
        print(f"Error loading AMMDesign: {e}", file=sys.stderr)
        sys.exit(1)
        
    try:
        engine = AMMEngine(design, base_data_path=str(Path(__file__).parent))
    except Exception as e:
        print(f"Error initializing AMMEngine: {e}", file=sys.stderr)
        sys.exit(1)
        
    # Process a single query if provided
    if args.query:
        try:
            result = engine.process_query(args.query)
            print(result)
            return
        except Exception as e:
            print(f"Error processing query: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Interactive mode
    print(f"AMM '{design.name}' is ready. Type your query (or 'exit' to quit):")
    while True:
        try:
            user_input = input("> ")
            if user_input.strip().lower() == "exit":
                break
            result = engine.process_query(user_input)
            print(f"\nAMM: {result}\n")
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error processing query: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
'''
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(code)

# For direct invocation (useful for quick testing)
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Build an AMM package from a design JSON")
    parser.add_argument("design_json", help="Path to the AMMDesign JSON file")
    parser.add_argument("--output-dir", "-o", default="build", help="Output directory")
    parser.add_argument("--requirements", "-r", help="Path to requirements.txt")
    parser.add_argument("--build-type", "-t", choices=["python_app", "mcp_server"], default="python_app", 
                      help="Type of build to create")
    
    args = parser.parse_args()
    
    build_amm(
        design_json_path=args.design_json,
        output_root_dir=args.output_dir,
        requirements_path=args.requirements,
        build_type=BuildType(args.build_type)
    )