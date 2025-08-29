#!/usr/bin/env python3
"""
Test Coqui TTS in isolated environment
"""

import subprocess
import sys
import os

def test_coqui_in_env():
    """Test Coqui TTS in its isolated environment"""
    
    env_python = os.path.join("envs", "venv_coqui_tts", "Scripts", "python.exe")
    
    if not os.path.exists(env_python):
        print("❌ Coqui TTS environment not found")
        return False
    
    # Test script to run inside the environment
    test_script = '''
import sys
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")

try:
    import TTS
    print("✓ TTS imported successfully")
    
    from TTS.api import TTS
    print("✓ TTS.api imported successfully")
    
    # List available models
    print("Available TTS models:")
    tts = TTS()
    models = tts.list_models()
    print(f"Found {len(models)} models")
    
    # Try to use a simple model for testing
    print("Testing with tts_models/en/ljspeech/tacotron2-DDC...")
    tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")
    
    # Test synthesis
    text = "Hello, this is a test of Coqui TTS."
    print(f"Testing synthesis: '{text}'")
    
    # Generate audio to file
    output_file = "test_coqui_output.wav"
    tts.tts_to_file(text=text, file_path=output_file)
    
    if os.path.exists(output_file):
        print(f"✓ Audio generated successfully: {output_file}")
        file_size = os.path.getsize(output_file)
        print(f"File size: {file_size} bytes")
        # Clean up
        os.remove(output_file)
    else:
        print("❌ Audio file was not created")
        sys.exit(1)
    
    print("🎉 Coqui TTS test completed successfully!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error during synthesis: {e}")
    sys.exit(1)
'''
    
    try:
        # Write test script to temporary file
        with open("temp_coqui_test.py", "w") as f:
            f.write(test_script)
        
        # Run the test script in the isolated environment
        result = subprocess.run([env_python, "temp_coqui_test.py"], 
                              capture_output=True, text=True, timeout=300)
        
        print("Coqui TTS Test Output:")
        print("=" * 40)
        print(result.stdout)
        
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        
        # Clean up
        if os.path.exists("temp_coqui_test.py"):
            os.remove("temp_coqui_test.py")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Test timed out")
        return False
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False

def install_coqui_tts():
    """Install Coqui TTS in the isolated environment"""
    env_pip = os.path.join("envs", "venv_coqui_tts", "Scripts", "pip.exe")
    
    if not os.path.exists(env_pip):
        print("❌ Coqui TTS environment not found")
        return False
    
    try:
        print("Installing Coqui TTS...")
        result = subprocess.run([env_pip, "install", "TTS"], 
                              capture_output=True, text=True, timeout=600)
        
        print("Installation Output:")
        print("=" * 30)
        print(result.stdout)
        
        if result.stderr:
            print("Installation Errors:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Installation timed out")
        return False
    except Exception as e:
        print(f"❌ Installation error: {e}")
        return False

def main():
    """Main test function"""
    print("🎤 Testing Coqui TTS in Isolated Environment")
    print("=" * 50)
    
    success = test_coqui_in_env()
    
    if not success:
        print("\n❌ Coqui TTS test failed")
        print("Trying to install Coqui TTS in the isolated environment...")
        
        if install_coqui_tts():
            print("✓ Installation completed, retesting...")
            success = test_coqui_in_env()
        else:
            print("❌ Installation failed")
    
    if success:
        print("\n✅ Coqui TTS is working correctly!")
    else:
        print("\n❌ Coqui TTS setup failed")
    
    return success

if __name__ == "__main__":
    main()
