# Quick Reference: Adding Harvest MCP to Your GitHub Projects

## Files to Copy to Each Project

```
harvest-mcp-server.py    # Main server
pyproject.toml           # Dependencies
requirements.txt         # Dependencies (alternative)
.gitignore              # Security (prevents committing secrets)
```

## In Each Project

### 1. Copy Files
Copy the 4 files above to your project root (or a subdirectory like `mcp-servers/`)

### 2. Install Dependencies
```bash
uv pip install -r requirements.txt
```

### 3. Create .mcp.json
Create `.mcp.json` in project root:

```json
{
  "mcpServers": {
    "harvest": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "harvest-mcp-server.py"]
    }
  }
}
```

If files are in a subdirectory:
```json
{
  "mcpServers": {
    "harvest": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "mcp-servers/harvest-mcp-server.py"]
    }
  }
}
```

### 4. Restart Claude Code
Close and reopen Claude Code

## One-Time Setup (System Environment Variables)

Set these **once** on your system:

**Windows (PowerShell - Run as Admin):**
```powershell
[System.Environment]::SetEnvironmentVariable('HARVEST_ACCOUNT_ID', 'your-account-id', 'User')
[System.Environment]::SetEnvironmentVariable('HARVEST_API_KEY', 'your-api-key', 'User')
```

**macOS/Linux:**
Add to `~/.bashrc` or `~/.zshrc`:
```bash
export HARVEST_ACCOUNT_ID="your-account-id"
export HARVEST_API_KEY="your-api-key"
```

Then: `source ~/.bashrc`

## That's It!

Once environment variables are set, every project just needs:
1. Copy 4 files
2. Create `.mcp.json`
3. Restart Claude Code

No credentials to manage per-project!

## Available Tools

- `list_users`, `get_user_details`
- `list_time_entries`, `create_time_entry`
- `start_timer`, `stop_timer`
- `list_projects`, `get_project_details`
- `get_project_time_entries` (with user aggregation)
- `list_clients`, `get_client_details`
- `list_tasks`
- `get_unsubmitted_timesheets`
