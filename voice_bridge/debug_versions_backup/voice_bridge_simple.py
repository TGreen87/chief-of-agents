#!/usr/bin/env python3
"""
Simple voice bridge without Deepgram for testing
Just echoes audio levels and tests ElevenLabs
"""
import asyncio
import json
import base64
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
import logging
import struct

from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

Config.validate()
elevenlabs = ElevenLabs(api_key=Config.ELEVENLABS_API_KEY)

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    audio_chunks_received = 0
    
    try:
        # Send initial message
        await websocket.send_json({
            "type": "status",
            "message": "Connected (Deepgram bypassed for testing)"
        })
        
        while True:
            message = await websocket.receive_json()
            
            if message["type"] == "audio":
                audio_data = base64.b64decode(message["data"])
                audio_chunks_received += 1
                
                # Calculate audio level
                pcm_data = struct.unpack(f'{len(audio_data)//2}h', audio_data)
                max_level = max(abs(min(pcm_data)), max(pcm_data)) if pcm_data else 0
                level_percent = (max_level / 32768) * 100
                
                # Every 10 chunks, send a test message
                if audio_chunks_received % 10 == 0:
                    test_text = f"Audio test: {audio_chunks_received} chunks received, level: {level_percent:.1f}%"
                    
                    await websocket.send_json({
                        "type": "transcription",
                        "text": test_text
                    })
                    
                    # Test ElevenLabs
                    try:
                        response = elevenlabs.text_to_speech.convert(
                            voice_id=Config.ELEVENLABS_VOICE_ID,
                            text=f"Testing audio. Level at {int(level_percent)} percent.",
                            model_id="eleven_monolingual_v1",
                            voice_settings=VoiceSettings(
                                stability=0.5,
                                similarity_boost=0.5
                            )
                        )
                        
                        audio_chunks = []
                        for chunk in response:
                            audio_chunks.append(chunk)
                        
                        audio_response = b''.join(audio_chunks)
                        
                        # Stream back
                        chunk_size = 4096
                        for i in range(0, len(audio_response), chunk_size):
                            chunk = audio_response[i:i + chunk_size]
                            await websocket.send_json({
                                "type": "audio",
                                "data": base64.b64encode(chunk).decode('utf-8')
                            })
                            await asyncio.sleep(0.01)
                        
                        await websocket.send_json({
                            "type": "response",
                            "text": f"ElevenLabs test successful! Audio level: {level_percent:.1f}%"
                        })
                        
                    except Exception as e:
                        logger.error(f"ElevenLabs error: {e}")
                        await websocket.send_json({
                            "type": "error",
                            "message": f"ElevenLabs error: {str(e)}"
                        })
    
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    import uvicorn
    print("🎤 Simple Voice Bridge (No Deepgram)")
    print("This will test audio capture and ElevenLabs TTS")
    uvicorn.run(app, host="0.0.0.0", port=8000)