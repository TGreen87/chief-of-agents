# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

***ALWAYS USE 'ULTRATHINK' WHEN THE USER ASKS ANY QUESTION***

## Project Overview: Nova - AI Chief of Staff

Nova is NOT just a voice interface project. It's an AI executive assistant system where Claude (YOU) acts as the brain with MCP tools for autonomous real-world actions. The key insight: **Claude IS Nova** - we're not building a separate AI.

## Nova's Purpose

- **AI Chief of Staff** for Tom (HR Executive with ADHD)
- **Executive Function Support** - proactive task management, meeting handling, email triage
- **Autonomous Action-Taking** - uses 20+ MCP tools to DO things, not just talk
- **Voice-First Interface** - enables hands-free operation while driving/walking/working

## Architecture

### System Flow
```
Voice Input → Voice Bridge → Claude Desktop → MCP Tools → Real Actions
                                  ↕
                           Memory Systems
```

### Core Components

1. **Voice Bridge** (`/voice_bridge/`)
   - WebSocket-based real-time streaming
   - Deepgram (speech-to-text) + ElevenLabs (text-to-speech)
   - **CRITICAL**: `generate_response()` is placeholder - needs MCP bridge connection

2. **Memory System** (Triple-layer for contextual permanence)
   - Knowledge Graph (entity relationships via MCP)
   - Memory Bank (long-term storage via MCP)
   - Local checkpoints (`nova_checkpoint.json`)

3. **MCP Integration**
   - Claude Code acts as MCP server
   - 20+ tools available (calendar, email, files, etc.)
   - NO API CALLS - uses Claude Desktop directly

## Common Development Commands

```bash
# Setup
pip install -r requirements.txt

# Run voice interface
cd voice_bridge
./launch.sh  # or launch.bat on Windows

# Monitor MCP activity
python monitor_claude_code.py

# Check project status
python quick-status.py

# Create checkpoint
./checkpoint-enhanced.sh "Description"
```

## Current State (May 27, 2025)

- ✅ Architecture clarified after nuclear cleanup
- ✅ Memory systems implemented
- ✅ Voice bridge structure built
- USER CLEANED UP FILE STRUCTURE:
   * fix all references / paths, 
   * understand new structure, 
   * added a memory folder which includes checkpoints and all memory files saved, this should function as the CORE ALIGNMENT folder between Claude Code, Claude Desktop and the User - Tom,
   * Removed old / redundant docs
   * Updated this file, Claude.md manually by user
   * User updated Nova_Project to be more clear about the design
   * User has moved the archived folder to another directory to ensure no confusion
- 📋 Next: TBC with consultation of the user

## Critical Context

### Technical Decisions
- **Please update this section based on my changes throughout the project, especially in /docs**

### Key Files
- `NOVA_PROJECT.md` - Project vision and current status
- `NOVA_MEMORY_ARCHITECTURE.md` - Memory system design - CRITICAL FOR AUTOMATIC UPDATE AND CONVERSATION PERSISTENCE
- `NOVA_COMPLETE_CONTEXT.md` - Full vision of the project
- `voice_bridge/mcp_bridge/` - Text files for Claude communication

## When Continuing This Project

1. Load checkpoint: Understand the full context of the project, CHECK with the user before making any changes

## Testing

```bash
# Test voice components
python nova-voice-test.py

# Verify MCP connection
python test-nova-components.py
```

## Important Notes

- The `/nova-archive-2025-05-27/` directory contains 82 old files - DO NOT USE
- Voice is just the interface - Nova's intelligence comes from Claude with MCP
- Priority is getting voice → action loop working, not perfecting the voice quality