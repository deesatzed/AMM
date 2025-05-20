#!/usr/bin/env python
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
            print(f"
AMM: {result}
")
        except KeyboardInterrupt:
            print("
Exiting...")
            break
        except Exception as e:
            print(f"Error processing query: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
