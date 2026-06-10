import pytest
import json
from unittest.mock import MagicMock, patch
from codejudge.core.compiler_helper import check_syntax, _check_python_syntax, _check_cpp_syntax
from codejudge.core.multi_agent_assessor import MultiAgentAssessor

class TestCompilerHelper:
    def test_python_syntax_valid(self):
        code = "def add(a, b):\n    return a + b\n"
        errors = check_syntax(code, "python")
        assert len(errors) == 0

    def test_python_syntax_invalid(self):
        code = "def add(a, b)\n    return a + b\n" # Missing colon
        errors = check_syntax(code, "python")
        assert len(errors) == 1
        assert "Line 1" in errors[0]

    @patch("tempfile.NamedTemporaryFile")
    @patch("subprocess.run")
    def test_cpp_syntax_valid_mocked(self, mock_run, mock_temp):
        # Mock temp file
        mock_file = MagicMock()
        mock_file.name = "/some/path/temp_file.cpp"
        mock_temp.return_value = mock_file
        
        # Mock successful g++ syntax check
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stderr = ""
        mock_run.return_value = mock_proc
        
        code = "#include <iostream>\nint main() { return 0; }"
        errors = check_syntax(code, "cpp")
        assert len(errors) == 0

    @patch("tempfile.NamedTemporaryFile")
    @patch("subprocess.run")
    def test_cpp_syntax_invalid_mocked(self, mock_run, mock_temp):
        # Mock temp file
        mock_file = MagicMock()
        mock_file.name = "/some/path/temp_file.cpp"
        mock_temp.return_value = mock_file
        
        # Mock failed g++ syntax check
        mock_proc = MagicMock()
        mock_proc.returncode = 1
        mock_proc.stderr = "/some/path/temp_file.cpp:3:1: error: expected ';' after struct"
        mock_run.return_value = mock_proc
        
        code = "struct Point { int x, y }" # Missing semicolon
        errors = check_syntax(code, "cpp")
        assert len(errors) == 1
        assert "error:" in errors[0]
        # Should sanitize paths
        assert "/some/path" not in errors[0]
        assert "student_code.cpp" in errors[0]


class TestMultiAgentAssessor:
    def test_clean_and_parse_json(self):
        assessor = MultiAgentAssessor(llm_client=MagicMock())
        
        # Test clean JSON
        res = assessor._clean_and_parse_json('["factor1", "factor2"]')
        assert res == ["factor1", "factor2"]
        
        # Test wrapped in markdown blocks
        res = assessor._clean_and_parse_json('```json\n{"a": 1}\n```')
        assert res == {"a": 1}
        
        # Test mixed text with JSON inside
        res = assessor._clean_and_parse_json('Here is your json: {"score": 10} hope it helps')
        assert res == {"score": 10}

    def test_extract_factors(self):
        mock_llm = MagicMock()
        mock_llm.call.return_value = '["Factor 1", "Factor 2"]'
        
        assessor = MultiAgentAssessor(llm_client=mock_llm)
        factors = assessor.extract_factors("Đề bài mẫu")
        
        assert factors == ["Factor 1", "Factor 2"]
        mock_llm.call.assert_called_once()

    def test_assess_factors(self):
        mock_llm = MagicMock()
        mock_response = {
            "Factor 1": {"compliance": 1.0, "reasoning": "Đúng"},
            "Factor 2": {"compliance": 0.5, "reasoning": "Thiếu"}
        }
        mock_llm.call.return_value = json.dumps(mock_response)
        
        assessor = MultiAgentAssessor(llm_client=mock_llm)
        evaluation = assessor.assess_factors("code", ["Factor 1", "Factor 2"], "python")
        
        assert evaluation["Factor 1"]["compliance"] == 1.0
        assert evaluation["Factor 2"]["compliance"] == 0.5
        mock_llm.call.assert_called_once()

    def test_calculate_score(self):
        assessor = MultiAgentAssessor(llm_client=MagicMock())
        
        factor_eval = {
            "Factor 1": {"compliance": 1.0},
            "Factor 2": {"compliance": 0.5}
        }
        
        # Test without syntax errors
        res = assessor.calculate_score(factor_eval, syntax_errors=[])
        assert res["factor_score_on_10"] == 7.5  # average(1.0, 0.5) * 10
        assert res["syntax_penalty_on_10"] == 0.0
        assert res["final_score_on_10"] == 7.5
        
        # Test with syntax errors (classified: "Error 1" is Major -> 1.5 penalty)
        res = assessor.calculate_score(factor_eval, syntax_errors=["Error 1"])
        assert res["factor_score_on_10"] == 7.5
        assert res["syntax_penalty_on_10"] == 1.5
        assert res["final_score_on_10"] == 6.0
        
        # Test with syntax errors (classified: "warning: unused" -> 0.25 penalty)
        res = assessor.calculate_score(factor_eval, syntax_errors=["warning: unused variable 'x'"])
        assert res["syntax_penalty_on_10"] == 0.25
        assert res["final_score_on_10"] == 7.25

        # Test with syntax errors (classified: "expected ';'" -> 0.5 penalty)
        res = assessor.calculate_score(factor_eval, syntax_errors=["expected ';' before 'return'"])
        assert res["syntax_penalty_on_10"] == 0.5
        assert res["final_score_on_10"] == 7.0
        
        # Test with question max scaling (Error 1 -> 1.5 penalty, final_score = 6.0)
        res = assessor.calculate_score(factor_eval, syntax_errors=["Error 1"], question_max=4.0)
        assert res["scaled_score"] == 2.4  # 6.0 / 10.0 * 4.0 = 2.4
        assert res["question_max"] == 4.0

    def test_generate_suggestions(self):
        assessor = MultiAgentAssessor(llm_client=MagicMock())
        
        factor_eval = {
            "Factor 1": {"compliance": 1.0, "reasoning": "OK"},
            "Factor 2": {"compliance": 0.5, "reasoning": "Thiếu vòng lặp"}
        }
        
        suggestions = assessor.generate_suggestions(factor_eval, syntax_errors=["Syntax error on line 5"])
        
        assert any("Syntax error on line 5" in s for s in suggestions)
        assert any("Factor 2" in s for s in suggestions)
        assert any("Thiếu vòng lặp" in s for s in suggestions)

    @patch("codejudge.core.multi_agent_assessor.check_syntax")
    def test_assess_end_to_end_mocked(self, mock_check_syntax):
        mock_check_syntax.return_value = []
        
        mock_llm = MagicMock()
        # Mock factor extraction response
        mock_llm.call.side_effect = [
            '["Factor 1"]', # First call: extract factors
            '{"Factor 1": {"compliance": 0.8, "reasoning": "Khá tốt"}}' # Second call: assess
        ]
        
        assessor = MultiAgentAssessor(llm_client=mock_llm)
        result = assessor.assess(
            question_text="Đề bài",
            student_code="print('Hello')",
            language="python",
            question_max=5.0
        )
        
        assert result["assessment_type"] == "multi_agent"
        assert len(result["syntax_errors"]) == 0
        assert result["factors"] == ["Factor 1"]
        assert result["factor_evaluation"]["Factor 1"]["compliance"] == 0.8
        assert result["scoring"]["final_score_on_10"] == 8.0
        assert result["scoring"]["scaled_score"] == 4.0  # 8.0/10.0 * 5.0
        assert result["final_score"] == 4.0

    @patch("codejudge.core.multi_agent_assessor.check_syntax")
    def test_assess_with_llm_error_mocked(self, mock_check_syntax):
        mock_check_syntax.return_value = []
        
        mock_llm = MagicMock()
        # Mock LLM client raising exception
        mock_llm.call.side_effect = Exception("OpenRouter API error (Rate limit)")
        
        assessor = MultiAgentAssessor(llm_client=mock_llm)
        result = assessor.assess(
            question_text="Đề bài",
            student_code="print('Hello')",
            language="python",
            question_max=5.0
        )
        
        assert result["assessment_type"] == "multi_agent"
        assert result["scoring"]["final_score_on_10"] == -1.0
        assert result["scoring"]["scaled_score"] == -1.0
        assert result["scoring"]["has_error"] is True
        assert "Lỗi Agent 1" in result["scoring"]["error_message"]
        assert result["final_score"] == -1.0
        assert result["factor_evaluation"]["Thực hiện đúng logic của câu hỏi"]["compliance"] == -1.0
