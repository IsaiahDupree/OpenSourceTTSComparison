# Fix Space Runtime Error - Quick Guide

## The Error

```
TypeError: Audio.__init__() got an unexpected keyword argument 'info'
```

This happens because newer Gradio versions removed the `info` parameter from `gr.Audio()`.

## Quick Fix (2 minutes)

### Step 1: Go to Your Space Files
1. Visit: **https://huggingface.co/spaces/theisaiahdupree/OpenVoiceV2**
2. Click the **"Files"** tab (top navigation)
3. Click on **`app.py`** to open it

### Step 2: Find and Fix Line 289

**Search for:** `gr.Audio(` or go to line 289

**Find this:**
```python
ref_gr = gr.Audio(
    label="Reference Audio",
    info="Upload a reference audio file",  # <-- DELETE THIS LINE
    ...
)
```

**Change to:**
```python
ref_gr = gr.Audio(
    label="Reference Audio",
    # info parameter removed - not supported in newer Gradio
    ...
)
```

### Step 3: Also Fix the Warning (Optional)

**Search for:** `max_choices` in dropdown components

**If you see:**
```python
gr.Dropdown(
    ...,
    max_choices=1,
    multiselect=False  # <-- If False, remove max_choices
)
```

**Change to:**
```python
gr.Dropdown(
    ...,
    # max_choices removed when multiselect=False
    multiselect=False
)
```

### Step 4: Save and Deploy

1. Click **"Commit changes"** button
2. Add commit message: "Fix Gradio compatibility - remove info parameter"
3. The Space will automatically redeploy
4. Wait 1-2 minutes for redeployment
5. Check if it's working!

## Alternative: Pin Older Gradio Version

If you prefer to use the old API, edit `requirements.txt`:

**Find:**
```
gradio
```

**Change to:**
```
gradio==3.50.0  # Or another version that supports 'info'
```

But **removing the parameter is better** - keeps you on latest Gradio.

## What to Look For

In `app.py`, search for:
- `gr.Audio(` - Find all Audio components
- `info=` - Find all info parameters
- Remove any `info=` parameters from Audio components

## After Fix

Once fixed and redeployed:
1. Your Space should start successfully
2. You can test it in the UI
3. Then use it with our pub/sub system!

The Space will be at: `https://huggingface.co/spaces/theisaiahdupree/OpenVoiceV2`
