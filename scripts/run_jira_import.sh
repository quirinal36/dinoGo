#!/bin/bash
# Jira Import Runner Script
# Loads environment variables from .mcp.json and runs the import

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🔧 Loading Jira credentials from .mcp.json..."

# Extract environment variables from .mcp.json using Python
export ATLASSIAN_SITE=$(python3 -c "import json; config=json.load(open('$PROJECT_ROOT/.mcp.json')); print(config['mcpServers']['atlassian']['env']['ATLASSIAN_SITE'])")
export ATLASSIAN_USER_EMAIL=$(python3 -c "import json; config=json.load(open('$PROJECT_ROOT/.mcp.json')); print(config['mcpServers']['atlassian']['env']['ATLASSIAN_USER_EMAIL'])")
export ATLASSIAN_API_TOKEN=$(python3 -c "import json; config=json.load(open('$PROJECT_ROOT/.mcp.json')); print(config['mcpServers']['atlassian']['env']['ATLASSIAN_API_TOKEN'])")

echo "✅ Environment variables loaded"
echo ""

# Activate virtual environment and run script
echo "🚀 Running Jira import script..."
source "$PROJECT_ROOT/venv/bin/activate"
python3 "$SCRIPT_DIR/jira_import.py"

echo ""
echo "✅ Import process completed!"
