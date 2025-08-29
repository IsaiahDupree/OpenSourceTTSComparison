#!/usr/bin/env python3
"""
Test Chatterbox TTS in isolated environment
"""

import subprocess
import sys
import os

def test_chatterbox_in_env():
    """Test Chatterbox in its isolated environment"""
    
    env_python = os.path.join("envs", "venv_chatterbox", "Scripts", "python.exe")
    
    if not os.path.exists(env_python):
        print("❌ Chatterbox environment not found")
        return False
    
    # Test script to run inside the environment
    test_script = '''
import sys
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")

try:
    import chatterbox
    print("✓ Chatterbox imported successfully")
    
    # Try to create TTS instance
    tts = chatterbox.ChatterboxTTS()
    print("✓ ChatterboxTTS instance created")
    
    # Test synthesis with a simple phrase
    text = "Hello, this is a test of Chatterbox TTS."
    print(f"Testing synthesis: '{text}'")
    
    # Generate audio (this might take a moment)
    audio = tts.synthesize(text)
    print(f"✓ Audio generated successfully, shape: {audio.shape if hasattr(audio, 'shape') else type(audio)}")
    
    print("🎉 Chatterbox TTS test completed successfully!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error during synthesis: {e}")
    sys.exit(1)
'''
    
    try:
        # Write test script to temporary file
        with open("temp_chatterbox_test.py", "w") as f:
            f.write(test_script)
        
        # Run the test script in the isolated environment
        result = subprocess.run([env_python, "temp_chatterbox_test.py"], 
                              capture_output=True, text=True, timeout=120)
        
        print("Chatterbox Test Output:")
        print("=" * 40)
        print(result.stdout)
        
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        
        # Clean up
        if os.path.exists("temp_chatterbox_test.py"):
            os.remove("temp_chatterbox_test.py")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Test timed out")
        return False
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False

def main():
    """Main test function"""
    print("🎤 Testing Chatterbox TTS in Isolated Environment")
    print("=" * 50)
    
    success = test_chatterbox_in_env()
    
    if success:
        print("\n✅ Chatterbox TTS is working correctly!")
    else:
        print("\n❌ Chatterbox TTS test failed")
        print("\nTrying to install Chatterbox in the isolated environment...")
        
        # Try to install chatterbox-tts in the environment
        env_pip = os.path.join("envs", "venv_chatterbox", "Scripts", "pip.exe")
        
        if os.path.exists(env_pip):
            try:
                print("Installing chatterbox-tts...")
                result = subprocess.run([env_pip, "install", "chatterbox-tts"], 
                                      capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    print("✓ Installation completed, retesting...")
                    success = test_chatterbox_in_env()
                else:
                    print(f"Installation failed: {result.stderr}")
                    
            except Exception as e:
                print(f"Installation error: {e}")
    
    return success

if __name__ == "__main__":
    main()
