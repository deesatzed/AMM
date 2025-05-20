"""
AMM Integration Utilities
------------------------
Functions for integrating the GUI with the AMM build system and engine.
"""
import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

# Add the parent directory to sys.path to import AMM modules
parent_dir = Path(__file__).parent.parent.parent
sys.path.append(str(parent_dir))

# Import AMM modules
try:
    from amm_project.engine.amm_engine import AMMEngine
    from amm_project.models.amm_models import AMMDesign
    from build_amm import build_amm, BuildType
except ImportError as e:
    print(f"Error importing AMM modules: {e}")


def validate_amm_design(design_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate an AMM design against the Pydantic schema.
    
    Args:
        design_data: Dictionary containing the AMM design data
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    try:
        # Validate using Pydantic model
        AMMDesign(**design_data)
        return True, []
    except Exception as e:
        # Extract error messages
        error_str = str(e)
        error_lines = error_str.split('\n')
        return False, error_lines


def build_amm_package(design_data: Dict[str, Any], output_dir: str) -> Tuple[bool, str]:
    """
    Build an AMM package from a design.
    
    Args:
        design_data: Dictionary containing the AMM design data
        output_dir: Directory where the built AMM will be saved
        
    Returns:
        Tuple of (success, message)
    """
    # First validate the design
    is_valid, errors = validate_amm_design(design_data)
    if not is_valid:
        return False, f"Design validation failed: {'; '.join(errors)}"
    
    # Save design to a temporary file
    temp_design_path = Path(parent_dir) / "temp" / f"{design_data['id']}_design.json"
    temp_design_path.parent.mkdir(exist_ok=True)
    
    with open(temp_design_path, "w") as f:
        json.dump(design_data, f, indent=2)
    
    try:
        # Call the build_amm function
        output_path = build_amm(
            design_path=str(temp_design_path),
            output_dir=output_dir
        )
        return True, f"AMM built successfully at: {output_path}"
    except Exception as e:
        return False, f"Error building AMM: {str(e)}"


def test_amm_query(design_data: Dict[str, Any], query: str) -> Tuple[bool, str]:
    """
    Test a query against an AMM design without building it.
    
    Args:
        design_data: Dictionary containing the AMM design data
        query: The query to test
        
    Returns:
        Tuple of (success, response)
    """
    try:
        # Create a temporary design
        design = AMMDesign(**design_data)
        
        # Initialize the engine
        engine = AMMEngine(design=design)
        
        # Process the query
        response = engine.process_query(query)
        return True, response
    except Exception as e:
        return False, f"Error processing query: {str(e)}"


def get_environment_status() -> Dict[str, Any]:
    """
    Get the status of the AMM environment.
    
    Returns:
        Dictionary with environment information
    """
    status = {
        "gemini_api_key_set": bool(os.environ.get("GEMINI_API_KEY")),
        "python_version": sys.version,
        "amm_modules_available": True
    }
    
    try:
        import google.generativeai
        status["google_ai_version"] = google.generativeai.__version__
    except (ImportError, AttributeError):
        status["google_ai_version"] = "Not available"
    
    try:
        import lancedb
        status["lancedb_version"] = lancedb.__version__
    except (ImportError, AttributeError):
        status["lancedb_version"] = "Not available"
    
    return status


def get_build_types():
    """
    Get the available build types for AMM packages.
    
    Returns:
        Enum class with available build types
    """
    try:
        # Import BuildType from build_amm.py
        from build_amm import BuildType
        return BuildType
    except ImportError:
        # Fallback if import fails
        from enum import Enum
        
        class FallbackBuildType(str, Enum):
            """Fallback build types if import fails."""
            PYTHON_APP = "python_app"
            MCP_SERVER = "mcp_server"
        
        return FallbackBuildType
