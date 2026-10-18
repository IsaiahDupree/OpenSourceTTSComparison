# OpenVoice Local Setup - Complete Guide

## ✅ Setup Status

Your local setup is ready! The checkpoints are already downloaded, and most dependencies are installed.

## ⚠️ Note About faster-whisper

The `faster-whisper` package failed to install due to FFmpeg build requirements on Windows. **This is OK** - we've made it optional in the code. The app will use the VAD (Voice Activity Detection) method instead, which doesn't require `faster-whisper`.

## 🚀 Running OpenVoice Locally

### Option 1: Use the Run Script (Recommended)

```bash
python run_openvoice_local.py
```

### Option 2: Run Directly

```bash
cd openvoice_deploy
python app.py
```

## 📍 Access the App

Once running, open your browser to:
- **http://localhost:7860**

## 🔧 Installing Missing Dependencies (Optional)

If you want to install the remaining dependencies (without faster-whisper):

```bash
pip install -r openvoice_deploy/requirements_local.txt
```

Or install individually:
```bash
pip install torch torchaudio
```

## 🎯 Testing

1. Open http://localhost:7860
2. Enter text: "Hello, this is a test"
3. Select style: "default"
4. Use a reference audio file (or the demo files in `resources/`)
5. Check "Agree"
6. Click "Send"

## 📁 Directory Structure

```
OpenSourceTTSComparison/
├── openvoice_deploy/
│   ├── app.py                    # Main application
│   ├── openvoice/                # OpenVoice module
│   ├── checkpoints/              # Model checkpoints (already downloaded)
│   ├── resources/                # Demo audio files
│   └── requirements.txt          # Full requirements
├── run_openvoice_local.py        # Run script
└── LOCAL_SETUP_COMPLETE.md       # This file
```

## 🆚 Local vs Hugging Face Space

| Feature | Local | Hugging Face Space |
|---------|-------|-------------------|
| Speed | Fast (no cold starts) | Slower (cold starts) |
| Control | Full code access | Limited |
| Setup | Manual | Automatic |
| Cost | Free | Free (with limits) |
| Access | Local network | Public internet |

## 🐛 Troubleshooting

### Port Already in Use
Change the port in `app.py`:
```python
demo.launch(server_port=7861)  # Different port
```

### CUDA/GPU Issues
The app will automatically use CPU if GPU is not available. To force CPU:
```python
device = 'cpu'  # In app.py
```

### Missing Checkpoints
Verify checkpoints exist:
```bash
ls openvoice_deploy/checkpoints/base_speakers/EN/
```

Should see: `checkpoint.pth`, `config.json`, `en_default_se.pth`, `en_style_se.pth`

## 🎉 Next Steps

- Test with your own voice samples
- Integrate with your pub/sub system
- Modify the code for your needs
- Use the API programmatically

## 📝 API Usage (Local)

```python
from gradio_client import Client

client = Client("http://localhost:7860")
result = client.predict(
    prompt="Your text here",
    style="default",
    audio_file_pth="path/to/audio.mp3",
    agree=True,
    api_name="/predict"
)
print(result)
```

Enjoy your local OpenVoice setup! 🎤

