#!/bin/bash
# Dashboard Startup Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🚀 Starting Atlassian Dashboard..."

# Activate virtual environment
if [ -f "$PROJECT_ROOT/venv/bin/activate" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
    echo "✅ Virtual environment activated"
else
    echo "⚠️  Virtual environment not found. Please create it with: python3 -m venv venv"
fi

# Load environment variables from .mcp.json
export ATLASSIAN_SITE=$(python3 -c "import json; config=json.load(open('$PROJECT_ROOT/.mcp.json')); print(config['mcpServers']['atlassian']['env']['ATLASSIAN_SITE'])" 2>/dev/null)
export ATLASSIAN_USER_EMAIL=$(python3 -c "import json; config=json.load(open('$PROJECT_ROOT/.mcp.json')); print(config['mcpServers']['atlassian']['env']['ATLASSIAN_USER_EMAIL'])" 2>/dev/null)
export ATLASSIAN_API_TOKEN=$(python3 -c "import json; config=json.load(open('$PROJECT_ROOT/.mcp.json')); print(config['mcpServers']['atlassian']['env']['ATLASSIAN_API_TOKEN'])" 2>/dev/null)

if [ -z "$ATLASSIAN_SITE" ]; then
    echo "❌ Failed to load credentials from .mcp.json"
    exit 1
fi

echo "✅ Credentials loaded"
echo ""
echo "📊 Dashboard will be available at:"
echo "   http://localhost:8000"
echo ""
echo "📖 API Documentation (Swagger UI):"
echo "   http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run uvicorn
cd "$SCRIPT_DIR"
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
