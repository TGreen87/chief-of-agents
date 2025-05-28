#!/usr/bin/env python3
"""
Quick fix for Deepgram deprecation warning
Run this to update voice_bridge.py
"""
import sys

print("🔧 Fixing Deepgram API deprecation...")

# Read the file
with open('voice_bridge.py', 'r') as f:
    content = f.read()

# Fix the deprecated API call
old_line = 'self.deepgram_connection = deepgram.listen.asynclive.v("1")'
new_line = 'self.deepgram_connection = deepgram.listen.asyncwebsocket.v("1")'

if old_line in content:
    content = content.replace(old_line, new_line)
    
    # Write back
    with open('voice_bridge.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed! Restart the server to apply changes.")
else:
    print("❓ Line not found or already fixed.")

# Also check if process_audio_chunk exists
if 'async def process_audio_chunk' not in content:
    print("\n⚠️  Warning: process_audio_chunk method is missing!")
    print("This means audio won't be sent to Deepgram properly.")