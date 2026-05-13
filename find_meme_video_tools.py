#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Find Meme Video Generators and Aggregators on GitHub

Agentically searches GitHub for tools that can create and aggregate
meme videos at scale, with comprehensive console logging.
"""

import sys
import io
import json
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


def search_github_meme_tools():
    """Search for meme video tools on GitHub."""
    log_section("SEARCHING GITHUB FOR MEME VIDEO TOOLS")
    
    search_queries = [
        "meme video generator",
        "meme video creator",
        "meme generator python",
        "meme aggregator",
        "automated meme video",
        "meme video automation",
        "meme template video",
        "bulk meme generator",
        "meme video maker",
        "meme compilation generator"
    ]
    
    github_searches = []
    
    log(f"Generating {len(search_queries)} GitHub search URLs...")
    print("")
    
    for i, query in enumerate(search_queries, 1):
        # Create GitHub search URL (sorted by stars)
        search_url = f"https://github.com/search?q={query.replace(' ', '+')}&type=repositories&s=stars"
        
        github_searches.append({
            "query": query,
            "url": search_url,
            "category": "meme_generation" if "generator" in query or "creator" in query else "meme_aggregation"
        })
        
        log(f"{i}. {query}")
        log(f"   URL: {search_url}")
    
    return github_searches


def get_known_meme_tools():
    """Get known meme video generation tools."""
    log_section("KNOWN MEME VIDEO TOOLS")
    
    known_tools = [
        {
            "name": "Meme Generator",
            "description": "Python library for creating memes",
            "github_url": "https://github.com/search?q=meme+generator+python&type=repositories&s=stars",
            "category": "generation",
            "features": ["Text overlay", "Image processing", "Template support"]
        },
        {
            "name": "Pillow (PIL)",
            "description": "Python imaging library for meme creation",
            "github_url": "https://github.com/python-pillow/Pillow",
            "category": "image_processing",
            "features": ["Image manipulation", "Text rendering", "Format support"]
        },
        {
            "name": "MoviePy",
            "description": "Video editing for meme videos",
            "github_url": "https://github.com/Zulko/moviepy",
            "category": "video_editing",
            "features": ["Video composition", "Text overlays", "Effects"]
        },
        {
            "name": "FFmpeg",
            "description": "Video processing for meme compilation",
            "github_url": "https://github.com/FFmpeg/FFmpeg",
            "category": "video_processing",
            "features": ["Video merging", "Format conversion", "Effects"]
        },
        {
            "name": "Meme Aggregator Tools",
            "description": "Tools to collect and compile memes",
            "github_url": "https://github.com/search?q=meme+aggregator&type=repositories&s=stars",
            "category": "aggregation",
            "features": ["Content collection", "Batch processing", "Compilation"]
        }
    ]
    
    log(f"Found {len(known_tools)} known tool categories")
    
    for tool in known_tools:
        log(f"\n- {tool['name']}")
        log(f"  Description: {tool['description']}")
        log(f"  GitHub: {tool['github_url']}")
        log(f"  Features: {', '.join(tool['features'])}")
    
    return known_tools


def create_meme_tools_report(github_searches: List[Dict], known_tools: List[Dict]):
    """Create comprehensive meme tools report."""
    log_section("CREATING MEME TOOLS REPORT")
    
    # Categorize searches
    generators = [s for s in github_searches if "generator" in s["query"] or "creator" in s["query"] or "maker" in s["query"]]
    aggregators = [s for s in github_searches if "aggregator" in s["query"] or "compilation" in s["query"]]
    automation = [s for s in github_searches if "automation" in s["query"] or "bulk" in s["query"]]
    
    report = {
        "search_date": datetime.now().isoformat(),
        "generator_searches": generators,
        "aggregator_searches": aggregators,
        "automation_searches": automation,
        "all_searches": github_searches,
        "known_tools": known_tools,
        "recommended_stack": {
            "image_processing": "Pillow (PIL) for image manipulation",
            "video_editing": "MoviePy for video composition",
            "video_processing": "FFmpeg for advanced processing",
            "automation": "Python scripts with YouTube API",
            "aggregation": "Custom scripts or existing aggregators"
        },
        "workflow_suggestions": [
            "1. Collect meme templates/images",
            "2. Generate memes with text overlays (Pillow)",
            "3. Compile into videos (MoviePy)",
            "4. Add effects/transitions (FFmpeg)",
            "5. Upload to platforms (YouTube API)"
        ]
    }
    
    # Save JSON report
    json_file = "meme_video_tools_report.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, default=str)
    
    log(f"JSON report saved: {json_file}")
    
    # Create Markdown report
    md_content = f"""# Meme Video Generators & Aggregators Report

## Search Date
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## GitHub Search URLs

### Meme Generators
Search these on GitHub (sorted by stars):

"""
    
    for i, search in enumerate(generators, 1):
        md_content += f"{i}. **{search['query']}**\n"
        md_content += f"   - {search['url']}\n\n"
    
    md_content += """### Meme Aggregators
Search these for content collection and compilation:

"""
    
    for i, search in enumerate(aggregators, 1):
        md_content += f"{i}. **{search['query']}**\n"
        md_content += f"   - {search['url']}\n\n"
    
    md_content += """### Automation Tools
Search these for bulk/automated meme creation:

"""
    
    for i, search in enumerate(automation, 1):
        md_content += f"{i}. **{search['query']}**\n"
        md_content += f"   - {search['url']}\n\n"
    
    md_content += """## Known Tools & Libraries

### Image Processing
- **Pillow (PIL)**: https://github.com/python-pillow/Pillow
  - Image manipulation and text overlay
  - Essential for meme generation

### Video Editing
- **MoviePy**: https://github.com/Zulko/moviepy
  - Python video editing library
  - Great for meme video compilation

### Video Processing
- **FFmpeg**: https://github.com/FFmpeg/FFmpeg
  - Industry-standard video processing
  - For advanced effects and merging

### Aggregation Tools
- Search: https://github.com/search?q=meme+aggregator&type=repositories&s=stars
- Look for tools that collect memes from multiple sources

## Recommended Stack for Meme Video Creation

### Python Stack
1. **Pillow** - Image processing and text overlay
2. **MoviePy** - Video composition and editing
3. **FFmpeg** - Advanced video processing
4. **YouTube API** - Upload automation

### Workflow
1. **Template Collection**: Gather meme templates/images
2. **Text Overlay**: Use Pillow to add text to images
3. **Video Compilation**: Combine images into videos with MoviePy
4. **Effects**: Add transitions/effects with FFmpeg
5. **Upload**: Automate uploads with YouTube API

## Meme Aggregator Workflow

1. **Content Collection**: Scrape/collect memes from sources
2. **Filtering**: Remove duplicates, filter by quality
3. **Compilation**: Create compilation videos
4. **Metadata**: Auto-generate titles, descriptions
5. **Distribution**: Upload to multiple platforms

## Popular Meme Video Types

- **Reaction Videos**: Compilations of reactions
- **Template Memes**: Same template, different text
- **Trending Memes**: Current popular memes
- **Compilation Videos**: Multiple memes in one video
- **Animated Memes**: GIFs converted to videos

## Next Steps

1. **Visit GitHub Search URLs**: Check the URLs above for active repositories
2. **Look for**:
   - High star count (500+)
   - Recent commits (active development)
   - Good documentation
   - Python support
3. **Test Tools**: Start with small batches
4. **Combine Tools**: Use multiple tools for complete pipeline
5. **Automate**: Create scripts for bulk generation

## Additional Resources

### Reddit APIs
- r/memes, r/dankmemes for content sources
- PRAW (Python Reddit API Wrapper)

### Image Sources
- Imgur API
- Giphy API (for GIFs)
- Unsplash/Pexels (for backgrounds)

### Video Platforms
- YouTube API (uploads)
- TikTok API (if available)
- Instagram API (for reels)

## Example Python Stack

```python
# Meme Generation Stack
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import *
import subprocess

# 1. Create meme image
img = Image.open("template.jpg")
draw = ImageDraw.Draw(img)
font = ImageFont.truetype("impact.ttf", 40)
draw.text((10, 10), "TOP TEXT", fill="white", font=font)
draw.text((10, img.height-50), "BOTTOM TEXT", fill="white", font=font)
img.save("meme.jpg")

# 2. Create video from image
clip = ImageClip("meme.jpg").set_duration(3)
clip.write_videofile("meme.mp4", fps=24)

# 3. Compile multiple memes
clips = [ImageClip(f"meme{i}.jpg").set_duration(3) for i in range(10)]
final = concatenate_videoclips(clips)
final.write_videofile("compilation.mp4")
```
"""
    
    md_file = "meme_video_tools_report.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    log(f"Markdown report saved: {md_file}")
    
    # Print summary
    print("")
    log("Summary:")
    log(f"  - Generator searches: {len(generators)}")
    log(f"  - Aggregator searches: {len(aggregators)}")
    log(f"  - Automation searches: {len(automation)}")
    log(f"  - Total searches: {len(github_searches)}")


def main():
    """Main function."""
    log_section("MEME VIDEO TOOLS FINDER")
    log(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Search GitHub
    github_searches = search_github_meme_tools()
    
    # Get known tools
    print("")
    known_tools = get_known_meme_tools()
    
    # Create report
    print("")
    create_meme_tools_report(github_searches, known_tools)
    
    log_section("COMPLETE")
    log("Meme tools search complete!", "INFO")
    log("")
    log("Check these files:")
    log("  - meme_video_tools_report.json (detailed data)")
    log("  - meme_video_tools_report.md (readable report)")
    log("")
    log("Visit the GitHub search URLs to find specific repositories!")


if __name__ == "__main__":
    main()


