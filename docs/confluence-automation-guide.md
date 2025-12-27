## Confluence Automation Guide

> **Complete guide to Confluence documentation automation using MCP Atlassian Server**

## 📚 Table of Contents

- [Overview](#overview)
- [Setup](#setup)
- [Confluence CLI Commands](#confluence-cli-commands)
- [Jira-Confluence Integration](#jira-confluence-integration)
- [Automation Features](#automation-features)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)

---

## Overview

This project provides comprehensive Confluence automation tools integrated with Jira for seamless documentation management. The system includes:

- 📝 **Automated documentation** - Generate project docs from Jira data
- 🔄 **Jira sync** - Automatic Epic/Story documentation
- 📊 **Reporting** - Space analytics and metrics
- 🔍 **Search** - CQL-based content discovery
- 💻 **CLI interface** - Easy command-line tools

---

## Setup

### Prerequisites

1. **Atlassian Confluence Cloud** access
2. **Python 3.10+** with atlassian-python-api
3. **API Token** with Confluence permissions

### Confluence Access Setup

The API token in `.mcp.json` needs Confluence permissions:

```bash
# Test Confluence access
./scripts/confluence spaces

# If unauthorized (401), you need to:
# 1. Verify Confluence is enabled on your Atlassian site
# 2. Check API token has Confluence permissions
# 3. Visit: https://id.atlassian.com/manage-profile/security/api-tokens
```

### Installation

```bash
# Activate virtual environment
source venv/bin/activate

# Make CLI executable
chmod +x scripts/confluence

# Test connection
./scripts/confluence spaces
```

---

## Confluence CLI Commands

### Basic Commands

```bash
# List all spaces
./scripts/confluence spaces

# List pages in space
./scripts/confluence pages --space DIN

# Show space dashboard
./scripts/confluence dashboard --space DIN
```

### Content Management

```bash
# Create new page
./scripts/confluence create \
  --title "Project Documentation" \
  --content "<h1>Hello World</h1>" \
  --space DIN

# Update existing page
./scripts/confluence update PAGE_ID \
  --title "Updated Title" \
  --content "<p>New content</p>"

# Search pages
./scripts/confluence search --query "title~'documentation'"

# Export page to PDF
./scripts/confluence export PAGE_ID --output report.pdf
```

### Jira Integration Commands

```bash
# Sync project overview
./scripts/confluence sync --type overview --project DIN

# Generate Epic documentation
./scripts/confluence sync --type epic --key DIN-58 --project DIN

# Generate Story documentation
./scripts/confluence sync --type story --key DIN-61 --project DIN

# Generate complete documentation
./scripts/confluence sync --type full --project DIN
```

---

## Jira-Confluence Integration

### Automated Documentation Generation

The integration automatically creates Confluence pages from Jira data:

#### 1. Project Overview Page

Generates a comprehensive project dashboard:

```bash
./scripts/confluence sync --type overview --project DIN
```

**Includes:**
- Total active issues
- Blocked/overdue counts
- Status distribution
- Priority breakdown
- Links to blocked/overdue issues

#### 2. Epic Documentation

Creates detailed Epic pages with stories:

```bash
./scripts/confluence sync --type epic --key DIN-58 --project DIN
```

**Includes:**
- Epic information (status, priority)
- Description
- List of all stories with links
- Story points summary

#### 3. Story Documentation

Generates Story pages with subtasks:

```bash
./scripts/confluence sync --type story --key DIN-61 --project DIN
```

**Includes:**
- Story information
- Description
- All subtasks with estimates
- Status tracking

#### 4. Complete Project Documentation

Generates full documentation hierarchy:

```bash
./scripts/confluence sync --type full --project DIN
```

**Creates:**
- 1 Project overview page
- N Epic pages (one per Epic)
- M Story pages (configurable limit)
- Automatic cross-linking

---

## Automation Features

### 1. Space Management

```python
from confluence_automation_manager import ConfluenceAutomationManager

manager = ConfluenceAutomationManager(space_key="DIN")

# List all spaces
spaces = manager.get_all_spaces()

# Get space info
info = manager.get_space_info("DIN")

# List pages in space
pages = manager.get_all_pages("DIN")
```

### 2. Page Operations

```python
# Create page
page_id = manager.create_page(
    title="New Documentation",
    body="<h1>Content</h1>",
    space_key="DIN"
)

# Update page
manager.update_page(
    page_id="123456",
    title="Updated Title",
    body="<h1>New Content</h1>"
)

# Update or create (upsert)
page_id = manager.update_or_create_page(
    title="Documentation",
    body="<p>Content</p>",
    space_key="DIN"
)

# Delete page
manager.delete_page("123456")
```

### 3. Search & Discovery

```python
# CQL search
results = manager.search_pages(
    query="title~'documentation'",
    space_key="DIN",
    limit=25
)

# Search by label
pages = manager.find_pages_by_label("important")

# Check page existence
exists = manager.page_exists("Page Title", "DIN")
```

### 4. Labels & Metadata

```python
# Add label
manager.add_label("123456", "documentation")

# Get labels
labels = manager.get_page_labels("123456")
```

### 5. Attachments

```python
# Attach file
manager.attach_file("123456", "/path/to/file.pdf")

# Get attachments
attachments = manager.get_attachments("123456")
```

### 6. Export & Reporting

```python
# Export to PDF
manager.export_page_to_pdf("123456", "output.pdf")

# Generate space report
report = manager.generate_space_report("DIN")

# Export report to JSON
manager.export_report_json("DIN", "report.json")
```

---

## Advanced Usage

### Custom Documentation Templates

Create custom HTML templates for documentation:

```python
from jira_confluence_integration import JiraConfluenceIntegration

integration = JiraConfluenceIntegration("DIN", "DIN")

# Custom Epic template
def generate_custom_epic_doc(epic_key):
    epic = integration.jira.jira.issue(epic_key)

    html = f"""
<ac:structured-macro ac:name="info">
  <ac:rich-text-body>
    <p>Epic: {epic['fields']['summary']}</p>
  </ac:rich-text-body>
</ac:structured-macro>

<h2>Epic Details</h2>
<table>
  <tr>
    <th>Key</th>
    <td>{epic_key}</td>
  </tr>
  <tr>
    <th>Status</th>
    <td>{epic['fields']['status']['name']}</td>
  </tr>
</table>
"""

    integration.confluence.create_page(
        title=f"Epic: {epic_key}",
        body=html,
        space_key="DIN"
    )
```

### Automated Sync Workflows

Set up automated documentation updates:

```python
#!/usr/bin/env python3
"""Daily documentation sync"""

from jira_confluence_integration import JiraConfluenceIntegration

def daily_sync():
    integration = JiraConfluenceIntegration("DIN", "DIN")

    # Update project overview
    integration.generate_project_overview_page()

    # Update sprint report
    integration.generate_sprint_report_page()

    print("✅ Daily sync complete!")

if __name__ == "__main__":
    daily_sync()
```

### Bulk Operations

```python
# Generate documentation for all epics
jql = 'project = DIN AND issuetype = "에픽"'
epics = manager.jira.search_issues(jql)

for epic in epics:
    epic_key = epic['key']
    integration.generate_epic_documentation(epic_key)
    print(f"✅ Generated docs for {epic_key}")
```

---

## API Reference

### ConfluenceAutomationManager

```python
manager = ConfluenceAutomationManager(space_key="DIN")
```

#### Space Methods

```python
get_all_spaces(limit=100) -> List[Dict]
get_space_info(space_key=None) -> Optional[Dict]
list_spaces() -> None
```

#### Page Methods

```python
get_all_pages(space_key=None, limit=100) -> List[Dict]
page_exists(title, space_key=None) -> bool
get_page_by_title(title, space_key=None) -> Optional[Dict]
get_page_by_id(page_id, expand='body.storage,version') -> Optional[Dict]
```

#### Content Operations

```python
create_page(title, body, space_key=None, parent_id=None) -> Optional[str]
update_page(page_id, title, body, minor_edit=False) -> bool
update_or_create_page(title, body, space_key=None, parent_id=None) -> Optional[str]
delete_page(page_id) -> bool
```

#### Search & Labels

```python
search_pages(query, space_key=None, limit=25) -> List[Dict]
find_pages_by_label(label, limit=50) -> List[Dict]
add_label(page_id, label) -> bool
get_page_labels(page_id) -> List[str]
```

#### Utilities

```python
export_page_to_pdf(page_id, output_path=None) -> bool
generate_space_report(space_key=None) -> Dict
export_report_json(space_key=None, filename=None) -> None
```

### JiraConfluenceIntegration

```python
integration = JiraConfluenceIntegration(project_key="DIN", space_key="DIN")
```

#### Documentation Generators

```python
generate_project_overview_page() -> Optional[str]
generate_epic_documentation(epic_key) -> Optional[str]
generate_story_documentation(story_key) -> Optional[str]
generate_complete_project_documentation() -> Dict[str, str]
generate_sprint_report_page() -> Optional[str]
```

---

## Troubleshooting

### Unauthorized (401) Error

```bash
❌ Error getting spaces: Unauthorized (401)
```

**Solutions:**

1. **Check Confluence Access**
   - Verify Confluence is enabled on your Atlassian site
   - Visit: https://YOUR-DOMAIN.atlassian.net/wiki

2. **Verify API Token Permissions**
   - Token needs both Jira AND Confluence permissions
   - Regenerate token with full permissions
   - Visit: https://id.atlassian.com/manage-profile/security/api-tokens

3. **Test with Browser**
   - Can you access Confluence via web browser?
   - Try: https://letscoding.atlassian.net/wiki

4. **Check Space Exists**
   - The "DIN" space may not exist in Confluence yet
   - Create it manually first or use different space key

### No Spaces Found

```bash
No spaces found or access denied.
```

**Solutions:**

1. **Create a Space First**
   - Go to Confluence → Create Space
   - Use space key "DIN" to match project

2. **Check Permissions**
   - User must have "View" permission on spaces
   - Contact Confluence admin to grant access

### Page Creation Fails

**Common issues:**
- Invalid HTML in body content
- Parent page doesn't exist
- No permission to create pages in space
- Space doesn't exist

### CQL Search Issues

**Tips:**
- Use double quotes for exact matches: `title="Documentation"`
- Use tilde for fuzzy search: `title~"doc"`
- Escape special characters
- Check CQL syntax: https://confluence.atlassian.com/doc/advanced-searching-using-cql-841186541.html

---

## Examples

### Daily Documentation Workflow

```bash
#!/bin/bash
# daily_docs.sh - Run daily to keep docs in sync

echo "📝 Daily Documentation Update"

# Update project overview
./scripts/confluence sync --type overview --project DIN

# Update sprint report
python3 << EOF
from jira_confluence_integration import JiraConfluenceIntegration
integration = JiraConfluenceIntegration("DIN", "DIN")
integration.generate_sprint_report_page()
EOF

echo "✅ Documentation updated!"
```

### Epic Documentation Generator

```python
#!/usr/bin/env python3
"""Generate documentation for all Epics"""

from jira_confluence_integration import JiraConfluenceIntegration

integration = JiraConfluenceIntegration("DIN", "DIN")

# Get all epics
jql = 'project = DIN AND issuetype = "에픽"'
epics = integration.jira.search_issues(jql)

print(f"Found {len(epics)} Epics\n")

# Generate docs for each
for epic in epics:
    epic_key = epic['key']
    epic_summary = epic['fields']['summary']

    print(f"Generating: {epic_key} - {epic_summary}")
    integration.generate_epic_documentation(epic_key)

print("\n✅ All Epic documentation generated!")
```

---

## Resources

**Official Documentation:**
- [Confluence REST API v2](https://developer.atlassian.com/cloud/confluence/rest/v2/)
- [Confluence Python API](https://atlassian-python-api.readthedocs.io/confluence.html)
- [Confluence REST API Examples](https://developer.atlassian.com/server/confluence/confluence-rest-api-examples/)
- [CQL Search Reference](https://confluence.atlassian.com/doc/advanced-searching-using-cql-841186541.html)

**Related Guides:**
- [Jira Automation Guide](./jira-automation-guide.md)
- [MCP Atlassian Setup](https://support.atlassian.com/atlassian-rovo-mcp-server/)

---

**📅 Last Updated**: 2025-12-27
**🔖 Version**: 1.0.0
**📦 Project**: dinoGo (DIN)
