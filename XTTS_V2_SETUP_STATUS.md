# XTTS-v2 Setup Status

## Current Status

✅ **TTS Library Installed**: Version 0.14.3
✅ **Bangla Compatibility Fixed**: Fixed Python 3.8 type hint issue
✅ **Some Dependencies Installed**: bnnumerizer, bnunicodenormalizer

❌ **Missing Dependencies**: Several optional dependencies for full functionality

## Issue

The `pip install -U TTS` command failed due to dependency resolution conflicts. However, TTS is installed but missing some optional dependencies.

## What Works

- TTS core library is installed
- Basic functionality should work for English voice cloning
- XTTS-v2 model can be loaded (will download on first use)

## What's Missing (Optional Dependencies)

These are needed for full multilingual support:
- `mecab-python3==1.0.5` - Japanese support
- `unidic-lite==1.0.8` - Japanese dictionary
- `umap-learn==0.5.1` - Some advanced features
- `k-diffusion` - Some model features

**Note**: These are optional. For English voice cloning with XTTS-v2, you may not need all of them.

## Manual Installation Steps

If you want full functionality, install missing dependencies:

```bash
# For Japanese support (optional)
pip install mecab-python3==1.0.5

# For other optional features
pip install umap-learn==0.5.1
pip install k-diffusion
```

## Test It

Try running the test script:
```bash
python test_xtts_v2.py
```

If it fails on import, install the missing dependency it reports.

## Recommendation

**For English voice cloning only**: You may not need all dependencies. Try the test script and install only what's needed.

**For full multilingual support**: Install all dependencies, but be aware of potential conflicts with your existing packages.

