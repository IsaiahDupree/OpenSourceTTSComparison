# Download High-Quality Voice Dataset from YouTube

## 🎯 Goal
Download YouTube videos with long, continuous speech segments to create a better voice cloning dataset with higher quality scores.

## 🚀 Quick Start

### Method 1: Interactive Download (Easiest)
```bash
python download_high_quality_voice_dataset.py
```

Then paste YouTube URLs when prompted.

### Method 2: Command Line
```bash
python download_high_quality_voice_dataset.py --urls \
  "https://www.youtube.com/watch?v=VIDEO_ID_1" \
  "https://www.youtube.com/watch?v=VIDEO_ID_2" \
  "https://youtu.be/VIDEO_ID_3"
```

### Method 3: Batch from File
1. Create `youtube_urls.txt` with URLs (one per line)
2. Run:
```bash
python download_high_quality_voice_dataset.py --file youtube_urls.txt
```

## 📋 What Makes a Good Video for Voice Cloning?

### ✅ Good Choices:
- **Long solo talking** (5+ minutes of continuous speech)
- **Clear audio** (no background music, minimal noise)
- **Consistent voice** (same person throughout)
- **Natural speech** (not reading scripts robotically)
- **Good microphone quality**

### ❌ Avoid:
- Videos with background music
- Interviews/conversations (multiple speakers)
- Very short videos (< 2 minutes)
- Poor audio quality
- Heavy background noise

## 🎛️ Download Settings

The script downloads with:
- ✅ **Best audio quality** (format: m4a)
- ✅ **Highest bitrate** available
- ✅ **Metadata** (video info, thumbnails)
- ✅ **Automatic naming** (video ID + title)

## 🔧 Process Downloaded Audio

After downloading, process to extract high-quality segments:

```bash
# Use improved processor (extracts longer, better segments)
python improved_audio_processor.py \
  --input audio_samples \
  --output processed_segments \
  --min-duration 5.0 \
  --max-duration 15.0 \
  --min-snr 15.0 \
  --min-voice-activity 0.85 \
  --segments-per-file 5
```

### Parameters Explained:
- `--min-duration 5.0`: Minimum segment length (5 seconds)
- `--max-duration 15.0`: Maximum segment length (15 seconds)
- `--min-snr 15.0`: Minimum signal-to-noise ratio (15 dB)
- `--min-voice-activity 0.85`: Minimum voice activity (85%)
- `--segments-per-file 5`: Keep top 5 segments per video

## 📊 Quality Improvements

### Old Processor:
- Segments: 3-4 seconds
- Quality score: ~0.60 average
- SNR: ~11.6 dB average

### Improved Processor:
- Segments: 5-15 seconds (longer = better for cloning)
- Quality score: Higher (better filtering)
- SNR: 15+ dB (only high-quality segments)
- Voice activity: 85%+ (more speech, less silence)

## 🎯 Workflow

1. **Download videos:**
   ```bash
   python download_high_quality_voice_dataset.py
   ```

2. **Process audio:**
   ```bash
   python improved_audio_processor.py \
     --input audio_samples \
     --output processed_segments
   ```

3. **Check results:**
   ```bash
   # View quality scores
   cat processed_segments/processing_results.json
   ```

4. **Use best segments:**
   - Check `best_segments` in results JSON
   - Use segments with highest `quality_score`
   - Longer segments (5-15s) work better

## 💡 Tips for Better Quality

1. **Download more videos** - More data = better quality
2. **Choose longer videos** - More speech segments
3. **Prefer solo talking** - Consistent voice
4. **Check audio quality** - Listen before processing
5. **Process with higher thresholds** - Better filtering

## 📈 Expected Results

With improved processor, you should see:
- ✅ Longer segments (5-15 seconds vs 3-4 seconds)
- ✅ Higher quality scores (0.65+ vs 0.60)
- ✅ Better SNR (15+ dB vs 11.6 dB)
- ✅ More voice activity (85%+ vs 78%)
- ✅ Better voice cloning results

## 🔍 Verify Quality

After processing, check:
```json
{
  "statistics": {
    "average_quality_score": 0.65+,  // Should be higher
    "best_quality_score": 0.70+,     // Should be higher
    "average_snr": 15.0+,            // Should be 15+ dB
    "average_duration": 7.0+         // Should be 5-15 seconds
  }
}
```

## 🎉 Next Steps

1. Download 5-10 high-quality videos
2. Process with improved processor
3. Use best segments for voice cloning
4. Test with Chatterbox or Coqui TTS
5. Compare results with old dataset

---

**The improved processor will give you better quality segments for voice cloning!**

