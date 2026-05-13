#!/usr/bin/env python3
"""
Find and Test Voice Cloning Spaces
===================================
Search for voice cloning spaces on Hugging Face and test them.
"""

import requests
import json
from typing import List, Dict
import time

def search_hf_spaces(query: str, limit: int = 20) -> List[Dict]:
    """Search Hugging Face Spaces"""
    print(f"Searching for: {query}...")
    
    # Hugging Face Spaces search API
    url = "https://huggingface.co/api/spaces"
    params = {
        "search": query,
        "limit": limit,
        "sort": "likes",
        "direction": -1
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            spaces = response.json()
            return spaces
        else:
            print(f"  [ERROR] Search failed: {response.status_code}")
            return []
    except Exception as e:
        print(f"  [ERROR] Exception: {e}")
        return []

def find_voice_cloning_spaces() -> List[Dict]:
    """Find voice cloning related spaces"""
    print("=" * 70)
    print(" Finding Voice Cloning Spaces on Hugging Face")
    print("=" * 70)
    
    # Search terms
    search_terms = [
        "voice cloning",
        "OpenVoice",
        "voice synthesis",
        "TTS voice clone",
        "text to speech clone",
        "voice conversion"
    ]
    
    all_spaces = []
    seen_ids = set()
    
    for term in search_terms:
        print(f"\nSearching: '{term}'...")
        spaces = search_hf_spaces(term, limit=15)
        
        for space in spaces:
            space_id = space.get('id', '')
            if space_id and space_id not in seen_ids:
                seen_ids.add(space_id)
                all_spaces.append(space)
                print(f"  Found: {space_id}")
    
    # Sort by likes
    all_spaces.sort(key=lambda x: x.get('likes', 0), reverse=True)
    
    return all_spaces

def test_space(space_id: str, token: str = None) -> Dict:
    """Test if a space is accessible and working"""
    result = {
        'space_id': space_id,
        'accessible': False,
        'has_api': False,
        'error': None
    }
    
    try:
        from gradio_client import Client
        
        # Try to connect
        if token:
            client = Client(space_id, hf_token=token)
        else:
            client = Client(space_id)
        
        result['accessible'] = True
        
        # Try to get API info
        try:
            api_info = client.view_api()
            result['has_api'] = True
            result['api_info'] = str(api_info)[:200]  # Truncate
        except:
            result['has_api'] = False
        
    except Exception as e:
        result['error'] = str(e)[:200]
    
    return result

def main():
    print("=" * 70)
    print(" Voice Cloning Spaces Discovery and Testing")
    print("=" * 70)
    
    # Find spaces
    print("\n[1] Searching for voice cloning spaces...")
    spaces = find_voice_cloning_spaces()
    
    print(f"\n[2] Found {len(spaces)} unique spaces")
    
    # Display top spaces
    print("\n" + "=" * 70)
    print(" Top Voice Cloning Spaces")
    print("=" * 70)
    
    for i, space in enumerate(spaces[:20], 1):  # Top 20
        space_id = space.get('id', 'N/A')
        likes = space.get('likes', 0)
        title = space.get('title', space_id)
        sdk = space.get('sdk', 'unknown')
        
        print(f"\n{i}. {title}")
        print(f"   ID: {space_id}")
        print(f"   Likes: {likes}")
        print(f"   SDK: {sdk}")
        print(f"   URL: https://huggingface.co/spaces/{space_id}")
    
    # Test top spaces
    print("\n" + "=" * 70)
    print(" Testing Top Spaces")
    print("=" * 70)
    
    token = None  # Can add token if needed
    test_results = []
    
    # Test top 10
    for space in spaces[:10]:
        space_id = space.get('id', '')
        if not space_id:
            continue
        
        print(f"\nTesting: {space_id}...")
        result = test_space(space_id, token)
        result['title'] = space.get('title', space_id)
        result['likes'] = space.get('likes', 0)
        test_results.append(result)
        
        if result['accessible']:
            print(f"  [OK] Accessible")
            if result['has_api']:
                print(f"  [OK] Has API")
            else:
                print(f"  [INFO] No API info available")
        else:
            print(f"  [ERROR] {result.get('error', 'Unknown error')}")
        
        time.sleep(1)  # Rate limiting
    
    # Summary
    print("\n" + "=" * 70)
    print(" Test Results Summary")
    print("=" * 70)
    
    accessible = [r for r in test_results if r['accessible']]
    with_api = [r for r in accessible if r['has_api']]
    
    print(f"\nTotal spaces found: {len(spaces)}")
    print(f"Accessible: {len(accessible)}")
    print(f"With API: {len(with_api)}")
    
    if with_api:
        print("\n[RECOMMENDED] Spaces with working APIs:")
        for r in with_api:
            print(f"  - {r['title']} ({r['space_id']})")
            print(f"    URL: https://huggingface.co/spaces/{r['space_id']}")
    
    # Save results
    with open('voice_cloning_spaces.json', 'w') as f:
        json.dump({
            'spaces': spaces[:20],
            'test_results': test_results
        }, f, indent=2)
    
    print(f"\n[INFO] Results saved to: voice_cloning_spaces.json")
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()

