# OpenVoice Local Setup Guide

This guide will help you set up and run OpenVoice locally on your machine.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- ~2 GB free disk space (for checkpoints)
- CUDA-capable GPU (recommended, but CPU will work)

## Quick Setup

Run the automated setup script:

```bash
python setup_local_openvoice.py
```

This will:
1. Check Python version
2. Install all dependencies
3. Download model checkpoints (~400 MB)
4. Create a run script

## Manual Setup

If you prefer to set up manually:

### 1. Install Dependencies

```bash
cd openvoice_deploy
pip install -r requirements.txt
```

### 2. Download Checkpoints

Download the checkpoints from:
https://myshell-public-repo-host.s3.amazonaws.com/openvoice/checkpoints_1226.zip

Extract to: `openvoice_deploy/checkpoints/`

The structure should be:
```
openvoice_deploy/
  checkpoints/
    base_speakers/
      EN/
        checkpoint.pth
        config.json
        en_default_se.pth
        en_style_se.pth
      ZH/
        checkpoint.pth
        config.json
        zh_default_se.pth
    converter/
      checkpoint.pth
      config.json
```

### 3. Run OpenVoice

```bash
cd openvoice_deploy
python app.py
```

Or use the run script:
```bash
python run_openvoice_local.py
```

## Accessing the App

Once running, open your browser to:
- **Local**: http://localhost:7860
- **Network**: http://YOUR_IP:7860

## Troubleshooting

### CUDA/GPU Issues

If you don't have a GPU, the app will automatically use CPU (slower but works).

To force CPU mode, edit `app.py` and change:
```python
device = 'cpu'  # Force CPU
```

### Missing Checkpoints

If you see errors about missing checkpoints:
1. Verify checkpoints are in `openvoice_deploy/checkpoints/`
2. Check file paths in `app.py` match your directory structure

### Port Already in Use

If port 7860 is already in use, edit `app.py` and change:
```python
demo.launch(server_port=7861)  # Use different port
```

### Import Errors

Make sure you're running from the `openvoice_deploy` directory or have it in your Python path.

## Differences from Hugging Face Space

- **Local**: Full control, faster (no cold starts), can modify code
- **Space**: Easy deployment, accessible from anywhere, but slower cold starts

## Next Steps

- Test with your own voice samples
- Modify the code for your needs
- Integrate with your pub/sub system
- Use the API programmatically

## API Usage (Local)

Once running, you can use the Gradio client:

```python
from gradio_client import Client

client = Client("http://localhost:7860")
result = client.predict(
    prompt="Your text here",
    style="default",
    audio_file_pth="path/to/your/audio.mp3",
    agree=True,
    api_name="/predict"
)
```

