# Quick Start: Docker Voice Cloning (No Build Issues!)

## ✅ Docker is Available on Your System!

You can use Docker to avoid ALL build issues. Here's how:

## Step 1: Pull the Coqui TTS Image

```bash
docker pull coqui/tts:latest
```

This downloads a pre-built image (~2-3GB). Takes 5-15 minutes depending on your internet.

## Step 2: Test It Works

```bash
docker run --rm coqui/tts:latest python -c "from TTS.api import TTS; print('Working!')"
```

## Step 3: Use Voice Cloning

### Quick Test (Windows):
```powershell
# Make sure you have a reference audio file (reference.wav)
docker run --rm -v "${PWD}:/workspace" -w /workspace coqui/tts:latest python -c "from TTS.api import TTS; model = TTS('tts_models/multilingual/multi-dataset/xtts_v2'); model.tts_to_file(text='Hello, this is a test', speaker_wav='reference.wav', file_path='output.wav')"
```

### Or Use the Helper Script:

Run the setup script:
```bash
python docker_voice_cloning.py
```

This will:
1. Pull the Docker image automatically
2. Test that it works
3. Create helper scripts for easy usage

## Advantages of Docker Approach

✅ **No build issues** - Everything is pre-built
✅ **No dependency conflicts** - Isolated environment
✅ **Works immediately** - No compilation needed
✅ **Easy to update** - Just pull new image
✅ **Same on all systems** - Windows, Mac, Linux

## Example: Complete Voice Cloning Workflow

1. **Prepare reference audio** (3-10 seconds of clear speech)
   - Save as `reference.wav` in your project folder

2. **Run voice cloning:**
   ```bash
   docker run --rm -v "${PWD}:/workspace" -w /workspace coqui/tts:latest python -c "
   from TTS.api import TTS
   model = TTS('tts_models/multilingual/multi-dataset/xtts_v2')
   model.tts_to_file(
       text='Your text to convert to speech here',
       speaker_wav='reference.wav',
       file_path='output.wav'
   )
   print('Done! Check output.wav')
   "
   ```

3. **Check output.wav** - Your cloned voice!

## Using docker-compose (Easier)

1. **Start container:**
   ```bash
   docker-compose up -d
   ```

2. **Run your script:**
   ```bash
   docker-compose exec coqui-tts python your_script.py
   ```

3. **Stop when done:**
   ```bash
   docker-compose down
   ```

## Troubleshooting

### "Docker daemon not running"
- Start Docker Desktop application
- Wait for it to fully start (whale icon in system tray)

### "Out of space"
- Clean up old images: `docker system prune -a`
- Check Docker Desktop settings for disk space

### "Permission denied"
- On Windows/Mac: Usually not an issue with Docker Desktop
- On Linux: May need `sudo` or add user to docker group

## Next Steps

1. **Pull the image:**
   ```bash
   docker pull coqui/tts:latest
   ```

2. **Or run the automated setup:**
   ```bash
   python docker_voice_cloning.py
   ```

3. **Start cloning voices!**

---

**This is the fastest way to get voice cloning working without any build issues!**

