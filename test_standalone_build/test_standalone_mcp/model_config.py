"""
Model Configuration
------------------
Configuration for AI models used in the AMM system.
Loads model names from environment variables when available.
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Default models (fallbacks if not in environment)
DEFAULT_MODEL = "gemini-1.5-pro"
DEFAULT_EMBEDDING_MODEL = "models/text-embedding-004"

# Get models from environment variables
CURRENT_MODELS = {
    # Main models
    "default": os.environ.get("MODEL", DEFAULT_MODEL),
    "secondary": os.environ.get("MODEL2", "gemini-2.5-pro-preview-05-06"),
    
    # Embedding models
    "embedding": os.environ.get("EMBEDDING", DEFAULT_EMBEDDING_MODEL),
    
    # Special purpose models
    "image_generation": os.environ.get("IMAGE_MODEL", "imagen-3.0-generate-002"),
    "video_generation": os.environ.get("VIDEO_MODEL", "veo-2.0-generate-001"),
}

# Model capabilities and descriptions
MODEL_CAPABILITIES = {
    "gemini-2.5-flash-preview-04-17": {
        "inputs": ["Audio", "Images", "Videos", "Text"],
        "outputs": ["Text"],
        "optimized_for": "Adaptive thinking, cost efficiency"
    },
    "gemini-2.5-pro-preview-05-06": {
        "inputs": ["Audio", "Images", "Videos", "Text"],
        "outputs": ["Text"],
        "optimized_for": "Enhanced thinking and reasoning, multimodal understanding, advanced coding"
    },
    "gemini-2.0-flash": {
        "inputs": ["Audio", "Images", "Videos", "Text"],
        "outputs": ["Text"],
        "optimized_for": "Next generation features, speed, thinking, and realtime streaming"
    },
    "gemini-2.0-flash-preview-image-generation": {
        "inputs": ["Audio", "Images", "Videos", "Text"],
        "outputs": ["Text", "Images"],
        "optimized_for": "Conversational image generation and editing"
    },
    "gemini-2.0-flash-lite": {
        "inputs": ["Audio", "Images", "Videos", "Text"],
        "outputs": ["Text"],
        "optimized_for": "Cost efficiency and low latency"
    },
    "gemini-1.5-flash": {
        "inputs": ["Audio", "Images", "Videos", "Text"],
        "outputs": ["Text"],
        "optimized_for": "Fast and versatile performance across a diverse variety of tasks"
    },
    "gemini-1.5-flash-8b": {
        "inputs": ["Audio", "Images", "Videos", "Text"],
        "outputs": ["Text"],
        "optimized_for": "High volume and lower intelligence tasks"
    },
    "gemini-1.5-pro": {
        "inputs": ["Audio", "Images", "Videos", "Text"],
        "outputs": ["Text"],
        "optimized_for": "Complex reasoning tasks requiring more intelligence"
    },
    "gemini-embedding-exp": {
        "inputs": ["Text"],
        "outputs": ["Text embeddings"],
        "optimized_for": "Measuring the relatedness of text strings"
    },
    "imagen-3.0-generate-002": {
        "inputs": ["Text"],
        "outputs": ["Images"],
        "optimized_for": "High quality image generation"
    },
    "veo-2.0-generate-001": {
        "inputs": ["Text", "Images"],
        "outputs": ["Video"],
        "optimized_for": "High quality video generation"
    }
}

def get_recommended_model(task_type: str) -> str:
    """
    Get the recommended model for a specific task type.
    
    Args:
        task_type: The type of task (e.g., 'chat', 'embedding', 'image_generation')
        
    Returns:
        The recommended model name
    """
    task_to_model = {
        "chat": CURRENT_MODELS["default"],
        "embedding": CURRENT_MODELS["embedding"],
        "image_generation": CURRENT_MODELS["image_generation"],
        "video_generation": CURRENT_MODELS["video_generation"],
        "reasoning": CURRENT_MODELS["secondary"],
        "coding": CURRENT_MODELS["secondary"],
    }
    
    return task_to_model.get(task_type, CURRENT_MODELS["default"])

def get_model_info(model_name: str) -> Dict[str, Any]:
    """
    Get information about a specific model.
    
    Args:
        model_name: The name of the model
        
    Returns:
        Dictionary with model information
    """
    return MODEL_CAPABILITIES.get(model_name, {
        "inputs": ["Text"],
        "outputs": ["Text"],
        "optimized_for": "Unknown"
    })
