@echo off
echo === Nova Voice Bridge Build Status ===
echo.
echo Checking for voice_bridge directory...
if exist "voice_bridge" (
    echo ✅ voice_bridge directory exists
    echo.
    echo Files created:
    dir /b /s voice_bridge
    echo.
    echo Directory structure:
    tree voice_bridge /f
) else (
    echo ❌ voice_bridge directory not yet created
)
echo.
echo === Recent Activity ===
if exist "claude_code_progress.log" (
    echo Last 10 log entries:
    powershell -command "Get-Content claude_code_progress.log -Tail 10"
) else (
    echo No progress log yet
)
echo.
pause