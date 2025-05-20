"""
Unit tests for MCP server implementation.
"""
import os
import sys
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from fastapi.testclient import TestClient

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import the MCP server template
mcp_server_path = Path(__file__).parent.parent.parent / "amm_project" / "templates" / "mcp_server.py"
if not mcp_server_path.exists():
    pytest.skip(f"MCP server template not found at {mcp_server_path}", allow_module_level=True)

# Create a minimal design for testing
MINIMAL_DESIGN = {
    "id": "test_amm",
    "name": "Test AMM",
    "description": "Test AMM for MCP server",
    "knowledge_sources": [],
    "agent_prompts": {
        "system_instruction": "You are a test assistant.",
        "welcome_message": "Hello, I'm a test assistant."
    },
    "adaptive_memory": {
        "enabled": False,
        "retrieval_limit": 5,
        "retention_policy_days": 30
    }
}

# Mock the AMMEngine and AMMDesign classes
class MockAMMEngine:
    def __init__(self, design, build_dir):
        self.design = design
        self.build_dir = build_dir
    
    def process_query(self, query_text):
        return {
            "response": f"Mock response to: {query_text}",
            "query_id": "mock_query_id",
            "timestamp": "2025-05-11T12:00:00Z",
            "knowledge_sources_used": [],
            "memory_records_used": []
        }

class MockAMMDesign:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @classmethod
    def model_validate(cls, data):
        return cls(**data)

# Patch the imports in the MCP server template
@pytest.fixture
def patched_mcp_server():
    with patch.dict('sys.modules', {
        'amm_engine': MagicMock(),
        'amm_models': MagicMock()
    }):
        # Mock the imports
        sys.modules['amm_engine'].AMMEngine = MockAMMEngine
        sys.modules['amm_models'].AMMDesign = MockAMMDesign
        
        # Execute the MCP server template
        with open(mcp_server_path, 'r') as f:
            mcp_server_code = f.read()
        
        # Create a temporary module namespace
        namespace = {
            '__file__': str(mcp_server_path),
            'os': os,
            'json': json,
            'logging': MagicMock(),
            'datetime': MagicMock(),
            'timezone': MagicMock(),
            'Path': Path,
            'Dict': dict,
            'Any': object,
            'List': list,
            'Optional': type(None),
            'Union': type(None),
            'FastAPI': MagicMock(),
            'Request': MagicMock(),
            'HTTPException': MagicMock(),
            'Depends': MagicMock(),
            'Header': MagicMock(),
            'JSONResponse': MagicMock(),
            'StreamingResponse': MagicMock(),
            'CORSMiddleware': MagicMock(),
            'BaseModel': MagicMock(),
            'Field': MagicMock(),
        }
        
        # Execute the code in the namespace
        exec(mcp_server_code, namespace)
        
        # Return the app and other components
        return namespace

@pytest.fixture
def test_client(patched_mcp_server):
    # Create a test client for the FastAPI app
    app = patched_mcp_server.get('app')
    if not app:
        pytest.skip("Failed to create FastAPI app from MCP server template")
    
    # Mock the model_server
    model_server = MockAMMEngine(MockAMMDesign(**MINIMAL_DESIGN), ".")
    patched_mcp_server['model_server'] = model_server
    
    # Return the test client
    return TestClient(app)

def test_health_endpoint(test_client):
    """Test the health endpoint."""
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"
    assert "timestamp" in data

def test_info_endpoint(test_client):
    """Test the info endpoint."""
    response = test_client.get("/info")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert data["name"] == "Test AMM"
    assert "description" in data
    assert "capabilities" in data
    assert "fixed_knowledge" in data["capabilities"]
    assert "adaptive_memory" in data["capabilities"]

def test_generate_endpoint(test_client):
    """Test the generate endpoint."""
    response = test_client.post(
        "/generate",
        json={"query": "Test query", "parameters": {}, "context": {}}
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "Mock response to: Test query" in data["response"]
    assert "metadata" in data
    assert "query_id" in data["metadata"]
    assert "timestamp" in data["metadata"]

def test_generate_endpoint_error_handling(test_client, patched_mcp_server):
    """Test error handling in the generate endpoint."""
    # Mock the process_request method to raise an exception
    with patch.object(patched_mcp_server['model_server'], 'process_query', side_effect=Exception("Test error")):
        response = test_client.post(
            "/generate",
            json={"query": "Test query", "parameters": {}, "context": {}}
        )
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Error" in data["detail"]

def test_api_key_validation(patched_mcp_server):
    """Test API key validation."""
    # Set API_KEY_REQUIRED to true
    with patch.dict('os.environ', {'API_KEY_REQUIRED': 'true', 'MCP_API_KEY': 'test_key'}):
        # Create a test client
        app = patched_mcp_server.get('app')
        client = TestClient(app)
        
        # Test without API key
        response = client.get("/info")
        assert response.status_code == 401
        
        # Test with correct API key in header
        response = client.get("/info", headers={"X-API-Key": "test_key"})
        assert response.status_code == 200
        
        # Test with correct API key in Authorization header
        response = client.get("/info", headers={"Authorization": "Bearer test_key"})
        assert response.status_code == 200
        
        # Test with incorrect API key
        response = client.get("/info", headers={"X-API-Key": "wrong_key"})
        assert response.status_code == 401

def test_build_amm_with_mcp_server():
    """Test building an AMM with MCP server option."""
    from build_amm import build_amm, BuildType
    
    # Create a temporary design file
    design_json = json.dumps(MINIMAL_DESIGN)
    
    # Mock the file operations
    with patch('builtins.open', mock_open(read_data=design_json)), \
         patch('pathlib.Path.mkdir'), \
         patch('shutil.copy'), \
         patch('shutil.copy2'), \
         patch('build_amm.write_run_amm'):
        
        # Call build_amm with MCP_SERVER build type
        output_path = build_amm(
            design_json_path="test_design.json",
            output_root_dir="test_output",
            requirements_path="test_requirements.txt",
            build_type=BuildType.MCP_SERVER
        )
        
        # Check that the output path is returned
        assert output_path is not None
        assert "test_output" in output_path
        assert "test_amm" in output_path
