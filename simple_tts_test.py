#!/usr/bin/env python3
"""
Simple TTS test using available Python packages
"""

import sys
import os

def test_available_tts():
    """Test what TTS libraries are available in the current environment"""
    
    print("🎤 Testing Available TTS Libraries")
    print("=" * 40)
    
    # Test 1: Try importing TTS (Coqui)
    try:
        import TTS
        print("✓ Coqui TTS (TTS) is available")
        
        from TTS.api import TTS as CoquiTTS
        print("✓ TTS.api imported successfully")
        
        # Try a simple model
        try:
            tts = CoquiTTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)
            text = "Hello, this is a test."
            
            # Generate to file
            output_file = "test_output.wav"
            tts.tts_to_file(text=text, file_path=output_file)
            
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                print(f"✓ Coqui TTS synthesis successful! Output: {output_file} ({file_size} bytes)")
                os.remove(output_file)
                return True
            else:
                print("❌ Coqui TTS synthesis failed - no output file")
                
        except Exception as e:
            print(f"❌ Coqui TTS synthesis error: {e}")
            
    except ImportError:
        print("❌ Coqui TTS not available")
    
    # Test 2: Try importing pyttsx3 (fallback TTS)
    try:
        import pyttsx3
        print("✓ pyttsx3 is available")
        
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        
        # Test synthesis to file
        text = "Hello, this is a test of pyttsx3."
        output_file = "test_pyttsx3.wav"
        engine.save_to_file(text, output_file)
        engine.runAndWait()
        
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"✓ pyttsx3 synthesis successful! Output: {output_file} ({file_size} bytes)")
            os.remove(output_file)
            return True
        else:
            print("❌ pyttsx3 synthesis failed - no output file")
            
    except ImportError:
        print("❌ pyttsx3 not available")
    except Exception as e:
        print(f"❌ pyttsx3 error: {e}")
    
    # Test 3: Try importing gTTS (Google TTS)
    try:
        from gtts import gTTS
        print("✓ gTTS is available")
        
        text = "Hello, this is a test of Google TTS."
        tts = gTTS(text=text, lang='en')
        output_file = "test_gtts.mp3"
        tts.save(output_file)
        
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"✓ gTTS synthesis successful! Output: {output_file} ({file_size} bytes)")
            os.remove(output_file)
            return True
        else:
            print("❌ gTTS synthesis failed - no output file")
            
    except ImportError:
        print("❌ gTTS not available")
    except Exception as e:
        print(f"❌ gTTS error: {e}")
    
    return False

def install_fallback_tts():
    """Install a simple TTS library as fallback"""
    
    print("\n📦 Installing fallback TTS libraries...")
    
    import subprocess
    
    libraries = ["pyttsx3", "gtts"]
    
    for lib in libraries:
        try:
            print(f"Installing {lib}...")
            result = subprocess.run([sys.executable, "-m", "pip", "install", lib], 
                                  capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print(f"✓ {lib} installed successfully")
            else:
                print(f"❌ Failed to install {lib}: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Error installing {lib}: {e}")

def main():
    """Main function"""
    
    # First test what's available
    if test_available_tts():
        print("\n🎉 At least one TTS library is working!")
        return True
    
    # If nothing works, try installing fallback libraries
    print("\n❌ No working TTS libraries found")
    install_fallback_tts()
    
    # Test again after installation
    print("\n🔄 Retesting after installation...")
    if test_available_tts():
        print("\n🎉 TTS setup successful!")
        return True
    else:
        print("\n❌ TTS setup failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
