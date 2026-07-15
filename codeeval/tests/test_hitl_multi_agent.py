import pytest
from unittest.mock import MagicMock
from codeeval.core.multi_agent_assessor import MultiAgentAssessor

def test_default_arithmetic_average_score():
    # Test that default calculate_score uses simple arithmetic average
    assessor = MultiAgentAssessor(llm_client=MagicMock())
    
    factor_eval = {
        "Factor A": {"compliance": 1.0, "reasoning": "Good"},
        "Factor B": {"compliance": 0.5, "reasoning": "Halfway"},
        "Factor C": {"compliance": 0.0, "reasoning": "Missing"}
    }
    
    # Simple average of (1.0 + 0.5 + 0.0) / 3 = 0.5. Out of 10 -> 5.0
    result = assessor.calculate_score(factor_eval, syntax_errors=[])
    assert result["compliance_average"] == pytest.approx(0.5)
    assert result["factor_score_on_10"] == pytest.approx(5.0)
    assert result["final_score_on_10"] == pytest.approx(5.0)

def test_custom_factor_weights():
    # Test that calculate_score respects custom weights
    assessor = MultiAgentAssessor(llm_client=MagicMock())
    
    factor_eval = {
        "Factor A": {"compliance": 1.0, "reasoning": "Good"},
        "Factor B": {"compliance": 0.5, "reasoning": "Halfway"},
        "Factor C": {"compliance": 0.0, "reasoning": "Missing"}
    }
    
    # Custom weights: A (60%), B (40%), C (0% weight) -> total weight 1.0
    factor_weights = {
        "Factor A": 0.6,
        "Factor B": 0.4,
        "Factor C": 0.0
    }
    
    # Score should be: 1.0 * 0.6 + 0.5 * 0.4 + 0.0 * 0.0 = 0.6 + 0.2 = 0.8. Out of 10 -> 8.0
    result = assessor.calculate_score(factor_eval, syntax_errors=[], factor_weights=factor_weights)
    assert result["compliance_average"] == pytest.approx(0.8)
    assert result["factor_score_on_10"] == pytest.approx(8.0)

def test_custom_factor_weights_normalization():
    # Test that calculate_score normalizes custom weights if they don't sum to 1.0
    assessor = MultiAgentAssessor(llm_client=MagicMock())
    
    factor_eval = {
        "Factor A": {"compliance": 1.0, "reasoning": "Good"},
        "Factor B": {"compliance": 0.5, "reasoning": "Halfway"}
    }
    
    # Weights sum to 4.0: A gets 3.0 (75%), B gets 1.0 (25%)
    factor_weights = {
        "Factor A": 3.0,
        "Factor B": 1.0
    }
    
    # Score: 1.0 * 0.75 + 0.5 * 0.25 = 0.75 + 0.125 = 0.875. Out of 10 -> 8.75
    result = assessor.calculate_score(factor_eval, syntax_errors=[], factor_weights=factor_weights)
    assert result["compliance_average"] == pytest.approx(0.875)
    assert result["factor_score_on_10"] == pytest.approx(8.75)

def test_custom_syntax_penalties():
    # Test that calculate_score utilizes custom syntax penalties
    assessor = MultiAgentAssessor(llm_client=MagicMock())
    
    factor_eval = {
        "Factor A": {"compliance": 1.0, "reasoning": "Good"}
    }
    
    # C++ warning, typo, and conceptual errors
    syntax_errors = [
        "warning: unused variable 'x'",
        "error: expected ';'",
        "error: major compiler crash"
    ]
    
    # Case 1: Default penalties: Warning: 0.25, Typo: 0.5, Major: 1.5 -> Sum = 2.25
    result_default = assessor.calculate_score(factor_eval, syntax_errors)
    assert result_default["syntax_penalty_on_10"] == pytest.approx(2.25)
    
    # Case 2: Custom penalties: Warning: 0.1, Typo: 0.2, Major: 1.0 -> Sum = 1.3
    custom_penalties = {
        "warning": 0.1,
        "typo": 0.2,
        "major": 1.0
    }
    result_custom = assessor.calculate_score(factor_eval, syntax_errors, syntax_penalties=custom_penalties)
    assert result_custom["syntax_penalty_on_10"] == pytest.approx(1.3)

def test_pre_extracted_factors_injection():
    # Test that assess bypasses Agent 1 when pre_extracted_factors is provided
    mock_client = MagicMock()
    # Mock assess_factors LLM call
    mock_client.call.return_value = '{"1": {"compliance": 1.0, "reasoning": "Mocked"}}'
    
    assessor = MultiAgentAssessor(llm_client=mock_client)
    
    # Custom factors provided
    pre_factors = ["My Custom Factor 1"]
    
    # Call assess
    result = assessor.assess(
        question_text="Dummy question",
        student_code="print('hello')",
        language="python",
        pre_extracted_factors=pre_factors
    )
    
    # Check that extract_factors was NOT called (no "Agent 1" call logic)
    # The prompt should be formatted with "1. My Custom Factor 1"
    assert "My Custom Factor 1" in result["factors"]
    assert len(result["factors"]) == 1
    
    # Verify mock client call was only made for grading, not extraction
    assert mock_client.call.call_count == 1
    # Check the user prompt contains our custom factor
    called_user_prompt = mock_client.call.call_args[1]["user_prompt"]
    assert "My Custom Factor 1" in called_user_prompt


def test_merge_folder_code_cpp(tmp_path):
    from codeeval.core.compiler_helper import merge_folder_code
    
    # Create temp headers and source files
    helper_h = tmp_path / "helper.h"
    helper_h.write_text("#ifndef HELPER_H\n#define HELPER_H\nvoid run();\n#endif\n", encoding="utf-8")
    
    helper_cpp = tmp_path / "helper.cpp"
    helper_cpp.write_text('#include <vector>\n#include "helper.h"\nvoid run() {}\n', encoding="utf-8")
    
    main_cpp = tmp_path / "main.cpp"
    main_cpp.write_text('#include <iostream>\n#include "helper.h"\nint main() { run(); return 0; }\n', encoding="utf-8")
    
    merged = merge_folder_code(tmp_path, "cpp")
    
    # Assert headers/files are structured
    assert "FILE: helper.h" in merged
    assert "FILE: helper.cpp" in merged
    assert "FILE: main.cpp" in merged
    
    # Assert system headers are stripped
    assert "#include <vector>" not in merged
    assert "#include <iostream>" not in merged
    
    # Assert local headers are commented out
    assert '// #include "helper.h"' in merged
    
    # Assert actual content exists
    assert "int main() { run(); return 0; }" in merged


def test_merge_folder_code_python(tmp_path):
    from codeeval.core.compiler_helper import merge_folder_code
    
    utils_py = tmp_path / "utils.py"
    utils_py.write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
    
    main_py = tmp_path / "main.py"
    main_py.write_text("import utils\nprint(utils.add(1, 2))\n", encoding="utf-8")
    
    merged = merge_folder_code(tmp_path, "python")
    
    assert "FILE: utils.py" in merged
    assert "FILE: main.py" in merged
    assert "def add(a, b):" in merged
    assert "print(utils.add(1, 2))" in merged


def test_check_syntax_cpp_directory(tmp_path):
    from codeeval.core.compiler_helper import check_syntax
    
    # 1. Test clean C++ directory syntax checking
    helper_h = tmp_path / "helper.h"
    helper_h.write_text("#ifndef HELPER_H\n#define HELPER_H\nvoid hello();\n#endif\n", encoding="utf-8")
    
    main_cpp = tmp_path / "main.cpp"
    main_cpp.write_text('#include "helper.h"\n#include <iostream>\nvoid hello() { std::cout << "hello"; }\nint main() { hello(); return 0; }\n', encoding="utf-8")
    
    errors = check_syntax(str(tmp_path), "cpp")
    # Should compile cleanly
    assert errors == []
    
    # 2. Test directory syntax check with an error
    bad_cpp = tmp_path / "bad.cpp"
    bad_cpp.write_text('int foo() { return "not an int"; }\n', encoding="utf-8") # mismatch return type or error
    
    errors_bad = check_syntax(str(tmp_path), "cpp")
    assert len(errors_bad) > 0
    assert any("error:" in err.lower() for err in errors_bad)


def test_check_syntax_python_directory(tmp_path):
    from codeeval.core.compiler_helper import check_syntax
    
    # 1. Clean Python directory syntax checking
    main_py = tmp_path / "main.py"
    main_py.write_text("def hello():\n    print('hello')\n", encoding="utf-8")
    
    errors = check_syntax(str(tmp_path), "python")
    assert errors == []
    
    # 2. Bad Python directory syntax checking
    bad_py = tmp_path / "bad.py"
    bad_py.write_text("def bad_func()\n    print('missing colon')\n", encoding="utf-8")
    
    errors_bad = check_syntax(str(tmp_path), "python")
    assert len(errors_bad) > 0
    assert any("bad.py" in err or "Line" in err for err in errors_bad)
