# OpenVoice Checkpoint Download and Upload Guide

## Overview

OpenVoice requires model checkpoints to function. These are large files (~GB) that need to be downloaded and uploaded to your Space.

## Checkpoint Structure

The checkpoints should be organized as:
```
checkpoints/
  base_speakers/
    EN/
      config.json
      checkpoint.pth
      en_default_se.pth
      en_style_se.pth
    ZH/
      config.json
      checkpoint.pth
      zh_default_se.pth
  converter/
    config.json
    checkpoint.pth
```

## Option 1: Download from GitHub (Recommended)

1. **Visit the OpenVoice Repository:**
   - Go to: https://github.com/myshell-ai/OpenVoice
   - Check the README for checkpoint download links

2. **Download Checkpoints:**
   - Look for "Checkpoint Download" section in README
   - Usually links to Hugging Face or Google Drive
   - Download the checkpoint files

3. **Extract to Local Directory:**
   ```bash
   # Extract to your local repository
   unzip checkpoints.zip -d openvoice_deploy/
   # Or manually create the structure
   ```

## Option 2: Download from Hugging Face Model Repository

1. **Visit Hugging Face Model:**
   - Go to: https://huggingface.co/myshell-ai/OpenVoice
   - Navigate to "Files" tab
   - Look for checkpoint files

2. **Download Files:**
   - Download individual files or use `huggingface-cli`
   ```bash
   huggingface-cli download myshell-ai/OpenVoice --local-dir openvoice_deploy/checkpoints
   ```

## Option 3: Use Automated Script

Run the provided script:
```bash
python download_and_upload_checkpoints.py
```

This will:
1. Check if you have local checkpoints
2. Guide you to download if missing
3. Upload them to your Space automatically

## Uploading to Your Space

### Method 1: Using the Script (Easiest)

```bash
python download_and_upload_checkpoints.py
```

### Method 2: Manual Upload via Web UI

1. Go to: https://huggingface.co/spaces/theisaiahdupree/OpenVoiceV2
2. Click **"Files"** tab
3. Click **"Add file"** → **"Upload files"**
4. Create `checkpoints/` directory structure
5. Upload each checkpoint file to the correct location

### Method 3: Using Hugging Face CLI

```bash
# Install if needed
pip install huggingface_hub

# Set token
export HF_TOKEN="your_token"

# Upload checkpoints
huggingface-cli upload theisaiahdupree/OpenVoiceV2 \
  checkpoints/base_speakers/EN/config.json \
  checkpoints/base_speakers/EN/checkpoint.pth \
  # ... etc for all files
```

## File Sizes

Checkpoints are large:
- `checkpoint.pth` files: ~100-500 MB each
- Total size: ~1-2 GB

Upload may take 10-30 minutes depending on your connection.

## After Upload

1. **Space will auto-detect** new files
2. **May need to rebuild** - check Space status
3. **Test the Space** - try generating speech

## Troubleshooting

### Checkpoints Not Found Error

If you see "Checkpoints not found" error:
1. Verify files are in `checkpoints/` directory in Space
2. Check file paths match exactly (case-sensitive)
3. Ensure all required files are uploaded

### Upload Fails

- Check your token has write permissions
- Verify file sizes aren't too large (may need Git LFS)
- Try uploading in smaller batches

## Quick Reference

- **Space**: https://huggingface.co/spaces/theisaiahdupree/OpenVoiceV2
- **OpenVoice Repo**: https://github.com/myshell-ai/OpenVoice
- **HF Model**: https://huggingface.co/myshell-ai/OpenVoice

