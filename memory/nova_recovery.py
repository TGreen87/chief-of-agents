#!/usr/bin/env python3
"""
Nova Session Recovery
For when you hit Claude's chat limit
"""

print("""
🚀 NOVA SESSION RECOVERY
======================

When you hit the chat cap, start a new chat and say:

"I'm Tom, continuing Nova. Load nova_checkpoint.json"

Nova will:
1. Load checkpoint from nova_checkpoint.json
2. Retrieve context from Memory Bank
3. Check Knowledge Graph for relationships
4. Continue exactly where you left off

Current Memory Systems:
- ✅ Knowledge Graph (relationships)
- ✅ Memory Bank (documents)
- ✅ Local checkpoint (immediate state)

This solves the context window problem!
""")

# Quick status check
import os
import json

if os.path.exists('nova_checkpoint.json'):
    with open('nova_checkpoint.json', 'r') as f:
        checkpoint = json.load(f)
    
    print("\n📊 Last Checkpoint:")
    print(f"Time: {checkpoint['timestamp']}")
    print(f"Task: {checkpoint['current_task']}")
    print(f"\nCompleted: {len(checkpoint['completed'])} items")
    print(f"Next Steps: {len(checkpoint['next_steps'])} items")
else:
    print("\n⚠️  No checkpoint found - start fresh")
