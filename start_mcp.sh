#!/bin/bash
# Simple script to find and launch the most recently built MCP server

# Set default port
PORT=${1:-8000}

# Find the most recently modified start_server.py file
NEWEST_SERVER=$(find /home/o2satz/MyGit/AFTER_CRASH/May19_AMM/build -name "start_server.py" -type f -printf '%T@ %p\n' | sort -nr | head -n1 | cut -d' ' -f2-)

if [ -z "$NEWEST_SERVER" ]; then
    echo "No MCP server builds found."
    exit 1
fi

SERVER_DIR=$(dirname "$NEWEST_SERVER")
echo "Found MCP server at: $SERVER_DIR"
echo "Starting server on port $PORT..."

# Launch the server
cd "$SERVER_DIR" && python start_server.py --port "$PORT" --host "0.0.0.0"