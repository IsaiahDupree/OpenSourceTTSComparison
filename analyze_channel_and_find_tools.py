#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agentic Channel Analysis + GitHub Tool Discovery

Analyzes a YouTube channel to understand video type, then searches GitHub
for tools that can reproduce similar videos at scale.
"""

import sys
import io
import subprocess
import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
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


class ChannelAnalyzer:
    """Analyze YouTube channel to understand video type."""
    
    def __init__(self, channel_url: str):
        self.channel_url = channel_url
        self.videos = []
        self.analysis = {}
    
    def fetch_channel_videos(self, max_videos: int = 20):
        """Fetch videos from channel."""
        log_section("FETCHING CHANNEL VIDEOS")
        log(f"Channel: {self.channel_url}")
        log(f"Max videos: {max_videos}")
        print("")
        
        try:
            cmd = [
                "yt-dlp",
                "--flat-playlist",
                "--print", "%(id)s|||%(title)s|||%(description)s|||%(duration)s|||%(view_count)s|||%(upload_date)s",
                self.channel_url,
                "--playlist-end", str(max_videos),
                "--no-warnings"
            ]
            
            log("Fetching video metadata...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                log(f"Error: {result.stderr[:200]}", "ERROR")
                return False
            
            videos = []
            for line in result.stdout.strip().split('\n'):
                if '|||' in line:
                    parts = line.split('|||')
                    if len(parts) >= 3:
                        videos.append({
                            "video_id": parts[0],
                            "title": parts[1] if len(parts) > 1 else "",
                            "description": parts[2] if len(parts) > 2 else "",
                            "duration": parts[3] if len(parts) > 3 else "0",
                            "view_count": parts[4] if len(parts) > 4 else "0",
                            "upload_date": parts[5] if len(parts) > 5 else "",
                            "url": f"https://www.youtube.com/watch?v={parts[0]}"
                        })
            
            self.videos = videos
            log(f"Found {len(videos)} videos")
            return True
            
        except Exception as e:
            log(f"Error fetching videos: {e}", "ERROR")
            return False
    
    def analyze_video_patterns(self):
        """Analyze video patterns to understand content type."""
        log_section("ANALYZING VIDEO PATTERNS")
        
        if not self.videos:
            log("No videos to analyze", "ERROR")
            return {}
        
        # Extract keywords from titles and descriptions
        all_text = " ".join([v.get("title", "") + " " + v.get("description", "") for v in self.videos])
        
        # Common video automation keywords
        automation_keywords = [
            "automation", "script", "generate", "create", "batch", "bulk",
            "api", "python", "tool", "software", "app", "program"
        ]
        
        # Video type indicators
        video_types = {
            "coding": ["code", "programming", "tutorial", "coding", "developer", "software"],
            "ai": ["ai", "artificial intelligence", "machine learning", "ml", "llm", "gpt"],
            "tech": ["technology", "tech", "software", "hardware", "review"],
            "educational": ["tutorial", "how to", "learn", "guide", "explain"],
            "automated": ["auto", "generated", "batch", "bulk", "script"]
        }
        
        # Analyze
        analysis = {
            "total_videos": len(self.videos),
            "common_keywords": {},
            "video_types": {},
            "automation_indicators": [],
            "tech_stack_hints": [],
            "content_pattern": ""
        }
        
        # Count keywords
        text_lower = all_text.lower()
        for keyword in automation_keywords:
            count = text_lower.count(keyword)
            if count > 0:
                analysis["common_keywords"][keyword] = count
        
        # Detect video types
        for vtype, keywords in video_types.items():
            score = sum(text_lower.count(kw) for kw in keywords)
            if score > 0:
                analysis["video_types"][vtype] = score
        
        # Look for tech stack mentions
        tech_terms = ["python", "javascript", "react", "node", "api", "github", "docker", "aws"]
        for term in tech_terms:
            if term in text_lower:
                analysis["tech_stack_hints"].append(term)
        
        # Analyze titles for patterns
        titles = [v.get("title", "") for v in self.videos[:10]]
        log("Sample titles:")
        for i, title in enumerate(titles[:5], 1):
            log(f"  {i}. {title[:60]}")
        
        # Determine content pattern
        if analysis["video_types"].get("coding", 0) > 5:
            analysis["content_pattern"] = "coding_tutorials"
        elif analysis["video_types"].get("ai", 0) > 5:
            analysis["content_pattern"] = "ai_content"
        elif analysis["video_types"].get("automated", 0) > 3:
            analysis["content_pattern"] = "automated_content"
        else:
            analysis["content_pattern"] = "mixed_content"
        
        self.analysis = analysis
        
        log("")
        log("Analysis results:")
        log(f"  Content pattern: {analysis['content_pattern']}")
        log(f"  Video types detected: {', '.join(analysis['video_types'].keys())}")
        log(f"  Tech hints: {', '.join(analysis['tech_stack_hints'][:5])}")
        
        return analysis


class GitHubToolFinder:
    """Search GitHub for tools that can create similar videos."""
    
    def __init__(self, analysis: Dict):
        self.analysis = analysis
        self.search_queries = []
        self.repositories = []
    
    def generate_search_queries(self):
        """Generate GitHub search queries based on analysis."""
        log_section("GENERATING GITHUB SEARCH QUERIES")
        
        content_pattern = self.analysis.get("content_pattern", "")
        tech_hints = self.analysis.get("tech_stack_hints", [])
        keywords = list(self.analysis.get("common_keywords", {}).keys())[:5]
        
        queries = []
        
        # Base queries for video automation
        base_queries = [
            "youtube video automation",
            "automated video generation",
            "youtube content creator automation",
            "video generation python",
            "youtube api automation"
        ]
        
        # Pattern-specific queries
        if content_pattern == "coding_tutorials":
            queries.extend([
                "coding tutorial video generator",
                "programming video automation",
                "code explanation video creator"
            ])
        elif content_pattern == "ai_content":
            queries.extend([
                "ai video generator",
                "llm video content creator",
                "ai automated video production"
            ])
        
        # Tech-specific queries
        if "python" in tech_hints:
            queries.append("python youtube automation")
        if "api" in tech_hints:
            queries.append("youtube api video creator")
        
        # Add keyword-based queries
        for keyword in keywords[:3]:
            queries.append(f"youtube {keyword} automation")
        
        self.search_queries = queries
        
        log(f"Generated {len(queries)} search queries:")
        for i, query in enumerate(queries[:10], 1):
            log(f"  {i}. {query}")
        
        return queries
    
    def search_github(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search GitHub for repositories."""
        log(f"Searching GitHub for: {query}")
        
        # Use GitHub search API via web search
        # In a real implementation, you'd use GitHub API with authentication
        # For now, we'll create search URLs and use web search
        
        github_search_url = f"https://github.com/search?q={query.replace(' ', '+')}&type=repositories"
        
        return {
            "query": query,
            "search_url": github_search_url,
            "results": []  # Would be populated with actual API results
        }
    
    def find_relevant_repos(self):
        """Find relevant GitHub repositories."""
        log_section("SEARCHING GITHUB FOR TOOLS")
        
        all_results = []
        
        for query in self.search_queries[:5]:  # Limit to top 5 queries
            result = self.search_github(query)
            all_results.append(result)
            time.sleep(1)  # Rate limiting
        
        self.repositories = all_results
        
        log(f"Searched {len(all_results)} queries")
        return all_results


def web_search_github(query: str):
    """Use web search to find GitHub repos."""
    from web_search import web_search
    
    search_term = f"site:github.com {query}"
    results = web_search(search_term)
    
    repos = []
    for result in results.get('results', [])[:10]:
        if 'github.com' in result.get('url', ''):
            repos.append({
                "title": result.get('title', ''),
                "url": result.get('url', ''),
                "snippet": result.get('snippet', '')
            })
    
    return repos


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Analyze YouTube channel and find GitHub tools for video automation"
    )
    parser.add_argument(
        "channel_url",
        help="YouTube channel URL (e.g., https://www.youtube.com/@HeftyLLM)"
    )
    parser.add_argument(
        "--max-videos",
        type=int,
        default=20,
        help="Max videos to analyze (default: 20)"
    )
    
    args = parser.parse_args()
    
    log_section("CHANNEL ANALYSIS + GITHUB TOOL DISCOVERY")
    log(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Analyze channel
    analyzer = ChannelAnalyzer(args.channel_url)
    
    if not analyzer.fetch_channel_videos(args.max_videos):
        log("Failed to fetch videos", "ERROR")
        return
    
    analysis = analyzer.analyze_video_patterns()
    
    # Step 2: Generate search queries
    finder = GitHubToolFinder(analysis)
    queries = finder.generate_search_queries()
    
    # Step 3: Search GitHub
    print("")
    log_section("SEARCHING GITHUB REPOSITORIES")
    log("This will search GitHub for tools that can create similar videos...")
    print("")
    
    # Use web search to find GitHub repos
    all_repos = []
    for query in queries[:5]:
        log(f"Searching: {query}")
        try:
            repos = web_search_github(query)
            all_repos.extend(repos)
            log(f"  Found {len(repos)} repositories")
        except Exception as e:
            log(f"  Search error: {e}", "WARNING")
        time.sleep(2)  # Rate limiting
    
    # Deduplicate
    seen_urls = set()
    unique_repos = []
    for repo in all_repos:
        if repo['url'] not in seen_urls:
            seen_urls.add(repo['url'])
            unique_repos.append(repo)
    
    # Step 4: Report findings
    print("")
    log_section("FOUND GITHUB REPOSITORIES")
    
    if unique_repos:
        log(f"Found {len(unique_repos)} relevant repositories:")
        print("")
        
        for i, repo in enumerate(unique_repos[:15], 1):
            log(f"{i}. {repo['title']}")
            log(f"   URL: {repo['url']}")
            if repo.get('snippet'):
                log(f"   Description: {repo['snippet'][:100]}...")
            print("")
    else:
        log("No repositories found via web search", "WARNING")
        log("Try manual GitHub search with these queries:", "INFO")
        for query in queries[:5]:
            log(f"  - {query}")
    
    # Save results
    results = {
        "channel_url": args.channel_url,
        "analysis": analysis,
        "search_queries": queries,
        "repositories": unique_repos,
        "timestamp": datetime.now().isoformat()
    }
    
    results_file = "channel_analysis_and_tools.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    
    log(f"Results saved: {results_file}")
    
    log_section("COMPLETE")
    log("Analysis and GitHub search completed!", "INFO")


if __name__ == "__main__":
    main()

