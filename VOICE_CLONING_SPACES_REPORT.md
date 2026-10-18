# Voice Cloning Spaces Discovery Report

## Summary

**Found:** 66 voice cloning spaces on Hugging Face  
**Tested:** Top 10 spaces  
**Working APIs:** 4 spaces  
**Actually Working:** 1 space (but not true voice cloning)

## Working Spaces

### ✅ 1. VoiceCloning-be/text-to-speech
- **Status:** ✅ API Works
- **Type:** Text-to-Speech (pre-made voices, NOT voice cloning)
- **API:** Simple TTS with voice selection
- **URL:** https://huggingface.co/spaces/VoiceCloning-be/text-to-speech
- **Note:** This is TTS, not voice cloning from your audio

### ⚠️ 2. myshell-ai/OpenVoice (V1)
- **Status:** ⚠️ API accessible but returns None error
- **Type:** Voice Cloning
- **Likes:** 1,120 (most popular)
- **URL:** https://huggingface.co/spaces/myshell-ai/OpenVoice
- **Issue:** Same None error as V2 - needs to be woken up

### ⚠️ 3. myshell-ai/OpenVoiceV2
- **Status:** ⚠️ API accessible but returns None error
- **Type:** Voice Cloning
- **Likes:** 343
- **URL:** https://huggingface.co/spaces/myshell-ai/OpenVoiceV2
- **Issue:** Same None error - needs to be woken up

### ⚠️ 4. Kikirilkov/Voice_Cloning
- **Status:** ⚠️ API accessible but uses spectrograms
- **Type:** Voice Cloning (different format)
- **Likes:** 66
- **URL:** https://huggingface.co/spaces/Kikirilkov/Voice_Cloning
- **Issue:** Requires spectrogram input format (not standard audio)

## Top Spaces by Popularity

1. **myshell-ai/OpenVoice** - 1,120 likes ⭐
2. **BilalSardar/Voice-Cloning** - 545 likes (PAUSED)
3. **myshell-ai/OpenVoiceV2** - 343 likes
4. **kevinwang676/Bark-with-Voice-Cloning** - 333 likes (RUNTIME_ERROR)
5. **amphion/singing_voice_conversion** - 261 likes (RUNTIME_ERROR)

## Common Issues Found

1. **Spaces Sleeping:** Many spaces need to be woken up via UI first
2. **Runtime Errors:** Several popular spaces are broken
3. **Paused Spaces:** Some spaces are paused by owners
4. **None Error:** OpenVoice spaces return None - likely sleeping or rate-limited

## Recommendations

### For Voice Cloning:

1. **Try OpenVoice V1 first:**
   - Visit: https://huggingface.co/spaces/myshell-ai/OpenVoice
   - Wake it up via UI
   - Then try API

2. **If V1 doesn't work, try V2:**
   - Visit: https://huggingface.co/spaces/myshell-ai/OpenVoiceV2
   - Wake it up via UI
   - Then try API

3. **Alternative: Use local installation**
   - Install OpenVoice locally
   - More reliable than API
   - No rate limits

### For Simple TTS:

- **VoiceCloning-be/text-to-speech** works but uses pre-made voices
- Good for testing the pub/sub system
- Not true voice cloning

## Next Steps

1. **Wake up OpenVoice V1:**
   ```bash
   # Visit in browser first:
   https://huggingface.co/spaces/myshell-ai/OpenVoice
   
   # Then test:
   $env:HF_TOKEN="your_token"
   python test_all_working_spaces.py
   ```

2. **Create processor for VoiceCloning-be:**
   - It works but isn't true voice cloning
   - Good for testing pub/sub workflow

3. **Consider local installation:**
   - More reliable
   - No API issues
   - Can integrate with pub/sub system

## Files Created

- `voice_cloning_spaces.json` - Full list of 66 spaces
- `find_voice_cloning_spaces.py` - Discovery script
- `test_all_working_spaces.py` - Testing script

## Conclusion

Most voice cloning spaces on Hugging Face are either:
- Sleeping (need UI wake-up)
- Broken (runtime errors)
- Paused by owners

The OpenVoice spaces (V1 and V2) are the best options but need to be woken up first. The pub/sub system is ready - we just need a working voice cloning API.

