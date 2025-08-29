#!/usr/bin/env python3
"""
TTS Benchmarking Framework

Comprehensive benchmarking system for comparing TTS models across:
- Voice quality metrics
- Latency and performance
- Voice cloning fidelity
- Multilingual capabilities
"""

import os
import time
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging
from dataclasses import dataclass
import soundfile as sf
import librosa
from pesq import pesq
from pystoi import stoi
import torch
import psutil
import memory_profiler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    """Container for benchmark results."""
    model_name: str
    test_type: str
    metrics: Dict[str, float]
    metadata: Dict[str, Any]
    timestamp: float


class TTSBenchmark:
    """Main benchmarking framework for TTS models."""
    
    def __init__(self, output_dir: str = "results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.results = []
        
    def benchmark_model(self, model_wrapper, test_cases: List[Dict]) -> List[BenchmarkResult]:
        """Benchmark a single TTS model."""
        model_results = []
        
        for test_case in test_cases:
            # Quality benchmark
            quality_result = self._benchmark_quality(model_wrapper, test_case)
            model_results.append(quality_result)
            
            # Performance benchmark
            perf_result = self._benchmark_performance(model_wrapper, test_case)
            model_results.append(perf_result)
            
            # Voice cloning benchmark (if applicable)
            if test_case.get('reference_audio'):
                clone_result = self._benchmark_voice_cloning(model_wrapper, test_case)
                model_results.append(clone_result)
        
        return model_results
    
    def _benchmark_quality(self, model_wrapper, test_case: Dict) -> BenchmarkResult:
        """Benchmark voice quality metrics."""
        text = test_case['text']
        
        # Generate audio
        start_time = time.time()
        generated_audio = model_wrapper.synthesize(text)
        generation_time = time.time() - start_time
        
        # Calculate quality metrics
        metrics = {
            'generation_time': generation_time,
            'audio_length': len(generated_audio) / 22050,
            'real_time_factor': generation_time / (len(generated_audio) / 22050)
        }
        
        # Add audio quality metrics if reference exists
        if test_case.get('reference_audio_path'):
            ref_audio, _ = librosa.load(test_case['reference_audio_path'], sr=22050)
            
            # Ensure same length for comparison
            min_len = min(len(generated_audio), len(ref_audio))
            gen_audio_trimmed = generated_audio[:min_len]
            ref_audio_trimmed = ref_audio[:min_len]
            
            # PESQ score (requires 16kHz)
            gen_16k = librosa.resample(gen_audio_trimmed, orig_sr=22050, target_sr=16000)
            ref_16k = librosa.resample(ref_audio_trimmed, orig_sr=22050, target_sr=16000)
            
            try:
                pesq_score = pesq(16000, ref_16k, gen_16k, 'wb')
                metrics['pesq_score'] = pesq_score
            except:
                metrics['pesq_score'] = None
            
            # STOI score
            try:
                stoi_score = stoi(ref_audio_trimmed, gen_audio_trimmed, 22050, extended=False)
                metrics['stoi_score'] = stoi_score
            except:
                metrics['stoi_score'] = None
        
        return BenchmarkResult(
            model_name=model_wrapper.name,
            test_type="quality",
            metrics=metrics,
            metadata=test_case,
            timestamp=time.time()
        )
    
    def _benchmark_performance(self, model_wrapper, test_case: Dict) -> BenchmarkResult:
        """Benchmark performance metrics."""
        text = test_case['text']
        
        # Memory usage before
        process = psutil.Process()
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # GPU memory before (if available)
        gpu_memory_before = 0
        if torch.cuda.is_available():
            gpu_memory_before = torch.cuda.memory_allocated() / 1024 / 1024  # MB
        
        # Benchmark multiple runs
        times = []
        for _ in range(3):
            start_time = time.time()
            _ = model_wrapper.synthesize(text)
            times.append(time.time() - start_time)
        
        # Memory usage after
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        gpu_memory_after = 0
        if torch.cuda.is_available():
            gpu_memory_after = torch.cuda.memory_allocated() / 1024 / 1024  # MB
        
        metrics = {
            'avg_inference_time': np.mean(times),
            'min_inference_time': np.min(times),
            'max_inference_time': np.max(times),
            'std_inference_time': np.std(times),
            'memory_usage_mb': memory_after - memory_before,
            'gpu_memory_usage_mb': gpu_memory_after - gpu_memory_before,
            'characters_per_second': len(text) / np.mean(times)
        }
        
        return BenchmarkResult(
            model_name=model_wrapper.name,
            test_type="performance",
            metrics=metrics,
            metadata=test_case,
            timestamp=time.time()
        )
    
    def _benchmark_voice_cloning(self, model_wrapper, test_case: Dict) -> BenchmarkResult:
        """Benchmark voice cloning capabilities."""
        if not hasattr(model_wrapper, 'clone_voice'):
            return BenchmarkResult(
                model_name=model_wrapper.name,
                test_type="voice_cloning",
                metrics={'supported': False},
                metadata=test_case,
                timestamp=time.time()
            )
        
        reference_audio = test_case['reference_audio']
        text = test_case['text']
        
        start_time = time.time()
        cloned_audio = model_wrapper.clone_voice(reference_audio, text)
        cloning_time = time.time() - start_time
        
        metrics = {
            'supported': True,
            'cloning_time': cloning_time,
            'reference_length': len(reference_audio) / 22050,
            'output_length': len(cloned_audio) / 22050
        }
        
        return BenchmarkResult(
            model_name=model_wrapper.name,
            test_type="voice_cloning",
            metrics=metrics,
            metadata=test_case,
            timestamp=time.time()
        )
    
    def save_results(self, filename: str = "benchmark_results.json"):
        """Save benchmark results to file."""
        results_data = []
        for result in self.results:
            results_data.append({
                'model_name': result.model_name,
                'test_type': result.test_type,
                'metrics': result.metrics,
                'metadata': result.metadata,
                'timestamp': result.timestamp
            })
        
        output_file = self.output_dir / filename
        with open(output_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        logger.info(f"Results saved to {output_file}")
    
    def generate_report(self) -> pd.DataFrame:
        """Generate comprehensive benchmark report."""
        if not self.results:
            return pd.DataFrame()
        
        # Convert results to DataFrame
        data = []
        for result in self.results:
            row = {
                'model': result.model_name,
                'test_type': result.test_type,
                **result.metrics
            }
            data.append(row)
        
        df = pd.DataFrame(data)
        
        # Save CSV report
        report_file = self.output_dir / "benchmark_report.csv"
        df.to_csv(report_file, index=False)
        logger.info(f"Report saved to {report_file}")
        
        return df


class ModelWrapper:
    """Base class for TTS model wrappers."""
    
    def __init__(self, name: str):
        self.name = name
    
    def synthesize(self, text: str) -> np.ndarray:
        """Synthesize speech from text."""
        raise NotImplementedError
    
    def clone_voice(self, reference_audio: np.ndarray, text: str) -> np.ndarray:
        """Clone voice and synthesize text."""
        raise NotImplementedError


# Model-specific wrappers will be implemented in separate files
