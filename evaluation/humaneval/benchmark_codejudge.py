"""
Benchmark CodeJudge trên HumanEval-X dataset

Cách chạy:
    python benchmark_codejudge.py --test_case python-small-test --limit 10 --model gpt-3.5-turbo-1106

Parameters:
    --test_case: Tên test case (e.g., python-small-test, cpp-small-test)
    --limit: Số lượng sample để test (default: None = all)
    --model: LLM model (gpt-3.5-turbo-1106, gpt-4, etc.)
    --output: Output file path
    --verbose: Chi tiết output
"""

import json
import sys
import os
import argparse
from pathlib import Path
from tqdm import tqdm
from typing import Dict, List, Tuple

# Add repo root to path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from codejudge import IntegratedAssessor


class HumanEvalBenchmark:
    """Benchmark CodeJudge trên HumanEval dataset"""
    
    def __init__(self, model: str = "gpt-3.5-turbo-1106", verbose: bool = False):
        """
        Args:
            model: LLM model name
            verbose: In chi tiết
        """
        self.model = model
        self.verbose = verbose
        self.assessor = IntegratedAssessor(model=model)
        
    def load_dataset(self, test_case: str) -> Tuple[List[Dict], List[Dict]]:
        """
        Load HumanEval dataset
        
        Args:
            test_case: Test case name (e.g., "python-small-test")
            
        Returns:
            (test_data, dataset_info)
        """
        language = test_case.split("-")[0]
        
        # Load test cases
        test_file = f"./data/humaneval/test_cases/{test_case}.jsonl"
        if not os.path.exists(test_file):
            raise FileNotFoundError(f"Test file not found: {test_file}")
            
        test_data = []
        with open(test_file, "r") as f:
            for line in f:
                test_data.append(json.loads(line))
        
        # Load dataset info
        dataset_file = f"./data/humaneval/dataset/{language}.json"
        if not os.path.exists(dataset_file):
            raise FileNotFoundError(f"Dataset file not found: {dataset_file}")
            
        with open(dataset_file, "r") as f:
            dataset = json.load(f)
        
        if self.verbose:
            print(f"✓ Loaded {len(test_data)} test cases")
            print(f"✓ Dataset has {len(dataset)} problems")
            
        return test_data, dataset
    
    def run_benchmark(self, test_case: str, limit: int = None) -> Dict:
        """
        Chạy benchmark
        
        Args:
            test_case: Test case name
            limit: Số lượng sample (None = all)
            
        Returns:
            Kết quả benchmark
        """
        test_data, dataset = self.load_dataset(test_case)
        
        if limit:
            test_data = test_data[:limit]
        
        results = {
            "model": self.model,
            "test_case": test_case,
            "total": len(test_data),
            "data": [],
            "metrics": {}
        }
        
        # Counters
        correct = 0  # CodeJudge prediction == actual pass
        tp = 0  # True Positive: both say pass
        tn = 0  # True Negative: both say fail
        fp = 0  # False Positive: CodeJudge says pass, actual fail
        fn = 0  # False Negative: CodeJudge says fail, actual pass
        errors = 0
        
        print(f"\n{'='*70}")
        print(f"Testing on {test_case} (limit={limit or 'all'})")
        print(f"Model: {self.model}")
        print(f"{'='*70}\n")
        
        for idx, test_item in enumerate(tqdm(test_data, desc="Benchmarking")):
            try:
                question_id = test_item["question_id"]
                program = test_item["program"]
                actual_pass = test_item.get("pass", 0)
                
                # Get problem info
                problem_info = dataset[question_id]
                prompt = problem_info["prompt"]
                canonical_solution = problem_info["canonical_solution"]
                
                # Assess with CodeJudge
                result = self.assessor.assess(
                    problem_statement=prompt,
                    student_code=program,
                    reference_code=canonical_solution
                )
                
                # Extract prediction
                predicted_pass = 1 if result['summary']['status'] == 'PASS' else 0
                
                # Store result
                record = {
                    "question_id": question_id,
                    "actual_pass": actual_pass,
                    "predicted_pass": predicted_pass,
                    "score": result['summary']['score'],
                    "grade": result['summary']['grade_letter'],
                    "binary_result": result['binary']['result'] if 'binary' in result else None,
                }
                
                results["data"].append(record)
                
                # Calculate metrics
                if predicted_pass == actual_pass:
                    correct += 1
                    
                if predicted_pass == 1 and actual_pass == 1:
                    tp += 1
                elif predicted_pass == 0 and actual_pass == 0:
                    tn += 1
                elif predicted_pass == 1 and actual_pass == 0:
                    fp += 1
                elif predicted_pass == 0 and actual_pass == 1:
                    fn += 1
                
                if self.verbose and idx < 3:
                    print(f"\n[{idx}] Question: {question_id}")
                    print(f"    Actual: {'PASS' if actual_pass else 'FAIL'}")
                    print(f"    Predicted: {'PASS' if predicted_pass else 'FAIL'}")
                    print(f"    Score: {result['summary']['score']:.2f}/10")
                    print(f"    Grade: {result['summary']['grade_letter']}")
                    
            except Exception as e:
                errors += 1
                record = {
                    "question_id": test_item.get("question_id", "unknown"),
                    "error": str(e)
                }
                results["data"].append(record)
                if self.verbose:
                    print(f"Error on {test_item.get('question_id')}: {e}")
        
        # Calculate metrics
        total_valid = len(test_data) - errors
        
        if total_valid > 0:
            accuracy = correct / total_valid
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        else:
            accuracy = precision = recall = f1 = 0
        
        results["metrics"] = {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "tp": tp,
            "tn": tn,
            "fp": fp,
            "fn": fn,
            "errors": errors,
            "correct": correct,
            "total_valid": total_valid,
        }
        
        return results
    
    def print_results(self, results: Dict):
        """In kết quả"""
        metrics = results["metrics"]
        
        print(f"\n{'='*70}")
        print(f"BENCHMARK RESULTS")
        print(f"{'='*70}\n")
        
        print(f"Test Case: {results['test_case']}")
        print(f"Model: {results['model']}")
        print(f"Total Samples: {results['total']}")
        print(f"Valid: {metrics['total_valid']} | Errors: {metrics['errors']}\n")
        
        print(f"Metrics:")
        print(f"  Accuracy:  {metrics['accuracy']:.2%}")
        print(f"  Precision: {metrics['precision']:.2%}")
        print(f"  Recall:    {metrics['recall']:.2%}")
        print(f"  F1 Score:  {metrics['f1']:.4f}\n")
        
        print(f"Confusion Matrix:")
        print(f"  TP (True Positive):   {metrics['tp']:3d}")
        print(f"  TN (True Negative):   {metrics['tn']:3d}")
        print(f"  FP (False Positive):  {metrics['fp']:3d}")
        print(f"  FN (False Negative):  {metrics['fn']:3d}")
        print(f"\n  Correct: {metrics['correct']}/{metrics['total_valid']} = {metrics['correct']/metrics['total_valid']:.2%}")
        print(f"\n{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(description="Benchmark CodeJudge on HumanEval")
    parser.add_argument("--test_case", type=str, default="python-small-test",
                       help="Test case name (default: python-small-test)")
    parser.add_argument("--limit", type=int, default=None,
                       help="Limit number of samples (default: None = all)")
    parser.add_argument("--model", type=str, default="gpt-3.5-turbo-1106",
                       help="LLM model (default: gpt-3.5-turbo-1106)")
    parser.add_argument("--output", type=str, default=None,
                       help="Output JSON file (default: None = don't save)")
    parser.add_argument("--verbose", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    # Create benchmark
    benchmark = HumanEvalBenchmark(model=args.model, verbose=args.verbose)
    
    # Run benchmark
    results = benchmark.run_benchmark(
        test_case=args.test_case,
        limit=args.limit
    )
    
    # Print results
    benchmark.print_results(results)
    
    # Save results
    if args.output:
        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"✓ Results saved to {args.output}\n")


if __name__ == "__main__":
    main()
