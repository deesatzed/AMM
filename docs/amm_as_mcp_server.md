# AMM as MCP Server Guide

This guide explains how to adapt a built AMM to function as an MCP (Model Control Protocol) server, allowing other applications to interact with it through a standardized API.

## Overview

The Model Control Protocol provides a standardized way for applications to interact with AI models and services. By implementing an MCP server interface for AMMs, we can enable seamless integration with a wide range of applications, including IDEs, productivity tools, and other software that supports the MCP standard.

## Implementation Approach

### 1. Create an MCP Server Wrapper

First, we'll create a wrapper that adapts the AMM Engine to the MCP server interface:

```python
# mcp_server.py
import json
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from amm_project.engine.amm_engine import AMMEngine
from amm_project.models.amm_models import AMMDesign

class MCPRequest(BaseModel):
    """Model for MCP requests."""
    query: str
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)

class MCPResponse(BaseModel):
    """Model for MCP responses."""
    response: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AMMModelServer:
    """Wrapper for AMM Engine that implements MCP server interface."""
    
    def __init__(self, design_path: str, build_dir: str):
        """Initialize with AMM design and build directory."""
        # Load the AMM design
        with open(design_path, 'r') as f:
            design_dict = json.load(f)
        
        self.design = AMMDesign.model_validate(design_dict)
        self.build_dir = build_dir
        
        # Initialize the AMM engine
        self.engine = AMMEngine(self.design, self.build_dir)
        print(f"Initialized AMM Engine for design: {self.design.name}")
    
    async def process_request(self, request: MCPRequest) -> MCPResponse:
        """Process an MCP request and return an MCP response."""
        try:
            # Extract query from request
            query_text = request.query
            
            # Process any special parameters or context
            # (e.g., add context to adaptive memory, filter knowledge sources)
            
            # Process the query using AMM engine
            result = self.engine.process_query(query_text)
            
            # Format the response according to MCP standards
            response = MCPResponse(
                response=result["response"],
                metadata={
                    "query_id": result.get("query_id", ""),
                    "timestamp": str(result.get("timestamp", "")),
                    "knowledge_sources_used": result.get("knowledge_sources_used", []),
                    "memory_records_used": result.get("memory_records_used", [])
                }
            )
            
            return response
        
        except Exception as e:
            # Log the error
            print(f"Error processing request: {type(e).__name__} - {e}")
            # Raise HTTP exception
            raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# Create FastAPI app
app = FastAPI(title="AMM MCP Server")

# Initialize AMM Model Server
# These paths would be configured when starting the server
DESIGN_PATH = os.environ.get("AMM_DESIGN_PATH", "path/to/design.json")
BUILD_DIR = os.environ.get("AMM_BUILD_DIR", "path/to/build_dir")
model_server = AMMModelServer(DESIGN_PATH, BUILD_DIR)

@app.post("/generate", response_model=MCPResponse)
async def generate(request: MCPRequest):
    """MCP-compatible endpoint for text generation."""
    response = await model_server.process_request(request)
    return response

@app.get("/info")
async def info():
    """Return information about this MCP server."""
    return {
        "name": model_server.design.name,
        "description": model_server.design.description,
        "version": "1.0.0",
        "capabilities": {
            "fixed_knowledge": len(model_server.design.knowledge_sources) > 0,
            "adaptive_memory": model_server.design.adaptive_memory.enabled,
            "streaming": False
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 2. Add to the AMM Build Process

Modify the AMM build process to include the MCP server wrapper:

```python
# In build_amm.py

def build_amm(design_json_path, output_root_dir, requirements_path):
    # ... existing build code ...
    
    # Add MCP server files
    shutil.copy("templates/mcp_server.py", build_dir / "mcp_server.py")
    
    # Add MCP server requirements
    with open(build_dir / "requirements.txt", "a") as f:
        f.write("\n# MCP Server Requirements\nfastapi>=0.95.0\nuvicorn>=0.22.0\n")
    
    # Create MCP server run script
    with open(build_dir / "run_mcp_server.py", "w") as f:
        f.write("""
import os
import sys
from pathlib import Path

# Set environment variables
os.environ["AMM_DESIGN_PATH"] = str(Path(__file__).parent / "design.json")
os.environ["AMM_BUILD_DIR"] = str(Path(__file__).parent)

# Run the MCP server
from mcp_server import app
import uvicorn

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    uvicorn.run(app, host="0.0.0.0", port=port)
""")
    
    # ... rest of build code ...
```

## Using the AMM MCP Server

### 1. Starting the Server

Once built, the AMM MCP server can be started with:

```bash
cd builds/adaptive_news_agent/
python run_mcp_server.py 8000
```

This will start the server on port 8000.

### 2. Client Integration

Applications can interact with the AMM through standard HTTP requests:

```python
# Example client code
import requests
import json

def query_amm(text):
    response = requests.post(
        "http://localhost:8000/generate",
        headers={"Content-Type": "application/json"},
        data=json.dumps({
            "query": text,
            "parameters": {},
            "context": {}
        })
    )
    return response.json()

# Example usage
result = query_amm("What's the latest news on AI?")
print(result["response"])
```

### 3. Integration with MCP-Compatible Applications

Many applications that support the MCP standard can now directly connect to your AMM:

1. Configure the application to use a custom MCP server
2. Point it to your AMM MCP server URL (e.g., `http://localhost:8000`)
3. The application will automatically discover the capabilities through the `/info` endpoint
4. Queries from the application will be processed by your AMM

## Advanced MCP Features

### API Key Management

The AMM system includes a dedicated MCP Key Manager tool for creating and managing API keys. This tool provides:

- Secure key generation with cryptographic randomness
- Key lifecycle management (creation, rotation, revocation)
- Automatic expiration dates for better security
- Environment file integration

See the [MCP Key Manager Guide](mcp_key_manager_guide.md) for detailed usage instructions.

### API Key Authentication

The MCP server supports API key authentication to secure your endpoints. This is managed through the MCP Key Manager tool included with the AMM system.

#### Creating and Managing API Keys

```bash
# Create a new API key and update your .env file
python mcp_key_manager/cli.py create "Production Key" --description "Key for production use" --use-in-env

# List all your API keys
python mcp_key_manager/cli.py list

# View details of a specific key
python mcp_key_manager/cli.py view <key_id>

# Revoke a key when it's no longer needed
python mcp_key_manager/cli.py revoke <key_id>
```

For more details, see the [MCP Key Manager Guide](mcp_key_manager_guide.md).

#### Client Authentication

Clients must include the API key in their requests using one of these methods:

```bash
# Using X-API-Key header
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-mcp-api-key" \
  -d '{"query": "Your query here"}'

# Or using Bearer authentication
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-mcp-api-key" \
  -d '{"query": "Your query here"}'
```

### Streaming Responses

For a more interactive experience, implement streaming responses:

```python
@app.post("/generate_stream")
async def generate_stream(request: MCPRequest):
    """Stream responses chunk by chunk."""
    # Implementation would depend on modifying the AMM engine
    # to support streaming generation
    pass
```

### Multiple Models

Support multiple AMMs in a single MCP server:

```python
@app.post("/models/{model_id}/generate")
async def generate_with_model(model_id: str, request: MCPRequest):
    """Generate text using a specific model."""
    # Load the appropriate AMM based on model_id
    pass
```

### Context Windows

Support for maintaining conversation context:

```python
@app.post("/conversations")
async def create_conversation():
    """Create a new conversation with context."""
    pass

@app.post("/conversations/{conversation_id}/generate")
async def generate_in_conversation(conversation_id: str, request: MCPRequest):
    """Generate text within a specific conversation context."""
    pass
```

## Security Considerations

When deploying an AMM as an MCP server, consider these security measures:

1. **Authentication**: Add API key or OAuth authentication
2. **Rate Limiting**: Prevent abuse with rate limits
3. **Input Validation**: Thoroughly validate all inputs
4. **HTTPS**: Use HTTPS for all communications
5. **Access Control**: Implement role-based access control

## Performance Optimization

For production deployments:

1. **Worker Processes**: Use multiple worker processes with Gunicorn
2. **Caching**: Implement response caching for common queries
3. **Connection Pooling**: Use connection pooling for database access
4. **Monitoring**: Add Prometheus metrics for monitoring

## Example Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy the AMM package
COPY ./builds/adaptive_news_agent/ /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port
EXPOSE 8000

# Run the MCP server
CMD ["python", "run_mcp_server.py"]
```

## Conclusion

By implementing an MCP server interface for your AMM, you create a standardized way for applications to interact with your intelligent agent. This approach provides flexibility, interoperability, and a path to wider adoption of your AMM across different platforms and use cases.
