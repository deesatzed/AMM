#!/usr/bin/env python3
"""
Build News Agent AMM
-------------------
Script to build the Adaptive News Briefing & Research Agent AMM package.
"""
import os
import sys
import argparse
from pathlib import Path

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the build_amm function
try:
    from build_amm import build_amm, BuildType
except ImportError:
    print("Error: Could not import build_amm. Make sure you're in the correct environment.")
    sys.exit(1)

def main():
    """Build the News Agent AMM package."""
    parser = argparse.ArgumentParser(description="Build the Adaptive News Briefing & Research Agent AMM")
    parser.add_argument("--design", default="designs/news_briefing_agent.json", help="Path to the AMM design JSON file")
    parser.add_argument("--output", default="build_news_agent", help="Output directory for the built AMM")
    parser.add_argument("--requirements", default=None, help="Path to requirements.txt file")
    parser.add_argument("--build-type", choices=["python_app", "mcp_server"], default="python_app",
                      help="Type of build to create")
    args = parser.parse_args()
    
    design_path = Path(args.design)
    output_dir = args.output
    requirements_path = args.requirements
    build_type = BuildType(args.build_type)
    
    # Check if the design file exists
    if not design_path.exists():
        print(f"Error: Design file not found at {design_path}")
        sys.exit(1)
    
    print(f"Building News Agent AMM from design: {design_path}")
    print(f"Output directory: {output_dir}")
    print(f"Build type: {build_type}")
    
    try:
        # Build the AMM
        output_path = build_amm(
            design_json_path=str(design_path),
            output_root_dir=output_dir,
            requirements_path=requirements_path,
            build_type=build_type
        )
        
        print(f"\nBuild successful! AMM package created at: {output_path}")
        print("\nTo run the AMM, use the following command:")
        print(f"cd {output_path} && python run_amm.py")
    except Exception as e:
        print(f"Error building AMM: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()