# MCP Bridge Implementation Guide

## Overview

The MCP Bridge connects Nova's voice interface to Claude Desktop, enabling voice control of MCP tools without API calls. This document explains the implementation completed on 2025-05-28.

## Architecture

```
Voice Input → Deepgram → Text → nova_input.txt → Claude Desktop → MCP Tools
                                                         ↓
Speaker ← ElevenLabs ← Text ← nova_output.txt ← Response
```

## Components Implemented

### 1. MCPBridgeHandler (`mcp_bridge_handler.py`)
- Manages file-based communication between voice interface and Claude Desktop
- Implements request-response pattern with unique IDs
- Features:
  - File locking to prevent race conditions
  - 30-second timeout for responses
  - JSON-based message format
  - Automatic file cleanup

### 2. Updated Voice Bridge (`voice_bridge.py`)
- Modified `generate_response()` to use MCPBridgeHandler
- Sends transcribed text to Claude via bridge files
- Maintains conversation context

### 3. Nova MCP Monitor (`nova_mcp_monitor.py`)
- Template script for monitoring bridge files
- Can be customized for specific MCP tools
- Shows example command patterns

### 4. Claude Desktop Bridge (`claude_desktop_nova_bridge.py`)
- Script to run IN Claude Desktop
- Monitors for voice commands
- Processes commands using MCP tools
- Sends responses back through bridge

## Usage Instructions

### Step 1: Start Voice Interface
```bash
cd voice_bridge
python voice_bridge.py
# or use ./launch.sh
```
Open http://localhost:8000 in your browser

### Step 2: Start Claude Desktop Monitor
1. Open Claude Desktop
2. Copy entire contents of `claude_desktop_nova_bridge.py`
3. Paste and run in Claude Desktop
4. Keep it running

### Step 3: Use Voice Commands
1. Click "Start Recording" in browser
2. Say commands like:
   - "What's on my calendar today?"
   - "Send an email to Sarah about the project"
   - "Create a task to review the proposal"
   - "Find the latest sales report"

## Message Format

### Request (nova_input.txt)
```json
{
  "id": "uuid-here",
  "timestamp": "2025-05-28T10:30:00",
  "message": "What meetings do I have today?",
  "context": [...previous messages...],
  "status": "pending"
}
```

### Response (nova_output.txt)
```json
{
  "request_id": "uuid-here",
  "timestamp": "2025-05-28T10:30:01",
  "message": "You have 3 meetings today...",
  "status": "complete"
}
```

## Error Handling

1. **Timeout**: 30-second timeout for responses
2. **File Locking**: Prevents concurrent access issues
3. **JSON Validation**: Handles malformed messages
4. **Connection Recovery**: Automatic retry on errors

## Testing the Bridge

1. **Manual Test**:
   - Write a test message to `nova_input.txt`
   - Run monitor in Claude Desktop
   - Check `nova_output.txt` for response

2. **Voice Test**:
   - Start voice interface
   - Start Claude Desktop monitor
   - Speak a command
   - Listen for response

## Next Steps

1. **Customize MCP Integration**: Modify `claude_desktop_nova_bridge.py` to use actual MCP tools
2. **Add More Commands**: Extend command patterns for your specific needs
3. **Improve Context**: Enhance context management for better conversations
4. **Deploy**: Set up for remote access (ngrok, cloud deployment)

## Troubleshooting

- **No response**: Check if monitor is running in Claude Desktop
- **File permissions**: Ensure bridge files are writable
- **Port conflicts**: Voice interface defaults to port 8000
- **API keys**: Verify Deepgram and ElevenLabs keys in `.env`