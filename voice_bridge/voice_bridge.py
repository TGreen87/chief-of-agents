import asyncio
import json
import base64
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
import logging
from config import Config
from context_manager import ContextManager

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

Config.validate()

deepgram = DeepgramClient(Config.DEEPGRAM_API_KEY)
elevenlabs = ElevenLabs(api_key=Config.ELEVENLABS_API_KEY)

class VoiceBridgeSession:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.context_manager = ContextManager(
            max_messages=Config.MAX_CONTEXT_MESSAGES,
            max_length=Config.MAX_MESSAGE_LENGTH
        )
        self.deepgram_connection = None
        self.is_processing = False
        self.last_audio_time = time.time()
        self.keep_alive_task = None
    
    async def start_deepgram(self):
        try:
            self.deepgram_connection = deepgram.listen.asyncwebsocket.v("1")
            
            async def on_message(result, **kwargs):
                logger.debug(f"Deepgram transcription result: {result}")
                sentence = result.channel.alternatives[0].transcript
                
                if result.is_final and len(sentence) > 0:
                    logger.info(f"Final transcription: {sentence}")
                    await self.handle_transcription(sentence)
                elif not result.is_final and len(sentence) > 0:
                    logger.debug(f"Interim transcription: {sentence}")
            
            async def on_error(error, **kwargs):
                logger.error(f"Deepgram error: {error}")
            
            async def on_metadata(metadata, **kwargs):
                logger.debug(f"Deepgram metadata: {metadata}")
            
            self.deepgram_connection.on(LiveTranscriptionEvents.Transcript, on_message)
            self.deepgram_connection.on(LiveTranscriptionEvents.Error, on_error)
            self.deepgram_connection.on(LiveTranscriptionEvents.Metadata, on_metadata)
            
            options = LiveOptions(
                model=Config.DEEPGRAM_MODEL,
                language="en-US",
                smart_format=True,
                encoding="linear16",
                channels=Config.AUDIO_CHANNELS,
                sample_rate=Config.AUDIO_SAMPLE_RATE,
                interim_results=True,
                utterance_end_ms=1000,
                vad_events=True
            )
            
            await self.deepgram_connection.start(options)
            logger.info("Deepgram connection started")
            
            # Start keep-alive task
            self.keep_alive_task = asyncio.create_task(self.keep_alive())
            
        except Exception as e:
            logger.error(f"Failed to start Deepgram: {e}")
            raise
    
    async def keep_alive(self):
        """Send keep-alive messages to Deepgram to prevent timeout"""
        while self.deepgram_connection:
            try:
                # Check if we haven't sent audio in 5 seconds
                if time.time() - self.last_audio_time > 5:
                    logger.debug("Sending keep-alive to Deepgram")
                    await self.deepgram_connection.keep_alive()
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Keep-alive error: {e}")
                break
    
    async def handle_transcription(self, text: str):
        if self.is_processing:
            return
        
        self.is_processing = True
        try:
            self.context_manager.add_message("user", text)
            
            await self.websocket.send_json({
                "type": "transcription",
                "text": text
            })
            
            response = await self.generate_response(text)
            
            self.context_manager.add_message("assistant", response)
            
            await self.websocket.send_json({
                "type": "response",
                "text": response
            })
            
            audio_stream = await self.generate_audio(response)
            await self.stream_audio(audio_stream)
            
        except Exception as e:
            logger.error(f"Error handling transcription: {e}")
            await self.websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        finally:
            self.is_processing = False
    
    async def generate_response(self, text: str) -> str:
        # Placeholder for AI response generation
        # In production, this would call Claude, GPT, or another AI service
        return f"I heard you say: '{text}'. This is a placeholder response."
    
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
    
    async def process_audio_chunk(self, audio_data: bytes):
        if self.deepgram_connection:
            self.last_audio_time = time.time()
            logger.debug(f"Sending audio chunk of size {len(audio_data)} to Deepgram")
            await self.deepgram_connection.send(audio_data)
    
    async def close(self):
        if self.keep_alive_task:
            self.keep_alive_task.cancel()
            try:
                await self.keep_alive_task
            except asyncio.CancelledError:
                pass
        
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
                logger.debug(f"Received audio chunk from client: {len(audio_data)} bytes")
                await session.process_audio_chunk(audio_data)
            
            elif message["type"] == "control":
                if message["action"] == "clear_context":
                    session.context_manager.clear()
                    await websocket.send_json({
                        "type": "status",
                        "message": "Context cleared"
                    })
                elif message["action"] == "get_summary":
                    summary = session.context_manager.get_summary()
                    await websocket.send_json({
                        "type": "summary",
                        "data": summary
                    })
    
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await session.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.HOST, port=Config.PORT)