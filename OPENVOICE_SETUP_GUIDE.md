# OpenVoice Hugging Face Setup Guide

## Current Issue: Invalid Token ❌

Your current token is returning a **401 Unauthorized** error. You need to create a new valid token.

## Step 1: Create a New Hugging Face Token

1. **Go to Hugging Face Settings:**
   - Visit: https://huggingface.co/settings/tokens
   - Log in to your account

2. **Create New Token:**
   - Click "New token" button
   - Give it a name (e.g., "OpenVoice-API")
   - Select permissions:
     - ✅ **Read** (required for API access)
     - Optionally: **Write** (if you need to upload models)
   - Click "Create token"

3. **Copy the Token:**
   - ⚠️ **Important**: Copy it immediately - it's only shown once!
   - Format: `${HF_TOKEN}`

4. **Set the Token:**
   ```powershell
   $env:HF_TOKEN="hf_your_new_token_here"
   ```

## Step 2: Verify Token Works

Run the check script:
```bash
python check_token_permissions.py
```

You should see:
- ✅ Token is valid
- ✅ Can access model information
- ✅ Can connect to Space API

## Step 3: OpenVoice Documentation

### Official Resources:

1. **OpenVoice V2 Model Page:**
   - https://huggingface.co/myshell-ai/OpenVoiceV2
   - Contains model info, usage examples, and features

2. **OpenVoice Space (Interactive UI):**
   - https://huggingface.co/spaces/myshell-ai/OpenVoiceV2
   - Test the model directly in the browser
   - Wake up the Space before API calls

3. **Gradio Client Documentation:**
   - https://www.gradio.app/guides/getting-started-with-the-python-client
   - For API usage with Hugging Face Spaces

### API Usage Pattern:

```python
from gradio_client import Client, handle_file

# Initialize client
client = Client("myshell-ai/OpenVoiceV2", hf_token="your_token")

# Prepare inputs
text = "Your text here"
style = "en_default"  # Options: en_default, en_us, en_br, en_au, en_in, etc.
reference_audio = handle_file("path/to/reference.wav")
agree = True  # Terms agreement

# Call API
result = client.predict(
    text,
    style,
    reference_audio,
    agree,
    fn_index=1
)

# Extract audio
audio_path = result[1]  # Second element is the generated audio
```

### Available Styles:

- `en_default` - Default English
- `en_us` - US English
- `en_br` - British English
- `en_au` - Australian English
- `en_in` - Indian English
- `es_default` - Spanish
- `fr_default` - French
- `jp_default` - Japanese
- `zh_default` - Chinese
- `kr_default` - Korean

## Step 4: Test with Your Voice

Once you have a valid token:

```bash
# Set token
$env:HF_TOKEN="your_new_token"

# Run high-quality processing
python process_voice_hq.py
```

## Troubleshooting

### Token Issues:
- **401 Error**: Token is invalid or expired → Create new token
- **403 Error**: Token lacks permissions → Add "Read" permission
- **429 Error**: Rate limit exceeded → Wait or upgrade to PRO

### API Issues:
- **ValueError: None**: Space might be sleeping → Visit Space UI to wake it
- **Connection timeout**: Space is down → Check https://status.huggingface.co/
- **File upload fails**: Check file format (must be WAV)

### Space Status:
- Check if Space is running: https://huggingface.co/spaces/myshell-ai/OpenVoiceV2
- If Space shows "This Space is sleeping", click to wake it up
- Some Spaces require accepting terms in UI before API works

## Next Steps

1. ✅ Create new token at https://huggingface.co/settings/tokens
2. ✅ Set it: `$env:HF_TOKEN="your_new_token"`
3. ✅ Verify: `python check_token_permissions.py`
4. ✅ Wake Space: Visit https://huggingface.co/spaces/myshell-ai/OpenVoiceV2
5. ✅ Test: `python process_voice_hq.py`

## Additional Resources

- **Hugging Face API Docs**: https://huggingface.co/docs/api-inference
- **Gradio Client Docs**: https://www.gradio.app/guides/getting-started-with-the-python-client
- **OpenVoice GitHub**: https://github.com/myshell-ai/OpenVoice (for local installation)

