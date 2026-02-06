import os
import json
import httpx
from datetime import datetime
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables from .env file if it exists (optional)
# System environment variables take precedence
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("harvest-api")

# Get environment variables for Harvest API
# Will use system environment variables if set, otherwise falls back to .env
HARVEST_ACCOUNT_ID = os.environ.get("HARVEST_ACCOUNT_ID")
HARVEST_API_KEY = os.environ.get("HARVEST_API_KEY")

if not HARVEST_ACCOUNT_ID or not HARVEST_API_KEY:
    raise ValueError(
        "Missing Harvest API credentials. Set HARVEST_ACCOUNT_ID and HARVEST_API_KEY "
        "as system environment variables or in a .env file."
    )


# Helper function to make Harvest API requests
async def harvest_request(path, params=None, method="GET"):
    headers = {
        "Harvest-Account-Id": HARVEST_ACCOUNT_ID,
        "Authorization": f"Bearer {HARVEST_API_KEY}",
        "User-Agent": "Harvest MCP Server",
        "Content-Type": "application/json",
    }

    url = f"https://api.harvestapp.com/v2/{path}"

    async with httpx.AsyncClient() as client:
        if method == "GET":
            response = await client.get(url, headers=headers, params=params)
        else:
            response = await client.request(method, url, headers=headers, json=params)

        if response.status_code != 200:
            raise Exception(
                f"Harvest API Error: {response.status_code} {response.text}"
            )

        return response.json()


# Helper function to fetch all pages of results automatically
async def harvest_request_all_pages(path, params=None):
    """Fetch all pages of results from a Harvest API endpoint.

    Args:
        path: API endpoint path
        params: Query parameters (optional)

    Returns:
        List of all items across all pages
    """
    if params is None:
        params = {}

    # Set initial page and per_page
    params["page"] = "1"
    if "per_page" not in params:
        params["per_page"] = "2000"

    all_items = []

    while True:
        response = await harvest_request(path, params)

        # Determine the key containing the items
        # Common keys: time_entries, users, projects, clients, tasks, etc.
        items_key = None
        for key in response:
            if isinstance(response[key], list):
                items_key = key
                break

        if items_key and response[items_key]:
            all_items.extend(response[items_key])

        # Check if there are more pages
        total_pages = response.get("total_pages", 1)
        current_page = response.get("page", 1)

        if current_page >= total_pages:
            break

        # Move to next page
        params["page"] = str(current_page + 1)

    return all_items


@mcp.tool()
async def list_users(is_active: bool = None, page: int = None, per_page: int = None):
    """List all users in your Harvest account.

    Args:
        is_active: Pass true to only return active users and false to return inactive users
        page: The page number for pagination
        per_page: The number of records to return per page (1-2000)
    """
    params = {}
    if is_active is not None:
        params["is_active"] = "true" if is_active else "false"
    else:
        params["is_active"] = "true"
    if page is not None:
        params["page"] = str(page)
    if per_page is not None:
        params["per_page"] = str(per_page)
    else:
        params["per_page"] = 2000

    response = await harvest_request("users", params)
    return json.dumps(response, indent=2)


@mcp.tool()
async def get_user_details(user_id: int):
    """Retrieve details for a specific user.

    Args:
        user_id: The ID of the user to retrieve
    """
    response = await harvest_request(f"users/{user_id}")
    return json.dumps(response, indent=2)


@mcp.tool()
async def list_time_entries(
    user_id: int = None,
    from_date: str = None,
    to_date: str = None,
    is_running: bool = None,
    is_billable: bool = None,
    page: int = None,
    per_page: int = None,
):
    """List time entries with optional filtering.

    Args:
        user_id: Filter by user ID
        from_date: Only return time entries with a spent_date on or after the given date (YYYY-MM-DD)
        to_date: Only return time entries with a spent_date on or before the given date (YYYY-MM-DD)
        is_running: Pass true to only return running time entries and false to return non-running time entries
        is_billable: Pass true to only return billable time entries and false to return non-billable time entries
        page: The page number for pagination
        per_page: The number of records to return per page (1-2000)
    """
    params = {}
    if user_id is not None:
        params["user_id"] = str(user_id)
    if from_date is not None:
        params["from"] = from_date
    if to_date is not None:
        params["to"] = to_date
    if is_running is not None:
        params["is_running"] = "true" if is_running else "false"
    if is_billable is not None:
        params["is_billable"] = "true" if is_billable else "false"
    if page is not None:
        params["page"] = str(page)
    if per_page is not None:
        params["per_page"] = str(per_page)
    else:
        params["per_page"] = "2000"

    response = await harvest_request("time_entries", params)
    return json.dumps(response, indent=2)


@mcp.tool()
async def create_time_entry(
    project_id: int, task_id: int, spent_date: str, hours: float, notes: str = None
):
    """Create a new time entry.

    Args:
        project_id: The ID of the project to associate with the time entry
        task_id: The ID of the task to associate with the time entry
        spent_date: The date when the time was spent (YYYY-MM-DD)
        hours: The number of hours spent
        notes: Optional notes about the time entry
    """
    params = {
        "project_id": project_id,
        "task_id": task_id,
        "spent_date": spent_date,
        "hours": hours,
    }

    if notes:
        params["notes"] = notes

    response = await harvest_request("time_entries", params, method="POST")
    return json.dumps(response, indent=2)


@mcp.tool()
async def stop_timer(time_entry_id: int):
    """Stop a running timer.

    Args:
        time_entry_id: The ID of the running time entry to stop
    """
    response = await harvest_request(
        f"time_entries/{time_entry_id}/stop", method="PATCH"
    )
    return json.dumps(response, indent=2)


@mcp.tool()
async def start_timer(project_id: int, task_id: int, notes: str = None):
    """Start a new timer.

    Args:
        project_id: The ID of the project to associate with the time entry
        task_id: The ID of the task to associate with the time entry
        notes: Optional notes about the time entry
    """
    params = {
        "project_id": project_id,
        "task_id": task_id,
    }

    if notes:
        params["notes"] = notes

    response = await harvest_request("time_entries", params, method="POST")
    return json.dumps(response, indent=2)


@mcp.tool()
async def list_projects(client_id: int = None, is_active: bool = None):
    """List projects with optional filtering.

    Args:
        client_id: Filter by client ID
        is_active: Pass true to only return active projects and false to return inactive projects
    """
    params = {}
    if client_id is not None:
        params["client_id"] = str(client_id)
    if is_active is not None:
        params["is_active"] = "true" if is_active else "false"

    response = await harvest_request("projects", params)
    return json.dumps(response, indent=2)


@mcp.tool()
async def get_project_details(project_id: int):
    """Get detailed information about a specific project.

    Args:
        project_id: The ID of the project to retrieve
    """
    response = await harvest_request(f"projects/{project_id}")
    return json.dumps(response, indent=2)


@mcp.tool()
async def list_clients(is_active: bool = None):
    """List clients with optional filtering.

    Args:
        is_active: Pass true to only return active clients and false to return inactive clients
    """
    params = {}
    if is_active is not None:
        params["is_active"] = "true" if is_active else "false"

    response = await harvest_request("clients", params)
    return json.dumps(response, indent=2)


@mcp.tool()
async def get_client_details(client_id: int):
    """Get detailed information about a specific client.

    Args:
        client_id: The ID of the client to retrieve
    """
    response = await harvest_request(f"clients/{client_id}")
    return json.dumps(response, indent=2)


@mcp.tool()
async def list_tasks(is_active: bool = None):
    """List all tasks with optional filtering.

    Args:
        is_active: Pass true to only return active tasks and false to return inactive tasks
    """
    params = {}
    if is_active is not None:
        params["is_active"] = "true" if is_active else "false"

    response = await harvest_request("tasks", params)
    return json.dumps(response, indent=2)


@mcp.tool()
async def get_unsubmitted_timesheets(
    user_id: int = None,
    from_date: str = None,
    to_date: str = None,
    page: int = None,
    per_page: int = None,
):
    """Get unsubmitted timesheets (time entries that haven't been submitted for approval).
    
    This function queries for time entries that are not yet closed/submitted, which typically
    means they are still editable and haven't been submitted for approval or invoicing.

    Args:
        user_id: Filter by specific user ID (optional)
        from_date: Only return time entries with a spent_date on or after the given date (YYYY-MM-DD)
        to_date: Only return time entries with a spent_date on or before the given date (YYYY-MM-DD)
        page: The page number for pagination
        per_page: The number of records to return per page (1-2000)
    """
    params = {}
    if user_id is not None:
        params["user_id"] = str(user_id)
    if from_date is not None:
        params["from"] = from_date
    if to_date is not None:
        params["to"] = to_date
    if page is not None:
        params["page"] = str(page)
    if per_page is not None:
        params["per_page"] = str(per_page)
    else:
        params["per_page"] = "2000"

    # Get all time entries first
    response = await harvest_request("time_entries", params)
    
    # Filter for unsubmitted entries (those that are not closed)
    unsubmitted_entries = []
    if "time_entries" in response:
        for entry in response["time_entries"]:
            # Time entries that are not closed are considered unsubmitted
            if not entry.get("is_closed", False):
                unsubmitted_entries.append(entry)
    
    # Create a response structure similar to the original API response
    filtered_response = {
        "time_entries": unsubmitted_entries,
        "per_page": response.get("per_page", len(unsubmitted_entries)),
        "total_pages": 1,  # Simplified since we're filtering client-side
        "total_entries": len(unsubmitted_entries),
        "next_page": None,
        "previous_page": None,
        "page": response.get("page", 1),
        "links": response.get("links", {})
    }
    
    return json.dumps(filtered_response, indent=2)


@mcp.tool()
async def get_project_time_entries(
    project_id: int,
    user_ids: list[int] = None,
    from_date: str = None,
    to_date: str = None,
    page: int = None,
    per_page: int = None,
    auto_paginate: bool = True,
):
    """Get time entries for a specific project with optional date and user filtering.

    This function fetches time entries and filters them by project ID and optionally by user IDs,
    then aggregates the results by user. By default, automatically fetches all pages.

    Args:
        project_id: The ID of the project to get time entries for
        user_ids: Optional list of user IDs to filter by (e.g., [5315565, 4964600])
        from_date: Only return time entries with a spent_date on or after the given date (YYYY-MM-DD)
        to_date: Only return time entries with a spent_date on or before the given date (YYYY-MM-DD)
        page: The page number for pagination (only used if auto_paginate is False)
        per_page: The number of records to return per page (1-2000, only used if auto_paginate is False)
        auto_paginate: If True (default), automatically fetches all pages. Set to False for manual pagination.
    """
    params = {}
    if from_date is not None:
        params["from"] = from_date
    if to_date is not None:
        params["to"] = to_date

    # Get time entries - either all pages or single page
    if auto_paginate:
        all_entries = await harvest_request_all_pages("time_entries", params)
    else:
        if page is not None:
            params["page"] = str(page)
        if per_page is not None:
            params["per_page"] = str(per_page)
        else:
            params["per_page"] = "200"

        response = await harvest_request("time_entries", params)
        all_entries = response.get("time_entries", [])

    # Filter for entries matching the project ID and user IDs
    project_entries = []
    user_totals = {}

    for entry in all_entries:
        # Check if entry matches the project
        if entry.get("project", {}).get("id") != project_id:
            continue

        # Check if entry matches the user filter (if provided)
        entry_user_id = entry.get("user", {}).get("id")
        if user_ids and entry_user_id not in user_ids:
            continue

        project_entries.append(entry)

        # Aggregate by user
        user_name = entry.get("user", {}).get("name", "Unknown")
        hours = entry.get("hours", 0)

        if entry_user_id not in user_totals:
            user_totals[entry_user_id] = {
                "user_id": entry_user_id,
                "user_name": user_name,
                "total_hours": 0,
                "entry_count": 0
            }

        user_totals[entry_user_id]["total_hours"] += hours
        user_totals[entry_user_id]["entry_count"] += 1

    # Create a response with both detailed entries and user summaries
    filtered_response = {
        "project_id": project_id,
        "time_entries": project_entries,
        "user_summaries": sorted(
            list(user_totals.values()),
            key=lambda x: x["total_hours"],
            reverse=True
        ),
        "total_hours": sum(u["total_hours"] for u in user_totals.values()),
        "total_entries": len(project_entries),
        "date_range": {
            "from": from_date,
            "to": to_date
        },
        "filtered_users": user_ids if user_ids else "all",
        "auto_paginated": auto_paginate
    }

    return json.dumps(filtered_response, indent=2)


@mcp.tool()
async def list_project_user_assignments(
    project_id: int,
    is_active: bool = None,
    page: int = None,
    per_page: int = None
):
    """Get all user assignments for a specific project.

    This shows which users are assigned to work on a project, along with their
    hourly rates, budgets, and whether they're active on the project.

    Args:
        project_id: The ID of the project to get user assignments for
        is_active: Pass true to only return active user assignments
        page: The page number for pagination
        per_page: The number of records to return per page (1-2000)
    """
    params = {}
    if is_active is not None:
        params["is_active"] = "true" if is_active else "false"
    if page is not None:
        params["page"] = str(page)
    if per_page is not None:
        params["per_page"] = str(per_page)
    else:
        params["per_page"] = "2000"

    response = await harvest_request(f"projects/{project_id}/user_assignments", params)
    return json.dumps(response, indent=2)


@mcp.tool()
async def list_user_project_assignments(
    user_id: int,
    page: int = None,
    per_page: int = None
):
    """Get all project assignments for a specific user.

    This shows which projects a user is assigned to work on.

    Args:
        user_id: The ID of the user to get project assignments for
        page: The page number for pagination
        per_page: The number of records to return per page (1-2000)
    """
    params = {
        "user_id": str(user_id)
    }
    if page is not None:
        params["page"] = str(page)
    if per_page is not None:
        params["per_page"] = str(per_page)
    else:
        params["per_page"] = "2000"

    response = await harvest_request("project_assignments", params)
    return json.dumps(response, indent=2)


@mcp.tool()
async def get_project_hours_summary(
    project_id: int,
    user_ids: list[int] = None,
    from_date: str = None,
    to_date: str = None
):
    """Get aggregated hours summary for a project, optionally filtered by specific users.

    This is ideal for tracking team member hours on a specific project over a date range.
    Automatically fetches all pages of results.

    Args:
        project_id: The ID of the project to get hours for
        user_ids: Optional list of user IDs to filter by (e.g., [5315565, 4964600])
        from_date: Only include time entries on or after this date (YYYY-MM-DD)
        to_date: Only include time entries on or before this date (YYYY-MM-DD)
    """
    params = {}
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date

    # Fetch all time entries across all pages
    all_entries = await harvest_request_all_pages("time_entries", params)

    # Filter for the specific project and users
    project_entries = []
    user_totals = {}

    for entry in all_entries:
        # Check if entry matches the project
        if entry.get("project", {}).get("id") != project_id:
            continue

        # Check if entry matches the user filter (if provided)
        entry_user_id = entry.get("user", {}).get("id")
        if user_ids and entry_user_id not in user_ids:
            continue

        project_entries.append(entry)

        # Aggregate by user
        user_name = entry.get("user", {}).get("name", "Unknown")
        hours = entry.get("hours", 0)

        if entry_user_id not in user_totals:
            user_totals[entry_user_id] = {
                "user_id": entry_user_id,
                "user_name": user_name,
                "total_hours": 0,
                "entry_count": 0
            }

        user_totals[entry_user_id]["total_hours"] += hours
        user_totals[entry_user_id]["entry_count"] += 1

    # Create summary response
    summary = {
        "project_id": project_id,
        "user_summaries": sorted(
            list(user_totals.values()),
            key=lambda x: x["total_hours"],
            reverse=True
        ),
        "total_hours": sum(u["total_hours"] for u in user_totals.values()),
        "total_entries": len(project_entries),
        "date_range": {
            "from": from_date,
            "to": to_date
        },
        "filtered_users": user_ids if user_ids else "all"
    }

    return json.dumps(summary, indent=2)


@mcp.tool()
async def get_user_hours_across_projects(
    user_id: int,
    project_ids: list[int] = None,
    from_date: str = None,
    to_date: str = None
):
    """Get aggregated hours for a user across multiple projects.

    Track how a user's time is distributed across different projects.
    Automatically fetches all pages of results.

    Args:
        user_id: The ID of the user to get hours for
        project_ids: Optional list of project IDs to filter by
        from_date: Only include time entries on or after this date (YYYY-MM-DD)
        to_date: Only include time entries on or before this date (YYYY-MM-DD)
    """
    params = {
        "user_id": str(user_id)
    }
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date

    # Fetch all time entries for the user across all pages
    all_entries = await harvest_request_all_pages("time_entries", params)

    # Aggregate by project
    project_totals = {}

    for entry in all_entries:
        project_id = entry.get("project", {}).get("id")
        project_name = entry.get("project", {}).get("name", "Unknown")

        # Check if entry matches the project filter (if provided)
        if project_ids and project_id not in project_ids:
            continue

        hours = entry.get("hours", 0)

        if project_id not in project_totals:
            project_totals[project_id] = {
                "project_id": project_id,
                "project_name": project_name,
                "total_hours": 0,
                "entry_count": 0
            }

        project_totals[project_id]["total_hours"] += hours
        project_totals[project_id]["entry_count"] += 1

    # Create summary response
    summary = {
        "user_id": user_id,
        "project_summaries": sorted(
            list(project_totals.values()),
            key=lambda x: x["total_hours"],
            reverse=True
        ),
        "total_hours": sum(p["total_hours"] for p in project_totals.values()),
        "total_entries": sum(p["entry_count"] for p in project_totals.values()),
        "date_range": {
            "from": from_date,
            "to": to_date
        },
        "filtered_projects": project_ids if project_ids else "all"
    }

    return json.dumps(summary, indent=2)


@mcp.tool()
async def get_team_hours_summary(
    user_ids: list[int],
    from_date: str = None,
    to_date: str = None,
    group_by: str = "user"
):
    """Get aggregated hours summary for a team of users.

    Track total hours for multiple team members across all their projects.
    Automatically fetches all pages of results.

    Args:
        user_ids: List of user IDs to include in the summary
        from_date: Only include time entries on or after this date (YYYY-MM-DD)
        to_date: Only include time entries on or before this date (YYYY-MM-DD)
        group_by: How to group results - "user" (default), "project", or "both"
    """
    params = {}
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date

    # Fetch all time entries across all pages
    all_entries = await harvest_request_all_pages("time_entries", params)

    # Filter for specified users and aggregate
    user_totals = {}
    project_totals = {}
    user_project_totals = {}

    for entry in all_entries:
        entry_user_id = entry.get("user", {}).get("id")

        # Only include entries from specified users
        if entry_user_id not in user_ids:
            continue

        user_name = entry.get("user", {}).get("name", "Unknown")
        project_id = entry.get("project", {}).get("id")
        project_name = entry.get("project", {}).get("name", "Unknown")
        hours = entry.get("hours", 0)

        # Aggregate by user
        if entry_user_id not in user_totals:
            user_totals[entry_user_id] = {
                "user_id": entry_user_id,
                "user_name": user_name,
                "total_hours": 0,
                "entry_count": 0
            }
        user_totals[entry_user_id]["total_hours"] += hours
        user_totals[entry_user_id]["entry_count"] += 1

        # Aggregate by project
        if project_id not in project_totals:
            project_totals[project_id] = {
                "project_id": project_id,
                "project_name": project_name,
                "total_hours": 0,
                "entry_count": 0
            }
        project_totals[project_id]["total_hours"] += hours
        project_totals[project_id]["entry_count"] += 1

        # Aggregate by user + project
        key = f"{entry_user_id}_{project_id}"
        if key not in user_project_totals:
            user_project_totals[key] = {
                "user_id": entry_user_id,
                "user_name": user_name,
                "project_id": project_id,
                "project_name": project_name,
                "total_hours": 0,
                "entry_count": 0
            }
        user_project_totals[key]["total_hours"] += hours
        user_project_totals[key]["entry_count"] += 1

    # Build response based on grouping preference
    summary = {
        "team_user_ids": user_ids,
        "date_range": {
            "from": from_date,
            "to": to_date
        }
    }

    if group_by == "user":
        summary["user_summaries"] = sorted(
            list(user_totals.values()),
            key=lambda x: x["total_hours"],
            reverse=True
        )
    elif group_by == "project":
        summary["project_summaries"] = sorted(
            list(project_totals.values()),
            key=lambda x: x["total_hours"],
            reverse=True
        )
    elif group_by == "both":
        summary["user_summaries"] = sorted(
            list(user_totals.values()),
            key=lambda x: x["total_hours"],
            reverse=True
        )
        summary["project_summaries"] = sorted(
            list(project_totals.values()),
            key=lambda x: x["total_hours"],
            reverse=True
        )
        summary["user_project_breakdown"] = sorted(
            list(user_project_totals.values()),
            key=lambda x: x["total_hours"],
            reverse=True
        )

    summary["total_hours"] = sum(u["total_hours"] for u in user_totals.values())
    summary["total_entries"] = sum(u["entry_count"] for u in user_totals.values())

    return json.dumps(summary, indent=2)


@mcp.tool()
async def list_project_task_assignments(
    project_id: int,
    is_active: bool = None,
    page: int = None,
    per_page: int = None
):
    """Get all task assignments for a specific project.

    This shows which tasks are available for time tracking on a project,
    along with their billable status and hourly rates.

    Args:
        project_id: The ID of the project to get task assignments for
        is_active: Pass true to only return active task assignments
        page: The page number for pagination
        per_page: The number of records to return per page (1-2000)
    """
    params = {}
    if is_active is not None:
        params["is_active"] = "true" if is_active else "false"
    if page is not None:
        params["page"] = str(page)
    if per_page is not None:
        params["per_page"] = str(per_page)
    else:
        params["per_page"] = "2000"

    response = await harvest_request(f"projects/{project_id}/task_assignments", params)
    return json.dumps(response, indent=2)


@mcp.tool()
async def get_task_details(task_id: int):
    """Get detailed information about a specific task.

    Args:
        task_id: The ID of the task to retrieve
    """
    response = await harvest_request(f"tasks/{task_id}")
    return json.dumps(response, indent=2)


@mcp.tool()
async def get_company_info():
    """Get information about your Harvest account/company.

    Returns details like company name, time format, expense feature status,
    invoice feature status, and other account-level settings.
    """
    response = await harvest_request("company")
    return json.dumps(response, indent=2)


@mcp.tool()
async def list_invoices(
    client_id: int = None,
    project_id: int = None,
    from_date: str = None,
    to_date: str = None,
    state: str = None,
    page: int = None,
    per_page: int = None
):
    """List invoices with optional filtering.

    Args:
        client_id: Filter by client ID
        project_id: Filter by project ID
        from_date: Only return invoices with an issue_date on or after the given date (YYYY-MM-DD)
        to_date: Only return invoices with an issue_date on or before the given date (YYYY-MM-DD)
        state: Filter by invoice state (draft, open, paid, closed)
        page: The page number for pagination
        per_page: The number of records to return per page (1-2000)
    """
    params = {}
    if client_id is not None:
        params["client_id"] = str(client_id)
    if project_id is not None:
        params["project_id"] = str(project_id)
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date
    if state:
        params["state"] = state
    if page is not None:
        params["page"] = str(page)
    if per_page is not None:
        params["per_page"] = str(per_page)
    else:
        params["per_page"] = "2000"

    response = await harvest_request("invoices", params)
    return json.dumps(response, indent=2)


@mcp.tool()
async def get_invoice_details(invoice_id: int):
    """Get detailed information about a specific invoice.

    Args:
        invoice_id: The ID of the invoice to retrieve
    """
    response = await harvest_request(f"invoices/{invoice_id}")
    return json.dumps(response, indent=2)


@mcp.tool()
async def get_project_budget_report(
    is_active: bool = None,
    page: int = None,
    per_page: int = None
):
    """Get project budget report showing budget vs actual hours.

    This endpoint returns pre-aggregated budget data for all projects,
    making it much faster than fetching individual time entries.
    Perfect for getting month-to-date totals and budget remaining.

    Args:
        is_active: Filter to return only active (true) or inactive (false) projects
        page: The page number for pagination
        per_page: The number of records to return per page (1-2000, default: 2000)
    """
    params = {}
    if is_active is not None:
        params["is_active"] = "true" if is_active else "false"
    if page is not None:
        params["page"] = str(page)
    if per_page is not None:
        params["per_page"] = str(per_page)
    else:
        params["per_page"] = "2000"

    response = await harvest_request("reports/project_budget", params)
    return json.dumps(response, indent=2)


@mcp.tool()
async def get_time_report_by_projects(
    from_date: str,
    to_date: str,
    include_fixed_fee: bool = None,
    page: int = None,
    per_page: int = None
):
    """Get aggregated time report by projects.

    This endpoint returns pre-aggregated time data by project, making it
    MUCH faster than fetching individual time entries. Use this for weekly
    status updates and project summaries.

    Returns total_hours, billable_hours, and billable_amount for each project.

    Args:
        from_date: Start date for time entries (YYYY-MM-DD, required)
        to_date: End date for time entries (YYYY-MM-DD, required)
        include_fixed_fee: Include billable amounts for fixed fee projects
        page: The page number for pagination
        per_page: The number of records to return per page (1-2000, default: 2000)

    Note: Date range cannot exceed 365 days
    """
    params = {
        "from": from_date,
        "to": to_date
    }
    if include_fixed_fee is not None:
        params["include_fixed_fee"] = "true" if include_fixed_fee else "false"
    if page is not None:
        params["page"] = str(page)
    if per_page is not None:
        params["per_page"] = str(per_page)
    else:
        params["per_page"] = "2000"

    response = await harvest_request("reports/time/projects", params)
    return json.dumps(response, indent=2)


@mcp.tool()
async def get_time_report_by_team(
    from_date: str,
    to_date: str,
    include_fixed_fee: bool = None,
    page: int = None,
    per_page: int = None
):
    """Get aggregated time report by team members.

    This endpoint returns pre-aggregated time data by user, making it
    MUCH faster than fetching individual time entries. Use this for weekly
    status updates with individual breakdowns.

    Returns total_hours, billable_hours, and billable_amount for each team member.

    Args:
        from_date: Start date for time entries (YYYY-MM-DD, required)
        to_date: End date for time entries (YYYY-MM-DD, required)
        include_fixed_fee: Include billable amounts for fixed fee projects
        page: The page number for pagination
        per_page: The number of records to return per page (1-2000, default: 2000)

    Note: Date range cannot exceed 365 days
    """
    params = {
        "from": from_date,
        "to": to_date
    }
    if include_fixed_fee is not None:
        params["include_fixed_fee"] = "true" if include_fixed_fee else "false"
    if page is not None:
        params["page"] = str(page)
    if per_page is not None:
        params["per_page"] = str(per_page)
    else:
        params["per_page"] = "2000"

    response = await harvest_request("reports/time/team", params)
    return json.dumps(response, indent=2)


@mcp.tool()
async def get_time_report_by_clients(
    from_date: str,
    to_date: str,
    include_fixed_fee: bool = None,
    page: int = None,
    per_page: int = None
):
    """Get aggregated time report by clients.

    This endpoint returns pre-aggregated time data by client, making it
    perfect for engagement managers tracking multiple projects for the same client.
    Shows total hours across ALL projects for each client.

    Returns total_hours, billable_hours, and billable_amount for each client.

    Args:
        from_date: Start date for time entries (YYYY-MM-DD, required)
        to_date: End date for time entries (YYYY-MM-DD, required)
        include_fixed_fee: Include billable amounts for fixed fee projects
        page: The page number for pagination
        per_page: The number of records to return per page (1-2000, default: 2000)

    Note: Date range cannot exceed 365 days

    Use case: "Show me total hours for Acme client this month across all their projects"
    """
    params = {
        "from": from_date,
        "to": to_date
    }
    if include_fixed_fee is not None:
        params["include_fixed_fee"] = "true" if include_fixed_fee else "false"
    if page is not None:
        params["page"] = str(page)
    if per_page is not None:
        params["per_page"] = str(per_page)
    else:
        params["per_page"] = "2000"

    response = await harvest_request("reports/time/clients", params)
    return json.dumps(response, indent=2)


@mcp.tool()
async def get_time_report_by_tasks(
    from_date: str,
    to_date: str,
    include_fixed_fee: bool = None,
    page: int = None,
    per_page: int = None
):
    """Get aggregated time report by tasks.

    This endpoint returns pre-aggregated time data by task type, helping you
    understand WHAT work is being done (Development, Design, Meetings, etc.)
    rather than just how much time is being spent.

    Returns total_hours, billable_hours, and billable_amount for each task type.

    Args:
        from_date: Start date for time entries (YYYY-MM-DD, required)
        to_date: End date for time entries (YYYY-MM-DD, required)
        include_fixed_fee: Include billable amounts for fixed fee projects
        page: The page number for pagination
        per_page: The number of records to return per page (1-2000, default: 2000)

    Note: Date range cannot exceed 365 days

    Use case: "Show me task breakdown for this month - how much time on development vs meetings?"
    """
    params = {
        "from": from_date,
        "to": to_date
    }
    if include_fixed_fee is not None:
        params["include_fixed_fee"] = "true" if include_fixed_fee else "false"
    if page is not None:
        params["page"] = str(page)
    if per_page is not None:
        params["per_page"] = str(per_page)
    else:
        params["per_page"] = "2000"

    response = await harvest_request("reports/time/tasks", params)
    return json.dumps(response, indent=2)


@mcp.tool()
async def get_project_budget_utilization(
    project_id: int,
    from_date: str = None,
    to_date: str = None
):
    """Get comprehensive budget utilization metrics for a project.

    This helper tool calculates useful budget metrics automatically:
    - Budget utilization percentage
    - Burn rate (hours per day)
    - Projected completion date
    - Budget health status

    Perfect for engagement managers tracking project health and budget status.

    Args:
        project_id: The ID of the project to analyze
        from_date: Optional start date to calculate burn rate (YYYY-MM-DD)
        to_date: Optional end date to calculate burn rate (YYYY-MM-DD, defaults to today)

    Returns:
        JSON with budget metrics including:
        - budget, budget_spent, budget_remaining
        - utilization_percentage
        - burn_rate (if dates provided)
        - projected_completion_date (if burn rate available)
        - health_status (on_track, at_risk, over_budget)
    """
    from datetime import datetime, timedelta

    # Get project budget data
    budget_response = await harvest_request("reports/project_budget")

    # Find the specific project
    project_data = None
    for result in budget_response.get("results", []):
        if result.get("project_id") == project_id:
            project_data = result
            break

    if not project_data:
        return json.dumps({
            "error": f"Project {project_id} not found in budget report",
            "project_id": project_id
        }, indent=2)

    # Extract budget data
    budget = project_data.get("budget")
    budget_spent = project_data.get("budget_spent", 0)
    budget_remaining = project_data.get("budget_remaining", 0)
    project_name = project_data.get("project_name")
    client_name = project_data.get("client_name")
    is_active = project_data.get("is_active")

    # Calculate utilization percentage
    utilization_pct = 0
    if budget and budget > 0:
        utilization_pct = (budget_spent / budget) * 100

    # Determine health status
    health_status = "on_track"
    if not budget or budget == 0:
        health_status = "no_budget_set"
    elif utilization_pct > 100:
        health_status = "over_budget"
    elif utilization_pct > 90:
        health_status = "at_risk"
    elif utilization_pct > 75:
        health_status = "caution"

    result = {
        "project_id": project_id,
        "project_name": project_name,
        "client_name": client_name,
        "is_active": is_active,
        "budget": budget,
        "budget_spent": budget_spent,
        "budget_remaining": budget_remaining,
        "utilization_percentage": round(utilization_pct, 2),
        "health_status": health_status
    }

    # Calculate burn rate if date range provided
    if from_date and to_date:
        try:
            # Parse dates
            start = datetime.strptime(from_date, "%Y-%m-%d")
            end = datetime.strptime(to_date, "%Y-%m-%d")
            days_elapsed = (end - start).days + 1  # Include both start and end days

            if days_elapsed > 0:
                # Get hours for the period
                time_response = await harvest_request("reports/time/projects", {
                    "from": from_date,
                    "to": to_date
                })

                # Find this project's hours
                period_hours = 0
                for proj in time_response.get("results", []):
                    if proj.get("project_id") == project_id:
                        period_hours = proj.get("total_hours", 0)
                        break

                # Calculate burn rate (hours per day)
                burn_rate = period_hours / days_elapsed if days_elapsed > 0 else 0
                result["burn_rate_hours_per_day"] = round(burn_rate, 2)
                result["period_analyzed"] = {
                    "from": from_date,
                    "to": to_date,
                    "days": days_elapsed,
                    "hours": period_hours
                }

                # Project completion date if burn rate is consistent
                if burn_rate > 0 and budget_remaining > 0:
                    days_remaining = budget_remaining / burn_rate
                    projected_date = datetime.now() + timedelta(days=days_remaining)
                    result["projected_completion_date"] = projected_date.strftime("%Y-%m-%d")
                    result["days_until_budget_exhausted"] = round(days_remaining, 1)
                elif budget_remaining <= 0:
                    result["projected_completion_date"] = "budget_exhausted"
                    result["days_until_budget_exhausted"] = 0
        except Exception as e:
            result["burn_rate_error"] = str(e)

    return json.dumps(result, indent=2)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
