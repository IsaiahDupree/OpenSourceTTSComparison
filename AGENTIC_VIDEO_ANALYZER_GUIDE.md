# Agentic YouTube Channel Video Analyzer

## 🎯 What It Does

Automatically analyzes your YouTube channel to find the **best videos** for voice cloning by:

1. ✅ **Fetches all videos** from your channel
2. ✅ **Analyzes metadata** (duration, title, views)
3. ✅ **Samples audio quality** (SNR, voice activity, music detection)
4. ✅ **Scores each video** based on multiple criteria
5. ✅ **Ranks and recommends** the best videos

## 🚀 Quick Start

### Basic Usage:
```bash
python agentic_video_analyzer.py "https://www.youtube.com/@yourchannel"
```

### With Options:
```bash
python agentic_video_analyzer.py \
  "https://www.youtube.com/@yourchannel" \
  --max-videos 100 \
  --top-n 15
```

### Faster Analysis (Skip Audio Sampling):
```bash
python agentic_video_analyzer.py \
  "https://www.youtube.com/@yourchannel" \
  --no-audio-sample
```

## 📊 Scoring Criteria

Videos are scored on:

1. **Duration (25%)**
   - Ideal: 5-30 minutes
   - Too short: < 3 minutes
   - Too long: > 60 minutes

2. **Audio Quality (35%)**
   - SNR (signal-to-noise ratio)
   - Voice activity percentage
   - Spectral quality
   - Music detection

3. **Title Analysis (15%)**
   - Keywords suggesting good content
   - Avoids music/compilation keywords

4. **Popularity (10%)**
   - View count (log scale)

5. **Recency (15%)**
   - Newer videos preferred

## 🎯 What Makes a Video Recommended?

A video is **recommended** if:
- Total score >= 0.65
- Duration: 5-30 minutes (ideal)
- High audio quality (SNR 15+ dB)
- High voice activity (85%+)
- No background music
- Good title keywords

## 📋 Output

### 1. Analysis Report (`video_analysis_report.json`)
Complete analysis with:
- All videos ranked by score
- Detailed scoring factors
- Audio quality metrics
- Recommendations with explanations

### 2. Recommended URLs (`recommended_video_urls.txt`)
List of URLs ready for download:
```
# Recommended videos for voice cloning dataset
https://www.youtube.com/watch?v=VIDEO_ID_1
https://www.youtube.com/watch?v=VIDEO_ID_2
...
```

### 3. Console Output
Real-time analysis progress and top recommendations

## 🔄 Complete Workflow

### Step 1: Analyze Channel
```bash
python agentic_video_analyzer.py "https://www.youtube.com/@yourchannel"
```

### Step 2: Review Recommendations
Check `video_analysis_report.json` for detailed analysis

### Step 3: Download Recommended Videos
```bash
python download_high_quality_voice_dataset.py \
  --file recommended_video_urls.txt
```

### Step 4: Process Audio
```bash
python improved_audio_processor.py \
  --input audio_samples \
  --output processed_segments \
  --min-duration 5.0 \
  --min-snr 15.0
```

## 💡 Tips

1. **Start with more videos** - Analyze 50-100 videos for better selection
2. **Use audio sampling** - More accurate but slower (default: enabled)
3. **Review scores** - Check why videos scored high/low
4. **Download top 10-15** - Best balance of quality and dataset size

## 📈 Example Output

```
======================================================================
TOP RECOMMENDED VIDEOS FOR VOICE CLONING
======================================================================

  1. Complete Guide to Voice Cloning Tutorial
     Score: 0.782
     Duration: 12.5 min
     Why: Ideal duration (5-30 minutes); High audio quality; Good signal-to-noise ratio; High voice activity (lots of talking); No background music detected
     URL: https://www.youtube.com/watch?v=ABC123

  2. Deep Dive into AI Technology Explained
     Score: 0.745
     Duration: 18.3 min
     Why: Ideal duration (5-30 minutes); High audio quality; Good signal-to-noise ratio
     URL: https://www.youtube.com/watch?v=XYZ789
```

## 🎯 Why This Is Better

### Manual Selection:
- ❌ Time-consuming
- ❌ Subjective
- ❌ Misses hidden gems
- ❌ No quality metrics

### Agentic Analysis:
- ✅ Automatic
- ✅ Objective scoring
- ✅ Finds best videos
- ✅ Quality metrics included
- ✅ Explains recommendations

## 🔧 Advanced Usage

### Analyze Specific Playlist:
```bash
python agentic_video_analyzer.py "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

### Custom Threshold:
Modify `recommended` threshold in code (default: 0.65)

### Export to CSV:
Add CSV export functionality for spreadsheet analysis

---

**This agentic system finds the best videos automatically, saving you hours of manual work!**

