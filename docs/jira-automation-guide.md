# Jira Automation Guide

> **Complete guide to Jira project management automation using MCP Atlassian Server**

## 📚 Table of Contents

- [Overview](#overview)
- [Setup](#setup)
- [CLI Commands](#cli-commands)
- [Automation Features](#automation-features)
- [Advanced Usage](#advanced-usage)
- [API Reference](#api-reference)

---

## Overview

This project provides comprehensive Jira automation tools built on the **Atlassian MCP (Model Context Protocol) Server**. The system includes:

- 🤖 **Automated workflows** - Issue transitions, bulk operations, auto-assignment
- 📊 **Health dashboards** - Real-time project health monitoring
- 🔍 **Advanced search** - JQL-based issue search and filtering
- 📈 **Reporting** - JSON export for analytics and visualization
- 💻 **CLI interface** - Easy-to-use command-line tools

---

## Setup

### Prerequisites

1. **Atlassian Cloud** account with Jira access
2. **Python 3.10+** and virtual environment
3. **MCP Atlassian Server** configured in [.mcp.json](../.mcp.json)

### Installation

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install atlassian-python-api requests

# Make scripts executable
chmod +x scripts/jira
chmod +x scripts/run_jira_automation.sh
```

### Configuration

Credentials are loaded from `.mcp.json`:

```json
{
  "mcpServers": {
    "atlassian": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-atlassian"],
      "env": {
        "ATLASSIAN_SITE": "letscoding.atlassian.net",
        "ATLASSIAN_USER_EMAIL": "your-email@example.com",
        "ATLASSIAN_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

---

## CLI Commands

### Quick Start

```bash
# View project health dashboard
./scripts/jira health

# Search issues
./scripts/jira search --jql "status = 'In Progress'"

# View Epic with stories
./scripts/jira epic DIN-58

# View Story with subtasks
./scripts/jira story DIN-61
```

### Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `health` | Project health dashboard | `./scripts/jira health` |
| `search` | Search with JQL | `./scripts/jira search --jql "priority = High"` |
| `epic` | View Epic details | `./scripts/jira epic DIN-58` |
| `story` | View Story details | `./scripts/jira story DIN-61` |
| `transition` | Change issue status | `./scripts/jira transition DIN-72 "In Progress"` |
| `comment` | Add comment | `./scripts/jira comment DIN-72 "Working on this"` |
| `blocked` | Show blocked issues | `./scripts/jira blocked` |
| `overdue` | Show overdue issues | `./scripts/jira overdue` |
| `unassigned` | Show unassigned issues | `./scripts/jira unassigned` |
| `report` | Export JSON report | `./scripts/jira report --output report.json` |

---

## Automation Features

### 1. Health Dashboard

Real-time project health monitoring:

```bash
./scripts/jira health
```

**Output:**
```
📊 DIN Project Health Dashboard
================================

📈 Summary:
  Total Active Issues: 100
  Blocked Issues: 0
  Overdue Issues: 0

📊 By Status:
  해야 할 일: 100

🎯 By Priority:
  High: 59
  Highest: 1
  Low: 4
  Medium: 36
```

### 2. JQL Search

Powerful JQL-based search:

```bash
# Find high-priority issues
./scripts/jira search --jql "priority = High AND status != Done"

# Find recent issues
./scripts/jira search --jql "created >= -7d ORDER BY created DESC"

# Find your assigned tasks
./scripts/jira search --jql "assignee = currentUser()"
```

### 3. Issue Transitions

Automate status changes:

```bash
# Move to In Progress
./scripts/jira transition DIN-72 "In Progress"

# Mark as Done
./scripts/jira transition DIN-72 "Done"
```

### 4. Bulk Operations

Python API for bulk operations:

```python
from jira_automation_manager import JiraAutomationManager

manager = JiraAutomationManager("DIN")

# Bulk transition
issues = ["DIN-72", "DIN-73", "DIN-74"]
manager.bulk_transition(issues, "In Progress")

# Bulk update priority
manager.bulk_update_priority("status = 'In Progress'", "High")
```

### 5. Automated Workflows

Built-in automation workflows:

```python
# Auto-flag overdue issues
manager.auto_flag_overdue_issues()

# Auto-assign unassigned high-priority issues
manager.auto_assign_unassigned(default_assignee_id="123456")

# Auto-close completed subtasks
manager.auto_close_completed_subtasks()
```

---

## Advanced Usage

### Epic and Story Hierarchy

```bash
# View Epic with all stories
./scripts/jira epic DIN-58

# View Story with all subtasks
./scripts/jira story DIN-61

# Search by Epic
./scripts/jira search --jql "parent = DIN-58"
```

### Reporting and Analytics

```bash
# Export JSON report
./scripts/jira report --output reports/sprint_report.json

# Use Python API
python3 << EOF
from jira_automation_manager import JiraAutomationManager

manager = JiraAutomationManager("DIN")
report = manager.generate_sprint_report()

print(f"Total Issues: {report['summary']['total_active']}")
print(f"Blocked: {report['summary']['blocked_count']}")
print(f"Overdue: {report['summary']['overdue_count']}")
EOF
```

### Custom JQL Queries

Common JQL patterns:

```bash
# Find bugs
./scripts/jira search --jql "issuetype = Bug AND status != Done"

# Find unassigned high-priority
./scripts/jira search --jql "assignee is EMPTY AND priority = High"

# Find recent updates
./scripts/jira search --jql "updated >= -1d ORDER BY updated DESC"

# Find issues by label
./scripts/jira search --jql "labels = urgent"

# Find issues in sprint
./scripts/jira search --jql "sprint in openSprints()"
```

---

## API Reference

### JiraAutomationManager Class

```python
from jira_automation_manager import JiraAutomationManager

manager = JiraAutomationManager(project_key="DIN")
```

#### Search Methods

```python
# Search with JQL
issues = manager.search_issues("status = 'In Progress'", max_results=50)

# Get Epic stories
stories = manager.get_epic_stories("DIN-58")

# Get Story subtasks
subtasks = manager.get_story_subtasks("DIN-61")

# Find blocked issues
blocked = manager.find_blocked_issues()

# Find overdue issues
overdue = manager.find_overdue_issues()

# Find unassigned issues
unassigned = manager.find_unassigned_issues()
```

#### Issue Management

```python
# Transition issue
manager.transition_issue("DIN-72", "In Progress")

# Update issue fields
manager.update_issue("DIN-72", {"priority": {"name": "High"}})

# Add comment
manager.add_comment("DIN-72", "Working on this now")

# Assign issue
manager.assign_issue("DIN-72", account_id="123456")
```

#### Bulk Operations

```python
# Bulk transition
manager.bulk_transition(["DIN-72", "DIN-73"], "Done")

# Bulk update priority
manager.bulk_update_priority("status = 'To Do'", "Medium")
```

#### Reporting

```python
# Generate report
report = manager.generate_sprint_report()

# Print dashboard
manager.print_project_health()

# Export to JSON
manager.export_report_json("reports/custom_report.json")
```

---

## Examples

### Daily Standup Report

```bash
#!/bin/bash
# Generate daily standup report

echo "📊 Daily Standup Report - $(date)"
echo "================================"

# Your tasks
./scripts/jira search --jql "assignee = currentUser() AND status = 'In Progress'"

# Blocked issues
./scripts/jira blocked

# Today's completed
./scripts/jira search --jql "assignee = currentUser() AND status = Done AND updated >= -1d"
```

### Sprint Health Check

```python
#!/usr/bin/env python3
from jira_automation_manager import JiraAutomationManager

manager = JiraAutomationManager("DIN")

# Print health dashboard
manager.print_project_health()

# Flag overdue issues
manager.auto_flag_overdue_issues()

# Export report
manager.export_report_json()
```

### Automated Triage

```python
#!/usr/bin/env python3
from jira_automation_manager import JiraAutomationManager

manager = JiraAutomationManager("DIN")

# Find unassigned high-priority bugs
jql = "issuetype = Bug AND priority = High AND assignee is EMPTY"
bugs = manager.search_issues(jql)

# Auto-assign to default assignee
for bug in bugs:
    manager.assign_issue(bug['key'], "default-assignee-id")
    manager.add_comment(bug['key'], "Auto-assigned for triage")
```

---

## Resources

- **MCP Atlassian Documentation**: https://github.com/atlassian/atlassian-mcp-server
- **Atlassian Support**: https://support.atlassian.com/atlassian-rovo-mcp-server/
- **JQL Reference**: https://support.atlassian.com/jira-software-cloud/docs/use-advanced-search-with-jira-query-language-jql/
- **Atlassian REST API**: https://developer.atlassian.com/cloud/jira/platform/rest/v3/

---

## Sources

Based on official MCP Atlassian documentation:
- [Atlassian MCP Server GitHub](https://github.com/atlassian/atlassian-mcp-server)
- [Getting Started with Atlassian Rovo MCP Server](https://support.atlassian.com/atlassian-rovo-mcp-server/docs/getting-started-with-the-atlassian-remote-mcp-server/)
- [Atlassian Blog: Remote MCP Server](https://www.atlassian.com/blog/announcements/remote-mcp-server)
- [Anthropic Integrations Announcement](https://www.anthropic.com/news/integrations)

---

**📅 Last Updated**: 2025-12-27
**🔖 Version**: 1.0.0
**📦 Project**: dinoGo (DIN)
