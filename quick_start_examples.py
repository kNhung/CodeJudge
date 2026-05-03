#!/usr/bin/env python3
"""
QUICK START - Calibration Examples Library

Chạy script này để:
1. Xem ví dụ calibration
2. Test integration
3. So sánh kết quả (WITH vs WITHOUT examples)
"""

import subprocess
import sys
import json
from pathlib import Path

def run_command(cmd: str, description: str):
    """Chạy command và log"""
    print(f"\n{'='*70}")
    print(f"▶️  {description}")
    print(f"{'='*70}")
    print(f"$ {cmd}\n")
    
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0

def main():
    print("""
╔════════════════════════════════════════════════════════════════════╗
║                 📚 CALIBRATION EXAMPLES - QUICK START              ║
╚════════════════════════════════════════════════════════════════════╝
    """)
    
    repo_root = Path(__file__).resolve().parent
    
    # Step 1: Test examples library
    print("\n📌 STEP 1: Test Examples Library")
    success = run_command(
        "python -m codejudge.tests.test_examples_library",
        "Kiểm tra examples library"
    )
    if not success:
        print("❌ Failed to test examples library")
        return False
    
    # Step 2: Run with small dataset (NO examples)
    print("\n📌 STEP 2: Baseline Run (NO examples)")
    print("Chạy evaluation trên 10 mẫu mà KHÔNG dùng calibration examples")
    
    success = run_command(
        "python evaluation/conala/score_conala.py "
        "--source baseline --limit 10 --mode taxonomy",
        "Baseline: Without Calibration Examples"
    )
    if not success:
        print("⚠️ Baseline run failed (có thể là do setup)")
    
    # Step 3: Run with examples
    print("\n📌 STEP 3: With Calibration Examples")
    print("Chạy evaluation trên 10 mẫu dùng calibration examples")
    
    success = run_command(
        "python evaluation/conala/score_conala.py "
        "--source baseline --limit 10 --mode taxonomy --use-examples --num-examples 2",
        "With Calibration Examples"
    )
    if not success:
        print("⚠️ With-examples run failed")
    
    # Summary
    print(f"\n{'='*70}")
    print("✅ QUICK START COMPLETED!")
    print(f"{'='*70}")
    print("""
📚 Next Steps:

1. 🔍 EXPLORE EXAMPLES
   python -c "from codejudge.core.examples_library import CALIBRATION_EXAMPLES; \
   import json; print(json.dumps(CALIBRATION_EXAMPLES, indent=2, ensure_ascii=False))"

2. 📊 RUN FULL EVALUATION
   # Without examples (baseline)
   python evaluation/conala/score_conala.py --source all --limit 100
   
   # With examples
   python evaluation/conala/score_conala.py --source all --limit 100 --use-examples

3. 📈 COMPARE RESULTS
   python -c "
   import json
   # Load both results and compare metrics
   with open('output1.jsonl') as f1, open('output2.jsonl') as f2:
       scores1 = [json.loads(l)['result']['summary']['score'] for l in f1]
       scores2 = [json.loads(l)['result']['summary']['score'] for l in f2]
   print(f'Mean WITHOUT examples: {sum(scores1)/len(scores1):.2f}')
   print(f'Mean WITH examples:    {sum(scores2)/len(scores2):.2f}')
   "

4. 📖 READ DOCS
   cat EXAMPLES_LIBRARY_README.md

5. ➕ ADD MORE EXAMPLES
   Edit: codejudge/core/examples_library.py
   Add your own problem with 8-10 examples (0-10 score range)

📞 For more info: 
   See EXAMPLES_LIBRARY_README.md
    """)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
