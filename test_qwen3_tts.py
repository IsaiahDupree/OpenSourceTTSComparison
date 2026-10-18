#!/usr/bin/env python3
"""
Test Qwen3-TTS Voice Design API
This API allows voice design using natural language descriptions
"""

from gradio_client import Client
import os
import time

def test_qwen3_tts():
    """Test Qwen3-TTS Voice Design API"""
    print("=" * 70)
    print(" Testing Qwen3-TTS Voice Design API")
    print("=" * 70)
    
    space_id = "Qwen/Qwen3-TTS-Voice-Design"
    token = os.getenv("HF_TOKEN", (__import__('os').environ['HF_TOKEN']))
    
    print(f"\n[1] Connecting to: {space_id}")
    try:
        client = Client(space_id, hf_token=token)
        print("  [OK] Connected successfully!")
    except Exception as e:
        print(f"  [ERROR] Connection failed: {e}")
        return False
    
    # Test cases from the examples
    test_cases = [
        {
            "name": "News Broadcasting - Female Voice",
            "text": "Welcome to the speech synthesis system. Please enter the text you would like to have read aloud.",
            "instruct": "A clear and natural female voice, moderate speed, stable tone, suitable for news broadcasting or daily conversation."
        },
        {
            "name": "Dramatic - Sobbing Quality",
            "text": "He's not going to make it... it's all my fault. He only trusted me.",
            "instruct": "Standard pronunciation with a dramatic, sobbing quality. The voice should convey deep emotion and regret."
        },
        {
            "name": "Powerful Male - Authoritative",
            "text": "Our entire fleet and army are overdue for an equipment upgrade.",
            "instruct": "A loud, powerful male voice exhibiting resilience and authority."
        },
        {
            "name": "Professional Broadcasting",
            "text": "Becoming a scientist is the dream of countless children. We should encourage their curiosity.",
            "instruct": "Professional broadcasting style. The pace starts slow and accelerates naturally."
        },
        {
            "name": "Calm and Confident",
            "text": "I have a couple of rifles here, but we have never had the habit of using them.",
            "instruct": "A calm and confident tone. The speed is steady, with very clear pronunciation."
        },
        {
            "name": "Young Female - Brave and Determined",
            "text": "They say a family stays together through the wind and rain. We will overcome this together.",
            "instruct": "A young female voice, brave and determined, filled with idealism and hope."
        },
        {
            "name": "Cheerful and Extroverted",
            "text": "In this village, there is a very traditional and unique delicacy that has been passed down for generations.",
            "instruct": "Cheerful and extroverted personality. Fast but fluent pace, full of energy."
        },
        {
            "name": "Bright Young Girl",
            "text": "I have a big brother named Wang. He's got a huge appetite for adventure and exploration.",
            "instruct": "A bright, high-pitched young girl's voice. Lively and animated, full of excitement."
        }
    ]
    
    print(f"\n[2] Running {len(test_cases)} test cases...")
    print("  Note: Each generation may take 10-30 seconds")
    
    results = []
    for i, test in enumerate(test_cases, 1):
        print(f"\n  Test {i}/{len(test_cases)}: {test['name']}")
        print(f"    Text: {test['text'][:60]}...")
        print(f"    Instruction: {test['instruct'][:60]}...")
        
        try:
            start_time = time.time()
            
            result = client.predict(
                test['text'],
                test['instruct'],
                api_name="/tts_interface"
            )
            
            elapsed = time.time() - start_time
            
            # Result is a filepath
            audio_file = result
            print(f"    [SUCCESS] Generated in {elapsed:.1f}s")
            print(f"    Output: {audio_file}")
            results.append((test['name'], True, elapsed, audio_file))
            
            # Small delay between requests
            if i < len(test_cases):
                time.sleep(2)
                
        except Exception as e:
            print(f"    [ERROR] Failed: {e}")
            results.append((test['name'], False, None, None))
            import traceback
            traceback.print_exc()
    
    # Summary
    print("\n" + "=" * 70)
    print(" Test Summary")
    print("=" * 70)
    
    passed = sum(1 for _, success, _, _ in results if success)
    total = len(results)
    
    print(f"\n  Results: {passed}/{total} tests passed")
    print("\n  Details:")
    for name, success, elapsed, audio_file in results:
        status = "[PASS]" if success else "[FAIL]"
        time_str = f" ({elapsed:.1f}s)" if elapsed else ""
        print(f"    {status} {name}{time_str}")
        if audio_file:
            print(f"      Audio: {audio_file}")
    
    print("\n" + "=" * 70)
    if passed == total:
        print(" [SUCCESS] All tests passed!")
    else:
        print(f" [PARTIAL] {passed}/{total} tests passed")
    print("=" * 70)
    
    return passed == total

if __name__ == "__main__":
    success = test_qwen3_tts()
    exit(0 if success else 1)

