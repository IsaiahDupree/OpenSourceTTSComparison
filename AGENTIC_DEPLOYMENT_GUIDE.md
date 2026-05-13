# Agentic Deployment Guide - Fix and Deploy OpenVoice

## Three Options to Fix and Deploy

### Option 1: Direct Fix in Hugging Face (Fastest) ⚡

**Time:** 2 minutes

1. Go to: https://huggingface.co/spaces/theisaiahdupree/OpenVoiceV2
2. Click **"Files"** tab
3. Click **"app.py"**
4. Click **"Edit"** button (pencil icon)
5. **Search for:** `gr.Audio(`
6. **Remove** any lines with `info=`
7. Click **"Commit changes"**
8. Wait 1-2 minutes for redeploy

**Done!** Your Space will be fixed and running.

---

### Option 2: Fork → Fix → Deploy via GitHub (Best for Version Control) 🔄

**Time:** 5-10 minutes

#### Step 1: Fork the Repository

1. Go to: https://github.com/myshell-ai/OpenVoice
2. Click **"Fork"** button (top right)
3. Fork to your GitHub account

#### Step 2: Clone Your Fork

```bash
git clone https://github.com/yourusername/OpenVoice.git openvoice_fork
cd openvoice_fork
```

#### Step 3: Fix app.py

Find `app.py` (might be in a subdirectory):
```bash
# Search for it
find . -name "app.py" -type f
```

Edit the file and remove `info=` parameters from `gr.Audio()` calls.

Or use the automated script:
```bash
python deploy_openvoice_fixed.py
```

#### Step 4: Commit and Push

```bash
git add app.py
git commit -m "Fix Gradio compatibility - remove info parameter"
git push origin main
```

#### Step 5: Connect Space to GitHub

1. Go to: https://huggingface.co/spaces/theisaiahdupree/OpenVoiceV2
2. Click **"Settings"** tab
3. Scroll to **"Repository"** section
4. Click **"Connect to GitHub"**
5. Select your fork: `yourusername/OpenVoice`
6. Set branch: `main`
7. Space will auto-deploy from GitHub!

**Benefits:**
- ✅ Version control
- ✅ Easy to update
- ✅ Auto-deploys on push
- ✅ Can collaborate

---

### Option 3: Automated Script (Fully Agentic) 🤖

**Time:** 3-5 minutes

```bash
# Install dependencies
pip install huggingface_hub

# Run the script
python deploy_openvoice_fixed.py
```

The script will:
1. ✅ Clone the repository
2. ✅ Find app.py
3. ✅ Fix Gradio compatibility issues automatically
4. ✅ Commit changes
5. ✅ Deploy to your Hugging Face Space

**Requirements:**
- Git installed
- HF_TOKEN set: `$env:HF_TOKEN="your_token"`
- huggingface_hub: `pip install huggingface_hub`

---

## What Gets Fixed

### Fix 1: Remove `info` Parameter

**Before:**
```python
ref_gr = gr.Audio(
    label="Reference Audio",
    info="Upload a reference audio file",  # <-- REMOVE
    ...
)
```

**After:**
```python
ref_gr = gr.Audio(
    label="Reference Audio",
    # info parameter removed
    ...
)
```

### Fix 2: Remove `max_choices` Warning

**Before:**
```python
gr.Dropdown(
    ...,
    max_choices=1,
    multiselect=False
)
```

**After:**
```python
gr.Dropdown(
    ...,
    multiselect=False
)
```

---

## After Deployment

Once your Space is fixed and running:

1. **Test it:**
   - Visit: https://huggingface.co/spaces/theisaiahdupree/OpenVoiceV2
   - Try generating audio in the UI

2. **Use with pub/sub:**
   ```python
   # Update Space ID in code
   SPACE_ID = "theisaiahdupree/OpenVoiceV2"
   
   # Then run
   python process_voice_hq.py
   ```

3. **Your Space is ready!**
   - No more runtime errors
   - Works with pub/sub system
   - Generate voice clones!

---

## Troubleshooting

### If Space Still Has Errors:

1. Check the logs in Space Settings
2. Verify all `info=` parameters are removed
3. Check Gradio version in `requirements.txt`
4. Try pinning Gradio version: `gradio==4.0.0`

### If Deployment Fails:

1. Check HF_TOKEN is valid
2. Verify you have write access to the Space
3. Check Git is installed and configured
4. Try manual deployment via Files tab

---

## Quick Start

**Fastest way:**
1. Go to Space → Files → app.py → Edit
2. Remove `info=` parameters
3. Commit
4. Done!

**Best for production:**
1. Fork repo on GitHub
2. Fix locally
3. Push to fork
4. Connect Space to GitHub
5. Auto-deploys on every push!

