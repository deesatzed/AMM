import pytest
from pydantic import ValidationError
import uuid

from amm_project.models.amm_models import (
    KnowledgeSourceType,
    GeminiModelType,
    KnowledgeSourceConfig,
    AdaptiveMemoryConfig,
    DynamicContextFunction,
    GeminiConfig,
    AgentPrompts,
    AMMDesign
)

# Helper to check if a string is a valid UUID
def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False

# Tests for KnowledgeSourceConfig
def test_knowledge_source_config_valid():
    config = KnowledgeSourceConfig(
        name="Test Source",
        type=KnowledgeSourceType.FILE,
        path="/test/path.txt"
    )
    assert config.name == "Test Source"
    assert config.type == KnowledgeSourceType.FILE
    assert config.path == "/test/path.txt"
    assert is_valid_uuid(config.id)
    assert config.description is None
    assert config.metadata == {}

def test_knowledge_source_config_missing_required():
    with pytest.raises(ValidationError):
        KnowledgeSourceConfig(type=KnowledgeSourceType.DIRECTORY, path="/another/path") # name missing
    with pytest.raises(ValidationError):
        KnowledgeSourceConfig(name="Test", path="/another/path") # type missing
    with pytest.raises(ValidationError):
        KnowledgeSourceConfig(name="Test", type=KnowledgeSourceType.FILE) # path missing

# Tests for AdaptiveMemoryConfig
def test_adaptive_memory_config_defaults():
    config = AdaptiveMemoryConfig()
    assert config.enabled is True
    assert config.db_name_prefix == "adaptive_memory_cache"
    assert config.retention_policy_days is None

def test_adaptive_memory_config_custom():
    config = AdaptiveMemoryConfig(enabled=False, db_name_prefix="custom_prefix", retention_policy_days=30)
    assert config.enabled is False
    assert config.db_name_prefix == "custom_prefix"
    assert config.retention_policy_days == 30

# Tests for DynamicContextFunction
def test_dynamic_context_function_valid():
    config = DynamicContextFunction(name="my_func", description="A test func", parameters={"key": "value"})
    assert config.name == "my_func"
    assert config.description == "A test func"
    assert config.parameters == {"key": "value"}
    assert is_valid_uuid(config.id)

def test_dynamic_context_function_missing_name():
    with pytest.raises(ValidationError):
        DynamicContextFunction(description="Test")

# Tests for GeminiConfig
def test_gemini_config_defaults():
    config = GeminiConfig()
    assert config.model_name == GeminiModelType.GEMINI_FLASH_LATEST
    assert config.api_key_env_var == "GEMINI_API_KEY"
    assert config.temperature == 0.7
    assert config.top_p is None
    assert config.top_k is None
    assert config.max_output_tokens == 2048

def test_gemini_config_invalid_temperature():
    with pytest.raises(ValidationError):
        GeminiConfig(temperature=2.0)
    with pytest.raises(ValidationError):
        GeminiConfig(temperature=-0.5)

def test_gemini_config_custom_model():
    config = GeminiConfig(model_name=GeminiModelType.GEMINI_PRO)
    assert config.model_name == GeminiModelType.GEMINI_PRO

# Tests for AgentPrompts
def test_agent_prompts_defaults():
    config = AgentPrompts()
    assert config.system_instruction == "You are a helpful AI assistant."
    assert config.welcome_message == "Hello! How can I assist you today?"

def test_agent_prompts_custom():
    config = AgentPrompts(system_instruction="Be precise.", welcome_message="Greetings!")
    assert config.system_instruction == "Be precise."
    assert config.welcome_message == "Greetings!"

# Tests for AMMDesign
def test_amm_design_minimal_valid():
    design = AMMDesign(name="My Test AMM")
    assert design.name == "My Test AMM"
    assert design.description is None
    assert design.version == "0.1.0"
    assert is_valid_uuid(design.design_id.replace("amm_design_", "")) # Check underlying UUID part
    assert design.knowledge_sources == []
    assert isinstance(design.adaptive_memory, AdaptiveMemoryConfig)
    assert design.dynamic_context_functions == []
    assert isinstance(design.gemini_config, GeminiConfig)
    assert isinstance(design.agent_prompts, AgentPrompts)
    assert design.ui_metadata == {}

def test_amm_design_missing_name():
    with pytest.raises(ValidationError):
        AMMDesign(description="A design without a name")

def test_amm_design_with_nested_configs():
    ks_config = KnowledgeSourceConfig(name="KS1", type=KnowledgeSourceType.FILE, path="/ks1.txt")
    dc_func = DynamicContextFunction(name="dc_func1")
    design = AMMDesign(
        name="Complex AMM",
        knowledge_sources=[ks_config],
        dynamic_context_functions=[dc_func]
    )
    assert len(design.knowledge_sources) == 1
    assert design.knowledge_sources[0].name == "KS1"
    assert len(design.dynamic_context_functions) == 1
    assert design.dynamic_context_functions[0].name == "dc_func1"

# To run these tests, navigate to the root directory of the project and run:
# pytest tests/unit/test_amm_models.py
