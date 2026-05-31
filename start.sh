#!/bin/bash

echo ""
echo "=========================================="
echo "🚀 WEB MANAGER - Starting..."
echo "=========================================="
echo ""

# Run error handler first
python3 error_handler.py

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo "⚠️ Installing cloudflared..."
    curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
    chmod +x cloudflared
    sudo mv cloudflared /usr/local/bin/
fi

# Start the app
python3 app.py