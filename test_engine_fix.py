#!/usr/bin/env python3
"""
Test script to verify the AMM engine fixes work correctly.
"""

import sys
from pathlib import Path
import json

# Add the project root to the Python path
project_root = Path(__file__).parent.resolve()
sys.path.append(str(project_root))

# Import the necessary classes
from amm_project.models.amm_models import AMMDesign
from amm_project.engine.amm_engine import AMMEngine

def main():
    """Test the AMM engine with a simple design."""
    print("Creating test AMM design...")
    
    # Ensure amm_instances directory exists
    amm_instances_dir = project_root / "amm_instances"
    amm_instances_dir.mkdir(exist_ok=True)
    print(f"Ensured amm_instances directory exists: {amm_instances_dir}")
    
    # Create a simple test design
    design = AMMDesign(
        id="test_engine_fix",
        name="Test Engine Fix",
        description="Testing the fixed AMM engine",
        knowledge_sources=[],
        gemini_config={
            "model_name": "gemini-pro",
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048
        },
        agent_prompts={
            "system_instruction": "You are a helpful assistant.",
            "welcome_message": "Hello! How can I help you?"
        },
        adaptive_memory={
            "enabled": True,
            "retrieval_limit": 5,
            "retention_policy_days": 30
        },
        metadata={},
        ui_metadata={}
    )
    
    print(f"Created design: {design.name} (ID: {design.design_id})")
    
    try:
        # Create AMM engine instance
        print("Initializing AMM engine...")
        engine = AMMEngine(design=design)
        print("AMM engine initialized successfully!")
        
        # Test processing a query
        query = "Tell me about the AMM project."
        print(f"Processing test query: '{query}'")
        response = engine.process_query(query)
        print("\n--- Response ---\n")
        print(response)
        print("\n--- End Response ---\n")
        
        print("Test completed successfully!")
        return True
    except Exception as e:
        print(f"Error during test: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)