# AMM System Architecture Guide

This document provides a detailed explanation of the Adaptive Memory Module (AMM) system architecture, component interactions, and implementation details.

## System Overview

The AMM system is built on a modular architecture that separates concerns into distinct components:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  AMM Design     │────▶│  AMM Build      │────▶│  AMM Runtime    │
│  Studio         │     │  System         │     │  Environment    │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Core Components

### 1. AMM Models (`amm_project/models/`)

The foundation of the system is a set of Pydantic models that define the structure and validation rules for AMM designs:

#### Key Models:

- **AMMDesign**: The root model containing all AMM configuration
- **KnowledgeSource**: Defines sources of fixed knowledge
- **AdaptiveMemory**: Configuration for the memory subsystem
- **AgentPrompts**: System and user prompts for the AI model

```python
# Example from amm_models.py
class AMMDesign(BaseModel):
    """Main model representing an AMM design."""
    id: str
    name: str
    description: str
    knowledge_sources: List[KnowledgeSource] = []
    adaptive_memory: AdaptiveMemory = Field(default_factory=AdaptiveMemory)
    agent_prompts: AgentPrompts = Field(default_factory=AgentPrompts)
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

### 2. AMM Engine (`amm_project/engine/`)

The core processing logic that handles:

- Query processing
- Fixed knowledge retrieval
- Adaptive memory management
- AI model interaction

#### Key Components:

- **AMMEngine**: Main class that orchestrates all components
- **Memory Models**: SQLAlchemy ORM models for adaptive memory
- **Embedding Functions**: Utilities for text embedding

```python
# Example from amm_engine.py
class AMMEngine:
    """Core engine for AMM processing."""
    
    def __init__(self, design: AMMDesign, build_dir: str):
        self.design = design
        self.build_dir = build_dir
        # Initialize components
        self._initialize_paths()
        self._initialize_logger()
        self._initialize_client()
        self._initialize_fixed_knowledge()
        self._initialize_adaptive_memory()
    
    def process_query(self, query_text: str) -> Dict[str, Any]:
        """Process a user query and return a response."""
        # Core query processing logic
        # ...
```

### 3. AMM Build System (`build_amm.py`)

Responsible for packaging AMM designs into standalone, runnable distributions:

- Validates AMM design
- Processes and embeds knowledge sources
- Creates directory structure
- Generates run scripts

```python
# Example from build_amm.py
def build_amm(design_json_path, output_root_dir, requirements_path):
    """Build a runnable AMM package from a design JSON."""
    # Load and validate design
    design_dict = json.loads(Path(design_json_path).read_text())
    design = AMMDesign.model_validate(design_dict)
    
    # Create build directory
    build_dir = Path(output_root_dir) / design.id
    build_dir.mkdir(parents=True, exist_ok=True)
    
    # Process knowledge sources
    # ...
    
    # Generate run script
    # ...
    
    return str(build_dir)
```

### 4. AMM Design Studio (`amm_gui/`)

A Streamlit-based web application for designing and testing AMMs:

- Visual design interface
- Knowledge source management
- Interactive testing
- Build integration

```python
# Example from app.py
def build_amm_from_design():
    """Build the AMM from the current design."""
    # Save design to temporary JSON
    design_json = st.session_state.design.model_dump_json(indent=2)
    temp_design_path = Path("temp_design.json")
    temp_design_path.write_text(design_json)
    
    # Call build_amm function
    build_dir = build_amm(str(temp_design_path), "builds", "requirements.txt")
    
    # Initialize engine for testing
    engine = AMMEngine(st.session_state.design, build_dir)
    st.session_state.engine = engine
```

## Data Flow

### 1. Design Phase

```
User Input → AMM Design Studio → AMMDesign Model → Design JSON
```

### 2. Build Phase

```
Design JSON → Build System → Process Knowledge → Create Directory Structure → Runnable AMM
```

### 3. Runtime Phase

```
User Query → AMMEngine → Retrieve Knowledge/Memory → AI Model → Response
```

## Memory Subsystems

The AMM system integrates three complementary memory components (see the Memory Components Guide for details):

1. **Fixed Knowledge**: LanceDB-based vector database
2. **Dynamic Context**: Frequently updated external files
3. **Adaptive Memory**: SQLite database with SQLAlchemy ORM

## Environment Configuration

The system uses environment variables for flexible configuration:

```
API_KEY=your-gemini-api-key
MODEL=gemini-2.5-flash-preview-04-17
MODEL2=gemini-2.5-pro-preview-05-06
EMBEDDING=models/text-embedding-004
```

This allows for:
- Different models for different tasks
- Easy switching between development and production environments
- Secure API key management

## Error Handling and Logging

The system implements comprehensive error handling and logging:

```python
# Example error handling pattern
try:
    # Operation that might fail
    result = some_operation()
except Exception as e:
    self.logger.error(f"Error in operation: {type(e).__name__} - {e}")
    # Graceful fallback
    result = default_value
```

Logging is configured with different levels:
- DEBUG: Detailed information for debugging
- INFO: Confirmation of expected behavior
- WARNING: Indication of potential issues
- ERROR: Runtime errors that don't halt execution
- CRITICAL: Severe errors that may cause program failure

## Testing Framework

The system includes a comprehensive testing framework:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete workflows

```python
# Example test from test_amm_engine.py
def test_process_query_placeholder(mock_client, minimal_design):
    """Test that process_query works with placeholder implementation."""
    engine = AMMEngine(minimal_design, "/tmp/test_build")
    engine.gemini_client = mock_client
    
    # Configure mock
    mock_client.generate_content.return_value.text = "Test response"
    
    # Call method under test
    result = engine.process_query("Test query")
    
    # Assertions
    assert result["response"] == "Test response"
    assert "query_id" in result
    assert "timestamp" in result
```

## Security Considerations

The AMM system implements several security best practices:

1. **API Key Management**: Keys stored in environment variables, not in code
2. **Input Validation**: Pydantic models validate all inputs
3. **Error Handling**: Exceptions caught and logged without exposing internals
4. **Dependency Management**: Explicit versioning of dependencies

## Performance Optimization

Several strategies are employed to optimize performance:

1. **Embedding Caching**: Avoid redundant embedding generation
2. **Query Batching**: Batch similar operations where possible
3. **Async Processing**: Use asynchronous operations for I/O-bound tasks
4. **Selective Retrieval**: Only retrieve relevant knowledge chunks

## Extensibility Points

The system is designed with several extension points:

1. **Custom Knowledge Sources**: Add new knowledge source types
2. **Alternative Vector Databases**: Replace LanceDB with alternatives
3. **Different AI Models**: Switch between different Gemini models or other providers
4. **Custom Retrieval Strategies**: Implement domain-specific retrieval logic

## Deployment Considerations

When deploying AMM systems to production, consider:

1. **Scaling**: How to handle multiple concurrent users
2. **Monitoring**: Tracking system health and performance
3. **Updates**: Strategies for updating knowledge sources
4. **Backup**: Ensuring adaptive memory is properly backed up
5. **Cost Management**: Optimizing API usage to control costs

## Best Practices for Developers

1. **Follow the Model-First Approach**: Start with well-defined Pydantic models
2. **Test Incrementally**: Build comprehensive tests as you develop
3. **Handle Errors Gracefully**: Implement robust error handling
4. **Document As You Go**: Maintain clear documentation
5. **Consider Performance Early**: Design with performance in mind
6. **Respect Privacy**: Be mindful of data storage and retention

## Future Directions

Potential areas for system enhancement:

1. **Multi-Modal Support**: Extend to handle images, audio, and video
2. **Federated Learning**: Distributed learning across multiple AMM instances
3. **Advanced Caching**: More sophisticated caching strategies
4. **Explainability**: Tools to understand why specific knowledge was retrieved
5. **User Feedback Loop**: Incorporate user feedback to improve retrieval
