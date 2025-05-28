# Nova Voice Bridge Build Progress Tracker

## How to Monitor Claude Code:

### 1. Start the File Monitor (Recommended)
Open a new terminal and run:
```
cd A:\dev\chief-of-agents
python monitor_claude_code.py
```

### 2. Check Status Anytime
Double-click: `check_progress.bat`

### 3. Watch the Log File
```
type claude_code_progress.log
```

### 4. Expected Build Sequence:
- [ ] voice_bridge/ directory created
- [ ] requirements.txt
- [ ] .env.example
- [ ] config.py
- [ ] mcp_bridge/ directory
- [ ] voice_bridge.py
- [ ] context_manager.py
- [ ] static/ directory
- [ ] static/index.html
- [ ] static/app.js
- [ ] static/manifest.json
- [ ] README.md

### 5. If Claude Code seems stuck:
- Check if it's waiting for permissions
- Look for any error messages
- Tell me "check Claude Code status"