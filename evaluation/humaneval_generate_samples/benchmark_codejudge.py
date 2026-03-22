"""
Benchmark CodeJudge trên HumanEval Generated Samples dataset

Cách chạy:
    # Binary mode (nhanh)
    python benchmark_codejudge.py \
      --data_file ./data/python_test.jsonl \
      --limit 10 \
      --provider gemini \
      --model gemini-2.0-flash \
      --mode binary
    
    # Taxonomy mode (chi tiết)
    python benchmark_codejudge.py \
      --data_file ./data/python_test.jsonl \
      --provider gemini \
      --model gemini-2.5-flash \
      --mode taxonomy \
      --run-name test_humaneval \
      --resume \
      --stop-on-rate-limit

Format data file:
    JSONL format mỗi line:
    {
        "task_id": "Python/0",
        "prompt": "def has_close_elements(...)",
        "generation": "code here"
    }
"""

import json
import sys
import os
import argparse
from pathlib import Path
from tqdm import tqdm
from typing import Dict, List, Tuple, Optional
import math
import time

# Add repo root to path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from codejudge import IntegratedAssessor, BinaryAssessor, TaxonomyAssessor, LLMFactory


class HumanEvalGeneratedBenchmark:
    """Benchmark CodeJudge trên HumanEval Generated Samples"""
    
    # Map model prefix to provider
    MODEL_TO_PROVIDER = {
        "gpt-": "openai",
        "claude-": "anthropic",
        "gemini-": "gemini",
        "llama": "local",
        "mistral": "local",
    }
    
    @staticmethod
    def get_provider(model: str) -> str:
        """Get provider from model name"""
        for prefix, provider in HumanEvalGeneratedBenchmark.MODEL_TO_PROVIDER.items():
            if model.startswith(prefix) or model.contains(prefix):
                return provider
        return "gemini"  # Default to gemini
    
    def __init__(
        self,
        data_file: str,
        provider: str = "gemini",
        model: str = "gemini-2.0-flash",
        mode: str = "binary",
        run_name: Optional[str] = None,
        resume: bool = False,
        stop_on_rate_limit: bool = False,
        verbose: bool = False
    ):
        """
        Args:
            data_file: Path to JSONL data file
            provider: LLM provider (gemini, openai, anthropic, local)
            model: Model name
            mode: Assessment mode (binary, taxonomy, integrated)
            run_name: Run name for structured output
            resume: Resume from checkpoint
            stop_on_rate_limit: Stop on rate limit error
            verbose: Verbose output
        """
        self.data_file = data_file
        self.provider = provider
        self.model = model
        self.mode = mode
        self.run_name = run_name or f"{Path(data_file).stem}_{model.replace('/', '_')}"
        self.resume = resume
        self.stop_on_rate_limit = stop_on_rate_limit
        self.verbose = verbose
        
        # Create output directory
        self.output_dir = Path(__file__).parent / "output" / self.run_name
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.output_file = self.output_dir / f"{self.run_name}.jsonl"
        self.metrics_file = self.output_dir / f"{self.run_name}_metrics.json"
        self.checkpoint_file = self.output_dir / f"{self.run_name}_checkpoint.json"
        
        # Create LLM client
        try:
            self.llm_client = LLMFactory.create(provider=provider, model_name=model)
            if self.verbose:
                print(f"✓ Created {provider} client with model: {model}")
        except Exception as e:
            print(f"✗ Failed to create LLM client: {e}")
            raise
        
        # Create assessor
        if mode == "binary":
            self.assessor = BinaryAssessor(llm_client=self.llm_client)
        elif mode == "taxonomy":
            self.assessor = TaxonomyAssessor(llm_client=self.llm_client)
        elif mode == "integrated":
            self.assessor = IntegratedAssessor(llm_client=self.llm_client)
        else:
            raise ValueError(f"Unknown mode: {mode}")
    
    def load_checkpoint(self) -> int:
        """Load checkpoint and return processed count"""
        if not self.checkpoint_file.exists():
            return 0
        
        try:
            with open(self.checkpoint_file, "r") as f:
                checkpoint = json.load(f)
            processed_count = checkpoint.get("processed", 0)
            if self.verbose:
                print(f"✓ Loaded checkpoint: {processed_count} processed")
            return processed_count
        except Exception as e:
            print(f"Warning: Failed to load checkpoint: {e}")
            return 0
    
    def save_checkpoint(self, processed_count: int):
        """Save checkpoint"""
        try:
            with open(self.checkpoint_file, "w") as f:
                json.dump({"processed": processed_count}, f)
        except Exception as e:
            print(f"Warning: Failed to save checkpoint: {e}")
    
    def load_dataset(self) -> List[Dict]:
        """Load HumanEval generated samples từ JSONL file"""
        if not os.path.exists(self.data_file):
            raise FileNotFoundError(f"Data file not found: {self.data_file}")
        
        data = []
        with open(self.data_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    item = json.loads(line)
                    data.append(item)
                except json.JSONDecodeError as e:
                    print(f"Warning: Failed to parse line: {e}")
        
        if self.verbose:
            print(f"✓ Loaded {len(data)} samples from {os.path.basename(self.data_file)}")
        return data
    
    def run_benchmark(self, limit: Optional[int] = None) -> Dict:
        """
        Chạy benchmark với support resume và rate limit handling
        
        Args:
            limit: Số lượng sample (None = all)
            
        Returns:
            Kết quả benchmark
        """
        data = self.load_dataset()
        
        if limit:
            data = data[:limit]
        
        # Load checkpoint nếu resume
        start_index = 0
        if self.resume:
            start_index = self.load_checkpoint()
        
        results = {
            "provider": self.provider,
            "model": self.model,
            "mode": self.mode,
            "data_file": self.data_file,
            "run_name": self.run_name,
            "total": len(data),
            "start_index": start_index,
            "data": [],
            "metrics": {}
        }
        
        # Counters
        scores_list = []
        errors = 0
        
        print(f"\n{'='*70}")
        print(f"HumanEval Generated Benchmark")
        print(f"{'='*70}")
        print(f"Dataset: {os.path.basename(self.data_file)}")
        print(f"Provider: {self.provider} | Model: {self.model}")
        print(f"Mode: {self.mode}")
        print(f"Total Samples: {len(data)}")
        print(f"Resume from: {start_index}")
        print(f"Output Dir: {self.output_dir}")
        print(f"{'='*70}\n")
        
        # Open output file in append mode
        file_mode = "a" if self.resume and self.output_file.exists() else "w"
        
        with open(self.output_file, file_mode, encoding="utf-8") as f:
            for idx, item in enumerate(data[start_index:], start=start_index):
                try:
                    task_id = item.get("task_id", f"task_{idx}")
                    prompt = item.get("prompt", "")
                    generation = item.get("generation", "")
                    
                    # Skip if missing critical fields
                    if not prompt or not generation:
                        if self.verbose:
                            print(f"⚠️  Skipping {task_id}: missing prompt or generation")
                        errors += 1
                        continue
                    
                    # Assess code
                    result = self.assessor.assess(
                        problem_statement=prompt,
                        student_code=generation
                    )
                    
                    # Extract metrics based on mode
                    if self.mode == "binary":
                        score = 10.0 if result.get("passed", False) else 0.0
                        passed = 1 if score >= 5.0 else 0
                        grade = "A" if passed else "F"
                    elif self.mode == "taxonomy":
                        score = result.get("final_score", 0)
                        passed = 1 if score >= 5.0 else 0
                        grade = result.get("grade_letter", "F")
                    elif self.mode == "integrated":
                        score = result.get("summary", {}).get("score", 0)
                        grade = result.get("summary", {}).get("grade_letter", "F")
                        passed = 1 if score >= 5.0 else 0
                    else:
                        score = 0
                        grade = "F"
                        passed = 0
                    
                    scores_list.append(score)
                    
                    # Store result
                    record = {
                        "task_id": task_id,
                        "score": score,
                        "grade": grade,
                        "passed": passed,
                    }
                    
                    results["data"].append(record)
                    
                    # Show progress periodically
                    if (idx + 1) % 5 == 0:
                        print(f"Processed: {idx + 1}/{len(data)}")
                    
                    if self.verbose and idx < 2:
                        print(f"\n[{idx}] {task_id}: Score={score:.2f}, Grade={grade}")
                        
                except Exception as e:
                    errors += 1
                    
                    # Check if rate limit error
                    if isinstance(e, Exception) and ("429" in str(e) or "rate" in str(e).lower()):
                        print(f"\n⚠️  Rate limit hit at sample {idx}!")
                        if self.stop_on_rate_limit:
                            print(f"Stopping due to rate limit. Resume with:")
                            print(f"  python benchmark_codejudge.py --run-name {self.run_name} --resume --stop-on-rate-limit")
                            break
                    
                    record = {
                        "task_id": item.get("task_id", f"task_{idx}"),
                        "error": str(e)
                    }
                    results["data"].append(record)
                    
                    if self.verbose:
                        print(f"❌ Error on sample {idx}: {e}")
                
                # Write record to JSONL (both success and error)
                f.write(json.dumps(record) + "\n")
                f.flush()
                
                # Save checkpoint every 10 items
                if (idx + 1) % 10 == 0:
                    self.save_checkpoint(idx + 1)
        
        # Calculate metrics
        total_valid = len(data) - errors
        
        if total_valid > 0:
            avg_score = sum(scores_list) / len(scores_list) if scores_list else 0
            std_score = self._std_dev(scores_list) if len(scores_list) > 1 else 0
            
            grades = [r.get("grade", "F") for r in results["data"] if "grade" in r]
            grade_dist = {
                "A": grades.count("A"),
                "B": grades.count("B"),
                "C": grades.count("C"),
                "D": grades.count("D"),
                "F": grades.count("F"),
            }
            
            pass_rate = sum(1 for g in grades if g in ["A", "B", "C"]) / len(grades) if grades else 0
        else:
            avg_score = std_score = pass_rate = 0
            grade_dist = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
        
        results["metrics"] = {
            "total_samples": len(data),
            "processed": len(results["data"]),
            "valid": total_valid,
            "errors": errors,
            "avg_score": avg_score,
            "std_score": std_score,
            "pass_rate": pass_rate,
            "grade_distribution": grade_dist,
        }
        
        # Save metrics
        with open(self.metrics_file, "w") as f:
            json.dump(results["metrics"], f, indent=2)
        
        # Clean checkpoint on success
        if errors == 0 and self.checkpoint_file.exists():
            self.checkpoint_file.unlink()
        
        return results
    
    @staticmethod
    def _std_dev(values: List[float]) -> float:
        """Calculate standard deviation"""
        if len(values) < 2:
            return 0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return math.sqrt(variance)
    
    def print_results(self, results: Dict):
        """In kết quả"""
        metrics = results["metrics"]
        
        print(f"\n{'='*70}")
        print(f"BENCHMARK RESULTS")
        print(f"{'='*70}\n")
        
        print(f"Run Name: {results['run_name']}")
        print(f"Model: {results['model']} ({results['provider']})")
        print(f"Mode: {results['mode']}")
        print(f"Dataset: {os.path.basename(results['data_file'])}")
        print(f"Samples: {metrics['processed']}/{metrics['total_samples']}")
        print(f"Valid: {metrics['valid']} | Errors: {metrics['errors']}\n")
        
        print(f"Score Statistics:")
        print(f"  Average Score: {metrics['avg_score']:.2f}/10")
        print(f"  Std Dev:       {metrics['std_score']:.2f}")
        print(f"  Pass Rate:     {metrics['pass_rate']:.2%}\n")
        
        print(f"Grade Distribution:")
        for grade in ["A", "B", "C", "D", "F"]:
            count = metrics['grade_distribution'][grade]
            pct = (count / metrics['valid'] * 100) if metrics['valid'] > 0 else 0
            bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            print(f"  {grade}: {count:3d} ({pct:5.1f}%) {bar}")
        
        print(f"\nOutput Files:")
        print(f"  Results: {self.output_file}")
        print(f"  Metrics: {self.metrics_file}")
        print(f"\n{'='*70}\n")
        
    def load_dataset(self, data_file: str) -> List[Dict]:
        """
        Load HumanEval generated samples từ JSONL file
        
        Args:
            data_file: Path to JSONL file
            
        Returns:
            List of data items
        """
        if not os.path.exists(data_file):
            raise FileNotFoundError(f"Data file not found: {data_file}")
        
        data = []
        with open(data_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    item = json.loads(line)
                    data.append(item)
                except json.JSONDecodeError as e:
                    print(f"Warning: Failed to parse line: {e}")
                    continue
        
        if self.verbose:
            print(f"✓ Loaded {len(data)} samples from {data_file}")
            
        return data
    
    def run_benchmark(self, data_file: str, limit: int = None) -> Dict:
        """
        Chạy benchmark
        
        Args:
            data_file: Path to JSONL file
            limit: Số lượng sample (None = all)
            
        Returns:
            Kết quả benchmark
        """
        data = self.load_dataset(data_file)
        
        if limit:
            data = data[:limit]
        
        results = {
            "model": self.model,
            "mode": self.mode,
            "data_file": data_file,
            "total": len(data),
            "data": [],
            "metrics": {}
        }
        
        # Counters
        correct = 0
        tp = 0  # Both say pass
        tn = 0  # Both say fail
        fp = 0  # Predicted pass but no reference
        fn = 0  # Predicted fail but no reference
        errors = 0
        
        # For correlation analysis
        scores_list = []
        
        print(f"\n{'='*70}")
        print(f"Benchmarking: {os.path.basename(data_file)}")
        print(f"Model: {self.model}")
        print(f"Mode: {self.mode}")
        print(f"Total Samples: {len(data)}")
        print(f"{'='*70}\n")
        
        for idx, item in enumerate(tqdm(data, desc="Processing")):
            try:
                task_id = item.get("task_id", f"task_{idx}")
                prompt = item.get("prompt", "")
                generation = item.get("generation", "")
                
                # Skip if missing critical fields
                if not prompt or not generation:
                    if self.verbose:
                        print(f"⚠️  Skipping {task_id}: missing prompt or generation")
                    errors += 1
                    continue
                
                # Assess code
                result = self.assessor.assess(
                    problem_statement=prompt,
                    student_code=generation
                )
                
                # Extract metrics based on mode
                if self.mode == "binary":
                    predicted_pass = 1 if result.get("passed", False) else 0
                    score = 10.0 if predicted_pass else 0.0
                    grade = "A" if predicted_pass else "F"
                elif self.mode == "taxonomy":
                    score = result.get("final_score", 0)
                    predicted_pass = 1 if score >= 5.0 else 0
                    grade = result.get("grade_letter", "F")
                elif self.mode == "integrated":
                    score = result.get("summary", {}).get("score", 0)
                    grade = result.get("summary", {}).get("grade_letter", "F")
                    predicted_pass = 1 if score >= 5.0 else 0
                else:
                    score = 0
                    grade = "F"
                    predicted_pass = 0
                
                scores_list.append(score)
                
                # Store result
                record = {
                    "task_id": task_id,
                    "score": score,
                    "grade": grade,
                    "passed": predicted_pass,
                }
                
                results["data"].append(record)
                
                if self.verbose and idx < 3:
                    print(f"\n[{idx}] Task: {task_id}")
                    print(f"    Score: {score:.2f}/10")
                    print(f"    Grade: {grade}")
                    
            except Exception as e:
                errors += 1
                record = {
                    "task_id": item.get("task_id", f"task_{idx}"),
                    "error": str(e)
                }
                results["data"].append(record)
                if self.verbose:
                    print(f"❌ Error on {item.get('task_id')}: {e}")
        
        # Calculate metrics
        total_valid = len(data) - errors
        
        if total_valid > 0:
            avg_score = sum(scores_list) / len(scores_list) if scores_list else 0
            std_score = self._std_dev(scores_list) if len(scores_list) > 1 else 0
            
            grades = [r.get("grade", "F") for r in results["data"] if "grade" in r]
            grade_dist = {
                "A": grades.count("A"),
                "B": grades.count("B"),
                "C": grades.count("C"),
                "D": grades.count("D"),
                "F": grades.count("F"),
            }
            
            pass_rate = sum(1 for g in grades if g in ["A", "B", "C"]) / len(grades) if grades else 0
        else:
            avg_score = std_score = pass_rate = 0
            grade_dist = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
        
        results["metrics"] = {
            "total_processed": len(data),
            "total_valid": total_valid,
            "errors": errors,
            "avg_score": avg_score,
            "std_score": std_score,
            "pass_rate": pass_rate,
            "grade_distribution": grade_dist,
        }
        
        return results
    
    def _std_dev(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if len(values) < 2:
            return 0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return math.sqrt(variance)
    
    def print_results(self, results: Dict):
        """In kết quả"""
        metrics = results["metrics"]
        
        print(f"\n{'='*70}")
        print(f"BENCHMARK RESULTS")
        print(f"{'='*70}\n")
        
        print(f"Dataset: {os.path.basename(results['data_file'])}")
        print(f"Model: {results['model']}")
        print(f"Mode: {results['mode']}")
        print(f"Total Samples: {metrics['total_processed']}")
        print(f"Valid: {metrics['total_valid']} | Errors: {metrics['errors']}\n")
        
        print(f"Score Statistics:")
        print(f"  Average Score: {metrics['avg_score']:.2f}/10")
        print(f"  Std Dev:       {metrics['std_score']:.2f}")
        print(f"  Pass Rate:     {metrics['pass_rate']:.2%}\n")
        
        print(f"Grade Distribution:")
        for grade in ["A", "B", "C", "D", "F"]:
            count = metrics['grade_distribution'][grade]
            pct = (count / metrics['total_valid'] * 100) if metrics['total_valid'] > 0 else 0
            bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            print(f"  {grade}: {count:3d} ({pct:5.1f}%) {bar}")
        
        print(f"\n{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(description="Benchmark CodeJudge on HumanEval Generated Samples")
    parser.add_argument("--data_file", type=str, default="./data/python_test.jsonl",
                       help="Path to JSONL data file (default: ./data/python_test.jsonl)")
    parser.add_argument("--limit", type=int, default=None,
                       help="Limit number of samples (default: None = all)")
    parser.add_argument("--provider", type=str, default="gemini",
                       choices=["gemini", "openai", "anthropic", "local"],
                       help="LLM provider (default: gemini)")
    parser.add_argument("--model", type=str, default="gemini-2.0-flash",
                       help="Model name (default: gemini-2.0-flash)")
    parser.add_argument("--mode", type=str, default="binary",
                       choices=["binary", "taxonomy", "integrated"],
                       help="Assessment mode (default: binary)")
    parser.add_argument("--run-name", type=str, default=None,
                       help="Run name for output (default: auto-generated)")
    parser.add_argument("--resume", action="store_true",
                       help="Resume from checkpoint")
    parser.add_argument("--stop-on-rate-limit", action="store_true",
                       help="Stop on rate limit (429) error")
    parser.add_argument("--verbose", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    # Create benchmark
    benchmark = HumanEvalGeneratedBenchmark(
        data_file=args.data_file,
        provider=args.provider,
        model=args.model,
        mode=args.mode,
        run_name=args.run_name,
        resume=args.resume,
        stop_on_rate_limit=args.stop_on_rate_limit,
        verbose=args.verbose
    )
    
    # Run benchmark
    results = benchmark.run_benchmark(data_file=args.data_file, limit=args.limit)
    
    # Print results
    benchmark.print_results(results)


if __name__ == "__main__":
    main()
