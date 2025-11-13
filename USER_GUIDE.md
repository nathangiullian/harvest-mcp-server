# Harvest MCP Server - User Guide

## What is This?

The Harvest MCP Server allows you to interact with your Harvest time tracking account through Claude (or other AI assistants that support the Model Context Protocol). Instead of logging into Harvest's web interface, you can manage your time entries, view projects, and track time through natural conversation.

## Prerequisites

Before you begin, you'll need:

1. **A Harvest account** with API access
2. **Harvest API credentials**:
   - Account ID
   - Personal Access Token (API Key)
3. **Python 3.11 or higher** installed on your computer
4. **Claude Desktop** (if integrating with Claude)

## Getting Your Harvest API Credentials

1. Log into your Harvest account at https://id.getharvest.com/
2. Go to **Settings** → **Developers**
3. Click **Create New Personal Access Token**
4. Give it a descriptive name (e.g., "Claude MCP Integration")
5. Copy the token immediately (you won't be able to see it again!)
6. Your Account ID is visible on the same page

## Installation

### Option 1: Using uv (Recommended)

**Check if you have uv installed:**
```bash
uv --version
```

**If you need to install uv:**

On macOS/Linux:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

On Windows (PowerShell):
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

After installation, restart your terminal, then:

```bash
# The project is already configured - just run it!
uv run harvest-mcp-server.py
```

### Option 2: Using pip

```bash
# Create a virtual environment
python -m venv .venv

# Activate it
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python harvest-mcp-server.py
```

## Integrating with Claude Desktop

### Step 1: Locate Your Claude Config File

The configuration file location depends on your operating system:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### Step 2: Edit the Configuration

Open the file in a text editor and add the Harvest server configuration. If the file doesn't exist, create it with this content:

```json
{
  "mcpServers": {
    "harvest": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "C:\\dev\\tools\\harvest-mcp-server",
        "harvest-mcp-server.py"
      ],
      "env": {
        "HARVEST_ACCOUNT_ID": "your_account_id_here",
        "HARVEST_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

**Important**: Replace the following values:
- `C:\\dev\\tools\\harvest-mcp-server` - Update to the actual path where you cloned this repository
- `your_account_id_here` - Your Harvest Account ID
- `your_api_key_here` - Your Harvest Personal Access Token

**Note for Windows users**: Use double backslashes (`\\`) in the path, or use forward slashes (`/`).

### Step 3: Restart Claude Desktop

Close Claude Desktop completely and reopen it.

### Step 4: Verify the Connection

Look for a hammer icon (🔨) in Claude's interface - this indicates that MCP tools are available. You can ask Claude: "What Harvest tools do you have access to?"

## What You Can Do

Once connected, you can interact with Harvest using natural language. Here are the capabilities:

### Managing Time Entries

**View your time entries:**
- "Show me my time entries from last week"
- "What did I log yesterday?"
- "Show me all time entries for this month"
- "Show me only billable hours from last week"
- "What time entries are currently running?"

**Create time entries:**
- "Log 3 hours to project 12345 and task 67890 for today with notes 'Fixed bug in authentication'"
- "Create a time entry for 2.5 hours on project ABC"

**Start and stop timers:**
- "Start a timer for project 12345 and task 67890"
- "Stop timer 98765"

**Check unsubmitted timesheets:**
- "Show me my unsubmitted time entries"
- "What time entries haven't been submitted yet this month?"

### Working with Projects

**List projects:**
- "Show me all my active projects"
- "List all projects for client 123"
- "What projects am I working on?"

**Get project details:**
- "Give me details about project 456"
- "Tell me more about project XYZ"

### Managing Clients

**List clients:**
- "Show me all active clients"
- "List all my clients"

**Get client details:**
- "Get details for client 789"
- "Tell me about client ABC"

### Working with Tasks

**List tasks:**
- "Show me all available tasks"
- "What tasks can I log time to?"

### User Information

**List users:**
- "Show me all users in the account"
- "List active team members"

**Get user details:**
- "Get details for user 123"

## Tips for Best Results

1. **Be specific with dates**: Use formats like "2025-01-15" or natural language like "last Monday"
2. **Use project and task IDs**: Ask Claude to show you projects first, then use their IDs for time entries
3. **Check running timers**: Before starting a new timer, check if you have any running
4. **Review before submitting**: Use the unsubmitted timesheets feature to review your time before submitting

## Troubleshooting

### "Missing Harvest API credentials" Error

**Cause**: The environment variables aren't set correctly.

**Solution**:
- Double-check your `claude_desktop_config.json` file
- Ensure HARVEST_ACCOUNT_ID and HARVEST_API_KEY are correct
- Restart Claude Desktop after making changes

### "API Error: 401 Unauthorized"

**Cause**: Your API credentials are invalid or expired.

**Solution**:
- Verify your API key is correct
- Generate a new Personal Access Token if needed
- Update the config file and restart Claude

### "API Error: 403 Forbidden"

**Cause**: Your API token doesn't have sufficient permissions.

**Solution**:
- Check your Harvest account permissions
- Ensure you have access to the resources you're trying to query

### Claude doesn't see the Harvest tools

**Cause**: The MCP server isn't loading properly.

**Solution**:
- Check that the path in your config file is correct
- Verify `uv` is installed and in your PATH
- Look at Claude's logs (Help → View Logs) for error messages
- Try using the absolute path to the Python script

### Connection Issues

**Cause**: Various environmental issues.

**Solution**:
- Ensure Python 3.11+ is installed: `python --version`
- Test the server manually: Set environment variables and run `python harvest-mcp-server.py`
- Check firewall settings aren't blocking the connection

## Security Best Practices

1. **Keep your API key secure** - Never share it or commit it to version control
2. **Use a dedicated API token** - Create a specific token for this integration
3. **Review permissions** - Only grant the minimum necessary access
4. **Rotate tokens regularly** - Periodically generate new tokens
5. **Don't share your config file** - It contains sensitive credentials

## Advanced Usage

### Using with Other MCP Clients

This server works with any MCP-compatible client, not just Claude Desktop. The server communicates over stdio, so you can integrate it with other tools that support the Model Context Protocol.

### Customizing the Server

The server is written in Python and uses the FastMCP framework. You can add new tools by:

1. Opening `harvest-mcp-server.py`
2. Adding a new function with the `@mcp.tool()` decorator
3. Implementing your desired functionality using the `harvest_request()` helper
4. Restarting Claude Desktop

### Running in Docker

A `Dockerfile` is included in the repository if you prefer to run the server in a container.

## Getting Help

- **Harvest API Documentation**: https://help.getharvest.com/api-v2/
- **MCP Documentation**: https://modelcontextprotocol.io/
- **FastMCP Documentation**: https://github.com/jlowin/fastmcp

## Example Workflow

Here's a typical workflow to get you started:

```
You: "Show me all my active projects"
Claude: [Lists your projects with IDs]

You: "Show me available tasks"
Claude: [Lists tasks with IDs]

You: "Start a timer for project 12345 and task 67890 with notes 'Working on user guide'"
Claude: [Starts the timer and confirms]

[... do your work ...]

You: "Show me running timers"
Claude: [Shows your active timer with ID]

You: "Stop timer 99999"
Claude: [Stops the timer and shows the final time entry]

You: "Show me unsubmitted time entries for this week"
Claude: [Lists entries that haven't been submitted]
```

## Limitations

- The server reads data in real-time from Harvest's API, so responses depend on API availability
- Some advanced Harvest features (like invoicing, expenses) are not yet implemented
- Pagination is automatic but may be slow for accounts with large amounts of data
- The server requires an internet connection to access the Harvest API

## What's Next?

Once you're comfortable with the basics, you can:
- Create custom workflows by chaining multiple queries
- Use Claude to analyze your time tracking patterns
- Generate reports on your billable vs non-billable hours
- Automate routine time tracking tasks

Happy time tracking!
