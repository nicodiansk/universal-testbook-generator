# ABOUTME: Unit tests for llm.py module.
# ABOUTME: Tests token counting, response parsing, and cost estimation.

import sys
from pathlib import Path

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llm import count_tokens, _parse_response, estimate_cost, MODEL_PRICING


class TestCountTokens:
    """Tests for token counting function."""

    def test_empty_string(self):
        assert count_tokens("") == 0

    def test_simple_text(self):
        result = count_tokens("Hello world")
        assert result > 0
        assert result < 10

    def test_longer_text(self):
        short = count_tokens("Hello")
        long = count_tokens("Hello world, this is a longer sentence.")
        assert long > short


class TestParseResponse:
    """Tests for LLM response parsing."""

    def test_direct_json_array(self):
        content = '[{"test_case_id": "TC01", "test_case_name": "Test"}]'
        result = _parse_response(content)
        assert len(result) == 1
        assert result[0]["test_case_id"] == "TC01"

    def test_json_in_markdown_block(self):
        content = '''```json
[{"test_case_id": "TC01", "test_case_name": "Test"}]
```'''
        result = _parse_response(content)
        assert len(result) == 1
        assert result[0]["test_case_id"] == "TC01"

    def test_json_in_plain_code_block(self):
        content = '''```
[{"test_case_id": "TC01"}]
```'''
        result = _parse_response(content)
        assert len(result) == 1

    def test_json_with_surrounding_text(self):
        content = '''Here are the test cases:
[{"test_case_id": "TC01"}]
That's all!'''
        result = _parse_response(content)
        assert len(result) == 1

    def test_invalid_json_raises_error(self):
        with pytest.raises(ValueError, match="Could not parse"):
            _parse_response("This is not JSON at all")

    def test_multiple_test_cases(self):
        content = '''[
            {"test_case_id": "TC01", "test_case_name": "First"},
            {"test_case_id": "TC02", "test_case_name": "Second"}
        ]'''
        result = _parse_response(content)
        assert len(result) == 2
        assert result[0]["test_case_name"] == "First"
        assert result[1]["test_case_name"] == "Second"


class TestEstimateCost:
    """Tests for cost estimation function."""

    def test_returns_positive_value(self):
        cost = estimate_cost("A user story", "Glossary", "Instructions", "gpt-4o")
        assert cost > 0

    def test_longer_input_costs_more(self):
        short_cost = estimate_cost("Short", None, None, "gpt-4o")
        long_cost = estimate_cost("A much longer user story " * 100, None, None, "gpt-4o")
        assert long_cost > short_cost

    def test_mini_model_cheaper_than_4o(self):
        cost_4o = estimate_cost("Test story", None, None, "gpt-4o")
        cost_mini = estimate_cost("Test story", None, None, "gpt-4o-mini")
        assert cost_mini < cost_4o

    def test_all_models_have_pricing(self):
        for model in MODEL_PRICING:
            cost = estimate_cost("Test", None, None, model)
            assert cost > 0
