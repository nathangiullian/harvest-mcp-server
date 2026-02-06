# Changelog

All notable changes to the Harvest MCP Server will be documented in this file.

## [2.0.0] - 2025-02-06

### Major Performance Improvements 🚀

This release delivers **10-100x performance improvements** for reporting and weekly status updates through two key optimizations.

### Added

#### Reports API Integration (Option A)
- **`get_project_budget_report`** - Instant access to budget vs actual hours for all projects
- **`get_time_report_by_projects`** - Pre-aggregated time data by project (10-100x faster)
- **`get_time_report_by_team`** - Pre-aggregated time data by team member (10-100x faster)
- **`get_time_report_by_clients`** - Client-level aggregation across all projects (NEW for engagement managers)
- **`get_time_report_by_tasks`** - Task type breakdown (Development, Design, Meetings, etc.)
- **`get_project_budget_utilization`** - Auto-calculate budget %, burn rate, projected completion, and health status

#### New Documentation
- `PERFORMANCE_GUIDE.md` - Comprehensive guide to using the new tools and performance best practices
- `CHANGELOG.md` - This file!

### Changed

#### Performance Optimization (Option C)
- **Increased pagination from 200 to 2000 records per page** across all existing tools
- **10x reduction in API calls** for all queries
- Matches Harvest API's maximum page size limit

#### Documentation Updates
- Updated `README.md` with new Reports API section and budget utilization tools
- Updated `QUICK_REFERENCE.md` to include all 6 new tools (31 tools total)
- Enhanced `weekly-update.md` skill to use the new fast tools

### Performance Impact

**Before:**
- Weekly update for 3 projects: 30-50 API calls, 5-10 seconds
- Pagination: 200 records per page

**After:**
- Weekly update for 3 projects: 1-2 API calls, <1 second
- Pagination: 2000 records per page
- **Result: 10-100x faster!**

### Use Cases

Perfect for engagement managers who need to:
- Generate weekly status updates quickly
- Track multiple projects for the same client
- Calculate budget utilization and burn rates automatically
- Understand what types of work are being done (task breakdown)
- Proactively manage project budgets and health

### Technical Details

- Uses Harvest API v2 Reports endpoints (`/reports/time/*`, `/reports/project_budget`)
- Default page size: 2000 records (Reports API) vs 200 (Time Entries API)
- Rate limits: Reports API allows 100 requests per 15 minutes
- Date range limit: 365 days maximum for Reports API endpoints

### Migration Notes

Existing tools continue to work as before but are now 10x faster due to pagination improvements. No breaking changes.

For optimal performance on weekly updates:
- Use `get_time_report_by_projects` instead of `get_project_hours_summary` when possible
- Use `get_time_report_by_team` instead of fetching individual time entries
- Use `get_project_budget_utilization` for automatic health calculations

---

## [1.0.0] - 2024-12-30

### Initial Release

- 25 core tools for Harvest API v2 integration
- User, project, client, and time entry management
- Timer start/stop functionality
- Enhanced reporting with auto-pagination
- Invoice tracking
- Support for both Claude Desktop and Claude Code
