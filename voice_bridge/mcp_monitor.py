#!/usr/bin/env python3
"""
Nova MCP Bridge Monitor
Watches for messages from voice bridge and simulates Nova responses
"""
import time
import os
from pathlib import Path

INPUT_FILE = Path("mcp_bridge/nova_input.txt")
OUTPUT_FILE = Path("mcp_bridge/nova_output.txt")

print("🤖 Nova MCP Bridge Monitor")
print("Waiting for voice messages...")
print("-" * 40)

last_input = ""

while True:
    try:
        if INPUT_FILE.exists():
            current_input = INPUT_FILE.read_text().strip()
            
            if current_input and current_input != last_input:
                print(f"\n📥 Received: {current_input}")
                
                # Simulate Nova processing
                response = f"I heard you say: '{current_input}'. This is Nova responding through the MCP bridge!"
                
                # Write response
                OUTPUT_FILE.write_text(response)
                print(f"📤 Responded: {response}")
                
                last_input = current_input
                
    except Exception as e:
        print(f"Error: {e}")
    
    time.sleep(0.5)