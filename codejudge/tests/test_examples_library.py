"""
Test Script - Kiểm tra Calibration Examples Library

Sử dụng để:
1. Xem các ví dụ calibration
2. So sánh model output với ground truth
3. Measure improvement khi sử dụng examples
"""

import sys
import json
from pathlib import Path

# Add parent to path
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from codejudge.core.examples_library import (
    get_calibration_examples,
    format_examples_for_prompt,
    get_score_distribution
)

def print_section(title: str):
    """In header section"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def test_view_examples():
    """Test 1: Xem các ví dụ"""
    print_section("TEST 1: Xem Calibration Examples")
    
    problem_data = get_calibration_examples("all_elements_same")
    print(f"✅ Problem: {problem_data['problem']}\n")
    print(f"📊 Total examples: {len(problem_data['examples'])}")
    
    # Phân bố điểm
    dist = get_score_distribution("all_elements_same")
    print(f"\n📈 Score Distribution:")
    for score, count in sorted(dist.items(), reverse=True):
        bar = "█" * int(count * 5)
        print(f"   {score:5.1f}/10: {bar} ({count})")

def test_format_examples():
    """Test 2: Format examples cho prompt"""
    print_section("TEST 2: Format Examples for Few-Shot Learning")
    
    formatted = format_examples_for_prompt("all_elements_same", num_examples=2)
    print(formatted[:1000])  # Print first 1000 chars
    print(f"\n... (cắt ngắn, toàn bộ độ dài: {len(formatted)} ký tự)")

def test_compare_scores():
    """Test 3: So sánh điểm các ví dụ"""
    print_section("TEST 3: Score Breakdown Analysis")
    
    examples_data = get_calibration_examples("all_elements_same")
    examples = examples_data["examples"]
    
    print(f"{'Score':<8} {'Idea':<6} {'Flow':<6} {'Syntax':<7} {'Correct':<8} {'Clarity':<7} Reasoning")
    print("-" * 90)
    
    for example in sorted(examples, key=lambda x: x["expected_score"], reverse=True):
        breakdown = example["score_breakdown"]
        score = example["expected_score"]
        reason_short = example["reasoning"].split("\n")[0][:30]
        
        print(f"{score:<8.1f} {breakdown['idea']:<6.1f} {breakdown['flow']:<6.1f} "
              f"{breakdown['syntax_execution']:<7.1f} {breakdown['correctness']:<8.1f} "
              f"{breakdown['clarity']:<7.1f} {reason_short}")

def test_prompt_integration():
    """Test 4: Integration test - Kiểm tra prompt format"""
    print_section("TEST 4: Prompt Integration (Mock)")
    
    from codejudge.core.prompts import PromptTemplates
    
    problem = "Kiểm tra xem tất cả phần tử có giống nhau không?"
    code = "return all(x == lst[0] for x in lst)"
    
    # Format with examples
    prompt_with_examples = PromptTemplates.format_taxonomy_with_examples(
        problem_statement=problem,
        student_code=code,
        reference_code=None,
        language="Python",
        include_examples=True,
        num_examples=2
    )
    
    print(f"✅ Prompt generated with examples:")
    print(f"   Length: {len(prompt_with_examples)} characters")
    print(f"   Contains examples: {'CALIBRATION EXAMPLES' in prompt_with_examples}")
    print(f"\n📝 First 500 characters:")
    print(prompt_with_examples[:500])

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("  📚 CALIBRATION EXAMPLES LIBRARY - TEST SUITE")
    print("="*70)
    
    tests = [
        ("View Examples", test_view_examples),
        ("Format Examples", test_format_examples),
        ("Compare Scores", test_compare_scores),
        ("Prompt Integration", test_prompt_integration),
    ]
    
    for i, (name, test_func) in enumerate(tests, 1):
        try:
            test_func()
            print(f"\n✅ Test {i} ({name}): PASSED")
        except Exception as e:
            print(f"\n❌ Test {i} ({name}): FAILED - {e}")
            import traceback
            traceback.print_exc()
    
    print_section("📊 SUMMARY")
    print("✅ All tests completed!")
    print("\n💡 Next Steps:")
    print("1. Chạy với examples: --use-examples flag")
    print("2. So sánh metrics trước/sau")
    print("3. Thêm ví dụ cho các problem khác")

if __name__ == "__main__":
    main()
