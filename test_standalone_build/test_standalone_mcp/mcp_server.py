"""
MCP Server implementation for AMM.
This file serves as a template that will be copied to the build directory.
"""

import json
import os
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from fastapi import FastAPI, Request, HTTPException, Depends, Header
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import AMM components
# Note: These imports will work in the built package
import sys
from pathlib import Path

# Add the current directory to the path to find the AMM modules
sys.path.append(str(Path(__file__).parent))

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
        # We'll handle this gracefully when initializing the model server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("amm_mcp_server")

# MCP Models
class MCPRequest(BaseModel):
    """Model for MCP requests."""
    query: str
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)

class MCPResponse(BaseModel):
    """Model for MCP responses."""
    response: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MCPStreamChunk(BaseModel):
    """Model for streaming response chunks."""
    chunk: str
    is_final: bool = False
    metadata: Optional[Dict[str, Any]] = None

class AMMModelServer:
    """Wrapper for AMM Engine that implements MCP server interface."""
    
    def __init__(self, design_path: str, build_dir: str):
        """Initialize with AMM design and build directory."""
        self.logger = logging.getLogger("amm_mcp_server")
        
        try:
            # Load design from file
            with open(design_path, 'r') as f:
                design_data = json.load(f)
                
            # Handle both 'id' and 'design_id' fields for backward compatibility
            if 'design_id' in design_data and 'id' not in design_data:
                design_data['id'] = design_data['design_id']
                print(f"Mapped 'design_id' to 'id' for compatibility: {design_data['id']}")
                
            # Ensure adaptive_memory and agent_prompts are properly initialized
            if 'adaptive_memory' not in design_data or design_data['adaptive_memory'] is None:
                design_data['adaptive_memory'] = {}
                print("Added default adaptive_memory configuration")
                
            if 'agent_prompts' not in design_data or design_data['agent_prompts'] is None:
                design_data['agent_prompts'] = {}
                print("Added default agent_prompts configuration")
                
            # Add empty metadata if not present
            if 'metadata' not in design_data:
                design_data['metadata'] = {}
                print("Added empty metadata field")
                
            # Convert back to JSON string for Pydantic validation
            design_json = json.dumps(design_data)
            self.design = AMMDesign.model_validate_json(design_json)
            
            # Initialize AMM Engine
            self.engine = AMMEngine(self.design, base_data_path=build_dir)
            self.logger.info(f"Initialized AMM Model Server for design: {self.design.name}")
        except Exception as e:
            self.logger.error(f"Failed to initialize AMM Model Server: {e}")
            # Create a minimal design for testing with proper defaults
            try:
                self.design = AMMDesign(
                    id="test_design",
                    name="Test Design",
                    description="A test design for MCP server",
                    knowledge_sources=[],
                    metadata={}
                )
                self.engine = AMMEngine(self.design, base_data_path=build_dir)
                self.logger.info("Created fallback test design for MCP server")
            except Exception as fallback_error:
                self.logger.error(f"Failed to create fallback design: {fallback_error}")
                raise
    
    async def process_request(self, request: MCPRequest) -> MCPResponse:
        """Process an MCP request and return an MCP response."""
        try:
            # Extract query from request
            query_text = request.query
            
            # Process any special parameters
            parameters = request.parameters or {}
            
            # Handle context if provided
            context = request.context or {}
            
            # Process the query using AMM engine
            result = self.engine.process_query(query_text)
            
            # Check if result is a string or a dictionary
            if isinstance(result, str):
                response_text = result
                metadata = {
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            else:
                response_text = result.get("response", str(result))
                metadata = {
                    "query_id": result.get("query_id", ""),
                    "timestamp": str(result.get("timestamp", datetime.now(timezone.utc).isoformat())),
                    "knowledge_sources_used": result.get("knowledge_sources_used", []),
                    "memory_records_used": result.get("memory_records_used", [])
                }
            
            # Format the response according to MCP standards
            response = MCPResponse(
                response=response_text,
                metadata=metadata
            )
            
            return response
        
        except Exception as e:
            # Log the error
            logger.error(f"Error processing request: {type(e).__name__} - {e}")
            # Raise HTTP exception
            raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# API Key validation (if enabled)
async def validate_api_key(
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None)
):
    """Validate API key if API_KEY_REQUIRED is set to true."""
    if os.environ.get("API_KEY_REQUIRED", "false").lower() == "true":
        api_key = os.environ.get("MCP_API_KEY")
        if not api_key:
            logger.warning("API_KEY_REQUIRED is true but MCP_API_KEY is not set")
            return
        
        # Check header
        provided_key = None
        if x_api_key:
            provided_key = x_api_key
        elif authorization and authorization.startswith("Bearer "):
            provided_key = authorization.replace("Bearer ", "")
        
        if not provided_key or provided_key != api_key:
            raise HTTPException(
                status_code=401,
                detail="Invalid API key"
            )

# Create FastAPI app
app = FastAPI(
    title="AMM MCP Server",
    description="Model Control Protocol server for Adaptive Memory Module",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Can be set to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AMM Model Server
# These paths would be configured when starting the server
DESIGN_PATH = os.environ.get("AMM_DESIGN_PATH", "design.json")
BUILD_DIR = os.environ.get("AMM_BUILD_DIR", ".")

# Print configuration for debugging
print(f"MCP Server Configuration:")
print(f"- Design Path: {DESIGN_PATH}")
print(f"- Build Directory: {BUILD_DIR}")
print(f"- Python Path: {sys.path}")

# Check if design file exists
if not Path(DESIGN_PATH).exists():
    print(f"WARNING: Design file not found at {DESIGN_PATH}")

try:
    model_server = AMMModelServer(DESIGN_PATH, BUILD_DIR)
    print(f"Successfully initialized model server for design: {model_server.design.name}")
except Exception as e:
    logger.error(f"Failed to initialize model server: {e}")
    print(f"ERROR initializing model server: {type(e).__name__} - {e}")
    # We'll initialize it lazily on first request
    model_server = None

@app.post("/generate", response_model=MCPResponse, dependencies=[Depends(validate_api_key)])
async def generate(request: MCPRequest):
    """MCP-compatible endpoint for text generation."""
    global model_server
    if model_server is None:
        try:
            print(f"Initializing model server on demand...")
            model_server = AMMModelServer(DESIGN_PATH, BUILD_DIR)
            print(f"Successfully initialized model server for design: {model_server.design.name}")
        except Exception as e:
            error_msg = f"Failed to initialize model server: {type(e).__name__} - {str(e)}"
            print(f"ERROR: {error_msg}")
            raise HTTPException(
                status_code=500, 
                detail=error_msg
            )
    
    try:
        print(f"Processing request: {request.query[:50]}...")
        response = await model_server.process_request(request)
        print(f"Successfully processed request")
        return response
    except Exception as e:
        error_msg = f"Error processing request: {type(e).__name__} - {str(e)}"
        print(f"ERROR: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/info", dependencies=[Depends(validate_api_key)])
async def info():
    """Return information about this MCP server."""
    global model_server
    if model_server is None:
        try:
            print(f"Initializing model server on demand...")
            model_server = AMMModelServer(DESIGN_PATH, BUILD_DIR)
            print(f"Successfully initialized model server for design: {model_server.design.name}")
        except Exception as e:
            error_msg = f"Failed to initialize model server: {type(e).__name__} - {str(e)}"
            print(f"ERROR: {error_msg}")
            raise HTTPException(
                status_code=500, 
                detail=error_msg
            )
    
    try:
        # Get design attributes safely
        name = getattr(model_server.design, 'name', 'Unknown')
        description = getattr(model_server.design, 'description', 'No description available')
        knowledge_sources = getattr(model_server.design, 'knowledge_sources', [])
        adaptive_memory = getattr(model_server.design, 'adaptive_memory', None)
        adaptive_memory_enabled = getattr(adaptive_memory, 'enabled', False) if adaptive_memory else False
        
        return {
            "name": name,
            "description": description,
            "version": "1.0.0",
            "capabilities": {
                "fixed_knowledge": len(knowledge_sources) > 0,
                "adaptive_memory": adaptive_memory_enabled,
                "streaming": False
            }
        }
    except Exception as e:
        error_msg = f"Error getting server info: {type(e).__name__} - {str(e)}"
        print(f"ERROR: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}

if __name__ == "__main__":
    import uvicorn
    import sys
    
    # Get port from command line or default to 8000
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    
    # Get host from environment or default to localhost
    host = os.environ.get("MCP_HOST", "127.0.0.1")
    
    print(f"Starting MCP server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)