#!/usr/bin/env python3
"""
Atlassian Dashboard - FastAPI Application
Real-time project dashboard integrating Jira, Confluence, and Compass
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.jira_automation_manager import JiraAutomationManager
from scripts.confluence_automation_manager import ConfluenceAutomationManager
from scripts.compass_automation_manager import CompassAutomationManager

app = FastAPI(
    title="Atlassian Integration Dashboard",
    description="Unified dashboard for Jira, Confluence, and Compass",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
jira_manager = None
confluence_manager = None
compass_manager = None


def init_managers():
    """Initialize managers with credentials"""
    global jira_manager, confluence_manager, compass_manager

    try:
        jira_manager = JiraAutomationManager(project_key="DIN")
        confluence_manager = ConfluenceAutomationManager(space_key="DIN")
        compass_manager = CompassAutomationManager()
    except Exception as e:
        print(f"Warning: Could not initialize all managers: {e}")


# Models
class ProjectHealth(BaseModel):
    total_issues: int
    blocked: int
    overdue: int
    by_status: Dict[str, int]
    by_priority: Dict[str, int]


class IssueInfo(BaseModel):
    key: str
    summary: str
    status: str
    priority: str
    assignee: Optional[str] = None


class SpaceInfo(BaseModel):
    key: str
    name: str
    total_pages: int


class ComponentInfo(BaseModel):
    id: str
    name: str
    type: str
    description: Optional[str] = None


# ==================== Health Check ====================

@app.get("/")
async def root():
    """Root endpoint with dashboard HTML"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Atlassian Dashboard</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 2rem;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            .header {
                text-align: center;
                color: white;
                margin-bottom: 2rem;
            }
            .header h1 {
                font-size: 3rem;
                margin-bottom: 0.5rem;
            }
            .header p {
                font-size: 1.2rem;
                opacity: 0.9;
            }
            .cards {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 1.5rem;
                margin-bottom: 2rem;
            }
            .card {
                background: white;
                border-radius: 12px;
                padding: 1.5rem;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                transition: transform 0.2s;
            }
            .card:hover {
                transform: translateY(-5px);
            }
            .card h2 {
                color: #333;
                margin-bottom: 1rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            .card .icon {
                font-size: 1.5rem;
            }
            .stat {
                display: flex;
                justify-content: space-between;
                padding: 0.75rem 0;
                border-bottom: 1px solid #eee;
            }
            .stat:last-child {
                border-bottom: none;
            }
            .stat-label {
                color: #666;
            }
            .stat-value {
                font-weight: bold;
                color: #667eea;
            }
            .api-links {
                background: white;
                border-radius: 12px;
                padding: 1.5rem;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            }
            .api-links h3 {
                margin-bottom: 1rem;
                color: #333;
            }
            .api-link {
                display: block;
                padding: 0.75rem 1rem;
                margin-bottom: 0.5rem;
                background: #f7fafc;
                border-radius: 6px;
                color: #667eea;
                text-decoration: none;
                transition: background 0.2s;
            }
            .api-link:hover {
                background: #edf2f7;
            }
            .loading {
                text-align: center;
                padding: 2rem;
                color: white;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Atlassian Dashboard</h1>
                <p>Unified view of Jira, Confluence, and Compass</p>
            </div>

            <div class="cards" id="stats">
                <div class="loading">Loading dashboard data...</div>
            </div>

            <div class="api-links">
                <h3>📡 API Endpoints</h3>
                <a href="/api/jira/health" class="api-link">📊 Jira Project Health</a>
                <a href="/api/jira/issues?limit=10" class="api-link">📋 Jira Issues</a>
                <a href="/api/confluence/spaces" class="api-link">📚 Confluence Spaces</a>
                <a href="/api/confluence/pages?space=DIN" class="api-link">📄 Confluence Pages</a>
                <a href="/api/compass/components" class="api-link">🔧 Compass Components</a>
                <a href="/docs" class="api-link">📖 API Documentation (Swagger UI)</a>
            </div>
        </div>

        <script>
            // Load dashboard data
            async function loadDashboard() {
                try {
                    const [jiraHealth, confluenceSpaces, compassComponents] = await Promise.all([
                        fetch('/api/jira/health').then(r => r.json()),
                        fetch('/api/confluence/spaces').then(r => r.json()),
                        fetch('/api/compass/components').then(r => r.json())
                    ]);

                    const statsHTML = `
                        <div class="card">
                            <h2><span class="icon">📊</span> Jira Project</h2>
                            <div class="stat">
                                <span class="stat-label">Total Issues</span>
                                <span class="stat-value">${jiraHealth.total_issues}</span>
                            </div>
                            <div class="stat">
                                <span class="stat-label">Blocked</span>
                                <span class="stat-value" style="color: ${jiraHealth.blocked > 0 ? 'red' : 'green'}">${jiraHealth.blocked}</span>
                            </div>
                            <div class="stat">
                                <span class="stat-label">Overdue</span>
                                <span class="stat-value" style="color: ${jiraHealth.overdue > 0 ? 'red' : 'green'}">${jiraHealth.overdue}</span>
                            </div>
                        </div>

                        <div class="card">
                            <h2><span class="icon">📚</span> Confluence</h2>
                            <div class="stat">
                                <span class="stat-label">Total Spaces</span>
                                <span class="stat-value">${confluenceSpaces.length}</span>
                            </div>
                            ${confluenceSpaces.map(s => `
                                <div class="stat">
                                    <span class="stat-label">${s.key}</span>
                                    <span class="stat-value">${s.total_pages} pages</span>
                                </div>
                            `).join('')}
                        </div>

                        <div class="card">
                            <h2><span class="icon">🔧</span> Compass</h2>
                            <div class="stat">
                                <span class="stat-label">Total Components</span>
                                <span class="stat-value">${compassComponents.length}</span>
                            </div>
                        </div>
                    `;

                    document.getElementById('stats').innerHTML = statsHTML;
                } catch (error) {
                    console.error('Error loading dashboard:', error);
                    document.getElementById('stats').innerHTML = `
                        <div class="card">
                            <h2>❌ Error Loading Data</h2>
                            <p>Please check API credentials and try again.</p>
                        </div>
                    `;
                }
            }

            loadDashboard();
            setInterval(loadDashboard, 60000); // Refresh every minute
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "jira": jira_manager is not None,
        "confluence": confluence_manager is not None,
        "compass": compass_manager is not None
    }


# ==================== Jira API ====================

@app.get("/api/jira/health", response_model=ProjectHealth)
async def jira_health():
    """Get Jira project health"""
    if not jira_manager:
        raise HTTPException(status_code=503, detail="Jira manager not initialized")

    try:
        report = jira_manager.generate_sprint_report()

        return ProjectHealth(
            total_issues=report['summary']['total_active'],
            blocked=report['summary']['blocked_count'],
            overdue=report['summary']['overdue_count'],
            by_status=report['issues_by_status'],
            by_priority=report['issues_by_priority']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jira/issues", response_model=List[IssueInfo])
async def jira_issues(jql: str = "project = DIN", limit: int = 50):
    """Get Jira issues"""
    if not jira_manager:
        raise HTTPException(status_code=503, detail="Jira manager not initialized")

    try:
        issues = jira_manager.search_issues(jql, max_results=limit)

        return [
            IssueInfo(
                key=issue['key'],
                summary=issue['fields']['summary'],
                status=issue['fields']['status']['name'],
                priority=issue['fields']['priority']['name'],
                assignee=issue['fields'].get('assignee', {}).get('displayName') if issue['fields'].get('assignee') else None
            )
            for issue in issues
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Confluence API ====================

@app.get("/api/confluence/spaces", response_model=List[SpaceInfo])
async def confluence_spaces():
    """Get Confluence spaces"""
    if not confluence_manager:
        raise HTTPException(status_code=503, detail="Confluence manager not initialized")

    try:
        spaces = confluence_manager.get_all_spaces(limit=100)

        result = []
        for space in spaces:
            pages = confluence_manager.get_all_pages(space['key'], limit=1000)
            result.append(SpaceInfo(
                key=space['key'],
                name=space['name'],
                total_pages=len(pages)
            ))

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/confluence/pages")
async def confluence_pages(space: str = "DIN", limit: int = 50):
    """Get Confluence pages"""
    if not confluence_manager:
        raise HTTPException(status_code=503, detail="Confluence manager not initialized")

    try:
        pages = confluence_manager.get_all_pages(space, limit=limit)

        return [
            {
                "id": page['id'],
                "title": page['title'],
                "type": page['type']
            }
            for page in pages
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Compass API ====================

@app.get("/api/compass/components", response_model=List[ComponentInfo])
async def compass_components():
    """Get Compass components"""
    if not compass_manager:
        raise HTTPException(status_code=503, detail="Compass manager not initialized")

    try:
        components = compass_manager.get_components()

        return [
            ComponentInfo(
                id=comp['id'],
                name=comp['name'],
                type=comp['typeId'],
                description=comp.get('description')
            )
            for comp in components
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Startup ====================

@app.on_event("startup")
async def startup_event():
    """Initialize managers on startup"""
    print("🚀 Starting Atlassian Dashboard...")
    init_managers()
    print("✅ Dashboard ready!")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
