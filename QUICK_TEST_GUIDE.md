# Quick Test Guide - What Works

## ✅ WORKING NOW

### Qwen3-TTS Web Interface
**This is the only fully working option right now.**

1. Open: https://qwen-qwen3-tts-voice-design.hf.space
2. Enter text: "Hello! This is a test."
3. Enter voice instruction: "A clear and natural female voice, moderate speed, stable tone."
4. Click "Generate Voice"
5. ✅ Audio will be generated!

## ⚠️ PARTIALLY WORKING

### Local OpenVoice Server
**Server runs but crashes on generation**

1. Check if server is running: `http://localhost:7860`
2. If not, start it: `python start_server.py`
3. Check the server window for error messages
4. Common errors:
   - `whisper_timestamped` not found
   - Model checkpoint missing
   - CUDA errors

## ❌ NOT WORKING

### OpenVoice V2 API
- Cold start issues
- `ValueError: None` errors
- Retry logic helps but not reliable

### Qwen3-TTS Python API
- WebSocket connection fails
- Use browser JavaScript instead

## 🎯 Quick Test Commands

```bash
# Test all APIs
python test_all_tts_apis.py

# Test what works
python test_what_works.py

# Test local server via HTTP
python test_local_http_direct.py
```

## 📋 Summary

| Solution | Status | Use For |
|----------|--------|---------|
| Qwen3-TTS Web | ✅ Working | Production use |
| Local OpenVoice | ⚠️ Server crashes | Fix errors first |
| OpenVoice V2 | ❌ Cold start | Wait for warm-up |
| Qwen3-TTS API | ❌ WebSocket | Use web interface |

**Best option right now: Qwen3-TTS Web Interface** ✅

