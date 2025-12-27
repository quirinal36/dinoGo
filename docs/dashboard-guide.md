# Atlassian Integration Dashboard Guide

## Overview

The Atlassian Integration Dashboard is a FastAPI-based web application that provides a unified, real-time view of your Jira, Confluence, and Compass data. It offers both a beautiful web interface and a comprehensive REST API.

## Features

- **Real-time Dashboard**: Auto-refreshing web interface showing project health across all systems
- **REST API**: Complete API for programmatic access to Jira, Confluence, and Compass
- **Beautiful UI**: Modern gradient design with responsive card-based layout
- **Auto-refresh**: Dashboard updates every 60 seconds automatically
- **Swagger Documentation**: Interactive API documentation at `/docs`

## Installation

### Prerequisites

- Python 3.10+
- Virtual environment activated
- Atlassian credentials configured in `.mcp.json`

### Setup

```bash
# Navigate to project root
cd /home/ubuntu/dinoGo

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r dashboard/requirements.txt
```

## Running the Dashboard

### Using the Startup Script

The easiest way to start the dashboard:

```bash
./dashboard/run.sh
```

This script will:
1. Activate the virtual environment
2. Load credentials from `.mcp.json`
3. Start the uvicorn server on port 8000
4. Enable auto-reload for development

### Manual Start

```bash
# Load environment variables
export ATLASSIAN_SITE=$(python3 -c "import json; config=json.load(open('.mcp.json')); print(config['mcpServers']['atlassian']['env']['ATLASSIAN_SITE'])")
export ATLASSIAN_USER_EMAIL=$(python3 -c "import json; config=json.load(open('.mcp.json')); print(config['mcpServers']['atlassian']['env']['ATLASSIAN_USER_EMAIL'])")
export ATLASSIAN_API_TOKEN=$(python3 -c "import json; config=json.load(open('.mcp.json')); print(config['mcpServers']['atlassian']['env']['ATLASSIAN_API_TOKEN'])")

# Start server
cd dashboard
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

## Accessing the Dashboard

Once started, the dashboard is available at:

- **Web Dashboard**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Health Check

```bash
GET /health
```

Returns the health status of all integrated systems.

**Response:**
```json
{
  "status": "healthy",
  "jira": true,
  "confluence": true,
  "compass": true
}
```

### Jira Endpoints

#### Get Project Health

```bash
GET /api/jira/health
```

Returns comprehensive project health metrics.

**Response:**
```json
{
  "total_issues": 100,
  "blocked": 0,
  "overdue": 0,
  "by_status": {
    "해야 할 일": 100
  },
  "by_priority": {
    "Low": 4,
    "Medium": 36,
    "High": 59,
    "Highest": 1
  }
}
```

#### Get Issues

```bash
GET /api/jira/issues?jql=project=DIN&limit=50
```

**Parameters:**
- `jql` (optional): JQL query string (default: "project = DIN")
- `limit` (optional): Maximum results (default: 50)

**Response:**
```json
[
  {
    "key": "DIN-113",
    "summary": "최종 성능 리포트 작성",
    "status": "해야 할 일",
    "priority": "Low",
    "assignee": null
  }
]
```

### Confluence Endpoints

#### Get Spaces

```bash
GET /api/confluence/spaces
```

Returns all accessible Confluence spaces with page counts.

**Response:**
```json
[
  {
    "key": "DIN",
    "name": "DIN",
    "total_pages": 5
  }
]
```

#### Get Pages

```bash
GET /api/confluence/pages?space=DIN&limit=50
```

**Parameters:**
- `space` (optional): Space key (default: "DIN")
- `limit` (optional): Maximum results (default: 50)

**Response:**
```json
[
  {
    "id": "98312",
    "title": "DIN - Project Overview",
    "type": "page"
  }
]
```

### Compass Endpoints

#### Get Components

```bash
GET /api/compass/components
```

Returns all Compass components.

**Response:**
```json
[
  {
    "id": "ari:cloud:compass:...",
    "name": "DinoGo Automation",
    "type": "SERVICE",
    "description": "AI automation for Chrome Dino game"
  }
]
```

## Web Dashboard Features

### Dashboard Cards

The web interface displays three main cards:

1. **Jira Project Card**
   - Total issues count
   - Blocked issues (color-coded: red if > 0)
   - Overdue issues (color-coded: red if > 0)

2. **Confluence Card**
   - Total spaces count
   - Pages per space breakdown

3. **Compass Card**
   - Total components count

### API Links Section

Quick access to all API endpoints and Swagger documentation.

### Auto-Refresh

The dashboard automatically refreshes data every 60 seconds to ensure you always see the latest information.

## Architecture

### Technology Stack

- **Framework**: FastAPI 0.109.0
- **Server**: Uvicorn with auto-reload
- **Data Models**: Pydantic for validation
- **HTTP Client**: Requests library
- **Atlassian Integration**: atlassian-python-api 3.41.0

### Application Structure

```
dashboard/
├── app.py              # Main FastAPI application
├── requirements.txt    # Python dependencies
└── run.sh             # Startup script
```

### Key Components

1. **Manager Initialization**
   - `JiraAutomationManager`: Handles Jira operations
   - `ConfluenceAutomationManager`: Manages Confluence operations
   - `CompassAutomationManager`: Controls Compass integration

2. **Data Models**
   - `ProjectHealth`: Jira project metrics
   - `IssueInfo`: Individual issue data
   - `SpaceInfo`: Confluence space information
   - `ComponentInfo`: Compass component data

3. **CORS Configuration**
   - Allows all origins (configure for production)
   - Supports credentials
   - All methods and headers enabled

## Configuration

### Environment Variables

The dashboard requires the following environment variables (loaded from `.mcp.json`):

- `ATLASSIAN_SITE`: Your Atlassian site (e.g., "letscoding.atlassian.net")
- `ATLASSIAN_USER_EMAIL`: Your email address
- `ATLASSIAN_API_TOKEN`: Your API token

### Default Project Settings

The dashboard uses "DIN" as the default project/space key. To change this:

1. Edit [dashboard/app.py](../dashboard/app.py:49)
2. Update the `init_managers()` function
3. Restart the dashboard

## Troubleshooting

### Port Already in Use

If port 8000 is already in use:

```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9

# Restart the dashboard
./dashboard/run.sh
```

### Manager Initialization Errors

If you see "Jira manager not initialized" errors:

1. Check `.mcp.json` has valid credentials
2. Verify network connectivity to Atlassian
3. Check the startup logs for specific errors

### API Deprecation Warnings

The dashboard uses Jira API v3 endpoints. If you see deprecation warnings:

1. Ensure you're using the latest code
2. Check that `search_issues()` in `jira_automation_manager.py` uses direct requests
3. Verify the URL format doesn't have double base URLs

### No Data Displayed

If the dashboard shows zero counts:

1. Verify issues exist in your Jira project
2. Check the JQL queries are correct for your project
3. Ensure the project key matches your actual project

## Development

### Running in Development Mode

The startup script runs uvicorn with `--reload` flag, which:
- Auto-reloads on file changes
- Shows detailed error messages
- Watches for code changes

### Adding New Endpoints

To add a new endpoint:

1. Define the Pydantic model in [dashboard/app.py](../dashboard/app.py)
2. Create the endpoint function with `@app.get()` decorator
3. Implement the logic using the managers
4. Test with Swagger UI at `/docs`

### Customizing the UI

The HTML dashboard is embedded in [dashboard/app.py](../dashboard/app.py:91). To customize:

1. Edit the `html_content` string in the `root()` function
2. Modify CSS styles in the `<style>` section
3. Update JavaScript in the `<script>` section
4. Save and the auto-reload will pick up changes

## Production Deployment

### Security Considerations

Before deploying to production:

1. **CORS**: Restrict `allow_origins` to specific domains
2. **Authentication**: Add OAuth or JWT authentication
3. **HTTPS**: Use TLS/SSL certificates
4. **Rate Limiting**: Implement API rate limits
5. **Logging**: Add structured logging

### Deployment Options

#### Docker Deployment

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY dashboard/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scripts/ scripts/
COPY dashboard/ dashboard/

ENV ATLASSIAN_SITE=""
ENV ATLASSIAN_USER_EMAIL=""
ENV ATLASSIAN_API_TOKEN=""

CMD ["uvicorn", "dashboard.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Systemd Service

```ini
[Unit]
Description=Atlassian Dashboard
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/dinoGo
Environment="PATH=/home/ubuntu/dinoGo/venv/bin"
ExecStart=/home/ubuntu/dinoGo/dashboard/run.sh
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name dashboard.example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## Performance

### Caching

Consider implementing caching for:
- Jira issue searches
- Confluence space listings
- Compass component data

### Optimization Tips

1. **Reduce API Calls**: Cache frequently accessed data
2. **Pagination**: Limit large result sets
3. **Async Operations**: Use FastAPI's async capabilities
4. **Connection Pooling**: Reuse HTTP connections

## Monitoring

### Health Checks

Use the `/health` endpoint for monitoring:

```bash
curl http://localhost:8000/health
```

### Logging

Check uvicorn logs for:
- Request/response logs
- Error messages
- Manager initialization status

## Examples

### Curl Examples

```bash
# Get project health
curl http://localhost:8000/api/jira/health

# Get issues with custom JQL
curl "http://localhost:8000/api/jira/issues?jql=project=DIN%20AND%20status='In%20Progress'&limit=10"

# Get Confluence pages
curl http://localhost:8000/api/confluence/pages?space=DIN

# Get Compass components
curl http://localhost:8000/api/compass/components
```

### Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000"

# Get health status
health = requests.get(f"{BASE_URL}/health").json()
print(f"Status: {health['status']}")

# Get project health
jira_health = requests.get(f"{BASE_URL}/api/jira/health").json()
print(f"Total Issues: {jira_health['total_issues']}")
print(f"Blocked: {jira_health['blocked']}")

# Get issues
issues = requests.get(
    f"{BASE_URL}/api/jira/issues",
    params={"jql": "project = DIN", "limit": 5}
).json()

for issue in issues:
    print(f"{issue['key']}: {issue['summary']}")
```

## Support

For issues or questions:
1. Check the logs for error messages
2. Verify credentials in `.mcp.json`
3. Test individual managers in isolation
4. Review the API documentation at `/docs`

## Related Documentation

- [Jira Automation Guide](./jira-automation-guide.md)
- [Confluence Automation Guide](./confluence-automation-guide.md)
- [Compass Integration](../scripts/compass_automation_manager.py)
- [CI/CD Workflows](../.github/workflows/)
