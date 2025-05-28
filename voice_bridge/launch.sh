#!/bin/bash
echo "=== Nova Voice Bridge Launcher ==="
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt
echo ""
echo "Starting Nova Voice Bridge..."
echo ""
echo "Web Interface: http://localhost:8000"
echo "WebSocket: ws://localhost:8000/ws"
echo ""
echo "Press Ctrl+C to stop"
echo ""
python3 voice_bridge.py