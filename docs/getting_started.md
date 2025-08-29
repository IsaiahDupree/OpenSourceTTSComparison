# Getting Started with TTS Comparison Study

## Quick Setup

1. **Initial Setup**
   ```bash
   python setup.py
   ```

2. **Install TTS Models**
   ```bash
   python scripts/install_models.py
   ```

3. **Prepare Audio Data**
   ```bash
   # Add your audio files to audio_samples/ directory
   python tools/audio_processor.py --input audio_samples/ --output processed/
   ```

4. **Run Benchmarks**
   ```bash
   python benchmark/run_all_tests.py
   ```

## Detailed Instructions

### 1. Environment Setup

Ensure you have Python 3.8+ and pip installed. The setup script will install all required dependencies.

### 2. Model Installation

The installation script supports installing specific models:

```bash
# Install all models
python scripts/install_models.py

# Install specific models
python scripts/install_models.py --models chatterbox coqui-tts

# Check system requirements
python scripts/install_models.py --check-requirements
```

### 3. Audio Processing

The audio processor extracts high-quality voice segments from your audio files:

```bash
# Process all audio files in a directory
python tools/audio_processor.py --input /path/to/audio --output processed/

# Limit number of files processed
python tools/audio_processor.py --input audio_samples/ --max-files 10

# Set target segment duration
python tools/audio_processor.py --input audio_samples/ --target-duration 15.0
```

### 4. Running Benchmarks

```bash
# Run all benchmarks
python benchmark/run_all_tests.py

# Test specific models
python benchmark/run_all_tests.py --models chatterbox openvoice

# Custom output directory
python benchmark/run_all_tests.py --output-dir my_results/
```

## Understanding Results

After running benchmarks, you'll find:

- `results/benchmark_report.md` - Comprehensive analysis
- `results/detailed_results.csv` - Raw benchmark data
- `results/performance_comparison.png` - Performance visualizations
- `results/quality_heatmap.png` - Quality metrics comparison

## Troubleshooting

### Common Issues

1. **Model Installation Fails**
   - Check internet connection
   - Ensure sufficient disk space
   - Try installing models individually

2. **CUDA/GPU Issues**
   - Install appropriate PyTorch version for your system
   - Check CUDA compatibility

3. **Audio Processing Errors**
   - Ensure audio files are in supported formats (wav, mp3, flac)
   - Check file permissions

### Getting Help

- Check installation logs in `models/installation_log.json`
- Review processing results in `processed/processing_results.json`
- Enable debug logging: `export PYTHONPATH=.:$PYTHONPATH`
