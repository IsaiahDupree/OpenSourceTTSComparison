# Qwen3-TTS Quick Test Guide

## Current Status

✅ **Space is accessible** - HTTP 200 OK
⚠️ **Python gradio_client has WebSocket issues** - Connection fails
✅ **Browser JavaScript works** - Use `@gradio/client` in browser

## Quick Test Options

### Option 1: Browser Test (Recommended)

1. Open `test_qwen3_browser.html` in a browser
2. It will automatically test the API
3. Audio will play if successful

### Option 2: Python (with known issues)

```bash
python test_qwen3_tts_simple.py
```

**Known Issue**: WebSocket connection fails with `gradio_client`

### Option 3: Use Web Interface

1. Visit: https://qwen-qwen3-tts-voice-design.hf.space
2. Enter text and voice instruction
3. Click "Generate Voice"

## API Features

- **No reference audio needed** - Just describe the voice
- **Natural language descriptions** - "A clear female voice, moderate speed"
- **Multiple voice dimensions** - Persona, Pace, Timbre, Emotion, Scenario

## Example Voice Instructions

- "A clear and natural female voice, moderate speed, stable tone"
- "A loud, powerful male voice exhibiting resilience and authority"
- "A bright, high-pitched young girl's voice. Lively and animated"
- "Professional broadcasting style. The pace starts slow and accelerates naturally"

## Files Created

- `test_qwen3_tts.py` - Full test suite
- `test_qwen3_tts_simple.py` - Quick test
- `test_qwen3_browser.html` - Browser test (works!)
- `QWEN3_TTS_TEST_SUMMARY.md` - Full documentation

