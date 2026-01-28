"""
Tests for prompt builder.

Verifies that prompts are correctly constructed with all necessary
context and constraints.
"""

import pytest

from app.llm.prompt_builder import build_basket_prompt, build_system_message
from app.schemas.basket import BasketRequest


def test_build_system_message():
    """Test system message generation."""
    message = build_system_message()
    
    assert isinstance(message, str)
    assert len(message) > 0
    assert "shopping assistant" in message.lower()
    assert "json" in message.lower()


def test_build_basket_prompt_includes_intent(sample_basket_request):
    """Test that prompt includes user intent."""
    prompt = build_basket_prompt(sample_basket_request)
    
    assert sample_basket_request.user_intent in prompt
    assert "weekly grocery shopping" in prompt


def test_build_basket_prompt_includes_budget(sample_basket_request):
    """Test that prompt includes budget and currency."""
    prompt = build_basket_prompt(sample_basket_request)
    
    assert str(sample_basket_request.budget) in prompt
    assert sample_basket_request.store_context.currency in prompt


def test_build_basket_prompt_includes_preferences(sample_basket_request):
    """Test that prompt includes dietary preferences."""
    prompt = build_basket_prompt(sample_basket_request)
    
    for pref in sample_basket_request.preferences:
        assert pref in prompt


def test_build_basket_prompt_includes_categories(sample_basket_request):
    """Test that prompt includes available categories."""
    prompt = build_basket_prompt(sample_basket_request)
    
    for category in sample_basket_request.store_context.available_categories:
        assert category in prompt


def test_build_basket_prompt_forces_json(sample_basket_request):
    """Test that prompt explicitly requests JSON output."""
    prompt = build_basket_prompt(sample_basket_request)
    
    assert "json" in prompt.lower()
    assert "basket" in prompt
    assert "estimated_total" in prompt
    assert "assumptions" in prompt


def test_build_basket_prompt_no_preferences(minimal_basket_request):
    """Test prompt building with no preferences."""
    prompt = build_basket_prompt(minimal_basket_request)
    
    assert "none specified" in prompt.lower()
    assert minimal_basket_request.user_intent in prompt


def test_build_basket_prompt_structure(sample_basket_request):
    """Test that prompt has proper structure."""
    prompt = build_basket_prompt(sample_basket_request)
    
    # Should include key sections
    assert "USER INTENT" in prompt
    assert "CONSTRAINTS" in prompt
    assert "INSTRUCTIONS" in prompt
    assert "CRITICAL" in prompt or "Return ONLY" in prompt
