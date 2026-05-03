"""
Bộ Thư Viện Ví Dụ Calibration (Examples Library)

Sử dụng few-shot learning để giúp LLM chấm điểm chính xác và nhất quán.
Mỗi ví dụ bao gồm:
- problem: Đề bài
- code: Code của sinh viên
- expected_score: Điểm kỳ vọng (0-10)
- score_breakdown: Chi tiết điểm từng tiêu chí
- reasoning: Giải thích cách chấm
"""

# ============================================================================
# CALIBRATION EXAMPLES - Các ví dụ để model học cách chấm
# ============================================================================

CALIBRATION_EXAMPLES = {
    "all_elements_same": {
        "problem": "Viết hàm kiểm tra xem tất cả phần tử trong danh sách có giống nhau không?",
        "examples": [
            {
                "code": """def check_all_same(lst):
    if not lst:
        return True
    return all(x == lst[0] for x in lst)""",
                "expected_score": 10,
                "score_breakdown": {
                    "idea": 3.0,
                    "flow": 2.0,
                    "syntax_execution": 2.0,
                    "correctness": 2.0,
                    "clarity": 1.0
                },
                "reasoning": "✅ PERFECT: Logic đúng, xử lý edge case (list rỗng), code rõ ràng"
            },
            {
                "code": """def check_all_same(lst):
    for i in range(len(lst)-1):
        if lst[i] != lst[i+1]:
            return False
    return True""",
                "expected_score": 8.5,
                "score_breakdown": {
                    "idea": 3.0,
                    "flow": 2.0,
                    "syntax_execution": 1.5,
                    "correctness": 1.5,
                    "clarity": 0.5
                },
                "reasoning": "✅ GOOD: Logic chính đúng nhưng có vấn đề:\n- ❌ Không xử lý list rỗng (sẽ fail)\n- ❌ Không xử lý list 1 phần tử (sẽ lỗi index)\n- ⚠️ Code thiếu readable (dùng loop thay vì built-in)"
            },
            {
                "code": """def check_all_same(lst):
    return len(set(lst)) <= 1""",
                "expected_score": 9.0,
                "score_breakdown": {
                    "idea": 3.0,
                    "flow": 2.0,
                    "syntax_execution": 2.0,
                    "correctness": 1.5,
                    "clarity": 0.5
                },
                "reasoning": "✅ GOOD: Ý tưởng tuyệt vời (dùng set), xử lý được list rỗng\n- ✅ Code ngắn gọn, Pythonic\n- ⚠️ Dữ liệu large → set() tốn bộ nhớ\n- ⚠️ Code hơi trừu tượng (không dễ hiểu cho người mới)"
            },
            {
                "code": """def check_all_same(lst):
    if len(lst) == 0:
        return True
    first = lst[0]
    for item in lst:
        if item != first:
            return False
    return True""",
                "expected_score": 8.0,
                "score_breakdown": {
                    "idea": 3.0,
                    "flow": 1.5,
                    "syntax_execution": 2.0,
                    "correctness": 2.0,
                    "clarity": -0.5
                },
                "reasoning": "✅ GOOD: Logic chính đúng, xử lý edge case rõ ràng\n- ✅ Dễ hiểu cho người mới\n- ⚠️ Dài dòng, có thể refactor\n- ⚠️ Kiểm tra len() trước là thừa thải (loop xử lý được)"
            },
            {
                "code": """def check_all_same(lst):
    for i in range(len(lst)):
        for j in range(i+1, len(lst)):
            if lst[i] != lst[j]:
                return False
    return True""",
                "expected_score": 5.5,
                "score_breakdown": {
                    "idea": 2.0,
                    "flow": 1.0,
                    "syntax_execution": 2.0,
                    "correctness": 0.5,
                    "clarity": 0.0
                },
                "reasoning": "⚠️ AVERAGE: Logic có vấn đề\n- ❌ Dùng nested loop O(n²) - quá phức tạp\n- ❌ Code khó hiểu\n- ✅ Tuy nhiên logic vẫn đúng (so sánh từng cặp)\n- ⚠️ Hiệu năng tồi"
            },
            {
                "code": """def check_all_same(lst):
    return len(set(lst)) == 1""",
                "expected_score": 4.0,
                "score_breakdown": {
                    "idea": 1.5,
                    "flow": 1.5,
                    "syntax_execution": 1.5,
                    "correctness": 0.0,
                    "clarity": 1.0
                },
                "reasoning": "❌ POOR: Logic sai\n- ❌ set(lst) != 1 khi list rỗng (set([]) độ dài 0, không 1)\n- ❌ Không xử lý được empty list\n- ❌ Kết quả sai\n- ⚠️ Mặc dù code Pythonic nhưng sai logic"
            },
            {
                "code": """def check_all_same(lst):
    if lst == []:
        return True
    x = lst[0]
    while lst:
        if lst[0] == x:
            lst.pop(0)
        else:
            return False
    return True""",
                "expected_score": 3.5,
                "score_breakdown": {
                    "idea": 1.0,
                    "flow": 1.0,
                    "syntax_execution": 1.0,
                    "correctness": 0.0,
                    "clarity": 0.0
                },
                "reasoning": "❌ POOR: Nhiều vấn đề\n- ❌ Modify input list (side effect tệ)\n- ⚠️ Logic hơi phức tạp cho bài toán đơn giản\n- ✅ Logic bản chất vẫn đúng nhưng cách làm rất xấu\n- ❌ Hiệu năng O(n²) do pop(0)"
            },
            {
                "code": """def check_all_same(lst):
    [x for x in lst]""",
                "expected_score": 0.0,
                "score_breakdown": {
                    "idea": 0.0,
                    "flow": 0.0,
                    "syntax_execution": 1.0,
                    "correctness": 0.0,
                    "clarity": 0.0
                },
                "reasoning": "❌ ZERO: Không giải quyết được vấn đề\n- ❌ Không có return statement\n- ❌ Chỉ tạo list, không kiểm tra gì\n- ❌ Hoàn toàn lệch đề\n- ✅ Syntax đúng nhưng logic chưa implement"
            },
            {
                "code": """def check_all_same(lst):
    return undefined_function(lst)""",
                "expected_score": 0.0,
                "score_breakdown": {
                    "idea": 0.0,
                    "flow": 0.0,
                    "syntax_execution": 0.0,
                    "correctness": 0.0,
                    "clarity": 0.0
                },
                "reasoning": "❌ ZERO: Không thể chạy\n- ❌ Gọi hàm undefined (NameError)\n- ❌ Runtime error\n- ❌ Không có implementation\n- ❌ Hoàn toàn không giải quyết bài toán"
            },
            {
                "code": """return all equal""",
                "expected_score": 0.0,
                "score_breakdown": {
                    "idea": 0.0,
                    "flow": 0.0,
                    "syntax_execution": 0.0,
                    "correctness": 0.0,
                    "clarity": 0.0
                },
                "reasoning": "❌ ZERO: Syntax error\n- ❌ Không phải function definition\n- ❌ Lệch đề hoàn toàn\n- ❌ Không thể chạy"
            }
        ]
    },
    
    # Có thể thêm nhiều problem khác ở đây
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_calibration_examples(problem_key: str = None) -> dict:
    """
    Lấy ví dụ calibration cho một bài toán
    
    Args:
        problem_key: Khóa của bài toán (e.g., "all_elements_same")
                    Nếu None, lấy all examples
    
    Returns:
        Dict chứa examples
    """
    if problem_key is None:
        return CALIBRATION_EXAMPLES
    
    if problem_key not in CALIBRATION_EXAMPLES:
        raise ValueError(f"Problem key '{problem_key}' not found. Available: {list(CALIBRATION_EXAMPLES.keys())}")
    
    return CALIBRATION_EXAMPLES[problem_key]


def format_examples_for_prompt(problem_key: str, num_examples: int = 3) -> str:
    """
    Format examples để thêm vào prompt (few-shot learning)
    
    Args:
        problem_key: Khóa bài toán
        num_examples: Số lượng ví dụ (sắp xếp từ tốt → xấu để model học)
    
    Returns:
        String chứa formatted examples để dùng trong prompt
    """
    examples_data = get_calibration_examples(problem_key)
    problem = examples_data["problem"]
    examples = examples_data["examples"]
    
    # Sắp xếp: 10 → 0 (từ tốt đến xấu)
    sorted_examples = sorted(examples, key=lambda x: x["expected_score"], reverse=True)
    selected = sorted_examples[:num_examples]
    
    formatted = f"""CALIBRATION EXAMPLES cho bài toán: {problem}
Dùng các ví dụ này để hiểu cách chấm điểm chính xác:

"""
    
    for i, example in enumerate(selected, 1):
        formatted += f"""[Ví dụ {i} - Điểm {example['expected_score']}/10]
Code:
```python
{example['code']}
```

Scoring:
- Ý tưởng (idea): {example['score_breakdown']['idea']}/3
- Luồng xử lý (flow): {example['score_breakdown']['flow']}/2
- Cú pháp/Chạy (syntax): {example['score_breakdown']['syntax_execution']}/2
- Tính đúng (correctness): {example['score_breakdown']['correctness']}/2
- Clarity: {example['score_breakdown']['clarity']}/1

Reasoning: {example['reasoning']}

---

"""
    
    return formatted


def get_score_distribution(problem_key: str) -> dict:
    """
    Thống kê phân bố điểm từ examples
    
    Returns:
        Dict với count theo điểm
    """
    examples_data = get_calibration_examples(problem_key)
    examples = examples_data["examples"]
    
    distribution = {}
    for example in examples:
        score = example["expected_score"]
        if score not in distribution:
            distribution[score] = 0
        distribution[score] += 1
    
    return dict(sorted(distribution.items(), reverse=True))


if __name__ == "__main__":
    # Test
    print("📚 Calibration Examples Library")
    print("=" * 60)
    
    for problem_key in CALIBRATION_EXAMPLES.keys():
        print(f"\n📌 Problem: {problem_key}")
        dist = get_score_distribution(problem_key)
        print(f"   Distribution: {dist}")
        
        # In 2 ví dụ tốt nhất
        print("\n   Ví dụ few-shot:")
        print(format_examples_for_prompt(problem_key, num_examples=2))
