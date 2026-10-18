#!/usr/bin/env python3
"""
Quick Fix and Deploy Script
===========================
Simplified version that fixes app.py and provides deployment instructions.
"""

import os
import re
from pathlib import Path

def fix_app_py_content(content):
    """Fix Gradio compatibility issues"""
    fixes = []
    
    # Fix 1: Remove info parameter from gr.Audio (more comprehensive)
    # Match: info="..." or info='...' with optional comma
    patterns = [
        (r',\s*info\s*=\s*["\'][^"\']*["\']', ', '),  # info with comma before
        (r'info\s*=\s*["\'][^"\']*["\']\s*,?\s*', ''),  # info with optional comma after
    ]
    
    original = content
    for pattern, replacement in patterns:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            fixes.append("Removed 'info' parameter from Audio components")
    
    # Fix 2: Remove max_choices when multiselect=False (simpler approach)
    # Find lines with both max_choices and multiselect=False
    lines = content.split('\n')
    fixed_lines = []
    for i, line in enumerate(lines):
        if 'max_choices' in line and 'multiselect=False' in content[max(0, i-5):i+5]:
            # Remove max_choices parameter
            line = re.sub(r',?\s*max_choices\s*=\s*\d+\s*,?\s*', '', line)
            fixes.append(f"Removed 'max_choices' from Dropdown at line {i+1}")
        fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    return content, fixes

def create_fix_patch():
    """Create a patch file that can be applied"""
    print("=" * 70)
    print(" Creating Fix Patch")
    print("=" * 70)
    
    patch_content = """# Fix for app.py - Gradio Compatibility

## Changes needed:

1. Remove 'info' parameter from all gr.Audio() calls
2. Remove 'max_choices' from Dropdown when multiselect=False

## Manual Fix Instructions:

### In app.py, find and replace:

**Find:**
```python
gr.Audio(
    ...,
    info="...",
    ...
)
```

**Replace with:**
```python
gr.Audio(
    ...,
    # info parameter removed
    ...
)
```

### For Dropdown:

**Find:**
```python
gr.Dropdown(
    ...,
    max_choices=1,
    multiselect=False
)
```

**Replace with:**
```python
gr.Dropdown(
    ...,
    multiselect=False
)
```

## Automated Fix:

Run this Python code in your Space's app.py editor:

```python
import re

# Read file
with open('app.py', 'r') as f:
    content = f.read()

# Remove info parameters
content = re.sub(r',\s*info\s*=\s*["\'][^"\']*["\']', '', content)
content = re.sub(r'info\s*=\s*["\'][^"\']*["\']\s*,?\s*', '', content)

# Remove max_choices when multiselect=False
content = re.sub(r',?\s*max_choices\s*=\s*\d+\s*,?\s*', '', content)

# Write back
with open('app.py', 'w') as f:
    f.write(content)
```
"""
    
    with open('fix_patch.md', 'w') as f:
        f.write(patch_content)
    
    print("\n[OK] Created fix_patch.md with instructions")

def main():
    print("=" * 70)
    print(" Quick Fix and Deploy Guide")
    print("=" * 70)
    
    print("\n[Option 1] Fix Directly in Hugging Face Space (Easiest)")
    print("-" * 70)
    print("""
1. Go to: https://huggingface.co/spaces/theisaiahdupree/OpenVoiceV2
2. Click "Files" tab
3. Click "app.py"
4. Click "Edit" button
5. Search for "gr.Audio("
6. Remove any "info=" parameters
7. Click "Commit changes"
8. Space will auto-redeploy
""")
    
    print("\n[Option 2] Fork, Fix, and Deploy via GitHub")
    print("-" * 70)
    print("""
1. Fork the repo: https://github.com/myshell-ai/OpenVoice
2. Clone your fork locally
3. Fix app.py (remove info parameters)
4. Push to your fork
5. Connect Space to your GitHub repo:
   - Go to Space Settings
   - Connect to your GitHub fork
   - Space will auto-deploy from GitHub
""")
    
    print("\n[Option 3] Use Automated Script")
    print("-" * 70)
    print("""
Run: python deploy_openvoice_fixed.py

This will:
- Clone the repo
- Fix app.py automatically
- Help you deploy to Hugging Face
""")
    
    create_fix_patch()
    
    print("\n" + "=" * 70)
    print(" See fix_patch.md for detailed fix instructions")
    print("=" * 70)

if __name__ == "__main__":
    main()

