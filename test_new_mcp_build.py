#!/usr/bin/env python
"""
Test script to verify the updated MCP server build process.
"""

import os
import sys
import json
import time
import subprocess
import requests
from pathlib import Path
from build_amm import build_amm, BuildType

def main():
    print("\n" + "=" * 60)
    print("TESTING UPDATED MCP SERVER BUILD")
    print("=" * 60)
    
    # Create a minimal test design
    print("Creating test design...")
    test_design = {
        "id": "test_standalone_mcp",
        "name": "Test Standalone MCP Build",
        "description": "Test design for standalone MCP server build",
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
    
    test_design_path = Path("./test_standalone_design.json")
    with open(test_design_path, "w") as f:
        json.dump(test_design, f, indent=2)
    
    # Create a test build output directory
    output_dir = Path("./test_standalone_build")
    output_dir.mkdir(exist_ok=True)
    
    try:
        # Build with MCP server build type
        print("\nBuilding standalone MCP server...")
        build_path = build_amm(
            design_json_path=str(test_design_path),
            output_root_dir=str(output_dir),
            build_type=BuildType.MCP_SERVER
        )
        
        # Verify build output
        build_dir = Path(build_path)
        print(f"\nVerifying build files in: {build_dir}")
        
        required_files = [
            "design.json",
            "mcp_server.py",
            "run_mcp_server.py",
            "start_server.py",  # New wrapper script
            "amm_models.py",    # Standalone modules
            "memory_models.py",
            "amm_engine.py",
            "model_config.py"
        ]
        
        missing_files = []
        for file in required_files:
            if not (build_dir / file).exists():
                missing_files.append(file)
        
        if missing_files:
            print(f"❌ Missing required files: {', '.join(missing_files)}")
            return False
        else:
            print("✓ All required files are present")
        
        # Start the server using the wrapper script
        print("\nStarting MCP server using wrapper script...")
        wrapper_script = build_dir / "start_server.py"
        print(f"Wrapper script path: {wrapper_script} (exists: {wrapper_script.exists()})")
        
        server_process = subprocess.Popen(
            [sys.executable, str(wrapper_script), "--port", "8765", "--host", "127.0.0.1"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(build_dir)
        )
        
        # Start a thread to print server output
        import threading
        def print_output():
            while server_process.poll() is None:
                line = server_process.stdout.readline()
                if line:
                    print(f"SERVER: {line.strip()}")
                line = server_process.stderr.readline()
                if line:
                    print(f"SERVER ERROR: {line.strip()}")
        
        output_thread = threading.Thread(target=print_output)
        output_thread.daemon = True
        output_thread.start()
        
        # Wait for server to start
        print("Waiting for server to start...", end="", flush=True)
        server_url = "http://127.0.0.1:8765"
        
        for _ in range(10):
            time.sleep(1)
            print(".", end="", flush=True)
            try:
                response = requests.get(f"{server_url}/health")
                if response.status_code == 200:
                    print("\n✓ Server started successfully!")
                    
                    # Test a query
                    print("\nTesting query...")
                    query_response = requests.post(
                        f"{server_url}/generate",
                        json={"query": "Hello, are you working?", "parameters": {}, "context": {}}
                    )
                    
                    if query_response.status_code == 200:
                        print("✓ Query successful!")
                        print(f"Response: {query_response.json()['response'][:100]}...")
                    else:
                        print(f"❌ Query failed with status code: {query_response.status_code}")
                        
                    break
            except requests.RequestException:
                pass
        else:
            print("\n❌ Server failed to start within timeout")
            return False
        
        # Clean up
        print("\nStopping server...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
            
        print("\n✅ Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {type(e).__name__} - {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up test files
        if test_design_path.exists():
            test_design_path.unlink()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)