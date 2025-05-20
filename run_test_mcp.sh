#!/bin/bash

# Script to test the MCP server standalone functionality

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

BUILD_DIR="$SCRIPT_DIR/test_standalone_build"
MCP_BUILD="$BUILD_DIR/test_standalone_mcp"

echo "===================================================="
echo "TESTING MCP SERVER STANDALONE MODE"
echo "===================================================="

# Create simple test design
cat > "$SCRIPT_DIR/test_standalone_design.json" << EOF
{
  "id": "test_standalone_mcp",
  "name": "Test Standalone MCP Build",
  "description": "Test design for standalone MCP server build",
  "knowledge_sources": [],
  "agent_prompts": {
    "system_instruction": "You are a helpful assistant.",
    "welcome_message": "Hello, how can I help you?"
  },
  "adaptive_memory": {
    "enabled": true,
    "retrieval_limit": 10
  },
  "metadata": {}
}
EOF

echo "Test design created: test_standalone_design.json"

# Create build directory
mkdir -p "$BUILD_DIR"

# Build MCP server
echo "Building MCP server..."
python build_amm.py test_standalone_design.json --output-dir "$BUILD_DIR" --build-type mcp_server

# Change to build directory to run server
echo "Changing to build directory..."
cd "$MCP_BUILD"

# Run server in background
echo "Starting MCP server on port 8765..."
python start_server.py --port 8765 --host 127.0.0.1 &
SERVER_PID=$!

# Wait for server to start
echo "Waiting for server to start..."
sleep 5

# Test health endpoint
echo "Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s -X GET http://localhost:8765/health)
echo "Health response: $HEALTH_RESPONSE"

# Test query
echo "Testing query..."
QUERY_RESPONSE=$(curl -s -X POST http://localhost:8765/generate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Hello, are you working?",
    "parameters": {},
    "context": {}
  }')
echo "Query response: $QUERY_RESPONSE"

# Kill server
echo "Stopping server..."
kill $SERVER_PID

# Clean up
echo "Cleaning up..."
cd "$SCRIPT_DIR"

echo "Test completed!"