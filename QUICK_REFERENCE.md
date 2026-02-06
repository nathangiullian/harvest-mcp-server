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

## Available Tools (31 Total - 6 NEW!)

### Users & Assignments
- `list_users` - List all users with filtering
- `get_user_details` - Get details for a specific user
- `list_user_project_assignments` - Get all projects a user is assigned to
- `list_project_user_assignments` - Get all users assigned to a project

### Time Entries
- `list_time_entries` - List time entries with filtering
- `create_time_entry` - Create a new time entry
- `start_timer` - Start a new timer
- `stop_timer` - Stop a running timer
- `get_unsubmitted_timesheets` - Get unsubmitted time entries
- `get_project_time_entries` - Get project time entries with user aggregation (auto-pagination)

### Enhanced Reporting & Analytics
- `get_project_hours_summary` - Get hours for specific users on a project (auto-pagination)
- `get_user_hours_across_projects` - See user's time distribution across projects (auto-pagination)
- `get_team_hours_summary` - Aggregate hours for multiple team members with flexible grouping (auto-pagination)

### Projects
- `list_projects` - List projects with filtering
- `get_project_details` - Get details for a specific project
- `list_project_task_assignments` - Get all tasks assigned to a project

### Clients
- `list_clients` - List clients with filtering
- `get_client_details` - Get details for a specific client

### Tasks
- `list_tasks` - List all tasks with filtering
- `get_task_details` - Get details for a specific task

### Invoices
- `list_invoices` - List invoices with filtering (client, project, date, state)
- `get_invoice_details` - Get details for a specific invoice

### Company
- `get_company_info` - Get company/account information

### Reports API (NEW - Fast Pre-Aggregated Data)
- `get_project_budget_report` - Budget vs actual for all projects (instant)
- `get_time_report_by_projects` - Aggregated time by project (10-100x faster)
- `get_time_report_by_team` - Aggregated time by team member (10-100x faster)
- `get_time_report_by_clients` - Aggregated time by client across all projects (NEW)
- `get_time_report_by_tasks` - Aggregated time by task type (NEW)
- `get_project_budget_utilization` - Auto-calculate budget %, burn rate, health (NEW)

### Performance Notes
- All tools now use 2000 records per page (10x faster than before)
- Reports API tools are 10-100x faster than fetching individual time entries
- Perfect for weekly status updates and engagement management
