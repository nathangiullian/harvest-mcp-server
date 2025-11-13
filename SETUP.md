# Harvest MCP Server Setup Guide

This guide will help you add the Harvest MCP server to any of your projects.

## Prerequisites

- Python 3.11 or higher
- `uv` (Python package manager) - Install with: `pip install uv`
- Harvest API credentials (Account ID and API Key)

## Step 1: Set System Environment Variables

### Windows (PowerShell - Persistent)
```powershell
# Set system-level environment variables (requires admin)
[System.Environment]::SetEnvironmentVariable('HARVEST_ACCOUNT_ID', 'your-account-id', 'User')
[System.Environment]::SetEnvironmentVariable('HARVEST_API_KEY', 'your-api-key', 'User')
```

### Windows (PowerShell - Current Session Only)
```powershell
$env:HARVEST_ACCOUNT_ID = "your-account-id"
$env:HARVEST_API_KEY = "your-api-key"
```

### Windows (Command Prompt - Persistent)
```cmd
setx HARVEST_ACCOUNT_ID "your-account-id"
setx HARVEST_API_KEY "your-api-key"
```

### macOS/Linux (Bash - Persistent)
Add to `~/.bashrc` or `~/.zshrc`:
```bash
export HARVEST_ACCOUNT_ID="your-account-id"
export HARVEST_API_KEY="your-api-key"
```

Then reload:
```bash
source ~/.bashrc  # or source ~/.zshrc
```

### Verify Environment Variables
```bash
# Windows PowerShell
echo $env:HARVEST_ACCOUNT_ID
echo $env:HARVEST_API_KEY

# Windows CMD
echo %HARVEST_ACCOUNT_ID%
echo %HARVEST_API_KEY%

# macOS/Linux
echo $HARVEST_ACCOUNT_ID
echo $HARVEST_API_KEY
```

## Step 2: Copy Files to Your Project

Copy these files to your project (recommended location: project root or a `mcp-servers` subdirectory):

```
your-project/
├── .mcp.json                    # MCP configuration
├── harvest-mcp-server.py        # Main server file
├── pyproject.toml               # Python dependencies
├── requirements.txt             # Alternative dependency list
└── .gitignore                   # Important: prevent committing sensitive files
```

## Step 3: Install Dependencies

Navigate to where you placed the MCP server files and run:

```bash
# Using uv (recommended)
uv pip install -r requirements.txt

# Or using pip
pip install -r requirements.txt
```

## Step 4: Configure MCP in Your Project

Create or update `.mcp.json` in your project root:

```json
{
  "mcpServers": {
    "harvest": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "run",
        "harvest-mcp-server.py"
      ]
    }
  }
}
```

If you placed the server files in a subdirectory, update the path:

```json
{
  "mcpServers": {
    "harvest": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "run",
        "mcp-servers/harvest-mcp-server.py"
      ]
    }
  }
}
```

## Step 5: Test the Server

Restart Claude Code to load the MCP server. You should now have access to these Harvest tools:

- `list_users` - List all users
- `get_user_details` - Get details for a specific user
- `list_time_entries` - List time entries with filtering
- `create_time_entry` - Create a new time entry
- `start_timer` - Start a new timer
- `stop_timer` - Stop a running timer
- `list_projects` - List projects
- `get_project_details` - Get project details
- `get_project_time_entries` - Get time entries for a specific project (with aggregation)
- `list_clients` - List clients
- `get_client_details` - Get client details
- `list_tasks` - List tasks
- `get_unsubmitted_timesheets` - Get unsubmitted timesheets

## For GitHub Repositories

### Important: Security

1. **Never commit your API credentials** to version control
2. The `.gitignore` file will prevent `.env` files from being committed
3. Always use environment variables or `.env` files (which are gitignored)
4. Add `.env.example` to show others what variables are needed

### Create .env.example (Optional)

If team members want to use `.env` files instead of system variables:

```bash
# .env.example
HARVEST_ACCOUNT_ID=your-account-id-here
HARVEST_API_KEY=your-api-key-here
```

Team members can copy this to `.env` and fill in their credentials.

## Troubleshooting

### Server doesn't start
- Verify environment variables are set correctly
- Check that Python 3.11+ is installed
- Ensure all dependencies are installed

### "Missing Harvest API credentials" error
- Environment variables may not be set in the current session
- Try restarting your terminal/IDE after setting environment variables
- On Windows, you may need to restart after using `setx`

### MCP server not showing up in Claude Code
- Verify `.mcp.json` is in the project root
- Check that the path to `harvest-mcp-server.py` is correct
- Restart Claude Code completely (close all windows)

## Getting Harvest API Credentials

1. Log in to your Harvest account
2. Go to **Settings** → **Integrations** → **Authorized Apps**
3. Create a new personal access token
4. Copy your Account ID and API Token

## Alternative: Using .env Files (Not Recommended for Multiple Projects)

If you prefer to use `.env` files per project:

1. Create a `.env` file in your project root:
   ```
   HARVEST_ACCOUNT_ID=your-account-id
   HARVEST_API_KEY=your-api-key
   ```

2. Make sure `.env` is in your `.gitignore`

**Note:** This requires managing `.env` files in every project, which is why system environment variables are recommended.
