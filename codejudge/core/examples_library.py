"""
Bộ Thư Viện Ví Dụ Calibration (Examples Library)

Sử dụng few-shot learning để giúp LLM chấm điểm chính xác và nhất quán.
Mỗi ví dụ bao gồm:
- code: Code của sinh viên
- expected_score: Điểm kỳ vọng (0-10) dựa theo logic thuật toán thuần túy
- score_breakdown: Chi tiết điểm 3 tiêu chí mới (Tổng = 10)
- reasoning: Giải thích cách chấm và nhấn mạnh việc bỏ qua lỗi khoảng trắng/typo định dạng
"""

# ============================================================================
# CALIBRATION EXAMPLES - Các ví dụ để model học cách chấm
# ============================================================================

CALIBRATION_EXAMPLES = {
    "sorting_by_two_criteria": {
        "problem": "Sorting a Python list by two criteria (Sắp xếp một danh sách Python theo hai tiêu chí).",
        "examples": [
            {
                "code": """sorted(list, key=lambda x: (x[0], -x[1]))""",
                "expected_score": 10.0,
                "score_breakdown": {
                    "idea": 4.0,
                    "flow": 3.0,
                    "correctness": 3.0
                },
                "reasoning": "PERFECT: Giải quyết xuất sắc bài toán. Sử dụng một tuple trong hàm lambda để định nghĩa chính xác cả hai tiêu chí sắp xếp (tiêu chí 1 tăng dần, tiêu chí 2 giảm dần)."
            },
            {
                "code": """sorted(x, cmp=lambda a, b: cmp(a[1], b[1]), key=lambda a: a[0])""",
                "expected_score": 8.0,
                "score_breakdown": {
                    "idea": 3.5,
                    "flow": 2.5,
                    "correctness": 2.0
                },
                "reasoning": "GOOD: Ý tưởng tốt, cố gắng giải quyết bằng cả tham số `cmp` và `key` để đạt 2 tiêu chí. Mặc dù `cmp` đã bị loại bỏ ở Python 3 (chỉ chạy ở Python 2) nhưng về mặt logic thuật toán thuần túy, học viên vẫn hiểu cách xử lý đa tiêu chí. Đánh giá ở mức Khá (Tương đương Grade 4/4 của một số hệ thống cũ)."
            },
            {
                "code": """sorted(l,key = lambda x:x [1])""",
                "expected_score": 5.0,
                "score_breakdown": {
                    "idea": 2.5,
                    "flow": 1.5,
                    "correctness": 1.0
                },
                "reasoning": "AVERAGE (Bản chất giống baseline/best-tranx): Có 2 vấn đề cần lưu ý:\n1. Về logic: Chỉ mới đáp ứng được 1 tiêu chí sắp xếp (`x[1]`), chưa giải quyết được yêu cầu 'two criteria' của đề bài. Do đó điểm logic chỉ ở mức trung bình.\n2. Về cú pháp: Có khoảng trắng thừa ở `x [1]`. TUYỆT ĐỐI KHÔNG phạt Fatal lỗi này vì nó không làm crash code Python, luồng xử lý vẫn chạy được. Giữ điểm ở mức 5.0 (Tương đương Grade 2 hoặc 3 trên thang điểm năng lực)."
            },
            {
                "code": """sorted(a,key = lambda x:x.lower() if x.startswith(`.`)else x.lower())""",
                "expected_score": 3.0,
                "score_breakdown": {
                    "idea": 1.5,
                    "flow": 1.0,
                    "correctness": 0.5
                },
                "reasoning": "POOR (Bản chất giống tranx-annot):\n1. Về logic: Hoàn toàn đi lệch hướng, cố gắng xử lý chuỗi và điều kiện `startswith` thay vì tập trung vào việc sắp xếp danh sách theo 2 tiêu chí dữ liệu.\n2. Về cú pháp: Sử dụng dấu backtick ( `.` ) thay vì dấu nháy chuẩn ( '.' ). Đây là lỗi typo định dạng hiển thị, hệ thống Python sẽ tự động hạ cấp xuống Negligible và không trừ thêm điểm phạt. Điểm số thuần túy phản ánh mức độ hiểu sai đề bài của thuật toán (Mức 3.0đ, tương đương Grade 1)."
            },
            {
                "code": """def sort_list(l):
    return l.sort()""",
                "expected_score": 1.5,
                "score_breakdown": {
                    "idea": 1.0,
                    "flow": 0.5,
                    "correctness": 0.0
                },
                "reasoning": "POOR: Học viên chỉ biết gọi hàm `.sort()` mặc định, không hề có ý tưởng hay giải pháp nào để cấu hình sắp xếp đa tiêu chí theo yêu cầu của đề bài. Hàm `.sort()` còn trả về `None`, làm sai lệch kết quả đầu ra."
            },
            {
                "code": """print('hello world')""",
                "expected_score": 0.0,
                "score_breakdown": {
                    "idea": 0.0,
                    "flow": 0.0,
                    "correctness": 0.0
                },
                "reasoning": "ZERO: Code hoàn toàn lạc đề, không giải quyết bất kỳ một khía cạnh nào của bài toán sắp xếp."
            }
        ]
    },
    
    "all_elements_same": {
        "problem": "Viết hàm kiểm tra xem tất cả phần tử trong danh sách có giống nhau không?",
        "examples": [
            {
                "code": """def check_all_same(lst):
    if not lst:
        return True
    return all(x == lst[0] for x in lst)""",
                "expected_score": 10.0,
                "score_breakdown": {
                    "idea": 4.0,
                    "flow": 3.0,
                    "correctness": 3.0
                },
                "reasoning": "PERFECT: Logic chuẩn xác, có xử lý tốt trường hợp biên danh sách rỗng, code viết theo phong cách Pythonic rõ ràng."
            },
            {
                "code": """def check_all_same(lst):
    return len(set(lst)) <= 1""",
                "expected_score": 9.0,
                "score_breakdown": {
                    "idea": 4.0,
                    "flow": 2.5,
                    "correctness": 2.5
                },
                "reasoning": "GOOD: Ý tưởng sử dụng toán tập hợp `set()` rất thông minh và xử lý được danh sách rỗng. Tuy nhiên nếu gặp danh sách có kích thước quá lớn (Large Data) sẽ tốn thêm tài nguyên bộ nhớ để khởi tạo set."
            },
            {
                "code": """def check_all_same(lst):
    for i in range(len(lst)-1):
        if lst [i] != lst[i+1]:
            return False
    return True""",
                "expected_score": 7.5,
                "score_breakdown": {
                    "idea": 3.0,
                    "flow": 2.5,
                    "correctness": 2.0
                },
                "reasoning": "AVERAGE: Thuật toán duyệt cặp kề nhau về cơ bản là đúng. Tuy nhiên chưa handle lỗi index nếu mảng rỗng. Đồng thời xuất hiện lỗi khoảng trắng `lst [i]`, lỗi này thuộc nhóm định dạng nên KHÔNG phạt nặng, điểm số chấm tập trung vào việc thiếu xử lý case biên."
            },
            {
                "code": """def check_all_same(lst):
    return len(set(lst)) == 1""",
                "expected_score": 4.0,
                "score_breakdown": {
                    "idea": 2.0,
                    "flow": 1.5,
                    "correctness": 0.5
                },
                "reasoning": "POOR: Thuật toán bị sai nghiêm trọng khi gặp danh sách rỗng (với danh sách rỗng, độ dài tập hợp bằng 0 chứ không bằng 1, khiến hàm trả về False thay vì True). Logic bị hỏng một nửa."
            }
        ]
    },

    "string_to_integer": {
        "problem": "function to convert strings into integers",
        "examples": [
            {
                "code": """int('123abc', base=10)""",
                "expected_score": 7.0,
                "score_breakdown": {
                    "idea": 3.0,
                    "flow": 2.0,
                    "correctness": 2.0
                },
                "reasoning": "AVERAGE: Cú pháp Python hoàn toàn chuẩn xác. Hành vi truyền chuỗi chứa chữ cái vào hàm int() sẽ gây lỗi ValueError khi chạy, đây là lỗi logic về dữ liệu đầu vào chứ không phải lỗi cú pháp cấu trúc. Giữ điểm ở mức Khá (Tương đương Grade 3/4)."
            },
            {
                "code": """list(map(int, [strings]))""",
                "expected_score": 7.5,
                "score_breakdown": {
                    "idea": 3.5,
                    "flow": 2.0,
                    "correctness": 2.0
                },
                "reasoning": "AVERAGE: Cú pháp lồng hàm hoàn toàn hợp lệ trong Python. Việc bọc thêm dấu ngoặc vuông `[strings]` là lỗi tư duy logic sắp xếp mảng bộ phận, không làm crash trình biên dịch. Đạt điểm Khá."
            }
        ]
    },
    
    "split_string_whitespaces": {
        "problem": "split string `my_string` on white spaces",
        "examples": [
            {
                "code": """`my_string.split(``)`""",
                "expected_score": 10.0,
                "score_breakdown": {
                    "idea": 4.0,
                    "flow": 3.0,
                    "correctness": 3.0
                },
                "reasoning": "PERFECT: Mặc dù code chứa các dấu backtick (`) thừa do lỗi trích xuất dữ liệu, nhưng logic thuật toán hoàn toàn chính xác là dùng hàm `.split()`. Tuyệt đối KHÔNG dìm điểm idea/flow/correctness về 0 vì lỗi định dạng Markdown này. Lỗi này là Negligible."
            },
            {
                "code": """print(s.split())""",
                "expected_score": 7.5,
                "score_breakdown": {
                    "idea": 3.0,
                    "flow": 2.5,
                    "correctness": 2.0
                },
                "reasoning": "AVERAGE: Sinh viên dùng sai tên biến (`s` thay vì `my_string`) và dùng `print` thay vì gán/trả về kết quả. Tuy nhiên, ý tưởng cốt lõi (dùng `split()`) là hoàn toàn đúng. Lỗi sai tên biến thuộc nhóm Small, KHÔNG ĐƯỢC đánh giá Fatal hay cho 0 điểm idea."
            }
        ]
    }
}

# ============================================================================
# HELPER FUNCTIONS 
# ============================================================================

def get_calibration_examples(problem_key: str = None) -> dict:
    """Lấy ví dụ calibration cho một bài toán"""
    if problem_key is None:
        return CALIBRATION_EXAMPLES
    
    # Cơ chế fallback key thông minh: Định tuyến dựa trên từ khóa trong đề bài
    if problem_key not in CALIBRATION_EXAMPLES:
        prob_lower = problem_key.lower()
        if "sort" in prob_lower or "criteria" in prob_lower:
            return CALIBRATION_EXAMPLES["sorting_by_two_criteria"]
        if "convert" in prob_lower and "integer" in prob_lower:
            return CALIBRATION_EXAMPLES["string_to_integer"]
        if "split" in prob_lower or "white space" in prob_lower or "whitespace" in prob_lower:
            return CALIBRATION_EXAMPLES["split_string_whitespaces"]
            
        return CALIBRATION_EXAMPLES["all_elements_same"] # Default fallback
    
    return CALIBRATION_EXAMPLES[problem_key]


def format_examples_for_prompt(problem_key: str, num_examples: int = 3) -> str:
    """Format examples để nạp trực tiếp vào Prompt (Few-shot Learning)"""
    examples_data = get_calibration_examples(problem_key)
    
    problem = examples_data.get("problem", "Yêu cầu bài toán")
    examples = examples_data.get("examples", [])
    
    # Sắp xếp từ điểm cao xuống điểm thấp để LLM học tư duy phân cấp điểm
    sorted_examples = sorted(examples, key=lambda x: x["expected_score"], reverse=True)
    selected = sorted_examples[:num_examples]
    
    formatted = f"--- BẮT ĐẦU CÁC VÍ DỤ MẪU CHUẨN (CALIBRATION EXAMPLES) ---\n"
    formatted += f"Dưới đây là các ví dụ chấm điểm mẫu cho bài toán tương tự: '{problem}'\n"
    formatted += "Hãy soi chiếu cách phân bổ điểm và cách nhìn nhận lỗi vặt dưới đây để áp dụng vào bài chấm hiện tại:\n\n"
    
    for i, example in enumerate(selected, 1):
        formatted += f"[Mẫu chấm số {i} - Điểm Mục Tiêu Đạt Được: {example['expected_score']}/10.0]\n"
        formatted += f"Mã nguồn sinh viên nộp:\n```python\n{example['code']}\n```\n\n"
        formatted += f"Phân rã điểm bắt buộc (score_breakdown):\n"
        formatted += f" - Ý tưởng (idea): {example['score_breakdown']['idea']}/4.0\n"
        formatted += f" - Luồng xử lý (flow): {example['score_breakdown']['flow']}/3.0\n"
        formatted += f" - Tính đúng đắn (correctness): {example['score_breakdown']['correctness']}/3.0\n\n"
        formatted += f"Lý do chấm từ chuyên gia (Reasoning): {example['reasoning']}\n"
        formatted += f"--------------------------------------------------\n\n"
        
    formatted += "--- KẾT THÚC CÁC VÍ DỤ MẪU CHUẨN. BÂY GIỜ HÃY TIẾN HÀNH CHẤM BÀI ĐƯỢC YÊU CẦU ---\n"
    return formatted

def get_score_distribution(problem_key: str) -> dict:
    """Thống kê phân bố điểm từ examples"""
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
    print("Calibration Examples Library")
    print("=" * 60)
    print(f"Tổng số bộ ví dụ: {len(CALIBRATION_EXAMPLES)}")
    for key, data in CALIBRATION_EXAMPLES.items():
        print(f"- {key}: {len(data['examples'])} mẫu")