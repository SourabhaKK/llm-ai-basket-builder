"""
Tests for LLM output validation and parsing.

Verifies that LLM responses are correctly parsed, cleaned, and validated
against schemas.
"""

import pytest
import json

from app.llm.response_parser import (
    clean_json_response,
    parse_llm_response,
    validate_basket_structure
)


def test_clean_json_response_plain():
    """Test cleaning plain JSON response."""
    raw = '{"key": "value"}'
    cleaned = clean_json_response(raw)
    
    assert cleaned == raw


def test_clean_json_response_with_markdown():
    """Test cleaning JSON wrapped in markdown code blocks."""
    raw = '```json\n{"key": "value"}\n```'
    cleaned = clean_json_response(raw)
    
    assert cleaned == '{"key": "value"}'
    assert "```" not in cleaned


def test_clean_json_response_with_whitespace():
    """Test cleaning JSON with extra whitespace."""
    raw = '  \n  {"key": "value"}  \n  '
    cleaned = clean_json_response(raw)
    
    assert cleaned == '{"key": "value"}'


def test_parse_llm_response_valid(mock_llm_response_valid):
    """Test parsing valid LLM response."""
    result = parse_llm_response(mock_llm_response_valid)
    
    assert result is not None
    assert "basket" in result
    assert "estimated_total" in result
    assert "assumptions" in result
    assert len(result["basket"]) > 0


def test_parse_llm_response_with_markdown(mock_llm_response_with_markdown):
    """Test parsing LLM response wrapped in markdown."""
    result = parse_llm_response(mock_llm_response_with_markdown)
    
    assert result is not None
    assert "basket" in result
    assert len(result["basket"]) > 0


def test_parse_llm_response_invalid(mock_llm_response_invalid):
    """Test parsing invalid LLM response returns None."""
    result = parse_llm_response(mock_llm_response_invalid)
    
    assert result is None


def test_parse_llm_response_none():
    """Test parsing None response returns None."""
    result = parse_llm_response(None)
    
    assert result is None


def test_parse_llm_response_empty_string():
    """Test parsing empty string returns None."""
    result = parse_llm_response("")
    
    assert result is None


def test_validate_basket_structure_valid(mock_llm_response_valid):
    """Test validating valid basket structure."""
    parsed = json.loads(mock_llm_response_valid)
    is_valid = validate_basket_structure(parsed)
    
    assert is_valid is True


def test_validate_basket_structure_empty_basket():
    """Test validating basket with empty basket array."""
    data = {
        "basket": [],
        "estimated_total": 0.0,
        "assumptions": []
    }
    is_valid = validate_basket_structure(data)
    
    assert is_valid is False


def test_validate_basket_structure_missing_basket():
    """Test validating basket without basket field."""
    data = {
        "estimated_total": 50.0,
        "assumptions": []
    }
    is_valid = validate_basket_structure(data)
    
    assert is_valid is False


def test_validate_basket_structure_negative_total():
    """Test validating basket with negative total."""
    data = {
        "basket": [
            {
                "category": "produce",
                "items": [{"name": "Apple", "reason": "Fruit"}]
            }
        ],
        "estimated_total": -10.0,
        "assumptions": []
    }
    is_valid = validate_basket_structure(data)
    
    assert is_valid is False


def test_validate_basket_structure_empty_category():
    """Test validating basket with category containing no items."""
    data = {
        "basket": [
            {
                "category": "produce",
                "items": []
            }
        ],
        "estimated_total": 20.0,
        "assumptions": []
    }
    is_valid = validate_basket_structure(data)
    
    assert is_valid is False
