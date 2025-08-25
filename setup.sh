#!/bin/bash

# Code Navigation MCP Server Setup Script

echo "========================================="
echo "Code Navigation MCP Server Setup"
echo "========================================="

# Check Python version
python3 --version || { echo "Python 3 is required but not found."; exit 1; }

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run tests
echo ""
echo "Running tests..."
python test_server.py

# Show configuration
echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "To integrate with Claude Desktop, add the following to your claude_desktop_config.json:"
echo ""
cat << EOF
{
  "mcpServers": {
    "code-navigation": {
      "command": "python",
      "args": ["$(pwd)/server.py"],
      "env": {
        "PYTHONPATH": "$(pwd)",
        "MCP_MODE": "server",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
EOF

echo ""
echo "To run the server manually:"
echo "  source venv/bin/activate"
echo "  python server.py"
echo ""
echo "To run with Docker:"
echo "  docker-compose up"