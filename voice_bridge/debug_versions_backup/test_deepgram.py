#!/usr/bin/env python3
"""
Test Deepgram API connection
"""
import asyncio
from deepgram import DeepgramClient, PrerecordedOptions
import os
from dotenv import load_dotenv

load_dotenv()

async def test_deepgram():
    api_key = os.getenv("DEEPGRAM_API_KEY")
    if not api_key:
        print("❌ No DEEPGRAM_API_KEY found in .env")
        return
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    try:
        # Test with a simple transcription
        deepgram = DeepgramClient(api_key)
        
        # Create a test audio file (silent)
        test_audio = b'\x00' * 32000  # 1 second of silence at 16kHz
        
        options = PrerecordedOptions(
            model="nova-2",
            language="en-US"
        )
        
        print("🔍 Testing Deepgram connection...")
        
        # This will test if the API key is valid
        response = await deepgram.listen.asyncprerecorded.v("1").transcribe_raw(
            {"buffer": test_audio}, 
            options
        )
        
        print("✅ Deepgram API key is valid!")
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"❌ Deepgram test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_deepgram())