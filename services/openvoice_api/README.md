# OpenVoice API (GPU)

FastAPI wrapper around MyShell OpenVoice V2 + MeloTTS for zero-shot cloning.
Dockerized with PyTorch CUDA 12.1. Exposes a simple HTTP API for other apps.

## Prerequisites

- Windows 11/10 with Docker Desktop (WSL2 backend)
- NVIDIA GPU + driver
- NVIDIA Container Toolkit enabled in Docker Desktop (WSL2 GPU passthrough)

## Build

From repo root (recommended to limit context to this folder):

```powershell
# PowerShell
docker build -t openvoice-api -f services/openvoice_api/Dockerfile services/openvoice_api
```

## Checkpoints

Download OpenVoice V2 checkpoints and place them under `services/openvoice_api/checkpoints_v2/`:

```powershell
Invoke-WebRequest -Uri "https://myshell-public-repo-host.s3.amazonaws.com/openvoice/checkpoints_v2_0417.zip" -OutFile \
  ".\services\openvoice_api\checkpoints_v2_0417.zip"
Expand-Archive -Path ".\services\openvoice_api\checkpoints_v2_0417.zip" -DestinationPath ".\services\openvoice_api\"
```

Resulting paths needed:
- `services/openvoice_api/checkpoints_v2/converter/config.json`
- `services/openvoice_api/checkpoints_v2/converter/checkpoint.pth`
- `services/openvoice_api/checkpoints_v2/base_speakers/ses/*.pth`

Alternatively, mount any host folder at runtime to `/app/checkpoints_v2`.

## Run (GPU)

```powershell
# Replace the left side of -v with your absolute Windows path
$CKPT="C:\\Users\\Isaia\\Documents\\Coding\\OpenSourceTTSComparison\\services\\openvoice_api\\checkpoints_v2"

# Default port is 8811. Override by changing API_PORT and host mapping.
docker run --rm -it --gpus all -e API_PORT=8811 -p 8811:8811 \
  -v "$CKPT:/app/checkpoints_v2" \
  openvoice-api
```

## Endpoints

- GET `/health` – device and checkpoint status
- GET `/languages` – supported language keys
- GET `/voices` – available base speaker SE filenames under `checkpoints_v2/base_speakers/ses`
- GET `/speakers?language=EN_NEWEST` – MeloTTS speaker keys for a given language model
- POST `/clone` – multipart form
  - fields: `text` (str), `language` (default `EN_NEWEST`), `speed` (float), `speaker` (optional)
  - file: `reference_audio` (wav/mp3/m4a)
  - returns: `audio/wav`

- POST `/convert` – convert an existing audio clip to the target voice
  - files: `reference_audio` (target voice ref), `audio_src` (source audio to convert)
  - returns: `audio/wav`

### cURL example

```bash
curl -X POST \
  -F "text=Hello from OpenVoice" \
  -F "language=EN_NEWEST" \
  -F "speed=1.0" \
  -F "reference_audio=@/absolute/path/to/reference.wav" \
  http://localhost:8811/clone --output output.wav
```

## Notes

- Container base image: `pytorch/pytorch:2.3.1-cuda12.1-cudnn8-runtime` (Python 3.10+). OpenVoice requirements (>=3.9) are compatible.
- First request may download additional model assets (MeloTTS, silero VAD cache, etc.).
- Configure checkpoints dir by env: `OPENVOICE_CKPT_DIR=/app/checkpoints_v2` (default). Server port is configurable via `API_PORT` (default 8811).
- If your reference audio is very short (<5s), VAD segmentation may produce no chunks. The API now falls back to no-VAD extraction automatically.
