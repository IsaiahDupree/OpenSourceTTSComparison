# Build Issues & Solutions Guide

This guide helps you overcome common build issues when installing voice cloning software.

## Windows Build Issues

### Problem: Microsoft Visual C++ 14.0 or greater is required

**Symptoms:**
```
error: Microsoft Visual C++ 14.0 or greater is required
error: subprocess-exited-with-error
```

**Solution:**

1. **Download Visual C++ Build Tools:**
   - Go to: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Download "Build Tools for Visual Studio 2022"

2. **Install the C++ Build Tools:**
   - Run the installer
   - Select "Desktop development with C++" workload
   - Make sure "MSVC v143 - VS 2022 C++ x64/x86 build tools" is checked
   - Click Install

3. **Restart your terminal/IDE** after installation

4. **Try installation again:**
   ```bash
   pip install TTS
   ```

**Alternative:** Use pre-built wheels when available:
```bash
pip install --only-binary :all: TTS
```

---

### Problem: Failed building wheel

**Symptoms:**
```
ERROR: Failed building wheel for [package]
```

**Solutions:**

1. **Upgrade pip, setuptools, and wheel:**
   ```bash
   python -m pip install --upgrade pip setuptools wheel
   ```

2. **Install build dependencies:**
   ```bash
   pip install cmake
   ```

3. **Try installing from pre-built wheels:**
   ```bash
   pip install --prefer-binary TTS
   ```

---

## CUDA/GPU Issues

### Problem: CUDA not detected

**Symptoms:**
```
CUDA not available
RuntimeError: CUDA out of memory
```

**Solutions:**

1. **Check PyTorch CUDA installation:**
   ```python
   import torch
   print(torch.cuda.is_available())
   print(torch.version.cuda)
   ```

2. **Reinstall PyTorch with CUDA support:**
   ```bash
   # For CUDA 11.8
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   
   # For CUDA 12.1
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```

3. **Use CPU mode (slower but works):**
   - Most models support CPU inference
   - Just slower than GPU
   - No CUDA required

---

## Network/Download Issues

### Problem: Model download fails

**Symptoms:**
```
ConnectionError: Failed to download model
TimeoutError: The read operation timed out
```

**Solutions:**

1. **Check internet connection**

2. **Increase timeout:**
   ```python
   import os
   os.environ['HF_HUB_DOWNLOAD_TIMEOUT'] = '300'  # 5 minutes
   ```

3. **Manual download from HuggingFace:**
   - Visit: https://huggingface.co/models
   - Search for the model (e.g., "coqui/XTTS-v2")
   - Download manually
   - Place in cache directory

4. **Use VPN if in restricted network**

5. **Retry with exponential backoff:**
   ```bash
   # The installation script handles this automatically
   python install_and_test_models.py
   ```

---

## Python Version Issues

### Problem: Python version incompatible

**Symptoms:**
```
ERROR: Package requires Python >=3.8
ERROR: This package requires Python 3.10+
```

**Solutions:**

1. **Check Python version:**
   ```bash
   python --version
   ```

2. **Upgrade Python:**
   - Download from: https://www.python.org/downloads/
   - Install Python 3.10 or 3.11 (recommended)

3. **Use virtual environment:**
   ```bash
   python -m venv venv_voice_cloning
   venv_voice_cloning\Scripts\activate  # Windows
   # or
   source venv_voice_cloning/bin/activate  # Linux/Mac
   ```

---

## Dependency Conflicts

### Problem: Package conflicts

**Symptoms:**
```
ERROR: Cannot install package X because it conflicts with package Y
```

**Solutions:**

1. **Use separate virtual environments:**
   ```bash
   # One environment per model
   python -m venv venv_coqui
   python -m venv venv_chatterbox
   ```

2. **Install with --no-deps and manage manually:**
   ```bash
   pip install --no-deps TTS
   pip install torch torchaudio  # Install dependencies separately
   ```

3. **Use conda for better dependency management:**
   ```bash
   conda create -n voice_cloning python=3.10
   conda activate voice_cloning
   conda install pytorch torchaudio -c pytorch
   pip install TTS
   ```

---

## Memory Issues

### Problem: Out of memory during installation or inference

**Symptoms:**
```
MemoryError: Unable to allocate array
RuntimeError: CUDA out of memory
```

**Solutions:**

1. **Close other applications**

2. **Use CPU mode:**
   ```python
   model = TTS("model_name", gpu=False)
   ```

3. **Reduce batch size** (if applicable)

4. **Use smaller models** when available

5. **Increase virtual memory (Windows):**
   - System Properties → Advanced → Virtual Memory
   - Increase page file size

---

## Platform-Specific Issues

### Windows

**Common issues:**
- Visual C++ Build Tools required
- Long path names (enable in Windows settings)
- Antivirus blocking downloads

**Solutions:**
- Install Visual C++ Build Tools (see above)
- Enable long paths: `git config --global core.longpaths true`
- Add exception in antivirus for Python/pip

### Linux

**Common issues:**
- Missing system libraries
- Permission issues

**Solutions:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install build-essential python3-dev

# CentOS/RHEL
sudo yum install gcc gcc-c++ python3-devel
```

### macOS

**Common issues:**
- Xcode Command Line Tools missing
- Architecture mismatches (Intel vs Apple Silicon)

**Solutions:**
```bash
# Install Xcode Command Line Tools
xcode-select --install

# For Apple Silicon, may need Rosetta or native builds
arch -arm64 python -m pip install TTS
```

---

## Quick Fixes Checklist

Before giving up, try these in order:

1. ✅ Upgrade pip: `python -m pip install --upgrade pip`
2. ✅ Upgrade setuptools/wheel: `pip install --upgrade setuptools wheel`
3. ✅ Clear pip cache: `pip cache purge`
4. ✅ Use virtual environment
5. ✅ Install build tools (Visual C++ on Windows)
6. ✅ Check Python version (3.8+)
7. ✅ Check internet connection
8. ✅ Try pre-built wheels: `pip install --prefer-binary package`
9. ✅ Install dependencies separately
10. ✅ Check error messages for specific guidance

---

## Getting Help

If you're still stuck:

1. **Check the error message** - it often contains specific guidance
2. **Search GitHub issues** for the specific package
3. **Check package documentation** for installation requirements
4. **Run the diagnostic script:**
   ```bash
   python install_and_test_models.py
   ```
   This will identify specific issues and suggest solutions

---

## Alternative: Use Pre-built Docker Images

If build issues persist, consider using Docker:

```bash
# Example for Coqui TTS
docker pull coqui/tts:latest
docker run -it coqui/tts:latest
```

This avoids all build issues but requires Docker installation.

