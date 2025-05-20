"""
MCP API Key Manager

A web application for creating and managing MCP API keys for AMM servers.
"""

import os
import json
import secrets
import datetime
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any

import streamlit as st
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("mcp_key_manager")

# Constants
KEY_LENGTH = 32  # Length of generated API keys in bytes (will be hex encoded)
KEY_STORE_PATH = Path("mcp_key_manager/keys.json")
ENV_FILE_PATH = Path(".env")

class ApiKey:
    """Represents an API key with metadata."""
    def __init__(self, key_id, key_value, name, description, created_at, 
                expires_at=None, is_active=True, 
                permissions=None, metadata=None):
        self.key_id = key_id
        self.key_value = key_value
        self.name = name
        self.description = description
        self.created_at = created_at
        self.expires_at = expires_at
        self.is_active = is_active
        self.permissions = permissions or ["generate", "info", "health"]
        self.metadata = metadata or {}

class KeyManager:
    """Manages API keys for MCP servers."""
    
    def __init__(self, key_store_path: Path = KEY_STORE_PATH):
        self.key_store_path = key_store_path
        self.keys = self._load_keys()
        
    def _load_keys(self) -> Dict[str, ApiKey]:
        """Load keys from the key store file."""
        if not self.key_store_path.exists():
            logger.info(f"Key store not found at {self.key_store_path}. Creating new store.")
            self.key_store_path.parent.mkdir(parents=True, exist_ok=True)
            return {}
        
        try:
            with open(self.key_store_path, 'r') as f:
                keys_data = json.load(f)
                return {
                    key_id: ApiKey(
                        key_id=key_data['key_id'],
                        key_value=key_data['key_value'],
                        name=key_data['name'],
                        description=key_data['description'],
                        created_at=key_data['created_at'],
                        expires_at=key_data.get('expires_at'),
                        is_active=key_data.get('is_active', True),
                        permissions=key_data.get('permissions', ["generate", "info", "health"]),
                        metadata=key_data.get('metadata', {})
                    )
                    for key_id, key_data in keys_data.items()
                }
        except Exception as e:
            logger.error(f"Error loading keys: {e}")
            return {}
    
    def _save_keys(self):
        """Save keys to the key store file."""
        try:
            keys_data = {
                key_id: {
                    'key_id': key.key_id,
                    'key_value': key.key_value,
                    'name': key.name,
                    'description': key.description,
                    'created_at': key.created_at,
                    'expires_at': key.expires_at,
                    'is_active': key.is_active,
                    'permissions': key.permissions,
                    'metadata': key.metadata
                }
                for key_id, key in self.keys.items()
            }
            
            with open(self.key_store_path, 'w') as f:
                json.dump(keys_data, f, indent=2)
                
            logger.info(f"Saved {len(self.keys)} keys to {self.key_store_path}")
        except Exception as e:
            logger.error(f"Error saving keys: {e}")
            st.error(f"Failed to save keys: {e}")
    
    def generate_key(self, name: str, description: str, 
                    expires_in_days: Optional[int] = None,
                    permissions: Optional[List[str]] = None,
                    metadata: Optional[Dict[str, Any]] = None) -> ApiKey:
        """Generate a new API key."""
        key_id = secrets.token_hex(8)  # 16 character ID
        key_value = secrets.token_hex(KEY_LENGTH)  # 64 character key
        created_at = datetime.datetime.now().isoformat()
        
        # Calculate expiration date if provided
        expires_at = None
        if expires_in_days is not None and expires_in_days > 0:
            expiration_date = datetime.datetime.now() + datetime.timedelta(days=expires_in_days)
            expires_at = expiration_date.isoformat()
        
        # Use default permissions if none provided
        if permissions is None:
            permissions = ["generate", "info", "health"]
            
        # Create the API key
        api_key = ApiKey(
            key_id=key_id,
            key_value=key_value,
            name=name,
            description=description,
            created_at=created_at,
            expires_at=expires_at,
            is_active=True,
            permissions=permissions,
            metadata=metadata or {}
        )
        
        # Store the key
        self.keys[key_id] = api_key
        self._save_keys()
        
        logger.info(f"Generated new API key: {key_id} ({name})")
        return api_key
    
    def revoke_key(self, key_id: str) -> bool:
        """Revoke an API key."""
        if key_id not in self.keys:
            logger.warning(f"Attempted to revoke non-existent key: {key_id}")
            return False
        
        self.keys[key_id].is_active = False
        self._save_keys()
        
        logger.info(f"Revoked API key: {key_id}")
        return True
    
    def delete_key(self, key_id: str) -> bool:
        """Delete an API key."""
        if key_id not in self.keys:
            logger.warning(f"Attempted to delete non-existent key: {key_id}")
            return False
        
        del self.keys[key_id]
        self._save_keys()
        
        logger.info(f"Deleted API key: {key_id}")
        return True
    
    def get_active_keys(self) -> List[ApiKey]:
        """Get all active API keys."""
        now = datetime.datetime.now().isoformat()
        
        return [
            key for key in self.keys.values()
            if key.is_active and (key.expires_at is None or key.expires_at > now)
        ]
    
    def get_all_keys(self) -> List[ApiKey]:
        """Get all API keys."""
        return list(self.keys.values())
    
    def update_env_file(self, key_id: str) -> bool:
        """Update the .env file with the selected API key."""
        if key_id not in self.keys:
            logger.warning(f"Attempted to use non-existent key: {key_id}")
            return False
        
        key = self.keys[key_id]
        
        # Check if the key is active
        if not key.is_active:
            logger.warning(f"Attempted to use inactive key: {key_id}")
            return False
        
        # Check if the key has expired
        if key.expires_at:
            now = datetime.datetime.now().isoformat()
            if key.expires_at < now:
                logger.warning(f"Attempted to use expired key: {key_id}")
                return False
        
        try:
            # Load current .env file if it exists
            env_vars = {}
            if ENV_FILE_PATH.exists():
                with open(ENV_FILE_PATH, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key_var, value = line.split('=', 1)
                            env_vars[key_var] = value
            
            # Update MCP API key and set API_KEY_REQUIRED to true
            env_vars['MCP_API_KEY'] = key.key_value
            env_vars['API_KEY_REQUIRED'] = 'true'
            
            # Write back to .env file
            with open(ENV_FILE_PATH, 'w') as f:
                for key_var, value in env_vars.items():
                    f.write(f"{key_var}={value}\n")
            
            logger.info(f"Updated .env file with API key: {key_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error updating .env file: {e}")
            return False

def main():
    """Main application function."""
    st.set_page_config(
        page_title="MCP API Key Manager",
        page_icon="🔑",
        layout="wide"
    )
    
    st.title("MCP API Key Manager")
    st.write("Create and manage API keys for your AMM MCP servers")
    
    # Initialize key manager
    key_manager = KeyManager()
    
    # Initialize session state if needed
    if 'last_generated_key_id' not in st.session_state:
        st.session_state.last_generated_key_id = None
    
    # Create tabs for different functions
    tab1, tab2, tab3 = st.tabs(["Create Key", "Manage Keys", "Settings"])
    
    # Tab 1: Create Key
    with tab1:
        st.header("Create New API Key")
        
        # Add button outside the form to use the key in .env file
        if st.session_state.last_generated_key_id:
            if st.button("Use this key in .env file"):
                if key_manager.update_env_file(st.session_state.last_generated_key_id):
                    st.success("Updated .env file with this API key")
                    # Clear the session state to avoid confusion
                    st.session_state.last_generated_key_id = None
                else:
                    st.error("Failed to update .env file")
        
        with st.form("create_key_form"):
            name = st.text_input("Key Name", placeholder="e.g., Production API Key")
            description = st.text_area("Description", placeholder="Purpose and usage of this key")
            
            col1, col2 = st.columns(2)
            with col1:
                expires = st.checkbox("Set Expiration", value=True)
            with col2:
                if expires:
                    expires_in_days = st.number_input("Expires In (Days)", 
                                                     min_value=1, max_value=365, value=90)
                else:
                    expires_in_days = None
            
            permissions = st.multiselect(
                "Permissions",
                options=["generate", "info", "health"],
                default=["generate", "info", "health"]
            )
            
            submitted = st.form_submit_button("Generate Key")
            
            if submitted:
                if not name:
                    st.error("Key name is required")
                else:
                    api_key = key_manager.generate_key(
                        name=name,
                        description=description,
                        expires_in_days=expires_in_days,
                        permissions=permissions
                    )
                    
                    st.success(f"API Key generated successfully: {api_key.key_id}")
                    
                    # Store the key_id in session state for use outside the form
                    st.session_state.last_generated_key_id = api_key.key_id
                    
                    # Display the key details
                    st.subheader("Key Details")
                    st.code(api_key.key_value, language="text")
                    st.warning("⚠️ Make sure to copy this key now. You won't be able to see it again!")
    
    # Tab 2: Manage Keys
    with tab2:
        st.header("Manage API Keys")
        
        # Get all keys
        all_keys = key_manager.get_all_keys()
        
        if not all_keys:
            st.info("No API keys found. Create a new key in the 'Create Key' tab.")
        else:
            # Display keys in a table
            key_data = []
            for key in all_keys:
                # Format dates
                created_at = datetime.datetime.fromisoformat(key.created_at).strftime("%Y-%m-%d %H:%M")
                if key.expires_at:
                    expires_at = datetime.datetime.fromisoformat(key.expires_at).strftime("%Y-%m-%d %H:%M")
                    # Check if expired
                    now = datetime.datetime.now()
                    is_expired = datetime.datetime.fromisoformat(key.expires_at) < now
                else:
                    expires_at = "Never"
                    is_expired = False
                
                status = "Active" if key.is_active and not is_expired else "Inactive" if not key.is_active else "Expired"
                
                key_data.append({
                    "ID": key.key_id,
                    "Name": key.name,
                    "Status": status,
                    "Created": created_at,
                    "Expires": expires_at,
                    "Description": key.description
                })
            
            # Display as dataframe
            st.dataframe(key_data)
            
            # Key actions
            st.subheader("Key Actions")
            
            col1, col2 = st.columns(2)
            
            with col1:
                selected_key_id = st.selectbox(
                    "Select Key",
                    options=[key.key_id for key in all_keys],
                    format_func=lambda x: f"{x} - {next((k.name for k in all_keys if k.key_id == x), '')}"
                )
            
            with col2:
                action = st.selectbox(
                    "Action",
                    options=["View Details", "Use in .env", "Revoke Key", "Delete Key"]
                )
            
            if st.button("Execute Action"):
                selected_key = next((k for k in all_keys if k.key_id == selected_key_id), None)
                
                if selected_key:
                    if action == "View Details":
                        st.subheader(f"Key Details: {selected_key.name}")
                        st.write(f"**ID:** {selected_key.key_id}")
                        st.write(f"**Status:** {'Active' if selected_key.is_active else 'Inactive'}")
                        st.write(f"**Created:** {datetime.datetime.fromisoformat(selected_key.created_at).strftime('%Y-%m-%d %H:%M')}")
                        
                        if selected_key.expires_at:
                            expires = datetime.datetime.fromisoformat(selected_key.expires_at)
                            st.write(f"**Expires:** {expires.strftime('%Y-%m-%d %H:%M')}")
                            
                            # Show expiration warning if needed
                            days_left = (expires - datetime.datetime.now()).days
                            if days_left < 0:
                                st.error("This key has expired")
                            elif days_left < 7:
                                st.warning(f"This key will expire in {days_left} days")
                        else:
                            st.write("**Expires:** Never")
                        
                        st.write(f"**Permissions:** {', '.join(selected_key.permissions)}")
                        st.write(f"**Description:** {selected_key.description}")
                        
                        # Only show the key value for active keys
                        if selected_key.is_active:
                            if st.checkbox("Show Key Value (sensitive)"):
                                st.code(selected_key.key_value, language="text")
                    
                    elif action == "Use in .env":
                        if key_manager.update_env_file(selected_key_id):
                            st.success(f"Updated .env file with key: {selected_key.name}")
                        else:
                            st.error("Failed to update .env file")
                    
                    elif action == "Revoke Key":
                        if key_manager.revoke_key(selected_key_id):
                            st.success(f"Revoked key: {selected_key.name}")
                        else:
                            st.error("Failed to revoke key")
                    
                    elif action == "Delete Key":
                        if st.checkbox("Confirm deletion"):
                            if key_manager.delete_key(selected_key_id):
                                st.success(f"Deleted key: {selected_key.name}")
                            else:
                                st.error("Failed to delete key")
                        else:
                            st.warning("Please confirm deletion by checking the box")
    
    # Tab 3: Settings
    with tab3:
        st.header("Settings")
        
        st.subheader("Key Store Location")
        st.write(f"Keys are stored at: `{KEY_STORE_PATH.absolute()}`")
        
        st.subheader("Environment File")
        st.write(f"Environment file path: `{ENV_FILE_PATH.absolute()}`")
        
        # Check if .env file exists and if MCP_API_KEY is set
        env_exists = ENV_FILE_PATH.exists()
        mcp_key_set = False
        api_key_required = False
        
        if env_exists:
            load_dotenv(ENV_FILE_PATH)
            mcp_key = os.environ.get("MCP_API_KEY")
            mcp_key_set = mcp_key is not None and len(mcp_key) > 0
            api_key_required = os.environ.get("API_KEY_REQUIRED", "").lower() == "true"
        
        st.write(f"Environment file exists: {'✅' if env_exists else '❌'}")
        st.write(f"MCP_API_KEY is set: {'✅' if mcp_key_set else '❌'}")
        st.write(f"API_KEY_REQUIRED is enabled: {'✅' if api_key_required else '❌'}")
        
        # Option to enable API key requirement
        if st.button("Enable API Key Requirement"):
            try:
                # Load current .env file if it exists
                env_vars = {}
                if ENV_FILE_PATH.exists():
                    with open(ENV_FILE_PATH, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#') and '=' in line:
                                key_var, value = line.split('=', 1)
                                env_vars[key_var] = value
                
                # Set API_KEY_REQUIRED to true
                env_vars['API_KEY_REQUIRED'] = 'true'
                
                # Write back to .env file
                with open(ENV_FILE_PATH, 'w') as f:
                    for key_var, value in env_vars.items():
                        f.write(f"{key_var}={value}\n")
                
                st.success("API key requirement enabled in .env file")
            except Exception as e:
                st.error(f"Failed to update .env file: {e}")

if __name__ == "__main__":
    main()
