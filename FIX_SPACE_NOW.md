# Fix Your Space Now - Two Options

## The Problem

Your Space is still using old code with the `info=` parameter in `gr.Audio()`, which causes the error:
```
TypeError: Audio.__init__() got an unexpected keyword argument 'info'
```

## ✅ Option 1: Connect Space to GitHub (Recommended - 2 minutes)

Your fixed code is already on GitHub! Just connect the Space:

1. **Go to your Space Settings:**
   - Visit: https://huggingface.co/spaces/theisaiahdupree/OpenVoiceV2/settings

2. **Connect to GitHub:**
   - Scroll to **"Repository"** section
   - Click **"Connect to GitHub"** button
   - Select: **IsaiahDupree/OpenVoice**
   - Set branch: **main**
   - Set root directory: **(leave empty)**
   - Click **"Save"**

3. **Wait for rebuild:**
   - The Space will automatically pull from GitHub
   - Wait 1-2 minutes for rebuild
   - Check status in the Space logs

**Done!** The Space will use your fixed code from GitHub.

---

## ✅ Option 2: Edit Directly in Space UI (Fastest - 1 minute)

If you can't connect to GitHub, edit directly:

1. **Go to your Space Files:**
   - Visit: https://huggingface.co/spaces/theisaiahdupree/OpenVoiceV2/tree/main

2. **Edit app.py:**
   - Click on **"app.py"**
   - Click **"Edit"** button (pencil icon)

3. **Find and Remove:**
   - Search for: `info="Click on the ✎ button to upload your own target speaker audio"`
   - Remove that entire line (including the comma if it's on its own line)

4. **Save:**
   - Click **"Commit changes"**
   - Wait 1-2 minutes for rebuild

**Done!** The Space will rebuild with the fix.

---

## What Was Fixed

The issue was this line in `gr.Audio()`:
```python
# BEFORE (causes error):
ref_gr = gr.Audio(
    label="Reference Audio",
    info="Click on the ✎ button to upload your own target speaker audio",  # ← REMOVE THIS
    type="filepath",
    value="resources/demo_speaker2.mp3",
)

# AFTER (fixed):
ref_gr = gr.Audio(
    label="Reference Audio",
    type="filepath",
    value="resources/demo_speaker2.mp3",
)
```

---

## Verify It Works

After the rebuild:
1. Check Space status shows "Running" (not "Building" or "Error")
2. Try uploading an audio file
3. Generate speech
4. No more `TypeError` errors!

---

## Why This Happened

Gradio removed the `info` parameter from `gr.Audio()` in newer versions. The Space is using a newer Gradio version that doesn't support this parameter.

Your fixed code on GitHub already has this removed:
- ✅ `openvoice/openvoice_app.py` - Fixed
- ✅ `app.py` - Fixed and ready for Space

Just connect the Space to GitHub and you're done!

