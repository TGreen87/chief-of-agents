# Voice Bridge

A real-time voice interaction system with WebSocket streaming, speech-to-text, and text-to-speech capabilities.

## Features

- **Real-time voice streaming** via WebSocket
- **Speech-to-text** using Deepgram Nova-2
- **Text-to-speech** using ElevenLabs
- **Mobile-friendly** web interface
- **Context management** with conversation limits
- **Low-latency** audio processing

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

Edit `.env`:
```
DEEPGRAM_API_KEY=your_actual_deepgram_key
ELEVENLABS_API_KEY=your_actual_elevenlabs_key
```

### 3. Run the Server

```bash
python voice_bridge.py
```

The server will start on `http://0.0.0.0:8000`

### 4. Access the Interface

- **Desktop**: Open `http://localhost:8000` in your browser
- **Mobile**: Open `http://[your-computer-ip]:8000` on your phone (must be on same network)

## Usage

1. **Hold to Talk**: Press and hold the blue button to speak
2. **Clear Context**: Reset the conversation history
3. **Get Summary**: View session statistics

## Architecture

- **FastAPI** - WebSocket server and static file hosting
- **Deepgram** - Real-time speech-to-text transcription
- **ElevenLabs** - Natural text-to-speech synthesis
- **Context Manager** - Maintains conversation history with limits

## Configuration

Edit `config.py` to modify:
- Voice model (default: Rachel)
- Context limits (default: 20 messages)
- Audio settings (sample rate, channels)
- Server host/port

## API Integration

The `generate_response()` method in `voice_bridge.py` is a placeholder. Replace it with your AI service:

```python
async def generate_response(self, text: str) -> str:
    # Replace with Claude, GPT, or your AI service
    response = await your_ai_service.complete(
        messages=self.context_manager.get_context()
    )
    return response
```

## Troubleshooting

### Microphone Access
- Browser must have microphone permissions
- HTTPS required for production (localhost works without)

### Connection Issues
- Check firewall settings for port 8000
- Ensure both devices on same network for mobile access

### Audio Quality
- Use headphones to prevent echo
- Check browser console for WebSocket errors