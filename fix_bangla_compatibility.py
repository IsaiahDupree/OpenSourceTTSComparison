#!/usr/bin/env python3
"""
Fix bangla package compatibility with Python 3.8
"""

import os
import sys

def fix_bangla():
    """Fix bangla package to work with Python 3.8"""
    bangla_path = None
    
    # Find bangla package
    for path in sys.path:
        bangla_init = os.path.join(path, 'bangla', '__init__.py')
        if os.path.exists(bangla_init):
            bangla_path = bangla_init
            break
    
    if not bangla_path:
        print("bangla package not found")
        return False
    
    print(f"Found bangla at: {bangla_path}")
    
    # Read the file
    with open(bangla_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the type hint syntax
    # Replace: bool | None with Optional[bool]
    if 'bool | None' in content:
        print("Fixing type hints...")
        content = content.replace('bool | None', 'Optional[bool]')
        
        # Add Optional import if not present
        if 'from typing import' in content:
            if 'Optional' not in content.split('from typing import')[1].split('\n')[0]:
                content = content.replace(
                    'from typing import',
                    'from typing import Optional,'
                )
        else:
            # Add typing import at the top
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    lines.insert(i, 'from typing import Optional')
                    break
            content = '\n'.join(lines)
        
        # Write back
        with open(bangla_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Fixed! Try importing TTS again.")
        return True
    else:
        print("No fixes needed (or already fixed)")
        return False

if __name__ == "__main__":
    fix_bangla()

