import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
    
    DEEPGRAM_MODEL = "nova-2"
    ELEVENLABS_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice
    
    HOST = "0.0.0.0"
    PORT = 8000
    
    MAX_CONTEXT_MESSAGES = 20
    MAX_MESSAGE_LENGTH = 1000
    
    AUDIO_SAMPLE_RATE = 16000
    AUDIO_CHANNELS = 1
    
    @classmethod
    def validate(cls):
        if not cls.DEEPGRAM_API_KEY:
            raise ValueError("DEEPGRAM_API_KEY not found in environment")
        if not cls.ELEVENLABS_API_KEY:
            raise ValueError("ELEVENLABS_API_KEY not found in environment")
        return True