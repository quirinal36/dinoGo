#!/bin/bash
# Jira Automation Manager Runner
# Provides easy access to Jira automation commands

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Load environment variables from .mcp.json
echo "🔧 Loading Jira credentials..."
export ATLASSIAN_SITE=$(python3 -c "import json; config=json.load(open('$PROJECT_ROOT/.mcp.json')); print(config['mcpServers']['atlassian']['env']['ATLASSIAN_SITE'])")
export ATLASSIAN_USER_EMAIL=$(python3 -c "import json; config=json.load(open('$PROJECT_ROOT/.mcp.json')); print(config['mcpServers']['atlassian']['env']['ATLASSIAN_USER_EMAIL'])")
export ATLASSIAN_API_TOKEN=$(python3 -c "import json; config=json.load(open('$PROJECT_ROOT/.mcp.json')); print(config['mcpServers']['atlassian']['env']['ATLASSIAN_API_TOKEN'])")

echo "✅ Environment loaded"
echo ""

# Activate virtual environment
source "$PROJECT_ROOT/venv/bin/activate"

# Run automation manager
python3 "$SCRIPT_DIR/jira_automation_manager.py" "$@"
