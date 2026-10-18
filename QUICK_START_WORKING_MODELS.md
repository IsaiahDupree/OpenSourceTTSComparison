# Quick Start: Using Previously Working Models

## 🎯 Summary

Based on repository analysis, **Chatterbox** has been successfully tested and worked before in this repo. Here's how to get it working again.

## ✅ Chatterbox - Previously Working Model

### Evidence It Worked:
- ✅ Virtual environment: `venv_chatterbox/` and `venv_chatterbox311/`
- ✅ Test output: `chatterbox_test_output.wav` exists
- ✅ Benchmark results: `results_chatterbox/` with complete metrics
- ✅ Performance data: 3.98s inference, voice cloning working

### Get It Working Again:

#### Method 1: Activate Existing Virtual Environment
```bash
# Windows PowerShell:
.\venv_chatterbox\Scripts\Activate.ps1

# Windows CMD:
venv_chatterbox\Scripts\activate.bat

# Or use Python 3.11 version:
venv_chatterbox311\Scripts\activate
```

Then test:
```bash
python test_chatterbox.py
```

#### Method 2: Reinstall in Current Environment
```bash
pip install chatterbox
python test_chatterbox.py
```

#### Method 3: Use the Pipeline Script
```bash
python run_chatterbox_pipeline.py
```

### Expected Results:
- ✅ Basic TTS synthesis works
- ✅ Voice cloning works (3.82s average)
- ✅ Output file: `chatterbox_test_output.wav`

---

## ⚠️ Coqui TTS - Not Currently Working

**Status:** Test files exist but no evidence of successful runs

### To Test:
```bash
python test_coqui_tts.py
```

### To Install:
```bash
pip install TTS
python test_coqui_tts.py
```

Or use our automated installer:
```bash
python direct_install_test.py
```

---

## 🚀 Recommended Action Plan

### Step 1: Try Chatterbox First (Highest Success Probability)
```bash
# Activate the working environment
venv_chatterbox311\Scripts\activate

# Test it
python test_chatterbox.py
```

### Step 2: If Chatterbox Doesn't Work, Reinstall
```bash
pip install --upgrade chatterbox
python test_chatterbox.py
```

### Step 3: If You Need Different Model, Try Coqui
```bash
python direct_install_test.py
# This will install and test Coqui TTS automatically
```

---

## 📊 What We Know Works

Based on `results_chatterbox/summary_stats.json`:

**Chatterbox Performance:**
- ✅ Inference Time: 3.98 seconds
- ✅ Characters/sec: 26.0
- ✅ Memory Usage: 8.3 MB
- ✅ Real-time Factor: 0.74 (good - under 1.0)
- ✅ Voice Cloning: 3.82 seconds average

**This proves Chatterbox was working and can work again!**

---

## 💡 Why Use What Worked Before?

1. **Proven Track Record** - Chatterbox has actual test results
2. **Virtual Environment Ready** - Already set up
3. **Test Scripts Available** - Ready to run
4. **Performance Known** - You know what to expect
5. **Voice Cloning Confirmed** - It worked before

---

## 🔧 Troubleshooting

### "Module not found" error:
```bash
# Reinstall in the venv
venv_chatterbox311\Scripts\activate
pip install --upgrade chatterbox
```

### "Virtual environment not activating":
```bash
# Use direct Python from venv
venv_chatterbox311\Scripts\python.exe test_chatterbox.py
```

### Want to start fresh:
```bash
# Create new venv and install
python -m venv venv_chatterbox_new
venv_chatterbox_new\Scripts\activate
pip install chatterbox
python test_chatterbox.py
```

---

## ✅ Verification

Run this to check what's available:
```bash
python verify_working_models.py
```

This will show:
- Which virtual environments exist
- Which test files are available
- Which output files were created
- Current import status

---

**Bottom Line:** **Chatterbox is your best bet** - it has a proven working history in this repo with complete test results and performance metrics.

