# Installation Guide for Voice Cloning Models

This guide provides step-by-step instructions for installing and testing each open-source voice cloning model.

## Quick Start: Easy-to-Install Models

### 1. Coqui TTS (XTTS-v2) - ⭐ RECOMMENDED FOR EASY SETUP

**Installation:**
```bash
pip install TTS
```

**Test Installation:**
```python
from TTS.api import TTS
model = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
audio = model.tts(text="Hello, this is a test", speaker_wav="reference.wav")
```

**Pros:**
- ✅ Very easy installation (single pip command)
- ✅ Mature and well-maintained
- ✅ Good voice cloning quality
- ✅ Multilingual support
- ✅ Active community

**Cons:**
- ⚠️ First run downloads large model files (~2GB)
- ⚠️ Requires GPU for best performance (CPU works but slower)

**GitHub**: https://github.com/coqui-ai/TTS

---

### 2. Chatterbox (Resemble AI)

**Installation:**
```bash
pip install chatterbox
```

**Test Installation:**
```python
import chatterbox
import torch
device = "cuda" if torch.cuda.is_available() else "cpu"
model = chatterbox.ChatterboxTTS.from_pretrained(device)
audio = model.generate("Hello, this is a test", audio_prompt_path="reference.wav")
```

**Pros:**
- ✅ Easy installation
- ✅ Production-grade quality
- ✅ Emotion control
- ✅ MIT license

**Cons:**
- ⚠️ Slower inference time
- ⚠️ Limited multilingual support

**GitHub**: https://github.com/resemble-ai/chatterbox

---

## Advanced Setup: Models Requiring Manual Installation

### 3. OpenVoice (MyShell)

**Installation Steps:**

1. Clone the repository:
```bash
git clone https://github.com/myshell-ai/OpenVoice.git
cd OpenVoice
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download model files (check repository for latest links):
```bash
# Download base speaker and converter models
# Links typically provided in repository README
```

**Pros:**
- ✅ Zero-shot cross-lingual voice cloning
- ✅ Instant voice cloning
- ✅ Rhythm and intonation control

**Cons:**
- ⚠️ Complex setup
- ⚠️ Requires manual model downloads
- ⚠️ Less documentation

**GitHub**: https://github.com/myshell-ai/OpenVoice

---

### 4. GPT-SoVITS

**Installation Steps:**

1. Clone the repository:
```bash
git clone https://github.com/RVC-Boss/GPT-SoVITS.git
cd GPT-SoVITS
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download pre-trained models (check repository)

**Pros:**
- ✅ High-similarity voice cloning
- ✅ Works with 5-10 seconds of reference
- ✅ Web interface available
- ✅ Cross-lingual support

**Cons:**
- ⚠️ Requires fine-tuning for best results
- ⚠️ More complex workflow

**GitHub**: https://github.com/RVC-Boss/GPT-SoVITS

---

### 5. Fish-Speech (FishAudio)

**Installation Steps:**

1. Clone the repository:
```bash
git clone https://github.com/fishaudio/fish-speech.git
cd fish-speech
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download model files (check repository)

**Pros:**
- ✅ State-of-the-art multilingual support
- ✅ Trained on 700k+ hours
- ✅ High quality

**Cons:**
- ⚠️ Very large model size
- ⚠️ Complex setup
- ⚠️ Resource intensive

**GitHub**: https://github.com/fishaudio/fish-speech

---

### 6. CosyVoice (FunAudioLLM)

**Installation Steps:**

1. Clone the repository:
```bash
git clone https://github.com/FunAudioLLM/CosyVoice.git
cd CosyVoice
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download model files

**Pros:**
- ✅ Full-stack multilingual TTS
- ✅ Low error rates
- ✅ Zero-shot voice cloning

**Cons:**
- ⚠️ Newer project, less community support
- ⚠️ Requires setup

**GitHub**: https://github.com/FunAudioLLM/CosyVoice

---

## Testing All Models

Run the comprehensive test script:

```bash
python test_all_voice_cloning.py
```

This will:
1. Check which models are installed
2. Test basic TTS functionality
3. Test voice cloning capabilities
4. Measure performance metrics
5. Generate a comprehensive report

Results will be saved to `results_voice_cloning/` directory.

---

## Recommendations by Use Case

### 🚀 **Quick Start / Easiest Setup**
**Coqui TTS (XTTS-v2)** - Single pip install, works immediately

### 🎯 **Production Use**
**Chatterbox** - Production-grade, good documentation, MIT license

### 🌍 **Multilingual Projects**
**Fish-Speech** or **CosyVoice** - Best multilingual support

### ⚡ **Fastest Setup with Good Quality**
**Coqui TTS** - Best balance of ease and quality

### 🔬 **Research / Advanced Features**
**OpenVoice** - Cross-lingual, advanced controls

---

## System Requirements

### Minimum:
- Python 3.8+
- 8GB RAM
- CPU (slower but works)

### Recommended:
- Python 3.10+
- 16GB+ RAM
- NVIDIA GPU with 6GB+ VRAM
- CUDA 11.8+

---

## Troubleshooting

### Common Issues:

1. **CUDA/GPU not detected**
   - Install appropriate CUDA toolkit
   - Check PyTorch CUDA installation: `python -c "import torch; print(torch.cuda.is_available())"`

2. **Model download fails**
   - Check internet connection
   - Some models require manual download from HuggingFace or other sources

3. **Out of memory errors**
   - Use CPU mode (slower)
   - Reduce batch size
   - Use smaller models if available

4. **Import errors**
   - Ensure virtual environment is activated
   - Reinstall dependencies: `pip install -r requirements.txt --upgrade`

