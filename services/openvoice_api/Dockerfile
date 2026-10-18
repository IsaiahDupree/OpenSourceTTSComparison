# GPU-enabled OpenVoice API container
# - Base image: PyTorch 2.3.1 with CUDA 12.1 + cuDNN 8 runtime
# - Requires: Docker Desktop + NVIDIA Container Toolkit on the host

FROM pytorch/pytorch:2.3.1-cuda12.1-cudnn8-runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    OPENVOICE_CKPT_DIR=/app/checkpoints_v2 \
    API_PORT=8811

# System deps: git for VCS installs, ffmpeg for audio, libsndfile for soundfile, espeak for TTS utils
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ffmpeg \
    libsndfile1 \
    espeak-ng \
    curl \
    wget \
    unzip \
    ca-certificates \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy service source
COPY main.py /app/main.py
COPY entrypoint.sh /app/entrypoint.sh

# Python deps (PyTorch already provided by base image)
RUN python -m pip install --upgrade pip setuptools wheel \
 && pip install fastapi uvicorn[standard] soundfile \
 && pip install git+https://github.com/myshell-ai/OpenVoice.git \
 && pip install git+https://github.com/myshell-ai/MeloTTS.git \
 && python -m unidic download \
 && chmod +x /app/entrypoint.sh

EXPOSE 8811

# Health check: basic endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 CMD \
  curl -fsS http://localhost:$API_PORT/health || exit 1

# Start API (exec form to propagate signals)
ENTRYPOINT ["/app/entrypoint.sh"]
