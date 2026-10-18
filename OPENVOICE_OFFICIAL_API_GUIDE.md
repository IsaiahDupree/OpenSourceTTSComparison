# OpenVoice V2 Official API Guide

## Key Information from Official Documentation

### API Endpoint

**Replica Endpoint (Recommended):**
```
https://myshell-ai-openvoicev2.hf.space/--replicas/c2rsh/
```

**Standard Endpoint:**
```
myshell-ai/OpenVoiceV2
```

### API Format

```python
from gradio_client import Client

client = Client("https://myshell-ai-openvoicev2.hf.space/--replicas/c2rsh/", hf_token="your_token")

result = client.predict(
    "Howdy!",                    # Text Prompt (str)
    "en_default",                # Style (str from dropdown)
    "path/to/reference.wav",     # Reference Audio (filepath or URL)
    True,                        # Agree to MIT License (bool)
    fn_index=1
)

# Returns:
# (
#   info: str,                    # Info textbox
#   synthesised_audio: filepath,  # Generated audio
#   reference_audio_used: filepath # Reference audio used
# )
```

### Important Constraints

1. **Text Prompt:**
   - One or two sentences at a time is better
   - Up to 200 text characters maximum
   - Longer text may cause issues

2. **Style Options:**
   - `en_default`, `en_us`, `en_br`, `en_au`, `en_in`
   - `es_default` (Spanish)
   - `fr_default` (French)
   - `jp_default` (Japanese)
   - `zh_default` (Chinese) - only supports 'default' style
   - `kr_default` (Korean)

3. **Reference Audio:**
   - Can be local filepath or URL
   - Should be a short audio clip of the target voice
   - WAV format recommended

4. **Agree:**
   - Must be `True` to agree to MIT License
   - Required for API calls

### Return Format

The API returns a tuple with 3 elements:
1. **Info** (str): Status/information message
2. **Synthesised Audio** (filepath): Path to generated audio file
3. **Reference Audio Used** (filepath): Path to reference audio that was used

### Updated Code

I've updated `pubsub/voice_processor.py` to:
- ✅ Use the replica endpoint first (more stable)
- ✅ Validate text length (truncate to 200 chars)
- ✅ Accept filepath directly (per docs)
- ✅ Fallback to handle_file if needed
- ✅ Use correct API format

### Current Status

**Connection:** ✅ Works (connects to replica endpoint)  
**API Calls:** ⚠️ Still returns None error (Space needs wake-up)

### Solution

The Space needs to be woken up first:

1. **Visit the Space UI:**
   - https://huggingface.co/spaces/myshell-ai/OpenVoiceV2

2. **Generate one audio manually:**
   - Upload reference audio
   - Enter text
   - Click generate
   - This wakes up the Space

3. **Then use the API:**
   ```bash
   $env:HF_TOKEN="your_token"
   python process_voice_hq.py
   ```

### Testing

Run the official API test:
```bash
python test_openvoice_official_api.py
```

This uses the exact format from the official documentation.

## Features of OpenVoice V2

- ✅ Better audio quality than V1
- ✅ Native multi-lingual support (6 languages)
- ✅ Free commercial use (MIT License)
- ✅ Granular voice style control
- ✅ Zero-shot cross-lingual voice cloning
- ✅ Tone color replication

## Next Steps

1. Wake up the Space via UI
2. Test with the updated code
3. The pub/sub system is ready - just needs a working Space

