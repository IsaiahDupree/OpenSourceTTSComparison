import os
import sys
from gradio_client import Client, handle_file
from pathlib import Path

def main():
    print("-" * 50)
    print(" OpenVoiceV2 Cloud Test (Hugging Face)")
    print("-" * 50)

    # 1. Setup Input Data
    # Use one of our high-quality segments
    ref_voice_path = Path("processed_segments/w4sarAE9h9I_Turn YouTube Transcripts into Effective Content with Make.com_segment_0.wav")
    
    if not ref_voice_path.exists():
        print(f"Error: Reference file not found: {ref_voice_path}")
        print("Please run 'python expand_dataset.py --limit 5 --process' first.")
        sys.exit(1)

    prompt_text = "This is a test of OpenVoice V2 running on the Hugging Face cloud. We are comparing it to our local Docker solution."
    style = "default"  # Assuming 'default' style exists, usually safe for OpenVoice
    
    print(f"[1/3] Connecting to myshell-ai/OpenVoiceV2...")
    try:
        # Get token from environment variable, fallback to hardcoded for now
        TOKEN = os.getenv("HF_TOKEN", (__import__('os').environ['HF_TOKEN']))
        if not TOKEN:
            print("Error: HF_TOKEN environment variable not set")
            sys.exit(1)
        client = Client("myshell-ai/OpenVoiceV2", hf_token=TOKEN)
    except Exception as e:
        print(f"Failed to connect to HF Space: {e}")
        sys.exit(1)

    print(f"[2/3] Sending request...")
    print(f"      Reference: {ref_voice_path.name}")
    print(f"      Text: {prompt_text}")
    print(f"      Style: {style}")
    
    try:
        # Correct Signature from Inspection:
        # predict(text_prompt, style, reference_audio, agree, fn_index=1)
        # Style options: 'en_default', 'en_us', etc.
        
        # We must use 'en_default' or similar from the allowed list
        actual_style = "en_default"
        
        # Use absolute path for handle_file
        abs_ref_path = ref_voice_path.resolve()
        print(f"      Using absolute path: {abs_ref_path}")
        
        # Handle file upload - try both string path and handle_file
        print(f"[3/3] Calling API...")
        # First try with handle_file
        try:
            audio_file = handle_file(str(abs_ref_path))
            print(f"      File handle created: {type(audio_file)}")
            
            result_tuple = client.predict(
                prompt_text,              # text_prompt
                actual_style,             # style
                audio_file,               # reference_audio
                True,                     # agree
                fn_index=1                # Unnamed endpoint
            )
        except ValueError as ve:
            # If handle_file fails, try with direct path string
            if "None" in str(ve) or "error" in str(ve).lower():
                print(f"      handle_file approach failed, trying direct path...")
                print(f"      Error: {ve}")
                result_tuple = client.predict(
                    prompt_text,              # text_prompt
                    actual_style,             # style
                    str(abs_ref_path),        # reference_audio - try as string
                    True,                     # agree
                    fn_index=1                # Unnamed endpoint
                )
            else:
                raise
        
        print(f"      Result type: {type(result_tuple)}")
        print(f"      Result length: {len(result_tuple) if result_tuple else 'None'}")
        
        if not result_tuple:
            print("❌ API returned None")
            sys.exit(1)
        
        # Return is: (info, synthesised_audio, reference_audio_used)
        if len(result_tuple) < 2:
            print(f"❌ Unexpected result format: {result_tuple}")
            sys.exit(1)
            
        result_path = result_tuple[1]
        
        if not result_path:
            print("❌ No audio path in result")
            print(f"   Full result: {result_tuple}")
            sys.exit(1)
        
        print("✅ Generation Complete!")
        print(f"   Cloud Path: {result_path}")
        
        # Move/Rename locally
        output_dir = Path("voice_clone_output")
        output_dir.mkdir(exist_ok=True)
        local_path = output_dir / "openvoice_cloud_test.wav"
        
        import shutil
        if Path(result_path).exists():
            shutil.move(result_path, local_path)
            print(f"   Saved to: {local_path.resolve()}")
        else:
            # If it's a URL or different format, try copying
            import urllib.request
            if result_path.startswith("http"):
                urllib.request.urlretrieve(result_path, local_path)
                print(f"   Downloaded to: {local_path.resolve()}")
            else:
                print(f"   Warning: Result path doesn't exist: {result_path}")
                print(f"   Saving path info to: {local_path}")
                with open(local_path.with_suffix('.txt'), 'w') as f:
                    f.write(str(result_path))
        
    except Exception as e:
        print(f"❌ API Call Failed: {e}")
        import traceback
        traceback.print_exc()
        # Print API info again for debugging
        print("\nAvailable API Endpoints:")
        client.view_api()
        sys.exit(1)

if __name__ == "__main__":
    # Ensure gradio_client is installed
    try:
        import gradio_client
        main()
    except ImportError:
        print("Please run: pip install gradio_client")
