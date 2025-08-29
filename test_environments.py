#!/usr/bin/env python3
"""
Test script to verify TTS model installations in their isolated environments
"""

import subprocess
import sys
import os
import json

def test_environment(env_name, test_import):
    """Test if a model can be imported in its environment"""
    env_path = os.path.join("envs", f"venv_{env_name}", "Scripts", "python.exe")
    
    if not os.path.exists(env_path):
        return False, f"Environment not found: {env_path}"
    
    try:
        # Test basic Python execution
        result = subprocess.run([env_path, "-c", "print('Environment active')"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            return False, f"Environment not working: {result.stderr}"
        
        # Test model import
        result = subprocess.run([env_path, "-c", test_import], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return True, "Success"
        else:
            return False, f"Import failed: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        return False, "Timeout during test"
    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    """Test all TTS model environments"""
    
    tests = {
        "chatterbox": "import chatterbox; print('Chatterbox imported successfully')",
        "coqui_tts": "import TTS; print('Coqui TTS imported successfully')"
    }
    
    results = {}
    
    print("Testing TTS model environments...")
    print("=" * 50)
    
    for model, test_code in tests.items():
        print(f"\nTesting {model}...")
        success, message = test_environment(model, test_code)
        results[model] = success
        
        if success:
            print(f"✓ {model}: {message}")
        else:
            print(f"✗ {model}: {message}")
    
    # Save results
    with open("envs/test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    for model, success in results.items():
        status = "PASS" if success else "FAIL"
        print(f"  {model}: {status}")
    
    print(f"\nResults saved to: envs/test_results.json")

if __name__ == "__main__":
    main()
