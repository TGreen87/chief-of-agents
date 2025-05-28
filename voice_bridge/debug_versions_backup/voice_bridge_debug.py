#!/usr/bin/env python3
"""
Debug version of voice bridge with better logging
"""
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
from datetime import datetime
from pathlib import Path

from config import Config
from context_manager import ContextManager

# Enhanced logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

Config.validate()

deepgram = DeepgramClient(Config.DEEPGRAM_API_KEY)
elevenlabs = ElevenLabs(api_key=Config.ELEVENLABS_API_KEY)

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
        self.audio_received = 0
        self.keep_alive_task = None
    
    async def start_deepgram(self):
        try:
            logger.info("Starting Deepgram connection...")
            self.deepgram_connection = deepgram.listen.asyncwebsocket.v("1")
            
            async def on_message(self, result, **kwargs):
                logger.debug(f"Deepgram transcript: {result}")
                sentence = result.channel.alternatives[0].transcript
                if len(sentence) > 0:
                    logger.info(f"Transcription: {sentence}")
                    await self.handle_transcription(sentence)
            
            async def on_error(self, error, **kwargs):
                logger.error(f"Deepgram error: {error}")
            
            async def on_open(self, open, **kwargs):
                logger.info("Deepgram connection opened")
            
            async def on_close(self, close, **kwargs):
                logger.info("Deepgram connection closed")
            
            self.deepgram_connection.on(LiveTranscriptionEvents.Transcript, on_message)
            self.deepgram_connection.on(LiveTranscriptionEvents.Error, on_error)
            self.deepgram_connection.on(LiveTranscriptionEvents.Open, on_open)
            self.deepgram_connection.on(LiveTranscriptionEvents.Close, on_close)
            
            options = LiveOptions(
                model=Config.DEEPGRAM_MODEL,
                language="en-US",
                smart_format=True,
                encoding="linear16",
                channels=1,
                sample_rate=16000,
                interim_results=True,
                utterance_end_ms=1000,
                vad_events=True,
                endpointing=300
            )
            
            await self.deepgram_connection.start(options)
            logger.info("Deepgram connection started")
            
            # Start keep-alive task
            self.keep_alive_task = asyncio.create_task(self.keep_alive())
            
        except Exception as e:
            logger.error(f"Failed to start Deepgram: {e}")
            raise    
    async def keep_alive(self):
        """Send keep-alive messages to Deepgram"""
        while self.deepgram_connection:
            await asyncio.sleep(5)
            if self.deepgram_connection:
                try:
                    await self.deepgram_connection.keep_alive()
                    logger.debug("Sent keep-alive to Deepgram")
                except Exception as e:
                    logger.error(f"Keep-alive error: {e}")
    
    async def process_audio_chunk(self, audio_data: bytes):
        """Send audio data to Deepgram"""
        self.audio_received += len(audio_data)
        logger.debug(f"Received audio chunk: {len(audio_data)} bytes (total: {self.audio_received})")
        
        try:
            if self.deepgram_connection:
                await self.deepgram_connection.send(audio_data)
                logger.debug("Sent audio to Deepgram")
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
            
            # Simple response for testing
            response = f"I heard you say: '{text}'. Audio received: {self.audio_received} bytes."
            
            await self.websocket.send_json({
                "type": "response",
                "text": response
            })
            
            # Test ElevenLabs
            try:
                audio_data = await self.generate_audio(response)
                await self.stream_audio(audio_data)
            except Exception as e:
                logger.error(f"Audio generation error: {e}")
        
        finally:
            self.is_processing = False
    
    async def generate_audio(self, text: str):
        try:
            response = elevenlabs.text_to_speech.convert(
                voice_id=Config.ELEVENLABS_VOICE_ID,
                text=text,
                model_id="eleven_monolingual_v1",
                voice_settings=VoiceSettings(
                    stability=0.5,
                    similarity_boost=0.5
                )
            )
            
            audio_chunks = []
            for chunk in response:
                audio_chunks.append(chunk)
            
            return b''.join(audio_chunks)
            
        except Exception as e:
            logger.error(f"Error generating audio: {e}")
            raise
    
    async def stream_audio(self, audio_data: bytes):
        chunk_size = 4096
        for i in range(0, len(audio_data), chunk_size):
            chunk = audio_data[i:i + chunk_size]
            await self.websocket.send_json({
                "type": "audio",
                "data": base64.b64encode(chunk).decode('utf-8')
            })
            await asyncio.sleep(0.01)
    
    async def close(self):
        if self.keep_alive_task:
            self.keep_alive_task.cancel()
        if self.deepgram_connection:
            await self.deepgram_connection.finish()
            self.deepgram_connection = None

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session = VoiceBridgeSession(websocket)
    
    try:
        await session.start_deepgram()
        
        while True:
            message = await websocket.receive_json()
            
            if message["type"] == "audio":
                audio_data = base64.b64decode(message["data"])
                await session.process_audio_chunk(audio_data)
            
            elif message["type"] == "control":
                if message["action"] == "clear_context":
                    session.context_manager.clear()
                    await websocket.send_json({
                        "type": "status",
                        "message": "Context cleared"
                    })
    
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await session.close()

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Nova Voice Bridge (Debug Mode)")
    uvicorn.run(app, host=Config.HOST, port=Config.PORT, log_level="debug")