@echo off
cd /d "%~dp0\index-tts"
echo Starting Index-TTS WebUI...
echo.
echo Please wait while models load...
echo A browser window should open at http://127.0.0.1:7860
echo.
uv run webui.py
pause
