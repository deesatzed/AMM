"""
AMM Design GUI - Main Application
--------------------------------
A Streamlit-based web interface for designing, building, and testing AMMs.
"""
import os
import json
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
import sys
import time
from enum import Enum

# Add components directory to path
sys.path.append(str(Path(__file__).parent))

# Import utilities
try:
    from utils.temp_manager import ensure_temp_dir, clean_temp_files, create_zip_from_dir
    from utils.amm_integration import get_build_types
except ImportError as e:
    print(f"Error importing utilities: {e}")

# Import components
try:
    from components.knowledge_source_manager import knowledge_source_manager
    from components.memory_manager import memory_manager
    from components.mcp_server_manager import mcp_server_manager
except ImportError as e:
    print(f"Error importing components: {e}")

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Get model versions from environment variables
DEFAULT_MODEL = os.environ.get('MODEL', 'gemini-2.5-flash-preview-04-17')
AVAILABLE_MODELS = [
    os.environ.get('MODEL', 'gemini-2.5-flash-preview-04-17'),
    os.environ.get('MODEL2', 'gemini-2.5-pro-preview-05-06'),
    'gemini-2.5-flash-preview-04-17',
    'gemini-2.5-pro-preview-05-06'
]
# Remove duplicates while preserving order
AVAILABLE_MODELS = list(dict.fromkeys(AVAILABLE_MODELS))

# Set page configuration
st.set_page_config(
    page_title="AMM Design Studio",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define paths
ROOT_DIR = Path(__file__).parent.parent
DESIGNS_DIR = ROOT_DIR / "designs"
DESIGNS_DIR.mkdir(exist_ok=True)

# Ensure all required directories exist
def ensure_required_directories():
    """Ensure all required directories for AMM operation exist."""
    directories = [
        ROOT_DIR / "designs",
        ROOT_DIR / "amm_instances",
        ROOT_DIR / "temp",
        ROOT_DIR / "build",
        ROOT_DIR / "knowledge_files"
    ]
    
    for directory in directories:
        directory.mkdir(exist_ok=True)
        print(f"Ensured directory exists: {directory}")

# Create required directories
ensure_required_directories()

# Ensure temp directory exists and clean old files
TEMP_DIR = ensure_temp_dir(ROOT_DIR)
clean_count = clean_temp_files(ROOT_DIR, keep_days=7)
if clean_count > 0:
    print(f"Cleaned up {clean_count} old temporary files")

# Initialize session state
if "amm_design" not in st.session_state:
    st.session_state.amm_design = {
        "id": "",
        "name": "",
        "description": "",
        "gemini_config": {
            "model_name": "gemini-2.5-pro-preview-05-06",
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048
        },
        "knowledge_sources": [],
        "agent_prompts": {
            "system_instruction": "",
            "welcome_message": ""
        },
        "adaptive_memory": {
            "enabled": True,
            "retrieval_limit": 5,
            "retention_policy_days": 30
        },
        "metadata": {},  # Initialize empty metadata dictionary
        "ui_metadata": {}  # Initialize empty UI metadata dictionary
    }

if "current_tab" not in st.session_state:
    st.session_state.current_tab = "Design"

# Sidebar navigation
st.sidebar.title("AMM Design Studio")
st.sidebar.image("https://raw.githubusercontent.com/google/generative-ai-python/main/docs/images/gemini_logo.png", width=100)

# Help section in sidebar
with st.sidebar.expander("📚 Knowledge & Memory Guide"):
    st.markdown("""
    Learn about different types of knowledge sources and memory in AMM:
    
    - **Fixed Knowledge**: Static information embedded during build
    - **Adaptive Memory**: Dynamic information from past interactions
    
    [View the complete guide](knowledge_memory_guide.md) for detailed explanations and best practices.
    """)
    
    # Display environment info
    st.divider()
    st.caption("Environment Configuration")
    st.code(f"Default Model: {DEFAULT_MODEL}\nAvailable Models: {', '.join(AVAILABLE_MODELS)}")
    
    if os.environ.get("GEMINI_API_KEY"):
        st.success("✓ GEMINI_API_KEY is set")
    else:
        st.error("✗ GEMINI_API_KEY is not set")


# Navigation
selected_tab = st.sidebar.radio(
    "Navigation",
    ["Design", "Build", "Test"],
    key="navigation"
)
st.session_state.current_tab = selected_tab

# Load and save functions
def save_design():
    """Save the current design to a JSON file"""
    if not st.session_state.amm_design["id"]:
        st.error("Please provide an ID for your AMM design before saving.")
        return False
    
    file_path = DESIGNS_DIR / f"{st.session_state.amm_design['id']}.json"
    with open(file_path, "w") as f:
        json.dump(st.session_state.amm_design, f, indent=2)
    
    st.success(f"Design saved to {file_path}")
    return True

def load_design(design_id):
    """Load a design from a JSON file"""
    file_path = DESIGNS_DIR / f"{design_id}.json"
    if not file_path.exists():
        st.error(f"Design file not found: {file_path}")
        return False
    
    with open(file_path, "r") as f:
        st.session_state.amm_design = json.load(f)
    
    st.success(f"Loaded design: {st.session_state.amm_design['name']}")
    return True

# Sidebar - Load existing design
st.sidebar.divider()
st.sidebar.subheader("Saved Designs")

# Get list of existing designs
existing_designs = [f.stem for f in DESIGNS_DIR.glob("*.json")]
if existing_designs:
    selected_design = st.sidebar.selectbox(
        "Load existing design",
        existing_designs
    )
    if st.sidebar.button("Load Selected Design"):
        load_design(selected_design)
else:
    st.sidebar.info("No saved designs found.")

# Sidebar - Save current design
st.sidebar.divider()
if st.sidebar.button("Save Current Design"):
    save_design()

# Main content area
if st.session_state.current_tab == "Design":
    st.title("Design Your AMM")
    
    # Design tabs
    design_tab = st.tabs(["Basic Info", "Gemini Config", "Knowledge Sources", "Prompts", "Adaptive Memory"])
    
    # Basic Info tab
    with design_tab[0]:
        st.header("Basic Information")
        
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.amm_design["id"] = st.text_input(
                "AMM ID",
                value=st.session_state.amm_design["id"],
                help="Unique identifier for this AMM"
            )
        
        with col2:
            st.session_state.amm_design["name"] = st.text_input(
                "AMM Name",
                value=st.session_state.amm_design["name"],
                help="Descriptive name for this AMM"
            )
        
        st.session_state.amm_design["description"] = st.text_area(
            "Description",
            value=st.session_state.amm_design["description"],
            help="Detailed description of this AMM's purpose and capabilities"
        )
    
    # Gemini Config tab
    with design_tab[1]:
        st.header("Gemini Model Configuration")
        
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.amm_design["gemini_config"]["model_name"] = st.selectbox(
                "Model",
                AVAILABLE_MODELS,
                index=AVAILABLE_MODELS.index(DEFAULT_MODEL) if DEFAULT_MODEL in AVAILABLE_MODELS else 0,
                help="Select the Gemini model to use (loaded from .env file)"
            )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.session_state.amm_design["gemini_config"]["temperature"] = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.amm_design["gemini_config"]["temperature"],
                step=0.1,
                help="Controls randomness: 0 is deterministic, 1 is creative"
            )
        
        with col2:
            st.session_state.amm_design["gemini_config"]["top_p"] = st.slider(
                "Top P",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.amm_design["gemini_config"]["top_p"],
                step=0.05,
                help="Controls diversity via nucleus sampling"
            )
        
        with col3:
            st.session_state.amm_design["gemini_config"]["top_k"] = st.slider(
                "Top K",
                min_value=1,
                max_value=100,
                value=st.session_state.amm_design["gemini_config"]["top_k"],
                step=1,
                help="Controls diversity by limiting the number of options considered"
            )
        
        st.session_state.amm_design["gemini_config"]["max_output_tokens"] = st.slider(
            "Max Output Tokens",
            min_value=1,
            max_value=8192,
            value=st.session_state.amm_design["gemini_config"]["max_output_tokens"],
            step=1,
            help="Maximum number of tokens to generate"
        )
    
    # Knowledge Sources tab
    with design_tab[2]:
        # Use the knowledge source manager component
        st.session_state.amm_design = knowledge_source_manager(st.session_state.amm_design)
    
    # Prompts tab
    with design_tab[3]:
        st.header("Agent Prompts")
        
        st.session_state.amm_design["agent_prompts"]["system_instruction"] = st.text_area(
            "System Instruction",
            value=st.session_state.amm_design["agent_prompts"]["system_instruction"],
            height=200,
            help="Instructions that define the AMM's behavior and capabilities"
        )
        
        st.session_state.amm_design["agent_prompts"]["welcome_message"] = st.text_area(
            "Welcome Message",
            value=st.session_state.amm_design["agent_prompts"]["welcome_message"],
            height=100,
            help="Message displayed when a user first interacts with the AMM"
        )
    
    # Adaptive Memory tab
    with design_tab[4]:
        # Use the memory manager component
        st.session_state.amm_design = memory_manager(st.session_state.amm_design)

elif st.session_state.current_tab == "Build":
    st.title("Build Your AMM")
    
    # Check if design is saved
    if not st.session_state.amm_design["id"]:
        st.warning("Please create and save a design before building.")
    else:
        st.write(f"Preparing to build AMM: **{st.session_state.amm_design['name']}**")
        
        # Build options
        st.subheader("Build Options")
        
        # Get build types
        build_types = get_build_types()
        
        col1, col2 = st.columns(2)
        
        with col1:
            build_dir = st.text_input(
                "Build Directory",
                value=f"build_{st.session_state.amm_design['id']}",
                help="Directory where the built AMM will be saved"
            )
        
        with col2:
            build_type = st.selectbox(
                "Build Type",
                options=[t.value for t in build_types],
                format_func=lambda x: "Python App" if x == "python_app" else "MCP Server",
                help="Type of AMM to build"
            )
        
        # MCP Server options
        if build_type == "mcp_server":
            st.subheader("MCP Server Options")
            
            mcp_col1, mcp_col2 = st.columns(2)
            
            with mcp_col1:
                mcp_port = st.number_input(
                    "Default Port",
                    min_value=1024,
                    max_value=65535,
                    value=8000,
                    help="Default port for the MCP server"
                )
            
            with mcp_col2:
                require_api_key = st.checkbox(
                    "Require API Key",
                    value=False,
                    help="Enable API key authentication for the MCP server"
                )
            
            # Show information about MCP server
            st.info("""
            **MCP Server Build**
            
            This will create an AMM that can be accessed via the Model Control Protocol (MCP).
            Applications that support MCP can connect to this server to use your AMM.
            
            The server will include:
            - FastAPI-based MCP server
            - API key authentication (optional)
            - Health check endpoint
            - Standard MCP endpoints (/generate, /info)
            """)
        
        # Build button
        if st.button("Build AMM", type="primary"):
            # Save the design to a temporary file
            temp_design_path = ensure_temp_dir(ROOT_DIR) / f"{st.session_state.amm_design['id']}_design.json"
            
            with open(temp_design_path, "w") as f:
                json.dump(st.session_state.amm_design, f, indent=2)
            
            # Create a progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Update status
            status_text.text("Preparing to build AMM...")
            progress_bar.progress(10)
            
            try:
                # Import the build_amm function
                sys.path.append(str(ROOT_DIR))
                from build_amm import build_amm, BuildType
                
                # Update status
                status_text.text("Building AMM...")
                progress_bar.progress(30)
                
                # Store MCP options in the design metadata if building MCP server
                if build_type == "mcp_server":
                    # Ensure metadata field exists
                    if "metadata" not in st.session_state.amm_design:
                        st.session_state.amm_design["metadata"] = {}
                    
                    st.session_state.amm_design["metadata"]["mcp_server"] = {
                        "port": mcp_port,
                        "require_api_key": require_api_key
                    }
                    
                    # Save updated design with metadata
                    with open(temp_design_path, "w") as f:
                        json.dump(st.session_state.amm_design, f, indent=2)
                
                # Build the AMM
                build_dir_path = ROOT_DIR / build_dir
                build_dir_path.mkdir(parents=True, exist_ok=True)
                
                output_path = build_amm(
                    design_json_path=str(temp_design_path),
                    output_root_dir=str(build_dir_path),
                    requirements_path=str(ROOT_DIR / "goog12_requirements.txt"),
                    build_type=build_type
                )
                
                # Update status
                progress_bar.progress(100)
                status_text.text("Build completed successfully!")
                
                # Check if output_path is valid
                if output_path:
                    # Success message
                    st.success(f"AMM built successfully! Output directory: {output_path}")
                else:
                    # Build completed but no path returned
                    st.success(f"AMM built successfully! Check the build directory: {build_dir_path}")
                
                # Create a zip file of the build directory for download
                status_text.text("Creating downloadable package...")
                
                # Determine the source directory for the zip
                if output_path:
                    source_dir = Path(output_path)
                else:
                    # If output_path is None, use the build_dir_path with the design_id appended
                    source_dir = build_dir_path / st.session_state.amm_design['id']
                
                # Use our utility to create the zip file
                zip_path = create_zip_from_dir(
                    source_dir=source_dir,
                    zip_name=f"{st.session_state.amm_design['id']}_build.zip"
                )
                
                # Read the zip file for download
                with open(zip_path, "rb") as f:
                    zip_data = f.read()
                
                # Download option
                st.download_button(
                    label="Download Built AMM",
                    data=zip_data,
                    file_name=f"{st.session_state.amm_design['id']}_build.zip",
                    mime="application/zip"
                )
                
                # Show run instructions
                if build_type == "python_app":
                    st.info(f"To run the AMM, navigate to {output_path} and execute: python run_amm.py")
                else:  # MCP server
                    st.info(f"""To run the AMM as an MCP server, navigate to {output_path} and execute:
                    
                    ```
                    # Recommended method (uses the wrapper script):
                    python start_server.py --port {mcp_port} --host 0.0.0.0 {" --api-key your_api_key --api-key-required" if require_api_key else ""}
                    
                    # Alternative method (legacy):
                    python run_mcp_server.py --port {mcp_port} --host 0.0.0.0 {"--require-api-key" if require_api_key else ""}
                    ```
                    
                    The MCP server will be available at http://localhost:{mcp_port}/
                    
                    API endpoints:
                    - GET /info - Get information about the AMM
                    - POST /generate - Generate a response from the AMM
                    - GET /health - Check if the server is running
                    
                    For complete documentation, see:
                    docs/MCP_SERVER_GUIDE.md
                    """)
                    
                    # Add example curl command
                    st.subheader("Example API Usage")
                    st.code(f"""
                    # Example request using curl
                    curl -X POST http://localhost:{mcp_port}/generate \
                      -H "Content-Type: application/json" \
                      -d '{{
                        "query": "What can you tell me about AI?",
                        "parameters": {{}},
                        "context": {{}}
                      }}'
                    """, language="bash")
                
            except Exception as e:
                st.error(f"Error building AMM: {str(e)}")
                st.info("Please check the console for more details.")
                print(f"Error building AMM: {e}")


elif st.session_state.current_tab == "Test":
    st.title("Test Your AMM")
    
    # Check if design is saved
    if not st.session_state.amm_design["id"]:
        st.warning("Please create and save a design before testing.")
    else:
        st.write(f"Testing AMM: **{st.session_state.amm_design['name']}**")
        
        # Add test mode selection
        test_mode = st.radio(
            "Test Mode",
            ["Direct Engine Test", "MCP Server Test"],
            index=0,
            help="Select how to test your AMM"
        )
        
        if test_mode == "MCP Server Test":
            # MCP Server test mode
            st.info("""
            **MCP Server Test Mode**
            
            This mode tests an already-built MCP server. 
            You can launch a server using the controls below or connect to an existing server.
            """)
            
            # Add the MCP server manager component
            #with st.expander("MCP Server Controls", expanded=True):
            st.subheader("MCP Server Controls")
            mcp_url = mcp_server_manager()
            
            # MCP Server connection details (if no server is running from the manager)
            if not mcp_url:
                col1, col2 = st.columns(2)
                with col1:
                    mcp_host = st.text_input("MCP Server Host", value="localhost")
                with col2:
                    mcp_port = st.number_input("MCP Server Port", value=8000, min_value=1, max_value=65535)
                
                mcp_url = f"http://{mcp_host}:{mcp_port}"
            
            # Test connection
            if st.button("Test Connection"):
                try:
                    import requests
                    response = requests.get(f"{mcp_url}/health", timeout=5)
                    if response.status_code == 200:
                        st.success(f"Successfully connected to MCP server at {mcp_url}")
                        # Get server info
                        try:
                            info_response = requests.get(f"{mcp_url}/info", timeout=5)
                            if info_response.status_code == 200:
                                info = info_response.json()
                                st.write("**Server Information:**")
                                st.write(f"- Name: {info.get('name', 'Unknown')}")
                                st.write(f"- Description: {info.get('description', 'No description')}")
                                capabilities = info.get('capabilities', {})
                                st.write("- Capabilities:")
                                st.write(f"  - Fixed Knowledge: {'✓' if capabilities.get('fixed_knowledge', False) else '✗'}")
                                st.write(f"  - Adaptive Memory: {'✓' if capabilities.get('adaptive_memory', False) else '✗'}")
                        except Exception as e:
                            st.warning(f"Connected but couldn't get server info: {e}")
                    else:
                        st.error(f"Failed to connect to MCP server: Status code {response.status_code}")
                except Exception as e:
                    st.error(f"Failed to connect to MCP server: {e}")
            
            # Initialize chat history for MCP
            if "mcp_chat_history" not in st.session_state:
                st.session_state.mcp_chat_history = []
            
            # Display chat history
            for message in st.session_state.mcp_chat_history:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
            
            # Chat input for MCP
            mcp_query = st.chat_input("Ask your MCP server a question...")
            
            if mcp_query:
                # Add user message to chat history
                st.session_state.mcp_chat_history.append({"role": "user", "content": mcp_query})
                
                # Display user message
                with st.chat_message("user"):
                    st.write(mcp_query)
                
                # Process query with MCP server
                with st.chat_message("assistant"):
                    with st.spinner("Processing query via MCP server..."):
                        try:
                            import requests
                            import json
                            
                            # Send request to MCP server
                            response = requests.post(
                                f"{mcp_url}/generate",
                                json={
                                    "query": mcp_query,
                                    "parameters": {},
                                    "context": {}
                                },
                                timeout=30
                            )
                            
                            if response.status_code == 200:
                                result = response.json()
                                response_text = result.get("response", "No response received")
                                st.write(response_text)
                                
                                # Show metadata if present
                                metadata = result.get("metadata", {})
                                if metadata and st.checkbox("Show metadata", value=False):
                                    st.json(metadata)
                                
                                # Add to chat history
                                st.session_state.mcp_chat_history.append({"role": "assistant", "content": response_text})
                            else:
                                error_message = f"Error from MCP server: Status code {response.status_code}"
                                st.error(error_message)
                                st.session_state.mcp_chat_history.append({"role": "assistant", "content": error_message})
                        except Exception as e:
                            error_message = f"Error querying MCP server: {str(e)}"
                            st.error(error_message)
                            st.session_state.mcp_chat_history.append({"role": "assistant", "content": error_message})
        
        else:
            # Direct Engine test mode - original implementation
            # Initialize chat history
            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []
            
            # Display chat history
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
            
            # Chat input
            user_query = st.chat_input("Ask your AMM a question...")
            
            if user_query:
                # Add user message to chat history
                st.session_state.chat_history.append({"role": "user", "content": user_query})
                
                # Display user message
                with st.chat_message("user"):
                    st.write(user_query)
                
                # Process query with AMMEngine
                with st.chat_message("assistant"):
                    with st.spinner("Processing query with direct engine..."):
                        try:
                            # Import AMMEngine and AMMDesign
                            sys.path.append(str(ROOT_DIR))
                            from amm_project.engine.amm_engine import AMMEngine
                            from amm_project.models.amm_models import AMMDesign
                            
                            # Check if we already have an engine instance
                            if "amm_engine" not in st.session_state:
                                # Create required directories
                                amm_instances_dir = ROOT_DIR / "amm_instances"
                                amm_instances_dir.mkdir(exist_ok=True)
                                
                                # Create a new AMMEngine instance
                                design = AMMDesign(**st.session_state.amm_design)
                                st.session_state.amm_engine = AMMEngine(design=design)
                                st.info("Initialized new AMM engine instance. Knowledge sources are being processed...")
                            
                            # Process the query
                            response = st.session_state.amm_engine.process_query(user_query)
                            st.write(response)
                        except Exception as e:
                            error_message = f"Error processing query: {str(e)}"
                            st.error(error_message)
                            response = error_message
                            print(f"Error in AMM test: {e}")
                
                # Add assistant response to chat history
                st.session_state.chat_history.append({"role": "assistant", "content": response})

# Footer
st.divider()
st.caption("AMM Design Studio - AG-Mem-Module Builder")
