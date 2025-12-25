# Your Voice Dataset from YouTube

## ✅ Yes! You Have YouTube Voice Dataset

### 📁 Raw Audio Samples (`audio_samples/`)

You have **5 YouTube videos** downloaded as audio:

1. **0YWpkJkbXxs** - "Never lose power again. UPS UNBOXING."
   - Format: `.m4a`
   - Status: ✅ Downloaded

2. **JXHPIahTayU** - "What era are you in？"
   - Format: `.m4a`
   - Status: ✅ Downloaded

3. **KpuEkonkuiU** - "2025 06 03 21 19 15"
   - Format: `.m4a`
   - Status: ✅ Downloaded

4. **Uh34kDEF500** - "AI's Revolutionary Impact on Software"
   - Format: `.m4a`
   - Status: ✅ Downloaded

5. **w4sarAE9h9I** - "Turn YouTube Transcripts into Effective Content with Make.com"
   - Format: `.m4a`
   - Status: ✅ Downloaded

### 📁 Processed Segments (`processed_segments/`)

Your audio has been **processed and segmented** into voice clips:

#### Available Segments:
- **0YWpkJkbXxs** (UPS video):
  - `_segment_0.wav`
  - `_segment_1.wav`
  - `_segment_2.wav`

- **KpuEkonkuiU** (2025 video):
  - `_segment_0.wav`
  - `_segment_1.wav`
  - `_segment_2.wav`

- **Uh34kDEF500** (AI Impact video):
  - `_segment_0.wav`
  - `_segment_1.wav`

- **w4sarAE9h9I** (Make.com video):
  - `_segment_0.wav`

**Total: 8 processed voice segments ready for voice cloning!**

### 📊 Processing Analysis

Check `processed_segments/processing_results.json` for:
- Segment durations
- Audio quality metrics
- Processing statistics

---

## 🎯 Using Your Voice Dataset for Voice Cloning

### Option 1: Use Individual Segments

```python
# Use any segment as reference for voice cloning
reference_audio = "processed_segments/0YWpkJkbXxs_Never lose power again. UPS UNBOXING._segment_0.wav"

# With Chatterbox
import chatterbox
tts = chatterbox.ChatterboxTTS.from_pretrained("cpu")
audio = tts.generate("Your text here", audio_prompt_path=reference_audio)
```

### Option 2: Combine Segments for Better Quality

Longer reference audio (3-10 seconds) usually gives better voice cloning results. You can:
- Concatenate multiple segments
- Use the full original audio files
- Select the best quality segments

### Option 3: Use Full Audio Files

```python
# Use full YouTube audio as reference
reference_audio = "audio_samples/Uh34kDEF500_AI's Revolutionary Impact on Software.m4a"

# Note: May need to convert .m4a to .wav first
```

---

## 🔧 Tools Available

### Download More Videos:
```bash
# Use the batch script
download_youtube.bat

# Or Python script
python download_and_process.py
```

### Process Audio:
```bash
python tools/audio_processor.py --input audio_samples --output processed_segments
```

### YouTube Downloader Scripts:
- `youtube_audio_downloader.py`
- `easy_youtube_dl.py`
- `scripts/youtube_downloader.py`
- `scripts/modular_youtube_downloader.py`

---

## 📈 Dataset Statistics

**Raw Audio:**
- 5 YouTube videos
- Format: `.m4a` (audio extracted)
- Total files: 5

**Processed Segments:**
- 8 voice segments
- Format: `.wav` (ready for TTS)
- From 4 videos (1 video not segmented yet)

**Ready for Voice Cloning:**
- ✅ 8 segments available
- ✅ Quality processed
- ✅ Ready to use as reference audio

---

## 🎤 Best Segments for Voice Cloning

For best results, use segments that:
1. ✅ Are 3-10 seconds long
2. ✅ Have clear speech (no background noise)
3. ✅ Are from the same speaker (your voice)
4. ✅ Have good audio quality

**Recommended:**
- Check `processed_segments/processing_results.json` for quality metrics
- Use segments with highest quality scores
- Combine multiple segments for longer reference

---

## 🚀 Quick Start: Use Your Voice Dataset

### Step 1: Check Available Segments
```bash
dir processed_segments\*.wav
```

### Step 2: Test Voice Cloning with Your Voice
```python
# Activate Chatterbox environment
venv_chatterbox311\Scripts\activate

# Use your voice segment
python -c "
import chatterbox
tts = chatterbox.ChatterboxTTS.from_pretrained('cpu')
audio = tts.generate(
    'Hello, this is a test using my voice from YouTube.',
    audio_prompt_path='processed_segments/0YWpkJkbXxs_Never lose power again. UPS UNBOXING._segment_0.wav'
)
import soundfile as sf
sf.write('my_voice_clone_test.wav', audio.squeeze(0).detach().cpu().numpy(), 24000)
print('Done! Check my_voice_clone_test.wav')
"
```

---

## 💡 Next Steps

1. **Review segments** - Check which segments have best quality
2. **Test voice cloning** - Use segments with Chatterbox
3. **Download more** - If you need more voice data
4. **Process more** - Segment additional videos if needed

---

## 📝 Notes

- Your dataset is **ready to use** for voice cloning
- Segments are in `.wav` format (compatible with TTS models)
- Original `.m4a` files are preserved in `audio_samples/`
- Processing results show quality metrics for each segment

**You have everything you need to clone your voice from YouTube videos!** 🎉

