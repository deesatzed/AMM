# AMM System Deployment Guide

<<<<<<< HEAD
This guide provides comprehensive instructions for deploying and running the Agno Memory Module (AMM) system, either directly from GitHub or as a local installation.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [GitHub Deployment](#github-deployment)
3. [Local Installation](#local-installation)
4. [Running the AMM Design Studio](#running-the-amm-design-studio)
5. [Building an AMM](#building-an-amm)
6. [Running an MCP Server](#running-an-mcp-server)
7. [Environment Variables](#environment-variables)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

Before deploying the AMM system, ensure you have the following:

- Python 3.11 or higher
- pip (Python package installer)
- Git (for GitHub deployment)
- Google Generative AI API key (for Gemini model access)

## GitHub Deployment

### Option 1: Clone the Repository
=======
This guide provides instructions for deploying and running the Agno Memory Module (AMM) system.

## Prerequisites

- Python 3.11 or higher
- pip (Python package installer)
- Google Generative AI API key

## Installation
>>>>>>> readme-update

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/agno-memory-module.git
   cd agno-memory-module
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   # Linux/macOS
   export API_KEY="your-google-generative-ai-api-key"
   
   # Windows (Command Prompt)
   set API_KEY=your-google-generative-ai-api-key
<<<<<<< HEAD
   
   # Windows (PowerShell)
   $env:API_KEY="your-google-generative-ai-api-key"
   ```

### Option 2: GitHub Codespaces

1. Navigate to the repository on GitHub
2. Click on the "Code" button
3. Select the "Codespaces" tab
4. Click "Create codespace on main"
5. Once the codespace is ready, set your API key as an environment variable:
   ```bash
   export API_KEY="your-google-generative-ai-api-key"
   ```

## Local Installation

1. Download the release package from GitHub:
   - Go to the Releases page
   - Download the latest release ZIP file
   - Extract the ZIP file to your desired location

2. Navigate to the extracted directory:
   ```bash
   cd path/to/extracted/folder
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   # Linux/macOS
   export API_KEY="your-google-generative-ai-api-key"
   
   # Windows (Command Prompt)
   set API_KEY=your-google-generative-ai-api-key
   
   # Windows (PowerShell)
   $env:API_KEY="your-google-generative-ai-api-key"
=======
>>>>>>> readme-update
   ```

## Running the AMM Design Studio

<<<<<<< HEAD
The AMM Design Studio is a web-based GUI for designing, building, and testing AMMs.

=======
>>>>>>> readme-update
1. Start the GUI:
   ```bash
   python run_amm_gui.py
   ```

2. Open your web browser and navigate to:
   ```
   http://localhost:8501
   ```

<<<<<<< HEAD
3. Use the interface to:
   - Create new AMM designs
   - Add knowledge sources
   - Configure agent prompts
   - Build AMMs as Python applications or MCP servers
   - Test your AMMs interactively

## Building an AMM

You can build an AMM either through the GUI or using the command line.

### Using the Command Line

#### Building as a Python Application

=======
## Building an AMM

### As a Python Application
>>>>>>> readme-update
```bash
python build_amm.py path/to/design.json output_directory --requirements requirements.txt
```

<<<<<<< HEAD
#### Building as an MCP Server

=======
### As an MCP Server
>>>>>>> readme-update
```bash
python build_amm.py path/to/design.json output_directory --requirements requirements.txt --build-type mcp_server
```

<<<<<<< HEAD
### Using the AMM Design Studio

1. Open the AMM Design Studio
2. Create or load an AMM design
3. Click on the "Build" tab
4. Select the build type (Python Application or MCP Server)
5. Click "Build AMM"

## Running an MCP Server

After building an AMM as an MCP server, you can run it as follows:

1. Navigate to the built AMM directory:
   ```bash
   cd output_directory/design_id
   ```

2. Run the server:
   ```bash
   python run_mcp_server.py
   ```

3. The server will start on the default port (8000) or an automatically selected port if 8000 is in use.

4. You can interact with the server using the following endpoints:
   - `/health`: Check if the server is running
   - `/info`: Get information about the AMM
   - `/generate`: Send queries to the AMM

### Example API Request

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"query": "Tell me about effective communication strategies"}'
```

If API key authentication is enabled:

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-mcp-api-key" \
  -d '{"query": "Tell me about effective communication strategies"}'
=======
## Running an MCP Server

```bash
cd output_directory/design_id
python run_mcp_server.py
>>>>>>> readme-update
```

## Environment Variables

<<<<<<< HEAD
The AMM system uses the following environment variables:

=======
>>>>>>> readme-update
| Variable | Description | Default |
|----------|-------------|---------|
| `API_KEY` | Google Generative AI API key | None (Required) |
| `MODEL` | Primary Gemini model | `gemini-2.5-flash-preview-04-17` |
| `MODEL2` | Secondary Gemini model | `gemini-2.5-pro-preview-05-06` |
| `EMBEDDING` | Embedding model | `models/text-embedding-004` |
<<<<<<< HEAD
| `MCP_API_KEY` | API key for MCP server authentication | None (Optional) |
| `API_KEY_REQUIRED` | Whether API key is required for MCP server | `false` |
| `MCP_PORT` | Port for the MCP server | `8000` |
| `MCP_HOST` | Host for the MCP server | `0.0.0.0` |

You can set these variables in a `.env` file in the project root directory.

## Troubleshooting

### Common Issues

#### Import Errors
If you encounter import errors, ensure that you're running the commands from the project root directory.

#### Port Binding Errors
If the MCP server fails to start due to a port binding error, it will automatically try to find an available port. You can also specify a different port using the `--port` option or the `MCP_PORT` environment variable.

#### API Key Issues
If you encounter authentication errors with the Gemini API, ensure that your API key is correctly set in the environment variables.

#### Database Errors
If you encounter database errors, ensure that the application has write permissions to the directory where it's running.

### Getting Help

If you encounter any issues not covered in this guide, please:

1. Check the [Troubleshooting Guide](docs/troubleshooting_guide.md) for more detailed solutions
2. Open an issue on the GitHub repository with a detailed description of your problem
3. Include any error messages and steps to reproduce the issue

## Additional Resources

- [AMM Architecture Guide](docs/architecture_guide.md)
- [Memory Components Guide](docs/memory_components_guide.md)
- [News Agent Guide](docs/news_agent_guide.md)
- [MCP Server Guide](docs/amm_as_mcp_server.md)
=======
| `MCP_API_KEY` | API key for MCP server | None (Optional) |
| `API_KEY_REQUIRED` | API key required | `false` |
| `MCP_PORT` | MCP server port | `8000` |
| `MCP_HOST` | MCP server host | `0.0.0.0` |
>>>>>>> readme-update
