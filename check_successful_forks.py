#!/usr/bin/env python3
"""
Check GitHub for successful OpenVoice forks with recent updates
"""

import subprocess
import json
from pathlib import Path

def check_github_forks():
    """Use GitHub API to find recent forks"""
    print("=" * 70)
    print(" Checking GitHub for Recent OpenVoice Forks")
    print("=" * 70)
    
    print("\n[1] Searching for recent forks...")
    print("    Repository: myshell-ai/OpenVoice")
    
    # Use GitHub API to get forks
    # Note: This requires GitHub CLI or we can use requests
    try:
        import requests
        
        # Get forks - valid sort options: newest, oldest, stargazers
        url = "https://api.github.com/repos/myshell-ai/OpenVoice/forks"
        params = {
            "sort": "newest",  # Sort by newest forks
            "per_page": 30,
            "page": 1
        }
        
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "OpenVoice-Fork-Checker"
        }
        
        print("    [INFO] Fetching forks from GitHub API...")
        response = requests.get(url, params=params, headers=headers, timeout=15)
        
        if response.status_code == 200:
            forks = response.json()
            print(f"    [OK] Found {len(forks)} forks")
            
            # Filter for recent updates (last month)
            from datetime import datetime, timedelta
            one_month_ago = datetime.now() - timedelta(days=30)
            
            recent_forks = []
            for fork in forks:
                updated_at = datetime.fromisoformat(fork['updated_at'].replace('Z', '+00:00'))
                if updated_at.replace(tzinfo=None) > one_month_ago.replace(tzinfo=None):
                    recent_forks.append({
                        'owner': fork['owner']['login'],
                        'url': fork['html_url'],
                        'updated': fork['updated_at'],
                        'default_branch': fork['default_branch']
                    })
            
            print(f"\n[2] Recent Forks (last 30 days): {len(recent_forks)}")
            print("-" * 70)
            
            if recent_forks:
                for i, fork in enumerate(recent_forks[:10], 1):
                    print(f"\n{i}. {fork['owner']}/OpenVoice")
                    print(f"   URL: {fork['url']}")
                    print(f"   Updated: {fork['updated']}")
                    print(f"   Branch: {fork['default_branch']}")
                    
                    # Check if they have app.py or requirements.txt changes
                    print(f"   [INFO] Check manually: {fork['url']}/tree/{fork['default_branch']}")
            else:
                print("    No forks updated in the last 30 days")
            
            print("\n" + "=" * 70)
            print(" Manual Check Recommendations:")
            print("=" * 70)
            print("\n1. Check Hugging Face Spaces for OpenVoice duplicates:")
            print("   https://huggingface.co/spaces?search=OpenVoice")
            print("\n2. Check GitHub Issues for deployment fixes:")
            print("   https://github.com/myshell-ai/OpenVoice/issues")
            print("\n3. Check recent commits in main repo:")
            print("   https://github.com/myshell-ai/OpenVoice/commits/main")
            
            return recent_forks
        else:
            print(f"    [ERROR] GitHub API returned {response.status_code}")
            if response.status_code == 403:
                print("    [INFO] Rate limited - GitHub API requires authentication for more requests")
                print("    [INFO] Try visiting: https://github.com/myshell-ai/OpenVoice/network/members")
            elif response.status_code == 404:
                print("    [INFO] Repository not found or private")
            else:
                try:
                    error_data = response.json()
                    print(f"    [INFO] Error details: {error_data.get('message', 'Unknown error')}")
                except:
                    print(f"    [INFO] Response: {response.text[:200]}")
            return []
            
    except ImportError:
        print("    [WARNING] requests not installed, using manual approach")
        print("\n    Please check manually:")
        print("    1. https://github.com/myshell-ai/OpenVoice/network/members")
        print("    2. https://huggingface.co/spaces?search=OpenVoice")
        return []
    except Exception as e:
        print(f"    [ERROR] {e}")
        return []

def check_huggingface_spaces():
    """Check Hugging Face for OpenVoice Spaces"""
    print("\n[3] Checking Hugging Face Spaces...")
    print("    [INFO] Search for OpenVoice duplicates:")
    print("    https://huggingface.co/spaces?search=OpenVoice")
    print("\n    [INFO] Look for Spaces with:")
    print("    - Recent activity")
    print("    - 'Running' status")
    print("    - Connected to GitHub forks")

if __name__ == "__main__":
    forks = check_github_forks()
    check_huggingface_spaces()
    
    print("\n" + "=" * 70)
    print(" Next Steps:")
    print("=" * 70)
    print("\n1. Manually check the forks listed above")
    print("2. Look at their app.py and requirements.txt files")
    print("3. See what fixes they applied")
    print("4. Compare with our fixes")

