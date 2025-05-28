import asyncio
import json
import base64
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
import logging
from pathlib import Path
from datetime import datetime

from config import Config
from context_manager import ContextManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize clients
Config.validate()
deepgram = DeepgramClient(Config.DEEPGRAM_API_KEY)
elevenlabs = ElevenLabs(api_key=Config.ELEVENLABS_API_KEY)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# MCP Bridge paths
MCP_INPUT = Path("mcp_bridge/nova_input.txt")
MCP_OUTPUT = Path("mcp_bridge/nova_output.txt")

class VoiceBridgeSession:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.context_manager = ContextManager(
            max_messages=Config.MAX_CONTEXT_MESSAGES,
            max_length=Config.MAX_MESSAGE_LENGTH
        )
        self.deepgram_connection = None
        self.is_processing = False
    
    async def start_deepgram(self):
        try:
            # Use the new asyncwebsocket API
            self.deepgram_connection = deepgram.listen.asyncwebsocket.v("1")
            
            async def on_message(self, result, **kwargs):
                sentence = result.channel.alternatives[0].transcript
                if len(sentence) > 0:
                    await self.handle_transcription(sentence)
            
            async def on_error(self, error, **kwargs):
                logger.error(f"Deepgram error: {error}")
            
            self.deepgram_connection.on(LiveTranscriptionEvents.Transcript, on_message)
            self.deepgram_connection.on(LiveTranscriptionEvents.Error, on_error)
            
            options = LiveOptions(
                model=Config.DEEPGRAM_MODEL,
                language="en-US",
                smart_format=True,
                encoding="linear16",
                channels=Config.AUDIO_CHANNELS,
                sample_rate=Config.AUDIO_SAMPLE_RATE
            )
            
            await self.deepgram_connection.start(options)
            logger.info("Deepgram connection started")
            
        except Exception as e:
            logger.error(f"Failed to start Deepgram: {e}")
            raise
    
    async def process_audio_chunk(self, audio_data: bytes):
        """Send audio data to Deepgram"""
        try:
            if self.deepgram_connection:
                await self.deepgram_connection.send(audio_data)
        except Exception as e:
            logger.error(f"Error sending audio to Deepgram: {e}")
    
    async def handle_transcription(self, text: str):
        if self.is_processing:
            return
        
        self.is_processing = True
        try:
            # Add to context
            self.context_manager.add_message("user", text)
            
            # Send transcription to client
            await self.websocket.send_json({
                "type": "transcription",
                "text": text
            })
            
            # Write to MCP bridge
            timestamp = datetime.now().isoformat()
            MCP_INPUT.write_text(f"[{timestamp}] {text}")
            logger.info(f"Wrote to MCP bridge: {text}")
            
            # Wait for response from MCP bridge
            response = await self.wait_for_mcp_response()
            
            # Generate audio response
            if response:
                audio_data = await self.generate_audio(response)
                await self.stream_audio(audio_data)
        
        finally:
            self.is_processing = False