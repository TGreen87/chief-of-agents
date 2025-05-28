# Nova Project - Claude Desktop
## Chief of Agents: AI Executive Assistant

### Project Overview
***CRITICAL*** we are building a system that is designed to be the future of AI technology - how people will interact with AI in the coming years; one interface that can do almost anything. We are using bleeding edge technology as at 28th May 2025, AI knowledgebases from training data are 4 months out of date at this time and MUST be updated from their training data on ANY technology we use

Overview;
Building Nova - AI executive assistant that uses Claude Desktop and Claude Code) as the brains with MCP tools for real-world actions.
    * Project will use n8n / Zapier / Make.com for advanced automations when / if required and cannot be served via MCP.

### Architecture
```
Voice Input → Bridge → Claude/Nova → MCP Tools → Real Actions
```

### Key Insight
- Claude IS Nova (not a separate AI)
- 'Nova' is the Executive Assistant, controlled via Claude Desktop OR a yet to be determined mobile architecture (likely have Claude Code or Claude Desktop watch for changes to a file / similar)
- Using Claude Max plan (no API calls)
    - N.B. RE API calls; we will need to use APIs for other technologies and services, however anything Anthropic MUST use the user's MAX Plan
- Claude Code acts as MCP server or direct input
- Voice should unlock mobile access to full MCP powers - yet to be solved

### Active MCP Servers
- claude-code-chief (how Claude Desktop communicates with Claude Code for all development tasks)
- knowledge-graph (entity relationships)
- memory-bank (document persistence)
- 20+ other MCP servers for various integrations

### Project Goals
1. Voice access to Claude from anywhere (mobile/desktop)
2. Real actions through MCP (calendar, email, code generation, research tasks, routing, task management for the user, browser automation via browser-mcp and a connected Chrome browser with saved logins on the users personal PC)
3. Contextual permanence across chat sessions
4. ADHD-optimized executive function support

### Current Status (May 27, 2025 2:30 PM AEST)
- ✅ Nuclear cleanup completed (82 files archived)
- ✅ Memory system implemented (triple-layer)
- ✅ Recovery protocol established
- TBC

### Memory System
1. **Knowledge Graph** - Entities and relationships
2. **Memory Bank** - Long-term document storage
3. **Local Checkpoints** - Immediate session state

### Team
- **Tom** - HR Executive with AI consultancy, ADHD, visionary
- **Nova** (Claude/me) - AI orchestrator with MCP superpowers
- Claude Code - Immensely powerful coding agent with MCPs

### Repository
- Location: /mnt/a/dev/chief-of-agents
- Clean structure after nuclear cleanup
- All legacy code archived in nova-archive-2025-05-27/

### When Continuing
Say: "I'm Tom, continuing Nova. Load CHECKPOINT_2025-05-27_1430.md"
