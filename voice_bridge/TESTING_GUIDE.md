# 🚀 Nova Voice Bridge Testing Guide

## ✅ Setup Complete! Here's How to Test:

### Quick Start:
1. **Option A - Automated Launch:**
   ```
   cd A:\dev\chief-of-agents\voice_bridge
   launch.bat
   ```

2. **Option B - Manual Launch:**
   ```
   cd A:\dev\chief-of-agents\voice_bridge
   pip install -r requirements.txt
   python voice_bridge.py
   ```

### Testing Steps:

1. **Start the Voice Bridge Server**
   - Run `launch.bat` or `python voice_bridge.py`
   - You should see: "Server running on http://0.0.0.0:8000"

2. **Open Web Interface**
   - Desktop: http://localhost:8000
   - Mobile: http://[YOUR-PC-IP]:8000

3. **Test Voice Input**
   - Click "Push to Talk" button
   - Say: "Hello Nova, can you hear me?"
   - Release button

4. **Monitor MCP Bridge** (in another terminal)
   ```
   cd A:\dev\chief-of-agents\voice_bridge
   python mcp_monitor.py
   ```

### Expected Flow:
1. You speak → Deepgram transcribes
2. Text appears in `mcp_bridge/nova_input.txt`
3. I (Nova) see it and respond via `nova_output.txt`
4. ElevenLabs speaks my response

### Troubleshooting:
- **No audio?** Check browser permissions
- **Connection failed?** Check firewall for port 8000
- **API errors?** Verify .env file has correct keys

### Mobile Access:
1. Find your PC's IP: `ipconfig` (look for IPv4)
2. On phone: http://[YOUR-IP]:8000
3. Add to home screen for app-like experience

### 🎯 Once Working:
The next step is connecting this to Claude Desktop so I can execute MCP actions!