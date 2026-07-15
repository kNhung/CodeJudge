import pytest
import json
from unittest.mock import MagicMock, patch
from codeeval.core.multi_agent_assessor import MultiAgentAssessor

class TestCachePolicy:
    @patch("codeeval.core.multi_agent_assessor.check_syntax")
    def test_assess_grader_cache_default_false(self, mock_check_syntax):
        mock_check_syntax.return_value = []
        
        mock_llm = MagicMock()
        mock_llm.call.side_effect = [
            '["Factor 1"]', # Agent 1
            '{"Factor 1": {"compliance": 1.0, "reasoning": "OK"}}' # Agent 2
        ]
        
        assessor = MultiAgentAssessor(llm_client=mock_llm)
        
        # Call assess with default parameters (use_grader_cache defaults to False)
        result = assessor.assess(
            question_text="Sample Question",
            student_code="print('hello')",
            language="python"
        )
        
        # Verify call arguments
        # 1. Agent 1 (Factor Extractor) - should NOT pass use_cache (defaults to None, using client's default cache)
        # 2. Agent 2 (Factor Grader) - should pass use_cache=False
        assert mock_llm.call.call_count == 2
        
        first_call_kwargs = mock_llm.call.call_args_list[0][1]
        assert "use_cache" not in first_call_kwargs
        
        second_call_kwargs = mock_llm.call.call_args_list[1][1]
        assert second_call_kwargs.get("use_cache") is False

    @patch("codeeval.core.multi_agent_assessor.check_syntax")
    def test_assess_grader_cache_force_true(self, mock_check_syntax):
        mock_check_syntax.return_value = []
        
        mock_llm = MagicMock()
        mock_llm.call.side_effect = [
            '["Factor 1"]', # Agent 1
            '{"Factor 1": {"compliance": 1.0, "reasoning": "OK"}}' # Agent 2
        ]
        
        assessor = MultiAgentAssessor(llm_client=mock_llm)
        
        # Call assess with use_grader_cache=True
        result = assessor.assess(
            question_text="Sample Question",
            student_code="print('hello')",
            language="python",
            use_grader_cache=True
        )
        
        assert mock_llm.call.call_count == 2
        
        second_call_kwargs = mock_llm.call.call_args_list[1][1]
        assert second_call_kwargs.get("use_cache") is True
