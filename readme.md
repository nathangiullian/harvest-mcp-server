[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/taiste-harvest-mcp-server-badge.png)](https://mseep.ai/app/taiste-harvest-mcp-server)

# Harvest MCP Server

This MCP (Model Context Protocol) server provides integration with the Harvest time tracking and project management API. It allows Claude and other MCP-compatible AI assistants to interact with your Harvest account, helping you manage time entries, projects, clients, and more.

## Features

The server provides the following functionality:

### Users

- List users with filtering options
- Get user details
- List user project assignments
- List project user assignments (see who's assigned to a project)

### Time Entries
- List time entries with filtering options (user, date range, billable, running, pagination)
- Create new time entries
- Start/stop timers
- Query time entry details
- Get unsubmitted timesheets (time entries not yet submitted for approval)
- Get project-specific time entries with user aggregation and summaries (with automatic pagination)

### Enhanced Reporting & Analytics
- **Get project hours summary** - Track specific team members' hours on a project
- **Get user hours across projects** - See how a user's time is distributed
- **Get team hours summary** - Aggregate hours for multiple team members with flexible grouping
- All reporting tools feature automatic pagination and sorted results

### Projects
- List projects with filtering options
- Retrieve detailed project information
- List project task assignments (see available tasks for a project)

### Clients
- List clients with filtering options
- Retrieve detailed client information

### Tasks
- List available tasks with filtering options
- Get detailed task information
- List project-specific task assignments

### Invoices
- List invoices with filtering by client, project, date range, and state
- Get detailed invoice information

### Company
- Get company/account information and settings

## Setup Instructions

### Prerequisites
- Python 3.11 or higher
- Harvest account with API access
- Harvest API key and Account ID
- `uv` package manager (install with: `pip install uv`)

### Quick Start

**For detailed setup instructions, see [SETUP.md](SETUP.md)**

#### 1. Set System Environment Variables (Recommended)

**Windows (PowerShell):**
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

#### 2. Install Dependencies

```bash
uv pip install -r requirements.txt
```

#### 3. Add to Your Project

Copy these files to your project:
- `harvest-mcp-server.py`
- `pyproject.toml`
- `requirements.txt`
- `.gitignore`

Create `.mcp.json` in your project root:
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

#### 4. Restart Claude Code

Close and reopen Claude Code to load the MCP server.

### Using with Multiple Projects

Once system environment variables are set, you can use this MCP server across **all your projects** by simply copying the files and adding the `.mcp.json` configuration. No need to manage separate credentials!

### Integrating with Claude Desktop (Alternative)

1. Create or edit your Claude Desktop configuration file:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. Add the Harvest MCP server configuration:
   ```json
    {
        "mcpServers": {
            "harvest": {
                "command": "uv",
                "args": [
                  "run",
                  "--directory",
                  "/path/to/harvest-mcp-server",
                  "harvest-mcp-server.py"
                ],
                "env": {
                    "HARVEST_ACCOUNT_ID": "your-account-id",
                    "HARVEST_API_KEY": "your-api-key"
                }
            }
        }
    }
   ```

3. Restart Claude Desktop.

4. Verify the integration by looking for the hammer icon in Claude's interface.

## Example Queries

Once connected, you can ask Claude about your Harvest data with queries like:

### Time Tracking
- "Show me my time entries from last week"
- "Start a timer for project [project_id] and task [task_id]"
- "Get my unsubmitted timesheets from this month"
- "Show me today's time entries"

### Project & Team Management
- "List all my active projects"
- "Show me who is assigned to project [project_id]"
- "What tasks are available for project [project_id]?"
- "Get all projects that user [user_id] is assigned to"

### Reporting & Analytics
- "How many hours has [user_name] logged on project [project_id] this month?"
- "Get a summary of hours for users [user_id_1, user_id_2, user_id_3] on project [project_id] in October"
- "Break down project hours by team member for the last 30 days"
- "Show me how user [user_id]'s time is distributed across all projects"
- "Get team hours summary for users [list] grouped by project"

### Clients & Invoices
- "Show me all active clients"
- "List invoices for project [project_id]"
- "Get invoice details for invoice [invoice_id]"

### Context & Configuration
- "Show me the company information"
- "What users are in the account?"

## Workflow Tips

### Storing Project Context

For projects where you frequently query Harvest data, add project IDs to your `claude.md` file:

```markdown
# Project Context

## Harvest Information
- **Project ID**: 42405187
- **Client ID**: 15131025
- **Team Members**:
  - Nathan Giullian (5315565)
  - Courtney Wild (4964600)
  - Seth Winsor (3950214)
  - Will Smith (5274845)
  - Logan Lewis (3768448)
```

Then you can easily query: "Get hours summary for the team members listed in claude.md on this project for last month"

### Automatic Pagination

All reporting tools automatically handle pagination, fetching all results across multiple pages. This is perfect for:
- Large teams with many time entries
- Long date ranges
- Comprehensive project reports

The original `get_project_time_entries` tool now supports an `auto_paginate` parameter (default: true) for consistent behavior across all tools.

## Customization

You can modify the server code to add more functionality or customize the existing tools to better suit your workflow. The server uses FastMCP, which makes it easy to add new tools by simply adding new functions with the `@mcp.tool()` decorator.

## Troubleshooting

- **API Errors**: Make sure your Harvest API key and Account ID are correct and have the necessary permissions.
- **Connection Issues**: Verify that your Claude Desktop configuration has the correct path to the server script.
- **Missing Dependencies**: Ensure you've installed all required packages in your Python environment.

## Security Notes

This server requires your Harvest API credentials to function. Make sure to:
- Keep your API key secure
- Never commit your `.env` file or credentials to version control
- Do not share your configuration files with credentials
- Consider using a dedicated API key with limited permissions for this integration
- Use system environment variables for maximum security across projects
- The included `.gitignore` prevents sensitive files from being committed to GitHub

## For GitHub Repositories

This MCP server is designed to work with GitHub repositories:
- `.gitignore` is pre-configured to exclude sensitive files
- `.env.example` shows required variables without exposing credentials
- System environment variables work across all your repos
- No credentials stored in the repository

## Documentation

- [SETUP.md](SETUP.md) - Detailed setup instructions for all platforms
- [.env.example](.env.example) - Template for environment variables
- [.mcp.json.example](.mcp.json.example) - Example MCP configuration
