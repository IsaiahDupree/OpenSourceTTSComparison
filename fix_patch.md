# Fix for app.py - Gradio Compatibility

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
content = re.sub(r',\s*info\s*=\s*["'][^"']*["']', '', content)
content = re.sub(r'info\s*=\s*["'][^"']*["']\s*,?\s*', '', content)

# Remove max_choices when multiselect=False
content = re.sub(r',?\s*max_choices\s*=\s*\d+\s*,?\s*', '', content)

# Write back
with open('app.py', 'w') as f:
    f.write(content)
```
