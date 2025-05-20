# MCP Key Manager Guide

The MCP Key Manager is a tool for creating and managing API keys for AMM MCP servers. It provides a secure way to control access to your MCP server endpoints and implement proper authentication.

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Command Line Interface](#command-line-interface)
4. [Key Management Best Practices](#key-management-best-practices)
5. [Integration with MCP Servers](#integration-with-mcp-servers)
6. [Troubleshooting](#troubleshooting)

## Introduction

When deploying AMMs as MCP servers, it's important to secure the API endpoints to prevent unauthorized access. The MCP Key Manager provides tools to:

- Generate cryptographically secure API keys
- Manage key lifecycles (creation, rotation, revocation)
- Enforce key expiration for better security
- Automatically update your environment configuration

## Installation

The MCP Key Manager is included with the AMM system. No additional installation is required.

## Command Line Interface

The MCP Key Manager provides a command-line interface for all key management operations.

### Creating a New API Key

```bash
python mcp_key_manager/cli.py create "Key Name" --description "Key description" [options]
```

Options:
- `--description`, `-d`: Description for the API key
- `--expires-in-days`, `-e`: Number of days until the key expires (default: 90, use 0 for no expiration)
- `--use-in-env`, `-u`: Update the .env file with this key

Example:
```bash
python mcp_key_manager/cli.py create "Production Key" --description "Key for production MCP server" --expires-in-days 90 --use-in-env
```

### Listing API Keys

```bash
python mcp_key_manager/cli.py list [options]
```

Options:
- `--active-only`, `-a`: Show only active keys
- `--show-keys`, `-k`: Show key values (sensitive)

Example:
```bash
python mcp_key_manager/cli.py list --active-only
```

### Viewing Key Details

```bash
python mcp_key_manager/cli.py view <key_id>
```

Example:
```bash
python mcp_key_manager/cli.py view fd5c5b5177095c73
```

### Revoking a Key

```bash
python mcp_key_manager/cli.py revoke <key_id>
```

Example:
```bash
python mcp_key_manager/cli.py revoke fd5c5b5177095c73
```

### Deleting a Key

```bash
python mcp_key_manager/cli.py delete <key_id>
```

Example:
```bash
python mcp_key_manager/cli.py delete fd5c5b5177095c73
```

### Using a Key in the .env File

```bash
python mcp_key_manager/cli.py use <key_id>
```

Example:
```bash
python mcp_key_manager/cli.py use fd5c5b5177095c73
```

### Enabling API Key Requirement

```bash
python mcp_key_manager/cli.py enable-requirement
```

## Key Management Best Practices

Follow these best practices for secure API key management:

1. **Regular Rotation**: Create new keys and retire old ones every 90 days
2. **Expiration Dates**: Always set an expiration date for keys (the default is 90 days)
3. **Principle of Least Privilege**: Create different keys for different purposes with appropriate permissions
4. **Secure Storage**: Keep your key store file (`mcp_key_manager/keys.json`) secure
5. **Revoke Immediately**: If a key is compromised, revoke it immediately
6. **Monitor Usage**: Regularly review which keys are active and revoke unused keys

## Integration with MCP Servers

The MCP Key Manager integrates with MCP servers through the `.env` file. When you create a key and use the `--use-in-env` option or the `use` command, it:

1. Sets the `MCP_API_KEY` environment variable to your key value
2. Sets `API_KEY_REQUIRED=true` to enforce authentication

### Client Authentication

Clients connecting to your MCP server must include the API key in their requests using one of these methods:

#### Using the X-API-Key header:

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{"query": "Your query here"}'
```

#### Using Bearer authentication:

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key-here" \
  -d '{"query": "Your query here"}'
```

## Troubleshooting

### Common Issues

#### Key Not Working

If your API key is not working:

1. Check that `API_KEY_REQUIRED=true` in your `.env` file
2. Verify that the key is active and not expired with `python mcp_key_manager/cli.py view <key_id>`
3. Ensure you're using the correct key value in your requests
4. Check that the key is being sent in the correct header format

#### Environment File Issues

If the `.env` file is not being updated:

1. Check file permissions
2. Verify the file path (default is `.env` in the project root)
3. Try manually adding the key with `python mcp_key_manager/cli.py use <key_id>`

#### Key Storage Issues

If you're having issues with the key store:

1. Check that the `mcp_key_manager` directory exists and is writable
2. Verify that `keys.json` is a valid JSON file
3. If the file is corrupted, you may need to create a new key store

For additional help, see the [Troubleshooting Guide](troubleshooting_guide.md) or open an issue on GitHub.
