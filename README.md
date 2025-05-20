# Agno Memory Module (AMM) System

The Agno Memory Module (AMM) System is a powerful framework for building AI agents with fixed knowledge and adaptive memory capabilities. It leverages Google's Generative AI (Gemini) models to create intelligent agents that can access knowledge sources and learn from interactions.

## 🚀 Features

- **Fixed Knowledge**: Store and retrieve structured knowledge using vector embeddings
- **PDF Knowledge Sources**: Support for text extraction and chunking from PDF documents
- **Adaptive Memory**: Maintain conversation history and learn from interactions
- **MCP Server**: Deploy as a FastAPI-based microservice
- **Web GUI**: Built with Streamlit for easy interaction
- **Key Management**: Secure API key management for MCP server
- **MCP Server Manager**: Launch and manage MCP servers directly from the GUI
- **CLI Tools**: Command-line tools for server and knowledge management
- **Modular Design**: Easily extensible architecture for custom components
- **GitHub-Ready Packaging**: Modular components designed for easy integration

## 📦 Installation

### Prerequisites
- Python 3.9+
- pip (Python package manager)
- [Poetry](https://python-poetry.org/) (recommended)
- Google Cloud account with Gemini API access

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/agno-memory-module.git
   cd agno-memory-module
   ```

2. **Set up a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   # Using pip
   pip install -r requirements.txt
   
   # Or using Poetry (recommended)
   poetry install
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

5. **Initialize the database**
   ```bash
   python -m agno.cli db-init
   ```

6. **Run tests**
   ```bash
   # Run MCP component tests
   ./run_mcp_tests.py
   
   # Run all tests
   python -m unittest discover tests
   ```

## 🏃‍♂️ Quick Start Guide

### MCP Server Features

Our MCP server implementation includes:

- **Standalone Operation**: All required modules included in the build directory
- **Import Fix Script**: Automatically fixes import issues in builds
- **CLI Tool**: Comprehensive command-line interface for server management
- **GUI Integration**: Powerful GUI for managing MCP servers from the Test tab
- **Network Binding**: Binds to all interfaces by default (0.0.0.0)
- **Interactive Mode**: Command-line interface with menu-driven operation
- **Comprehensive Tests**: Unit tests for all MCP server components

### Running the Demo

1. **Start the AMM Server**
   ```bash
   # Development server
   python -m agno.server
   
   # Or with hot reload
   uvicorn agno.server:app --reload
   ```

2. **Access the Web UI**
   ```bash
   streamlit run agno/gui/app.py
   ```
   Then open http://localhost:8501 in your browser.

### Basic Usage

#### Using the Python API

```python
from agno import AMMEngine
from agno.models import AMMDesign

# Initialize the engine
design = AMMDesign(
    name="my_agent",
    description="A sample AMM agent"
)
engine = AMMEngine(design)

# Process a query
response = engine.process_query("What is the capital of France?")
print(response)
```

#### Using the CLI

```bash
# Start an interactive session
python -m agno.cli chat

# Process a single query
python -m agno.cli query "Your question here"
```

## 🔑 API Key Management

To create and manage API keys for your MCP servers:

```bash
# Create a new API key and update your .env file
python mcp_key_manager/cli.py create "Production Key" --description "Key for production use" --use-in-env

# List all your API keys
python mcp_key_manager/cli.py list

# View details of a specific key
python mcp_key_manager/cli.py view <key_id>
```

## 🧪 Testing

The AMM project includes comprehensive tests for all components:

```bash
# Run MCP component tests
./run_mcp_tests.py

# Run with verbose output
./run_mcp_tests.py --verbose

# Run specific test modules
python -m unittest tests/unit/test_mcp_cli.py

# Run all tests in the project
python -m unittest discover tests
```

See the [Running Tests Guide](docs/running_tests_guide.md) for more detailed instructions.

## 🧩 Project Structure

```
agno-memory-module/
├── agno/                    # Core AMM package
│   ├── core/               # Core functionality
│   ├── models/             # Data models
│   ├── utils/              # Utility functions
│   ├── cli/                # Command-line interface
│   └── gui/                # Web interface
├── docs/                   # Documentation
├── tests/                  # Test suite
├── .env.example           # Example environment variables
├── pyproject.toml         # Project metadata and dependencies
└── README.md              # This file
```

## 📚 Documentation

For more detailed information, refer to the following guides:

- [Deployment Guide](DEPLOYMENT_GUIDE.md) - How to deploy AMM in production
- [Architecture Guide](docs/architecture_guide.md) - System architecture overview
- [Memory Components](docs/memory_components_guide.md) - Working with fixed and adaptive memory
- [PDF Knowledge Guide](docs/pdf_knowledge_guide.md) - Working with PDF knowledge sources
- [MCP Server Guide](docs/amm_as_mcp_server.md) - Running AMM as an MCP server
- [Troubleshooting](docs/troubleshooting_guide.md) - Common issues and solutions
- [MCP Server Testing](docs/mcp_server_testing_guide.md) - Testing MCP servers with the GUI
- [Running Tests](docs/running_tests_guide.md) - Guide to running all tests
- [Testing MCP Components](docs/testing_mcp_components.md) - Unit testing the MCP components

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on how to submit pull requests and report issues.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google's Gemini API for powerful language models
- The open-source community for valuable libraries and tools
- All contributors who have helped improve this project
