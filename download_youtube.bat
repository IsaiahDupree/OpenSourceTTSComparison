@echo off
echo Downloading YouTube videos...

yt-dlp --extract-audio --audio-format mp3 --audio-quality 0 --output "audio_samples/%%(id)s.%%(ext)s" "https://www.youtube.com/watch?v=Uh34kDEF500"
yt-dlp --extract-audio --audio-format mp3 --audio-quality 0 --output "audio_samples/%%(id)s.%%(ext)s" "https://www.youtube.com/watch?v=KpuEkonkuiU"
yt-dlp --extract-audio --audio-format mp3 --audio-quality 0 --output "audio_samples/%%(id)s.%%(ext)s" "https://www.youtube.com/watch?v=JXHPIahTayU"
yt-dlp --extract-audio --audio-format mp3 --audio-quality 0 --output "audio_samples/%%(id)s.%%(ext)s" "https://www.youtube.com/watch?v=w4sarAE9h9I"
yt-dlp --extract-audio --audio-format mp3 --audio-quality 0 --output "audio_samples/%%(id)s.%%(ext)s" "https://www.youtube.com/watch?v=0YWpkJkbXxs"

echo Download complete!
echo Processing audio segments...

python tools/audio_processor.py --input audio_samples --output processed_segments

echo All done! Ready for TTS benchmarking.
