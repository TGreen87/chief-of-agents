"""MCP Bridge Handler for Nova Voice Interface

This module handles communication between the voice interface and Claude Desktop
using text files as a bridge. It implements a request-response pattern with
proper timing, file locking, and error handling.
"""

import json
import time
import os
import asyncio
from pathlib import Path
import logging
from datetime import datetime
import fcntl
import uuid

logger = logging.getLogger(__name__)

class MCPBridgeHandler:
    def __init__(self, input_file="mcp_bridge/nova_input.txt", output_file="mcp_bridge/nova_output.txt"):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)
        self.timeout = 30  # seconds to wait for response
        self.poll_interval = 0.1  # seconds between polling attempts
        
        # Ensure directories exist
        self.input_file.parent.mkdir(parents=True, exist_ok=True)
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize files if they don't exist
        if not self.input_file.exists():
            self.input_file.write_text("")
        if not self.output_file.exists():
            self.output_file.write_text("")
    
    async def send_to_claude(self, message: str, context: list = None) -> str:
        """Send a message to Claude via the MCP bridge and wait for response."""
        request_id = str(uuid.uuid4())
        
        # Prepare the request
        request = {
            "id": request_id,
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "context": context or [],
            "status": "pending"
        }
        
        # Write to input file with file locking
        try:
            with open(self.input_file, 'w') as f:
                # Acquire exclusive lock
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    json.dump(request, f, indent=2)
                    f.flush()
                    os.fsync(f.fileno())
                finally:
                    # Release lock
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                    
            logger.info(f"Sent request {request_id} to Claude")
            
            # Wait for response
            response = await self._wait_for_response(request_id)
            return response
            
        except Exception as e:
            logger.error(f"Error sending to Claude: {e}")
            return f"I'm having trouble connecting to my brain. Please try again. (Error: {str(e)})"
    
    async def _wait_for_response(self, request_id: str) -> str:
        """Poll the output file for a response with the matching request ID."""
        start_time = time.time()
        last_content = None
        
        while time.time() - start_time < self.timeout:
            try:
                # Read output file with shared lock
                with open(self.output_file, 'r') as f:
                    fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                    try:
                        content = f.read().strip()
                    finally:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                
                # Check if content changed and is valid JSON
                if content and content != last_content:
                    try:
                        response_data = json.loads(content)
                        
                        # Check if this is our response
                        if response_data.get("request_id") == request_id:
                            if response_data.get("status") == "complete":
                                logger.info(f"Received response for {request_id}")
                                
                                # Clear the output file for next response
                                with open(self.output_file, 'w') as f:
                                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                                    try:
                                        f.write("")
                                        f.flush()
                                        os.fsync(f.fileno())
                                    finally:
                                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                                
                                return response_data.get("message", "No response message")
                            elif response_data.get("status") == "error":
                                return f"Error from Claude: {response_data.get('message', 'Unknown error')}"
                    
                    except json.JSONDecodeError:
                        # Not valid JSON yet, keep waiting
                        pass
                    
                    last_content = content
                
            except Exception as e:
                logger.error(f"Error reading response: {e}")
            
            # Wait before polling again
            await asyncio.sleep(self.poll_interval)
        
        # Timeout reached
        logger.warning(f"Timeout waiting for response to {request_id}")
        return "I'm taking too long to think. Please try again."
    
    def clear_bridge_files(self):
        """Clear both bridge files - useful for initialization."""
        try:
            with open(self.input_file, 'w') as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.write("")
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                    
            with open(self.output_file, 'w') as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    f.write("")
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                    
            logger.info("Cleared bridge files")
        except Exception as e:
            logger.error(f"Error clearing bridge files: {e}")