import os
import httpx
from datetime import datetime
from dotenv import load_dotenv
from collections import defaultdict

# Load environment variables
load_dotenv()

HARVEST_ACCOUNT_ID = os.environ.get("HARVEST_ACCOUNT_ID")
HARVEST_API_KEY = os.environ.get("HARVEST_API_KEY")

headers = {
    "Harvest-Account-Id": HARVEST_ACCOUNT_ID,
    "Authorization": f"Bearer {HARVEST_API_KEY}",
    "User-Agent": "Harvest MCP Server",
}

# Charge Recon project ID
project_id = 42580673
from_date = "2025-11-01"
to_date = "2025-11-12"

# Fetch all time entries for November
url = "https://api.harvestapp.com/v2/time_entries"
params = {
    "from": from_date,
    "to": to_date,
    "per_page": 200
}

user_hours = defaultdict(lambda: {"name": "", "hours": 0, "entries": []})
total_hours = 0

print(f"Fetching time entries for Charge Recon project (ID: {project_id})")
print(f"Date range: {from_date} to {to_date}\n")

page = 1
while True:
    params["page"] = page
    response = httpx.get(url, headers=headers, params=params)
    data = response.json()

    for entry in data.get("time_entries", []):
        if entry.get("project", {}).get("id") == project_id:
            user_id = entry.get("user", {}).get("id")
            user_name = entry.get("user", {}).get("name")
            hours = entry.get("hours", 0)
            spent_date = entry.get("spent_date")
            notes = entry.get("notes", "")

            user_hours[user_id]["name"] = user_name
            user_hours[user_id]["hours"] += hours
            user_hours[user_id]["entries"].append({
                "date": spent_date,
                "hours": hours,
                "notes": notes
            })
            total_hours += hours

    # Check if there are more pages
    if data.get("next_page") is None:
        break
    page += 1

# Print results
print("=" * 80)
print(f"CHARGE RECON PROJECT - TIME SUMMARY")
print(f"November 1-12, 2025")
print("=" * 80)
print()

if not user_hours:
    print("No time entries found for this project in the specified date range.")
else:
    # Sort by hours descending
    sorted_users = sorted(user_hours.items(), key=lambda x: x[1]["hours"], reverse=True)

    for user_id, data in sorted_users:
        print(f"{data['name']}")
        print(f"  Total Hours: {data['hours']:.2f}")
        print(f"  Entries: {len(data['entries'])}")
        print()
        for entry in data["entries"]:
            print(f"    {entry['date']}: {entry['hours']:.2f}h - {entry['notes'][:60]}...")
        print()

    print("=" * 80)
    print(f"TOTAL HOURS: {total_hours:.2f}")
    print("=" * 80)
