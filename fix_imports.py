#!/usr/bin/env python
"""
Fix MCP Server Import Issues

This script fixes import issues in mcp_server.py by ensuring all necessary
modules are properly imported, even when run from a standalone build directory.
"""

import os
import sys
import re
from pathlib import Path

def fix_mcp_server_imports(mcp_server_path):
    """Fix import issues in the MCP server file."""
    if not os.path.exists(mcp_server_path):
        print(f"Error: MCP server file not found at {mcp_server_path}")
        return False
    
    print(f"Fixing imports in {mcp_server_path}")
    
    # Read the file
    with open(mcp_server_path, 'r') as f:
        content = f.read()
    
    # Ensure we're importing the right modules regardless of their structure
    if "from amm_engine import AMMEngine" not in content:
        # Add direct imports section if not present
        import_fix = """# Direct imports - standalone version with all required modules
try:
    # Force use of local modules
    from amm_engine import AMMEngine
    from amm_models import AMMDesign, AdaptiveMemoryConfig, AgentPrompts
    from memory_models import MemoryRecord
    print("Using direct local imports")
except ImportError as e:
    print(f"Direct import error: {e}")
    try:
        # Try package imports as fallback
        from amm_project.engine.amm_engine import AMMEngine
        from amm_project.models.amm_models import AMMDesign, AdaptiveMemoryConfig, AgentPrompts
        from amm_project.models.memory_models import MemoryRecord
        print("Using package imports")
    except ImportError as e:
        print(f"Error importing AMM modules: {e}")
        print("Please ensure the AMM modules are available in the Python path.")
"""
        
        # Add our import fix after the sys.path.append line
        content = re.sub(
            r'(sys\.path\.append\(.*\))\s*',
            r'\1\n\n' + import_fix,
            content
        )
    else:
        # Old style import section - replace it
        old_import_section = """
# Try different import paths to handle both direct imports and package imports
try:
    # Direct imports (when files are copied to build dir)
    from amm_engine import AMMEngine
    from amm_models import AMMDesign, AdaptiveMemoryConfig, AgentPrompts
except ImportError:
    try:
        # Package imports (when installed as a package)
        from amm_project.engine.amm_engine import AMMEngine
        from amm_project.models.amm_models import AMMDesign, AdaptiveMemoryConfig, AgentPrompts
    except ImportError as e:
        print(f"Error importing AMM modules: {e}")
        print("Please ensure the AMM modules are available in the Python path.")
        # We'll handle this gracefully when initializing the model server"""
        
        new_import_section = """
# Direct imports - standalone version with all required modules in the build directory
try:
    print("Trying direct imports...")
    # Force use of local modules
    from amm_engine import AMMEngine
    from amm_models import AMMDesign, AdaptiveMemoryConfig, AgentPrompts
    from memory_models import MemoryRecord
    print("Direct imports successful!")
except ImportError as e:
    print(f"Direct import error: {e}")
    try:
        # Try package imports as fallback
        print("Trying package imports...")
        from amm_project.engine.amm_engine import AMMEngine
        from amm_project.models.amm_models import AMMDesign, AdaptiveMemoryConfig, AgentPrompts
        from amm_project.models.memory_models import MemoryRecord
        print("Package imports successful!")
    except ImportError as e:
        print(f"Error importing AMM modules: {e}")
        print("Please ensure the AMM modules are available in the Python path.")
        # The code will still try to initialize model server, which may fail gracefully"""
        
        # Replace the import section if found
        if old_import_section.strip() in content:
            content = content.replace(old_import_section, new_import_section)
    
    # Update model server initialization to handle AMMDesign properly
    model_server_pattern = r'try:\s*model_server = AMMModelServer\(DESIGN_PATH, BUILD_DIR\)[^}]*?except Exception as e:'  
    if re.search(model_server_pattern, content, re.DOTALL):
        old_init_section = re.search(model_server_pattern, content, re.DOTALL).group(0)
        
        new_init_section = """try:
    # Verify that AMMDesign is available before trying to use it
    if 'AMMDesign' not in globals():
        print("WARNING: AMMDesign class not available. Server will not function correctly.")
        model_server = None
    else:
        model_server = AMMModelServer(DESIGN_PATH, BUILD_DIR)
        print(f"Successfully initialized model server for design: {model_server.design.name}")
except Exception as e:"""
        
        content = content.replace(old_init_section, new_init_section)
    
    # Write the updated file
    with open(mcp_server_path, 'w') as f:
        f.write(content)
    
    print("MCP server imports fixed successfully!")
    return True
    """Fix import issues in the MCP server file."""
    if not os.path.exists(mcp_server_path):
        print(f"Error: MCP server file not found at {mcp_server_path}")
        return False
    
    print(f"Fixing imports in {mcp_server_path}")
    
    # Read the file
    with open(mcp_server_path, 'r') as f:
        content = f.read()
    
    # Fix the import section
    old_import_section = """# Try different import paths to handle both direct imports and package imports
try:
    # Direct imports (when files are copied to build dir)
    from amm_engine import AMMEngine
    from amm_models import AMMDesign, AdaptiveMemoryConfig, AgentPrompts
except ImportError:
    try:
        # Package imports (when installed as a package)
        from amm_project.engine.amm_engine import AMMEngine
        from amm_project.models.amm_models import AMMDesign, AdaptiveMemoryConfig, AgentPrompts
    except ImportError as e:
        print(f"Error importing AMM modules: {e}")
        print("Please ensure the AMM modules are available in the Python path.")
        # We'll handle this gracefully when initializing the model server"""
    
    new_import_section = """# Direct imports - standalone version with all required modules in the build directory
try:
    print("Trying direct imports...")
    # Force use of local modules
    from amm_engine import AMMEngine
    from amm_models import AMMDesign, AdaptiveMemoryConfig, AgentPrompts
    from memory_models import MemoryRecord
    print("Direct imports successful!")
except ImportError as e:
    print(f"Direct import error: {e}")
    try:
        # Try package imports as fallback
        print("Trying package imports...")
        from amm_project.engine.amm_engine import AMMEngine
        from amm_project.models.amm_models import AMMDesign, AdaptiveMemoryConfig, AgentPrompts
        from amm_project.models.memory_models import MemoryRecord
        print("Package imports successful!")
    except ImportError as e:
        print(f"Error importing AMM modules: {e}")
        print("Please ensure the AMM modules are available in the Python path.")
        # The code will still try to initialize model server, which may fail gracefully"""
    
    # Replace the import section
    updated_content = content.replace(old_import_section, new_import_section)
    
    # Update SystemModelServer initialization to better handle import errors
    old_init_section = """try:
    model_server = AMMModelServer(DESIGN_PATH, BUILD_DIR)
    print(f"Successfully initialized model server for design: {model_server.design.name}")
except Exception as e:
    logger.error(f"Failed to initialize model server: {e}")
    print(f"ERROR initializing model server: {type(e).__name__} - {e}")
    # We'll initialize it lazily on first request
    model_server = None"""
    
    new_init_section = """try:
    # Verify that AMMDesign is available before trying to use it
    if 'AMMDesign' not in globals():
        print("WARNING: AMMDesign class not available. Server will not function correctly.")
        model_server = None
    else:
        model_server = AMMModelServer(DESIGN_PATH, BUILD_DIR)
        print(f"Successfully initialized model server for design: {model_server.design.name}")
except Exception as e:
    logger.error(f"Failed to initialize model server: {e}")
    print(f"ERROR initializing model server: {type(e).__name__} - {e}")
    # We'll initialize it lazily on first request
    model_server = None"""
    
    # Replace the initialization section
    updated_content = updated_content.replace(old_init_section, new_init_section)
    
    # Write the updated file
    with open(mcp_server_path, 'w') as f:
        f.write(updated_content)
    
    print("MCP server imports fixed successfully!")
    return True

def fix_amm_engine_imports(amm_engine_path):
    """Fix imports in amm_engine.py for standalone use."""
    if not os.path.exists(amm_engine_path):
        print(f"Error: AMM engine file not found at {amm_engine_path}")
        return False
    
    print(f"Fixing imports in {amm_engine_path}")
    
    # Read the file
    with open(amm_engine_path, 'r') as f:
        content = f.read()
    
    # Fix imports for standalone use - be careful with replacements to avoid duplicates
    if "try:\n    from amm_models import" not in content:
        content = content.replace(
            "from amm_project.models.amm_models import",
            "try:\n    from amm_models import\nexcept ImportError:\n    from amm_project.models.amm_models import"
        )
    
    if "try:\n    from memory_models import" not in content:
        content = content.replace(
            "from amm_project.models.memory_models import",
            "try:\n    from memory_models import\nexcept ImportError:\n    from amm_project.models.memory_models import"
        )
    
    # Check for config import too
    if "try:\n    from model_config import" not in content and "from amm_project.config.model_config import" in content:
        content = content.replace(
            "from amm_project.config.model_config import",
            "try:\n    from model_config import\nexcept ImportError:\n    from amm_project.config.model_config import"
        )
    
    # Write the updated file
    with open(amm_engine_path, 'w') as f:
        f.write(content)
    
    print("AMM engine imports fixed successfully!")
    return True

def fix_model_imports(amm_models_path):
    """Fix imports in amm_models.py for standalone use."""
    if not os.path.exists(amm_models_path):
        print(f"Error: AMM models file not found at {amm_models_path}")
        return False
    
    print(f"Fixing imports in {amm_models_path}")
    
    # Read the file
    with open(amm_models_path, 'r') as f:
        content = f.read()
    
    # Fix imports for standalone use - check if already fixed
    if "try:\n    from model_config import" not in content and "from amm_project.config.model_config import" in content:
        content = content.replace(
            "from amm_project.config.model_config import",
            "try:\n    from model_config import\nexcept ImportError:\n    from amm_project.config.model_config import"
        )
    
    # Write the updated file
    with open(amm_models_path, 'w') as f:
        f.write(content)
    
    print("AMM models imports fixed successfully!")
    return True

def fix_memory_models_imports(memory_models_path):
    """Fix imports in memory_models.py for standalone use."""
    if not os.path.exists(memory_models_path):
        print(f"Error: Memory models file not found at {memory_models_path}")
        return False
    
    print(f"Fixing imports in {memory_models_path}")
    
    # Read the file
    with open(memory_models_path, 'r') as f:
        content = f.read()
    
    # Fix imports for standalone use - check if already fixed
    if "try:\n    from amm_models import" not in content and "from amm_project.models.amm_models import" in content:
        content = content.replace(
            "from amm_project.models.amm_models import",
            "try:\n    from amm_models import\nexcept ImportError:\n    from amm_project.models.amm_models import"
        )
    
    # Write the updated file
    with open(memory_models_path, 'w') as f:
        f.write(content)
    
    print("Memory models imports fixed successfully!")
    return True

def create_init_file(directory):
    """Create __init__.py file in the directory if it doesn't exist."""
    init_file = os.path.join(directory, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, 'w') as f:
            f.write("# This file makes the directory a Python package\n")
        print(f"Created __init__.py in {directory}")

def print_help():
    """Print help information."""
    print("MCP Server Import Fixer")
    print("======================\n")
    print("This tool fixes import issues in MCP server builds.")
    print("\nUsage:")
    print("  python fix_imports.py PATH          - Fix imports in the specified directory")
    print("  python fix_imports.py --help       - Show this help message")
    print("  python fix_imports.py --version    - Show version information")
    print("\nOptions:")
    print("  --help      Show this help message and exit")
    print("  --version   Show version information and exit")
    print("\nExamples:")
    print("  python fix_imports.py ./build/my_server")
    print("  python fix_imports.py /path/to/mcp/server\n")

if __name__ == "__main__":
    # Process command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print_help()
            sys.exit(0)
        elif sys.argv[1] == "--version" or sys.argv[1] == "-v":
            print("MCP Server Import Fixer v1.0.0")
            sys.exit(0)
        else:
            target_dir = sys.argv[1]
    else:
        print_help()
        target_dir = input("\nEnter path to MCP server build directory: ")
    
    # Use absolute path
    target_dir = os.path.abspath(target_dir)
    print(f"Fixing imports in {target_dir}")
    
    # Fix all import issues
    mcp_server_path = os.path.join(target_dir, "mcp_server.py")
    amm_engine_path = os.path.join(target_dir, "amm_engine.py")
    amm_models_path = os.path.join(target_dir, "amm_models.py")
    memory_models_path = os.path.join(target_dir, "memory_models.py")
    
    # Create __init__.py
    create_init_file(target_dir)
    
    # Fix imports in all files
    fixed_mcp = fix_mcp_server_imports(mcp_server_path)
    fixed_engine = fix_amm_engine_imports(amm_engine_path)
    fixed_models = fix_model_imports(amm_models_path)
    fixed_memory = fix_memory_models_imports(memory_models_path)
    
    if fixed_mcp and fixed_engine and fixed_models and fixed_memory:
        print("\nAll imports fixed successfully!")
        print(f"Try running the server again: python {os.path.join(target_dir, 'start_server.py')} --port 8000 --host 0.0.0.0")
    else:
        print("\nSome fixes may not have been applied. Please check the errors above.")
        
    print("\nYou can also use the convenient launch script:")
    print("./start_mcp.sh")