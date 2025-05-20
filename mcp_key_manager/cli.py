#!/usr/bin/env python3
"""
MCP API Key Manager (CLI Version)

A command-line tool for creating and managing MCP API keys for AMM servers.
"""

import os
import sys
import json
import secrets
import datetime
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Any

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
            return True
        except Exception as e:
            logger.error(f"Error saving keys: {e}")
            print(f"Error: Failed to save keys: {e}")
            return False
    
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

def print_key_details(key: ApiKey):
    """Print details of an API key."""
    print(f"\nKey ID: {key.key_id}")
    print(f"Name: {key.name}")
    print(f"Description: {key.description}")
    
    # Format dates
    created_at = datetime.datetime.fromisoformat(key.created_at).strftime("%Y-%m-%d %H:%M")
    print(f"Created: {created_at}")
    
    if key.expires_at:
        expires_at = datetime.datetime.fromisoformat(key.expires_at).strftime("%Y-%m-%d %H:%M")
        # Check if expired
        now = datetime.datetime.now()
        is_expired = datetime.datetime.fromisoformat(key.expires_at) < now
        
        if is_expired:
            print(f"Expires: {expires_at} (EXPIRED)")
        else:
            days_left = (datetime.datetime.fromisoformat(key.expires_at) - now).days
            print(f"Expires: {expires_at} ({days_left} days left)")
    else:
        print("Expires: Never")
    
    print(f"Status: {'Active' if key.is_active else 'Inactive'}")
    print(f"Permissions: {', '.join(key.permissions)}")
    print(f"Key Value: {key.key_value}")
    print()

def create_key(args):
    """Create a new API key."""
    key_manager = KeyManager()
    
    # Get key details
    name = args.name
    description = args.description or "Created via CLI"
    expires_in_days = args.expires_in_days
    
    # Generate the key
    api_key = key_manager.generate_key(
        name=name,
        description=description,
        expires_in_days=expires_in_days
    )
    
    print(f"\nAPI Key generated successfully: {api_key.key_id}")
    print_key_details(api_key)
    
    # Update .env file if requested
    if args.use_in_env:
        if key_manager.update_env_file(api_key.key_id):
            print("Updated .env file with this API key")
        else:
            print("Failed to update .env file")

def list_keys(args):
    """List all API keys."""
    key_manager = KeyManager()
    
    if args.active_only:
        keys = key_manager.get_active_keys()
        print(f"\nActive API Keys ({len(keys)}):")
    else:
        keys = key_manager.get_all_keys()
        print(f"\nAll API Keys ({len(keys)}):")
    
    if not keys:
        print("No keys found.")
        return
    
    for i, key in enumerate(keys, 1):
        # Format dates
        created_at = datetime.datetime.fromisoformat(key.created_at).strftime("%Y-%m-%d %H:%M")
        
        if key.expires_at:
            expires_at = datetime.datetime.fromisoformat(key.expires_at).strftime("%Y-%m-%d %H:%M")
            # Check if expired
            now = datetime.datetime.now()
            is_expired = datetime.datetime.fromisoformat(key.expires_at) < now
            
            if is_expired:
                status = "Expired"
            else:
                status = "Active" if key.is_active else "Inactive"
        else:
            expires_at = "Never"
            status = "Active" if key.is_active else "Inactive"
        
        print(f"{i}. {key.key_id} - {key.name} ({status})")
        print(f"   Created: {created_at}, Expires: {expires_at}")
        
        if args.show_keys:
            print(f"   Key: {key.key_value}")
        
        print()

def view_key(args):
    """View details of a specific API key."""
    key_manager = KeyManager()
    
    # Get the key
    if args.key_id not in key_manager.keys:
        print(f"Error: Key not found: {args.key_id}")
        return
    
    key = key_manager.keys[args.key_id]
    print_key_details(key)

def revoke_key(args):
    """Revoke an API key."""
    key_manager = KeyManager()
    
    # Revoke the key
    if key_manager.revoke_key(args.key_id):
        print(f"Successfully revoked key: {args.key_id}")
    else:
        print(f"Failed to revoke key: {args.key_id}")

def delete_key(args):
    """Delete an API key."""
    key_manager = KeyManager()
    
    # Delete the key
    if key_manager.delete_key(args.key_id):
        print(f"Successfully deleted key: {args.key_id}")
    else:
        print(f"Failed to delete key: {args.key_id}")

def use_key(args):
    """Use a key in the .env file."""
    key_manager = KeyManager()
    
    # Update the .env file
    if key_manager.update_env_file(args.key_id):
        print(f"Successfully updated .env file with key: {args.key_id}")
    else:
        print(f"Failed to update .env file with key: {args.key_id}")

def enable_api_key_requirement(args):
    """Enable API key requirement in the .env file."""
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
        
        print("API key requirement enabled in .env file")
        return True
    except Exception as e:
        print(f"Failed to update .env file: {e}")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="MCP API Key Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Create key command
    create_parser = subparsers.add_parser("create", help="Create a new API key")
    create_parser.add_argument("name", help="Name for the API key")
    create_parser.add_argument("--description", "-d", help="Description for the API key")
    create_parser.add_argument("--expires-in-days", "-e", type=int, default=90, 
                             help="Number of days until the key expires (0 for no expiration)")
    create_parser.add_argument("--use-in-env", "-u", action="store_true", 
                             help="Update the .env file with this key")
    create_parser.set_defaults(func=create_key)
    
    # List keys command
    list_parser = subparsers.add_parser("list", help="List all API keys")
    list_parser.add_argument("--active-only", "-a", action="store_true", 
                           help="Show only active keys")
    list_parser.add_argument("--show-keys", "-k", action="store_true", 
                           help="Show key values (sensitive)")
    list_parser.set_defaults(func=list_keys)
    
    # View key command
    view_parser = subparsers.add_parser("view", help="View details of a specific API key")
    view_parser.add_argument("key_id", help="ID of the key to view")
    view_parser.set_defaults(func=view_key)
    
    # Revoke key command
    revoke_parser = subparsers.add_parser("revoke", help="Revoke an API key")
    revoke_parser.add_argument("key_id", help="ID of the key to revoke")
    revoke_parser.set_defaults(func=revoke_key)
    
    # Delete key command
    delete_parser = subparsers.add_parser("delete", help="Delete an API key")
    delete_parser.add_argument("key_id", help="ID of the key to delete")
    delete_parser.set_defaults(func=delete_key)
    
    # Use key command
    use_parser = subparsers.add_parser("use", help="Use a key in the .env file")
    use_parser.add_argument("key_id", help="ID of the key to use")
    use_parser.set_defaults(func=use_key)
    
    # Enable API key requirement command
    enable_parser = subparsers.add_parser("enable-requirement", 
                                        help="Enable API key requirement in .env file")
    enable_parser.set_defaults(func=enable_api_key_requirement)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute the command
    args.func(args)

if __name__ == "__main__":
    main()
