#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quick script to get actual video durations from the analysis report."""

import json
import subprocess
import sys
from pathlib import Path

# Load report
with open('video_analysis_report.json', 'r', encoding='utf-8') as f:
    report = json.load(f)

print(f"Getting durations for top {len(report['top_videos'])} videos...")

for i, video in enumerate(report['top_videos'][:20], 1):
    video_id = video['video_id']
    title = video['title'][:50]
    
    try:
        cmd = [
            "yt-dlp",
            "--print", "%(duration)s",
            f"https://www.youtube.com/watch?v={video_id}",
            "--no-warnings",
            "--quiet"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and result.stdout.strip().isdigit():
            duration_sec = int(result.stdout.strip())
            duration_min = duration_sec / 60
            print(f"{i:2d}. {title:50s} - {duration_min:5.1f} min ({duration_sec}s)")
        else:
            print(f"{i:2d}. {title:50s} - Duration unknown")
    except:
        print(f"{i:2d}. {title:50s} - Error getting duration")

