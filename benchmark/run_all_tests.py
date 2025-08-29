#!/usr/bin/env python3
"""
Main script to run comprehensive TTS benchmarks across all models.
"""

import json
import logging
import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List

from tts_benchmark import TTSBenchmark, BenchmarkResult
import sys
sys.path.append(str(Path(__file__).parent.parent / "models"))
from model_wrappers import ModelFactory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComprehensiveTTSBenchmark:
    """Comprehensive benchmarking suite for all TTS models."""
    
    def __init__(self, output_dir: str = "results"):
        self.benchmark = TTSBenchmark(output_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def load_test_cases(self, test_file: str = "data/test_cases.json") -> Dict:
        """Load test cases from JSON file."""
        with open(test_file, 'r') as f:
            return json.load(f)
    
    def run_full_benchmark(self, models: List[str] = None) -> Dict:
        """Run complete benchmark suite."""
        if models is None:
            models = ModelFactory.get_available_models()
        
        test_data = self.load_test_cases()
        all_results = {}
        
        for model_name in models:
            logger.info(f"\n{'='*60}")
            logger.info(f"BENCHMARKING {model_name.upper()}")
            logger.info(f"{'='*60}")
            
            try:
                # Create and load model wrapper
                wrapper = ModelFactory.create_wrapper(model_name)
                if not wrapper.load_model():
                    logger.error(f"❌ Failed to load {model_name}, skipping...")
                    continue
                
                # Run benchmarks
                model_results = self._benchmark_single_model(wrapper, test_data)
                all_results[model_name] = model_results
                
                logger.info(f"✅ Completed benchmarking {model_name}")
                
            except Exception as e:
                logger.error(f"❌ Error benchmarking {model_name}: {e}")
                continue
        
        # Generate comprehensive report
        self._generate_comprehensive_report(all_results)
        
        return all_results
    
    def _benchmark_single_model(self, wrapper, test_data: Dict) -> List[BenchmarkResult]:
        """Benchmark a single model with all test cases."""
        results = []
        
        # Basic synthesis tests
        logger.info("Running basic synthesis tests...")
        for test_case in test_data['test_cases']:
            try:
                result = self.benchmark._benchmark_quality(wrapper, test_case)
                results.append(result)
                
                perf_result = self.benchmark._benchmark_performance(wrapper, test_case)
                results.append(perf_result)
                
            except Exception as e:
                logger.error(f"❌ Test case {test_case['id']} failed: {e}")
                continue
        
        # Voice cloning tests (if supported)
        if wrapper.supports_voice_cloning():
            logger.info("Running voice cloning tests...")
            for test_case in test_data.get('voice_cloning_tests', []):
                try:
                    # Create dummy reference audio for testing
                    import numpy as np
                    dummy_reference = np.random.randn(22050 * 3)  # 3 seconds of noise
                    test_case['reference_audio'] = dummy_reference
                    
                    result = self.benchmark._benchmark_voice_cloning(wrapper, test_case)
                    results.append(result)
                    
                except Exception as e:
                    logger.error(f"❌ Voice cloning test {test_case['id']} failed: {e}")
                    continue
        
        return results
    
    def _generate_comprehensive_report(self, all_results: Dict):
        """Generate comprehensive analysis report."""
        logger.info("Generating comprehensive report...")
        
        # Convert results to DataFrame
        data = []
        for model_name, results in all_results.items():
            for result in results:
                row = {
                    'model': model_name,
                    'test_type': result.test_type,
                    **result.metrics
                }
                if 'metadata' in result.__dict__ and result.metadata:
                    row.update({f"meta_{k}": v for k, v in result.metadata.items() if isinstance(v, (str, int, float, bool))})
                data.append(row)
        
        if not data:
            logger.warning("No results to analyze")
            return
        
        df = pd.DataFrame(data)
        
        # Save detailed results
        df.to_csv(self.output_dir / "detailed_results.csv", index=False)
        
        # Generate summary statistics
        self._generate_summary_stats(df)
        
        # Create visualizations
        self._create_visualizations(df)
        
        # Generate markdown report
        self._generate_markdown_report(df)
    
    def _generate_summary_stats(self, df: pd.DataFrame):
        """Generate summary statistics."""
        summary_stats = {}
        
        # Performance metrics
        perf_df = df[df['test_type'] == 'performance']
        if not perf_df.empty:
            summary_stats['performance'] = {
                'avg_inference_time': perf_df.groupby('model')['avg_inference_time'].mean().to_dict(),
                'characters_per_second': perf_df.groupby('model')['characters_per_second'].mean().to_dict(),
                'memory_usage_mb': perf_df.groupby('model')['memory_usage_mb'].mean().to_dict()
            }
        
        # Quality metrics
        quality_df = df[df['test_type'] == 'quality']
        if not quality_df.empty:
            summary_stats['quality'] = {
                'real_time_factor': quality_df.groupby('model')['real_time_factor'].mean().to_dict(),
                'pesq_score': quality_df.groupby('model')['pesq_score'].mean().to_dict(),
                'stoi_score': quality_df.groupby('model')['stoi_score'].mean().to_dict()
            }
        
        # Voice cloning support
        cloning_df = df[df['test_type'] == 'voice_cloning']
        if not cloning_df.empty:
            summary_stats['voice_cloning'] = {
                'supported_models': cloning_df[cloning_df['supported'] == True]['model'].unique().tolist(),
                'avg_cloning_time': cloning_df.groupby('model')['cloning_time'].mean().to_dict()
            }
        
        # Save summary
        with open(self.output_dir / "summary_stats.json", 'w') as f:
            json.dump(summary_stats, f, indent=2, default=str)
        
        logger.info("Summary statistics saved")
    
    def _create_visualizations(self, df: pd.DataFrame):
        """Create benchmark visualizations."""
        plt.style.use('seaborn-v0_8')
        
        # Performance comparison
        perf_df = df[df['test_type'] == 'performance']
        if not perf_df.empty:
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            
            # Inference time
            perf_df.boxplot(column='avg_inference_time', by='model', ax=axes[0,0])
            axes[0,0].set_title('Average Inference Time by Model')
            axes[0,0].set_ylabel('Time (seconds)')
            
            # Characters per second
            perf_df.boxplot(column='characters_per_second', by='model', ax=axes[0,1])
            axes[0,1].set_title('Characters per Second by Model')
            axes[0,1].set_ylabel('Characters/second')
            
            # Memory usage
            perf_df.boxplot(column='memory_usage_mb', by='model', ax=axes[1,0])
            axes[1,0].set_title('Memory Usage by Model')
            axes[1,0].set_ylabel('Memory (MB)')
            
            # Real-time factor
            quality_df = df[df['test_type'] == 'quality']
            if not quality_df.empty:
                quality_df.boxplot(column='real_time_factor', by='model', ax=axes[1,1])
                axes[1,1].set_title('Real-time Factor by Model')
                axes[1,1].set_ylabel('RTF (lower is better)')
            
            plt.tight_layout()
            plt.savefig(self.output_dir / 'performance_comparison.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        # Quality metrics heatmap
        quality_df = df[df['test_type'] == 'quality']
        if not quality_df.empty and 'pesq_score' in quality_df.columns:
            quality_metrics = quality_df.groupby('model')[['pesq_score', 'stoi_score', 'real_time_factor']].mean()
            
            plt.figure(figsize=(10, 6))
            sns.heatmap(quality_metrics.T, annot=True, cmap='RdYlGn', center=0)
            plt.title('Quality Metrics Heatmap')
            plt.tight_layout()
            plt.savefig(self.output_dir / 'quality_heatmap.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        logger.info("Visualizations saved")
    
    def _generate_markdown_report(self, df: pd.DataFrame):
        """Generate markdown report."""
        report_lines = [
            "# TTS Models Comparison Report",
            "",
            f"**Generated:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Executive Summary",
            "",
            f"This report compares {df['model'].nunique()} TTS models across {df['test_type'].nunique()} different test categories.",
            "",
            "## Models Tested",
            ""
        ]
        
        # Add model list
        for model in sorted(df['model'].unique()):
            report_lines.append(f"- **{model.title()}**")
        
        report_lines.extend([
            "",
            "## Performance Results",
            ""
        ])
        
        # Performance summary
        perf_df = df[df['test_type'] == 'performance']
        if not perf_df.empty:
            perf_summary = perf_df.groupby('model').agg({
                'avg_inference_time': 'mean',
                'characters_per_second': 'mean',
                'memory_usage_mb': 'mean'
            }).round(3)
            
            report_lines.append("| Model | Avg Inference Time (s) | Characters/sec | Memory Usage (MB) |")
            report_lines.append("|-------|------------------------|----------------|-------------------|")
            
            for model, row in perf_summary.iterrows():
                report_lines.append(f"| {model.title()} | {row['avg_inference_time']:.3f} | {row['characters_per_second']:.1f} | {row['memory_usage_mb']:.1f} |")
        
        # Quality results
        quality_df = df[df['test_type'] == 'quality']
        if not quality_df.empty:
            report_lines.extend([
                "",
                "## Quality Results",
                ""
            ])
            
            if 'pesq_score' in quality_df.columns:
                quality_summary = quality_df.groupby('model').agg({
                    'pesq_score': 'mean',
                    'stoi_score': 'mean',
                    'real_time_factor': 'mean'
                }).round(3)
                
                report_lines.append("| Model | PESQ Score | STOI Score | Real-time Factor |")
                report_lines.append("|-------|------------|------------|------------------|")
                
                for model, row in quality_summary.iterrows():
                    pesq = row['pesq_score'] if pd.notna(row['pesq_score']) else 'N/A'
                    stoi = row['stoi_score'] if pd.notna(row['stoi_score']) else 'N/A'
                    rtf = row['real_time_factor'] if pd.notna(row['real_time_factor']) else 'N/A'
                    report_lines.append(f"| {model.title()} | {pesq} | {stoi} | {rtf} |")
        
        # Voice cloning support
        cloning_df = df[df['test_type'] == 'voice_cloning']
        if not cloning_df.empty:
            report_lines.extend([
                "",
                "## Voice Cloning Support",
                ""
            ])
            
            supported_models = cloning_df[cloning_df['supported'] == True]['model'].unique()
            for model in sorted(df['model'].unique()):
                status = "✅ Supported" if model in supported_models else "❌ Not Supported"
                report_lines.append(f"- **{model.title()}**: {status}")
        
        report_lines.extend([
            "",
            "## Recommendations",
            "",
            "### Best Overall Performance",
            "- **Fastest Inference**: TBD based on results",
            "- **Best Quality**: TBD based on results", 
            "- **Best Voice Cloning**: TBD based on results",
            "",
            "### Use Case Recommendations",
            "- **Real-time Applications**: Models with RTF < 1.0",
            "- **High Quality Synthesis**: Models with highest PESQ/STOI scores",
            "- **Voice Cloning**: Models with voice cloning support",
            "",
            "## Files Generated",
            "- `detailed_results.csv` - Complete benchmark data",
            "- `summary_stats.json` - Summary statistics",
            "- `performance_comparison.png` - Performance visualizations",
            "- `quality_heatmap.png` - Quality metrics heatmap"
        ])
        
        # Save report
        with open(self.output_dir / "benchmark_report.md", 'w') as f:
            f.write('\n'.join(report_lines))
        
        logger.info("Markdown report generated")


def main():
    parser = argparse.ArgumentParser(description='Run comprehensive TTS benchmarks')
    parser.add_argument('--models', nargs='+', help='Specific models to test')
    parser.add_argument('--output-dir', default='results', help='Output directory')
    parser.add_argument('--test-file', default='data/test_cases.json', help='Test cases file')
    
    args = parser.parse_args()
    
    benchmark_suite = ComprehensiveTTSBenchmark(args.output_dir)
    results = benchmark_suite.run_full_benchmark(args.models)
    
    print(f"\n🎉 Benchmarking complete! Results saved to: {args.output_dir}/")
    print(f"📊 Check benchmark_report.md for detailed analysis")


if __name__ == "__main__":
    main()
