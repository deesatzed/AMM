# AMM System - May 19, 2025 Version

This is a clean, organized version of the Agno Memory Module (AMM) System, prepared on May 19, 2025. The AMM system is a framework for building AI agents with fixed knowledge and adaptive memory capabilities, leveraging Google's Generative AI (Gemini) models.

## Project Structure

```
May19_AMM/
├── amm_project/            # Core AMM library
│   ├── config/             # Configuration utilities
│   ├── engine/             # Core processing engine
│   ├── models/             # Data models and schemas
│   └── templates/          # Templates for MCP server
├── amm_gui/                # Streamlit GUI for AMM design
│   ├── components/         # UI components
│   └── utils/              # GUI utilities
├── mcp_key_manager/        # API key management tools
├── tests/                  # Test suite
│   └── unit/               # Unit tests
├── docs/                   # Documentation
├── knowledge_files/        # Sample knowledge files
└── designs/                # Sample AMM designs
```

## Setup Instructions

### Using Conda (Recommended)

```bash
# Create the conda environment
conda env create -f environment.yml

# Activate the environment
conda activate mcp-env

# Create a .env file from the example
cp .env.example .env
# Edit .env with your API keys
```

### Running the Application

```bash
# Start the AMM Design Studio
python run_amm_gui.py

# Run the demo MCP server
python demo_mcp_server.py

# Run the MCP Key Manager
python run_mcp_key_manager.py
```

### Testing

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/unit/test_amm_engine.py
```

## Key Components

1. **AMM Engine** - The core processing engine that handles query processing, knowledge retrieval, and adaptive memory
2. **AMM Design Studio** - A Streamlit-based GUI for designing and building AMMs
3. **MCP Server** - A FastAPI-based server that exposes AMMs as standardized APIs
4. **MCP Key Manager** - A tool for creating and managing API keys for MCP servers

## Important Notes

- This version uses the `mcp-env` conda environment as specified
- No mock processes or placeholders are included
- All files are organized for optimal clarity and maintainability
- Documentation is included in the `docs/` directory

## Contact

For support or questions, please contact the AMM development team.