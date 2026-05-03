#!/usr/bin/env python3
"""
COMPARISON SCRIPT - So sánh kết quả WITH vs WITHOUT calibration examples

Chạy script này để:
1. So sánh score distribution
2. Phân tích improvement
3. Generate report
"""

import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any
from scipy import stats

def load_results(filepath: str) -> List[Dict[str, Any]]:
    """Load results từ JSONL file"""
    records = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records

def extract_scores(records: List[Dict]) -> List[float]:
    """Extract scores từ records"""
    scores = []
    for record in records:
        try:
            result = record.get('result', {})
            if isinstance(result, dict):
                # Try different paths
                score = (result.get('summary', {}).get('score') or
                        result.get('taxonomy', {}).get('final_score') or
                        result.get('final_score'))
                if score is not None:
                    scores.append(float(score))
        except:
            pass
    return scores

def compute_stats(scores: List[float]) -> Dict[str, float]:
    """Compute statistics"""
    if not scores:
        return {}
    
    return {
        'mean': np.mean(scores),
        'std': np.std(scores),
        'median': np.median(scores),
        'min': np.min(scores),
        'max': np.max(scores),
        'q25': np.percentile(scores, 25),
        'q75': np.percentile(scores, 75),
    }

def print_header(text: str):
    """Print section header"""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def compare_files(without_examples: str, with_examples: str):
    """Compare two result files"""
    
    print_header("📊 CALIBRATION EXAMPLES - COMPARISON REPORT")
    
    # Load files
    print(f"📁 Loading WITHOUT examples: {without_examples}")
    records1 = load_results(without_examples)
    scores1 = extract_scores(records1)
    
    print(f"📁 Loading WITH examples:    {with_examples}")
    records2 = load_results(with_examples)
    scores2 = extract_scores(records2)
    
    print(f"✅ Loaded {len(scores1)} scores from WITHOUT")
    print(f"✅ Loaded {len(scores2)} scores from WITH")
    
    # Compute statistics
    stats1 = compute_stats(scores1)
    stats2 = compute_stats(scores2)
    
    print_header("📈 STATISTICS COMPARISON")
    
    metrics = ['mean', 'std', 'median', 'min', 'max', 'q25', 'q75']
    print(f"{'Metric':<12} {'WITHOUT Exs':<15} {'WITH Exs':<15} {'Δ (Diff)':<15}")
    print("-" * 57)
    
    for metric in metrics:
        val1 = stats1.get(metric, 0)
        val2 = stats2.get(metric, 0)
        delta = val2 - val1
        pct_change = (delta / val1 * 100) if val1 != 0 else 0
        
        print(f"{metric:<12} {val1:>14.2f} {val2:>14.2f} "
              f"{delta:>6.2f} ({pct_change:>6.1f}%)")
    
    # Distribution analysis
    print_header("📊 SCORE DISTRIBUTION")
    
    print(f"{'Score Range':<20} {'WITHOUT':<15} {'WITH':<15}")
    print("-" * 50)
    
    ranges = [(0, 2), (2, 4), (4, 6), (6, 8), (8, 10)]
    for low, high in ranges:
        count1 = sum(1 for s in scores1 if low <= s < high)
        count2 = sum(1 for s in scores2 if low <= s < high)
        pct1 = count1 / len(scores1) * 100 if scores1 else 0
        pct2 = count2 / len(scores2) * 100 if scores2 else 0
        
        print(f"{low}-{high} (out of 10): {count1:>3} ({pct1:>5.1f}%) | "
              f"{count2:>3} ({pct2:>5.1f}%)")
    
    # Statistical test
    print_header("📉 STATISTICAL ANALYSIS")
    
    # T-test
    if len(scores1) > 1 and len(scores2) > 1:
        t_stat, p_value = stats.ttest_ind(scores1, scores2)
        print(f"t-test:")
        print(f"  t-statistic: {t_stat:.4f}")
        print(f"  p-value:     {p_value:.4f}")
        if p_value < 0.05:
            print(f"  ✅ Significant difference (p < 0.05)")
        else:
            print(f"  ⚠️ No significant difference (p >= 0.05)")
    
    # Correlation with grade (if available)
    print(f"\n✅ Analysis complete!")
    
    # Recommendations
    print_header("💡 RECOMMENDATIONS")
    
    mean_change = stats2['mean'] - stats1['mean']
    std_change = stats2['std'] - stats1['std']
    
    print("📌 Interpretation:")
    print(f"  • Mean score changed by {mean_change:+.2f} points")
    if mean_change < 0:
        print(f"    → Scores are more realistic (lower, not inflated)")
    elif mean_change > 0:
        print(f"    → Scores are higher (less critical)")
    else:
        print(f"    → No significant change in average")
    
    print(f"  • Std deviation changed by {std_change:+.2f} points")
    if std_change > 0:
        print(f"    → More variance (wider range)")
    elif std_change < 0:
        print(f"    → Less variance (more consistent)")
    else:
        print(f"    → Similar variance")
    
    # Export summary
    summary = {
        'without_examples': stats1,
        'with_examples': stats2,
        'num_samples_without': len(scores1),
        'num_samples_with': len(scores2),
        'mean_change': mean_change,
        'std_change': std_change,
    }
    
    summary_file = Path(with_examples).parent / "comparison_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n✅ Summary saved to: {summary_file}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("""
Usage:
  python compare_results.py <without_examples.jsonl> <with_examples.jsonl>

Example:
  python compare_results.py baseline_no_exs.jsonl baseline_with_exs.jsonl
        """)
        sys.exit(1)
    
    without_examples = sys.argv[1]
    with_examples = sys.argv[2]
    
    compare_files(without_examples, with_examples)
