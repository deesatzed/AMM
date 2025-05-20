#!/usr/bin/env python
"""
MCP Server Demo Script

This script provides a complete end-to-end demonstration of the MCP server:
1. Creates a sample AMM design with knowledge sources
2. Builds the AMM with MCP server support
3. Starts the MCP server
4. Provides an interactive client to test the server

Usage:
    python demo_mcp_server.py [--port PORT] [--no-server]
"""

import os
import sys
import json
import time
import argparse
import subprocess
import requests
import tempfile
import shutil
import logging
import signal
import atexit
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mcp_demo")

# Sample knowledge content
KNOWLEDGE_CONTENT = """
# Effective Communication Strategies

Effective communication is the cornerstone of successful relationships, both personal and professional. Here are some key strategies:

## Active Listening
- Give your full attention to the speaker
- Avoid interrupting
- Ask clarifying questions
- Paraphrase to confirm understanding

## Clear Messaging
- Be concise and specific
- Organize your thoughts before speaking
- Use simple language
- Avoid jargon unless necessary

## Non-verbal Communication
- Maintain appropriate eye contact
- Be aware of your body language
- Notice facial expressions
- Pay attention to tone of voice

## Feedback
- Provide constructive feedback
- Be specific about behaviors, not personality
- Focus on improvement, not criticism
- Be open to receiving feedback yourself

## Digital Communication
- Choose the appropriate medium for your message
- Be mindful of tone in written communication
- Respond in a timely manner
- Proofread before sending

Remember that communication is a two-way process that requires both expression and understanding.
"""

# Sample AMM design
DEMO_DESIGN = {
    "id": "mcp_demo_amm",
    "name": "MCP Demo Assistant",
    "description": "A demonstration AMM for the MCP server with communication knowledge",
    "knowledge_sources": [
        {
            "id": "communication_strategies",
            "name": "Communication Strategies",
            "description": "Information about effective communication techniques",
            "type": "text",
            "content": KNOWLEDGE_CONTENT
        }
    ],
    "agent_prompts": {
        "system_instruction": "You are a helpful communication assistant with knowledge about effective communication strategies. Help users improve their communication skills by providing advice, examples, and techniques based on your knowledge sources. Be friendly, concise, and practical in your responses.",
        "welcome_message": "Hello! I'm your communication assistant. I can help you improve your communication skills. What would you like to know about effective communication?"
    },
    "adaptive_memory": {
        "enabled": True,
        "retrieval_limit": 5,
        "retention_policy_days": 30
    },
    "metadata": {
        "created_by": "demo_script",
        "version": "1.0.0"
    }
}

class MCPServerDemo:
    """Demo harness for MCP server functionality."""
    
    def __init__(
        self, 
        port: int = 8000,
        start_server: bool = True
    ):
        """Initialize the demo harness.
        
        Args:
            port: Port to use for the MCP server
            start_server: Whether to start the server or just build the AMM
        """
        self.port = port
        self.start_server_flag = start_server
        self.temp_dir = Path(tempfile.mkdtemp(prefix="mcp_demo_"))
        logger.info(f"Created temporary directory: {self.temp_dir}")
        
        # Register cleanup handler
        atexit.register(self.cleanup_resources)
        
        # Set up design
        self.design = DEMO_DESIGN
        
        # Save design to temp file
        self.design_path = self.temp_dir / "demo_design.json"
        with open(self.design_path, 'w') as f:
            json.dump(self.design, f, indent=2)
        
        # Initialize other attributes
        self.build_dir = None
        self.server_process = None
        self.server_url = f"http://localhost:{self.port}"
    
    def cleanup_resources(self):
        """Clean up temporary resources."""
        if self.server_process:
            logger.info("Stopping MCP server process")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
    
    def build_amm(self) -> bool:
        """Build the AMM with MCP server support.
        
        Returns:
            bool: True if build was successful, False otherwise
        """
        print("\n" + "=" * 60)
        print("BUILDING AMM WITH MCP SERVER SUPPORT")
        print("=" * 60)
        
        try:
            # Import build_amm from the project
            sys.path.append(str(Path(__file__).parent))
            from build_amm import build_amm, BuildType
            
            # Build the AMM
            # Use goog12_requirements.txt which is available in the project
            self.build_dir = build_amm(
                design_json_path=str(self.design_path),
                output_root_dir=str(self.temp_dir / "build"),
                requirements_path=str(Path(__file__).parent / "goog12_requirements.txt"),
                build_type=BuildType.MCP_SERVER
            )
            
            print(f"\n✅ AMM built successfully at: {self.build_dir}")
            return True
        except Exception as e:
            print(f"\n❌ Error building AMM: {e}")
            return False
    
    def start_server(self) -> bool:
        """Start the MCP server.
        
        Returns:
            bool: True if server started successfully, False otherwise
        """
        if not self.build_dir:
            print("❌ Cannot start server: AMM not built")
            return False
        
        print("\n" + "=" * 60)
        print(f"STARTING MCP SERVER ON PORT {self.port}")
        print("=" * 60)
        
        try:
            # Path to run_mcp_server.py
            run_script = Path(self.build_dir) / "run_mcp_server.py"
            
            # Start the server process
            self.server_process = subprocess.Popen(
                [sys.executable, str(run_script), "--port", str(self.port), "--host", "127.0.0.1"],
                cwd=self.build_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to start
            print("Starting server...", end="", flush=True)
            for i in range(10):
                time.sleep(1)
                print(".", end="", flush=True)
                try:
                    response = requests.get(f"{self.server_url}/health")
                    if response.status_code == 200:
                        print("\n✅ Server started successfully!")
                        return True
                except requests.RequestException:
                    pass
            
            print("\n❌ Server failed to start within timeout")
            return False
        except Exception as e:
            print(f"\n❌ Error starting server: {e}")
            return False
    
    def show_server_info(self):
        """Display information about the server."""
        try:
            response = requests.get(f"{self.server_url}/info")
            response.raise_for_status()
            info = response.json()
            
            print("\n" + "=" * 60)
            print("MCP SERVER INFORMATION")
            print("=" * 60)
            print(f"Name: {info['name']}")
            print(f"Description: {info['description']}")
            print(f"Version: {info.get('version', 'N/A')}")
            print("\nCapabilities:")
            for capability, enabled in info.get('capabilities', {}).items():
                print(f"  - {capability}: {'✓' if enabled else '✗'}")
            print("\nAPI Endpoints:")
            print("  - GET /info - Get information about the AMM")
            print("  - POST /generate - Generate a response from the AMM")
            print("  - GET /health - Check if the server is running")
        except Exception as e:
            print(f"\n❌ Error getting server info: {e}")
    
    def interactive_client(self):
        """Provide an interactive client to test the server."""
        print("\n" + "=" * 60)
        print("INTERACTIVE MCP CLIENT")
        print("=" * 60)
        print("Type your queries to interact with the MCP server.")
        print("Type 'exit' to quit, 'info' to show server info, or 'curl' to show curl command.")
        
        while True:
            try:
                query = input("\n> ")
                
                if query.lower() in ('exit', 'quit'):
                    break
                elif query.lower() == 'info':
                    self.show_server_info()
                    continue
                elif query.lower() == 'curl':
                    print("\nCURL command to query the server:")
                    print(f"""curl -X POST http://localhost:{self.port}/generate \\
  -H "Content-Type: application/json" \\
  -d '{{
    "query": "What are some active listening techniques?",
    "parameters": {{}},
    "context": {{}}
  }}'""")
                    continue
                
                # Prepare request data
                request_data = {
                    "query": query,
                    "parameters": {},
                    "context": {}
                }
                
                # Send request
                print("Sending request to server...", flush=True)
                start_time = time.time()
                response = requests.post(
                    f"{self.server_url}/generate",
                    json=request_data
                )
                response.raise_for_status()
                data = response.json()
                end_time = time.time()
                
                # Print response
                print(f"\nResponse (in {end_time - start_time:.2f}s):")
                print("-" * 60)
                print(data['response'])
                print("-" * 60)
                
                # Print metadata
                if 'metadata' in data:
                    print("\nMetadata:")
                    for key, value in data['metadata'].items():
                        if key == 'knowledge_sources_used' and value:
                            print(f"  - Knowledge sources used: {len(value)}")
                        elif key == 'memory_records_used' and value:
                            print(f"  - Memory records used: {len(value)}")
                        else:
                            print(f"  - {key}: {value}")
            
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    
    def run_demo(self) -> bool:
        """Run the complete demo.
        
        Returns:
            bool: True if demo completed successfully, False otherwise
        """
        # Build the AMM
        if not self.build_amm():
            return False
        
        # Start the server if requested
        if self.start_server_flag:
            if not self.start_server():
                return False
            
            # Show server info
            self.show_server_info()
            
            # Run interactive client
            self.interactive_client()
        else:
            # Just show the build directory
            print(f"\nAMM with MCP server built at: {self.build_dir}")
            print("To start the server, run:")
            print(f"python {self.build_dir}/run_mcp_server.py --port {self.port} --host 0.0.0.0")
        
        return True

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Demonstrate MCP server functionality")
    parser.add_argument("--port", type=int, default=8000, help="Port to use for the MCP server")
    parser.add_argument("--no-server", action="store_true", help="Only build the AMM, don't start the server")
    args = parser.parse_args()
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\nExiting...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create and run demo
    demo = MCPServerDemo(
        port=args.port,
        start_server=not args.no_server
    )
    
    try:
        success = demo.run_demo()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
