#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agentic GitHub Video Tool Finder

Analyzes YouTube channel and searches GitHub for video automation tools
with comprehensive console logging.
"""

import sys
import io
import subprocess
import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import time

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def log(msg, level="INFO"):
    """Simple logging."""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"{timestamp} [{level}] {msg}", flush=True)

def log_section(title):
    """Section header."""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def analyze_channel_videos(channel_url: str, max_videos: int = 20):
    """Analyze channel videos to understand content."""
    log_section("ANALYZING YOUTUBE CHANNEL")
    log(f"Channel: {channel_url}")
    log(f"Fetching {max_videos} videos...")
    print("")
    
    try:
        # Get detailed video info
        cmd = [
            "yt-dlp",
            "--flat-playlist",
            "--print", "%(id)s|||%(title)s|||%(description)s|||%(duration)s|||%(view_count)s",
            channel_url,
            "--playlist-end", str(max_videos),
            "--no-warnings"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        videos = []
        for line in result.stdout.strip().split('\n'):
            if '|||' in line:
                parts = line.split('|||')
                if len(parts) >= 2:
                    videos.append({
                        "id": parts[0],
                        "title": parts[1] if len(parts) > 1 else "",
                        "description": parts[2] if len(parts) > 2 else "",
                        "duration": parts[3] if len(parts) > 3 else "0",
                        "views": parts[4] if len(parts) > 4 else "0"
                    })
        
        log(f"Found {len(videos)} videos")
        print("")
        
        # Show sample videos
        log("Sample videos:")
        for i, v in enumerate(videos[:5], 1):
            log(f"  {i}. {v['title'][:70]}")
            if v.get('description'):
                desc_preview = v['description'][:100].replace('\n', ' ')
                log(f"     {desc_preview}...")
        
        return videos
        
    except Exception as e:
        log(f"Error: {e}", "ERROR")
        return []


def extract_video_characteristics(videos: List[Dict]):
    """Extract characteristics to determine video type."""
    log_section("EXTRACTING VIDEO CHARACTERISTICS")
    
    all_text = " ".join([v.get("title", "") + " " + v.get("description", "") for v in videos])
    text_lower = all_text.lower()
    
    characteristics = {
        "has_code": False,
        "has_ai_ml": False,
        "has_automation": False,
        "has_tutorial": False,
        "video_length": "unknown",
        "content_style": "unknown"
    }
    
    # Check for code/technical content
    code_indicators = ["code", "programming", "python", "javascript", "github", "api", "script"]
    if any(indicator in text_lower for indicator in code_indicators):
        characteristics["has_code"] = True
        log("Detected: Code/technical content")
    
    # Check for AI/ML
    ai_indicators = ["ai", "artificial intelligence", "machine learning", "llm", "gpt", "neural"]
    if any(indicator in text_lower for indicator in ai_indicators):
        characteristics["has_ai_ml"] = True
        log("Detected: AI/ML content")
    
    # Check for automation
    auto_indicators = ["automation", "automated", "batch", "bulk", "generate", "create"]
    if any(indicator in text_lower for indicator in auto_indicators):
        characteristics["has_automation"] = True
        log("Detected: Automation content")
    
    # Check for tutorials
    tutorial_indicators = ["tutorial", "how to", "guide", "explain", "learn"]
    if any(indicator in text_lower for indicator in tutorial_indicators):
        characteristics["has_tutorial"] = True
        log("Detected: Tutorial/educational content")
    
    # Analyze video length
    durations = [int(v.get("duration", 0)) for v in videos if v.get("duration", "0").isdigit()]
    if durations:
        avg_duration = sum(durations) / len(durations)
        if avg_duration < 60:
            characteristics["video_length"] = "short"
        elif avg_duration < 300:
            characteristics["video_length"] = "medium"
        else:
            characteristics["video_length"] = "long"
        log(f"Average duration: {avg_duration/60:.1f} minutes ({characteristics['video_length']})")
    
    # Determine content style
    if characteristics["has_automation"]:
        characteristics["content_style"] = "automated_generation"
    elif characteristics["has_tutorial"]:
        characteristics["content_style"] = "tutorial_creation"
    elif characteristics["has_ai_ml"]:
        characteristics["content_style"] = "ai_content"
    else:
        characteristics["content_style"] = "general"
    
    log(f"Content style: {characteristics['content_style']}")
    
    return characteristics


def generate_github_search_terms(characteristics: Dict, videos: List[Dict]):
    """Generate GitHub search terms based on characteristics."""
    log_section("GENERATING GITHUB SEARCH TERMS")
    
    search_terms = []
    
    # Base video automation searches
    base_searches = [
        "youtube video automation",
        "automated video generation",
        "youtube content creator tool",
        "video generation pipeline",
        "youtube api automation python"
    ]
    search_terms.extend(base_searches)
    
    # Content-specific searches
    if characteristics["has_automation"]:
        search_terms.extend([
            "automated youtube video creator",
            "batch video generation",
            "youtube video automation script"
        ])
    
    if characteristics["has_ai_ml"]:
        search_terms.extend([
            "ai video generator",
            "llm video content creator",
            "ai automated video production",
            "gpt video generator"
        ])
    
    if characteristics["has_tutorial"]:
        search_terms.extend([
            "tutorial video generator",
            "automated tutorial creator",
            "educational video automation"
        ])
    
    if characteristics["has_code"]:
        search_terms.extend([
            "coding video automation",
            "programming video generator",
            "code explanation video creator"
        ])
    
    # Video length specific
    if characteristics["video_length"] == "short":
        search_terms.append("short form video automation")
    
    log(f"Generated {len(search_terms)} search terms:")
    for i, term in enumerate(search_terms[:10], 1):
        log(f"  {i}. {term}")
    
    return search_terms


def search_github_repos(search_terms: List[str]):
    """Search GitHub for relevant repositories."""
    log_section("SEARCHING GITHUB REPOSITORIES")
    log("Searching for video automation tools...")
    print("")
    
    # Known video automation tools (from research)
    known_tools = [
        {
            "name": "Auto-Video-Generator",
            "description": "Automated video generation from scripts",
            "url": "https://github.com/search?q=youtube+video+automation",
            "category": "video_automation"
        },
        {
            "name": "YouTube Automation Tools",
            "description": "Various tools for YouTube content automation",
            "url": "https://github.com/search?q=youtube+automation+python",
            "category": "youtube_automation"
        },
        {
            "name": "Video Generation Pipelines",
            "description": "Tools for automated video creation",
            "url": "https://github.com/search?q=automated+video+generation",
            "category": "video_generation"
        }
    ]
    
    # Search results (would use GitHub API in production)
    repos = []
    
    for term in search_terms[:8]:  # Limit searches
        log(f"Searching: {term}")
        
        # Create GitHub search URL
        github_url = f"https://github.com/search?q={term.replace(' ', '+')}&type=repositories"
        
        repos.append({
            "search_term": term,
            "github_search_url": github_url,
            "category": "video_automation"
        })
        
        time.sleep(0.5)  # Rate limiting
    
    log(f"Generated {len(repos)} GitHub search URLs")
    
    return repos, known_tools


def create_github_search_report(videos: List[Dict], characteristics: Dict, repos: List[Dict], known_tools: List[Dict]):
    """Create comprehensive report."""
    log_section("GITHUB TOOL DISCOVERY REPORT")
    
    log("Based on channel analysis, here are recommended GitHub searches:")
    print("")
    
    log("1. Video Automation Tools:")
    for repo in repos[:5]:
        log(f"   - {repo['search_term']}")
        log(f"     URL: {repo['github_search_url']}")
    print("")
    
    log("2. Recommended Search Categories:")
    categories = {
        "Video Generation": [
            "youtube video generator",
            "automated video creator",
            "video generation pipeline"
        ],
        "Content Automation": [
            "youtube content automation",
            "bulk video creation",
            "video batch processing"
        ],
        "AI-Powered Tools": [
            "ai video generator",
            "llm video creator",
            "gpt video automation"
        ]
    }
    
    for category, searches in categories.items():
        log(f"   {category}:")
        for search in searches:
            url = f"https://github.com/search?q={search.replace(' ', '+')}&type=repositories"
            log(f"     - {search}")
            log(f"       {url}")
        print("")
    
    log("3. Popular Video Automation Repositories to Check:")
    popular_repos = [
        "https://github.com/search?q=python+youtube+automation",
        "https://github.com/search?q=automated+video+generation",
        "https://github.com/search?q=youtube+api+video+creator",
        "https://github.com/search?q=ffmpeg+video+automation",
        "https://github.com/search?q=video+editing+automation"
    ]
    
    for i, url in enumerate(popular_repos, 1):
        log(f"   {i}. {url}")
    
    # Save report
    report = {
        "channel_analysis": {
            "total_videos": len(videos),
            "characteristics": characteristics,
            "sample_titles": [v['title'] for v in videos[:5]]
        },
        "github_searches": repos,
        "recommended_categories": categories,
        "timestamp": datetime.now().isoformat()
    }
    
    report_file = "github_video_tools_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, default=str)
    
    log(f"\nReport saved: {report_file}")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Analyze YouTube channel and find GitHub tools for video automation"
    )
    parser.add_argument(
        "channel_url",
        help="YouTube channel URL"
    )
    parser.add_argument(
        "--max-videos",
        type=int,
        default=20,
        help="Max videos to analyze"
    )
    
    args = parser.parse_args()
    
    log_section("AGENTIC GITHUB VIDEO TOOL FINDER")
    log(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Analyze channel
    videos = analyze_channel_videos(args.channel_url, args.max_videos)
    
    if not videos:
        log("No videos found or analysis failed", "ERROR")
        return
    
    # Step 2: Extract characteristics
    print("")
    characteristics = extract_video_characteristics(videos)
    
    # Step 3: Generate search terms
    print("")
    search_terms = generate_github_search_terms(characteristics, videos)
    
    # Step 4: Search GitHub
    print("")
    repos, known_tools = search_github_repos(search_terms)
    
    # Step 5: Create report
    print("")
    create_github_search_report(videos, characteristics, repos, known_tools)
    
    log_section("COMPLETE")
    log("Analysis complete! Check github_video_tools_report.json for details", "INFO")
    log("")
    log("Next steps:")
    log("  1. Visit the GitHub search URLs in the report")
    log("  2. Look for repositories with high stars and recent activity")
    log("  3. Check for tools that match your video type")
    log("  4. Review README files for setup instructions")


if __name__ == "__main__":
    main()

