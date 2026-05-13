#!/usr/bin/env python3
"""
Analyze recent OpenVoice forks to find successful Hugging Face Space deployments
"""

import requests
from datetime import datetime, timedelta

def check_fork_for_space(fork_owner):
    """Check if a fork has a Hugging Face Space"""
    # Try to find Space by searching
    space_url = f"https://huggingface.co/spaces/{fork_owner}/OpenVoice"
    space_url_v2 = f"https://huggingface.co/spaces/{fork_owner}/OpenVoiceV2"
    
    # Check if Space exists
    try:
        r1 = requests.head(space_url, timeout=5, allow_redirects=True)
        if r1.status_code == 200:
            return space_url
    except:
        pass
    
    try:
        r2 = requests.head(space_url_v2, timeout=5, allow_redirects=True)
        if r2.status_code == 200:
            return space_url_v2
    except:
        pass
    
    return None

def check_fork_files(fork_owner):
    """Check if fork has app.py or requirements.txt with fixes"""
    try:
        # Check for app.py
        app_url = f"https://raw.githubusercontent.com/{fork_owner}/OpenVoice/main/app.py"
        req_url = f"https://raw.githubusercontent.com/{fork_owner}/OpenVoice/main/requirements.txt"
        
        app_response = requests.get(app_url, timeout=5)
        req_response = requests.get(req_url, timeout=5)
        
        results = {}
        
        if app_response.status_code == 200:
            app_content = app_response.text
            # Check for fixes
            if 'info=' in app_content and 'gr.Audio' in app_content:
                results['app_has_info_param'] = True
            else:
                results['app_has_info_param'] = False
            results['app_exists'] = True
        else:
            results['app_exists'] = False
        
        if req_response.status_code == 200:
            req_content = req_response.text
            results['requirements_exists'] = True
            results['has_torch'] = 'torch' in req_content.lower()
            results['has_faster_whisper'] = 'faster-whisper' in req_content.lower()
        else:
            results['requirements_exists'] = False
        
        return results
    except Exception as e:
        return {'error': str(e)}

def main():
    print("=" * 70)
    print(" Analyzing Recent OpenVoice Forks")
    print("=" * 70)
    
    # Get recent forks
    url = "https://api.github.com/repos/myshell-ai/OpenVoice/forks"
    params = {"sort": "newest", "per_page": 20}
    headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "OpenVoice-Analyzer"}
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"[ERROR] GitHub API returned {response.status_code}")
            return
        
        forks = response.json()
        one_month_ago = datetime.now() - timedelta(days=30)
        
        print(f"\n[1] Found {len(forks)} forks")
        print(f"[2] Checking for Hugging Face Spaces and fixes...\n")
        
        successful_forks = []
        
        for i, fork in enumerate(forks[:15], 1):  # Check top 15
            owner = fork['owner']['login']
            updated = fork['updated_at']
            
            updated_dt = datetime.fromisoformat(updated.replace('Z', '+00:00'))
            if updated_dt.replace(tzinfo=None) < one_month_ago.replace(tzinfo=None):
                continue
            
            print(f"\n{i}. {owner}/OpenVoice")
            print(f"   Updated: {updated}")
            
            # Check for Space
            space_url = check_fork_for_space(owner)
            if space_url:
                print(f"   ✅ HAS HUGGING FACE SPACE: {space_url}")
                successful_forks.append({'owner': owner, 'space': space_url})
            else:
                print(f"   ⚠️  No Space found")
            
            # Check files
            file_info = check_fork_files(owner)
            if 'error' not in file_info:
                if file_info.get('app_exists'):
                    if not file_info.get('app_has_info_param', True):
                        print(f"   ✅ app.py FIXED (no info= parameter)")
                    else:
                        print(f"   ⚠️  app.py still has info= parameter")
                
                if file_info.get('requirements_exists'):
                    print(f"   📦 requirements.txt: ", end="")
                    if file_info.get('has_torch'):
                        print("✅ has torch", end="")
                    if file_info.get('has_faster_whisper'):
                        print(" ✅ has faster-whisper", end="")
                    print()
        
        print("\n" + "=" * 70)
        print(" Summary")
        print("=" * 70)
        
        if successful_forks:
            print(f"\n✅ Found {len(successful_forks)} forks with Hugging Face Spaces:")
            for fork in successful_forks:
                print(f"   - {fork['owner']}: {fork['space']}")
        else:
            print("\n⚠️  No forks with Hugging Face Spaces found in recent forks")
        
        print("\n[3] Manual Check Links:")
        print("   - All forks: https://github.com/myshell-ai/OpenVoice/network/members")
        print("   - HF Spaces search: https://huggingface.co/spaces?search=OpenVoice")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

