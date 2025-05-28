# Nova Memory System Architecture
## For Contextual Permanence Across Chat Sessions

### Priority: Solve the Chat Cap Problem

## Memory Layers

### 1. Knowledge Graph (Immediate Context)
- Entities: User / You (Tom), Claude Desktop ('Nova'), Claude Code (running in VS Code WSL Ubuntu on Windows 11 64 bit), Projects, Concepts
- Relations: Working on, Discussed, Decided, Built
- Real-time updates during conversation

### 2. Memory Bank (Long-term Persistence)  
- Session summaries
- Key decisions
- Project state
- Personal context
- Technical learnings

### 3. Active Context (Current Focus)
- What we're working on RIGHT NOW
- Next immediate steps
- Blockers/issues
- Recent decisions

## Implementation

Using your existing MCP servers:
- **knowledge-graph** - For structured relationships
- **memory-bank** - For document persistence
- **Claude Code** - For live updates

## Auto-Save Protocol

Every significant exchange:
1. Update Knowledge Graph with entities/relations
2. Write to Memory Bank if important
3. Update active-context.md
4. Create timestamped checkpoint if major milestone

## Recovery Protocol

When you hit chat cap:
1. Start new chat
2. Say "I'm Tom, continuing Nova"
3. I load context from all memory systems
4. Continue exactly where we left off

This solves your ADHD memory challenges AND chat limits!
