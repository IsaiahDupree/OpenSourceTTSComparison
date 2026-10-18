# Console Logging Guide

All scripts now have comprehensive console logging with real-time progress indicators.

## ✅ Updated Scripts

All scripts now include:
- ✅ **Real-time console output** - See progress as it happens
- ✅ **File logging** - Persistent logs saved to `.log` files
- ✅ **Progress indicators** - Clear status messages
- ✅ **Error handling** - Detailed error messages
- ✅ **Windows encoding fix** - Proper Unicode support

## 📋 Scripts with Logging

### 1. `agentic_video_analyzer.py`
- **Log file**: `agentic_analyzer.log`
- **Console**: Real-time analysis progress
- **Shows**: Video analysis, scoring, recommendations

### 2. `download_high_quality_voice_dataset.py`
- **Log file**: `download_voice_dataset.log`
- **Console**: Download progress, file sizes
- **Shows**: Download status, errors, completion

### 3. `improved_audio_processor.py`
- **Log file**: `audio_processor.log`
- **Console**: Processing progress, quality metrics
- **Shows**: Segments found, quality scores, statistics

### 4. `build_and_test.py`
- **Log file**: `build_test.log`
- **Console**: Build and test progress
- **Shows**: Installation, testing, results

### 5. `run_full_workflow.py` (NEW)
- **Log file**: `full_workflow.log`
- **Console**: Complete workflow progress
- **Shows**: All steps with real-time output

## 🚀 Using the Full Workflow Script

The new `run_full_workflow.py` orchestrates everything with full logging:

```bash
# Complete workflow with logging
python run_full_workflow.py "https://www.youtube.com/channel/UCnDBsELI2OIaEI5yxA77HNA"

# With options
python run_full_workflow.py \
  "https://www.youtube.com/channel/UCnDBsELI2OIaEI5yxA77HNA" \
  --max-videos 50 \
  --top-n 15

# Analysis only (no download/process)
python run_full_workflow.py \
  "https://www.youtube.com/channel/UCnDBsELI2OIaEI5yxA77HNA" \
  --no-download \
  --no-process
```

## 📊 Log Format

### Console Output:
```
11:45:51 [INFO] ======================================================================
11:45:51 [INFO] STEP 1: ANALYZING CHANNEL FOR BEST VIDEOS
11:45:51 [INFO] ======================================================================
11:45:51 [INFO] Channel URL: https://www.youtube.com/channel/...
11:45:52 [INFO] Found 100 videos
11:45:52 [INFO] [1/100] Analyzing video...
11:45:52 [INFO] ✅ Analysis completed
```

### File Logs:
- More detailed information
- Timestamps with dates
- Debug information
- Full error traces

## 🔍 Viewing Logs

### Real-time (Console):
All scripts output to console in real-time.

### After Completion:
```bash
# View latest log
type agentic_analyzer.log
type download_voice_dataset.log
type audio_processor.log
type full_workflow.log
```

## 💡 Benefits

1. **See Progress** - Know what's happening in real-time
2. **Debug Issues** - Detailed logs help troubleshoot
3. **Track Time** - See how long each step takes
4. **Monitor Quality** - See quality scores as they're calculated
5. **Error Details** - Full error messages with context

## 🎯 Example Output

```
======================================================================
FULL WORKFLOW: VOICE CLONING DATASET CREATION
======================================================================
Started: 2025-12-24 11:45:00

======================================================================
STEP 1: ANALYZING CHANNEL FOR BEST VIDEOS
======================================================================
Channel URL: https://www.youtube.com/channel/...
Max videos to analyze: 50
Top N to recommend: 15

Running: python agentic_video_analyzer.py ...
  [INFO] Found 100 videos
  [INFO] Analyzing video 1/100...
  [INFO] ✅ Quality: 0.782, SNR: 18.5dB
  ...
✅ Channel analysis completed
✅ Found 100 videos
✅ Recommended: 15 videos

======================================================================
STEP 2: DOWNLOADING RECOMMENDED VIDEOS
======================================================================
Found 15 video URLs to download
  [INFO] Downloading video 1/15...
  [INFO] ✅ Downloaded: video_1.m4a (45.2 MB)
  ...
✅ Video downloads completed

======================================================================
STEP 3: PROCESSING AUDIO SEGMENTS
======================================================================
  [INFO] Processing: video_1.m4a
  [INFO] Found 8 segments
  [INFO] ✅ Extracted 5 high-quality segments
  ...
✅ Audio processing completed
✅ Total segments: 75
✅ Average quality: 0.682
✅ Best quality: 0.745
```

## 🔧 Customization

All scripts use `logging_config.py` for consistent logging. To customize:

```python
from logging_config import setup_logging

logger = setup_logging(
    __name__,
    log_file="custom.log",
    level=logging.DEBUG  # More verbose
)
```

---

**All scripts now have comprehensive console logging!** You'll see exactly what's happening at every step.

