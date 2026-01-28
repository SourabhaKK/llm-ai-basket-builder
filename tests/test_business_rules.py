"""
Tests for business rules.

Verifies budget enforcement, dietary validation, and fallback generation.
"""

import pytest
import json

from app.rules.budget import enforce_budget_cap, validate_budget
from app.rules.dietary import validate_dietary_preferences, check_item_compliance
from app.rules.fallback import generate_fallback_basket, is_basket_valid


class TestBudgetRules:
    """Tests for budget enforcement."""
    
    def test_enforce_budget_within_limit(self, mock_llm_response_valid):
        """Test basket within budget is unchanged."""
        basket_data = json.loads(mock_llm_response_valid)
        max_budget = 60.0
        
        result = enforce_budget_cap(basket_data, max_budget)
        
        assert result["estimated_total"] <= max_budget
    
    def test_enforce_budget_over_limit(self, mock_llm_response_over_budget):
        """Test basket over budget is trimmed."""
        basket_data = json.loads(mock_llm_response_over_budget)
        max_budget = 60.0
        
        result = enforce_budget_cap(basket_data, max_budget)
        
        assert result["estimated_total"] <= max_budget
        assert any("trimmed" in assumption.lower() or "budget" in assumption.lower() 
                  for assumption in result.get("assumptions", []))
    
    def test_validate_budget_pass(self):
        """Test budget validation passes for valid basket."""
        basket_data = {"estimated_total": 50.0}
        max_budget = 60.0
        
        is_valid = validate_budget(basket_data, max_budget)
        
        assert is_valid is True
    
    def test_validate_budget_fail(self):
        """Test budget validation fails for over-budget basket."""
        basket_data = {"estimated_total": 70.0}
        max_budget = 60.0
        
        is_valid = validate_budget(basket_data, max_budget)
        
        assert is_valid is False


class TestDietaryRules:
    """Tests for dietary constraint validation."""
    
    def test_check_item_compliance_vegetarian_pass(self):
        """Test vegetarian item passes vegetarian check."""
        is_compliant = check_item_compliance(
            "Spinach",
            "Healthy vegetable",
            "vegetarian"
        )
        
        assert is_compliant is True
    
    def test_check_item_compliance_vegetarian_fail(self):
        """Test meat item fails vegetarian check."""
        is_compliant = check_item_compliance(
            "Chicken Breast",
            "Lean protein",
            "vegetarian"
        )
        
        assert is_compliant is False
    
    def test_check_item_compliance_vegan_dairy_fail(self):
        """Test dairy item fails vegan check."""
        is_compliant = check_item_compliance(
            "Greek Yogurt",
            "High-protein dairy",
            "vegan"
        )
        
        assert is_compliant is False
    
    def test_validate_dietary_preferences_filters_meat(self, mock_llm_response_with_meat):
        """Test dietary validation filters out meat for vegetarian preference."""
        basket_data = json.loads(mock_llm_response_with_meat)
        preferences = ["vegetarian"]
        
        result = validate_dietary_preferences(basket_data, preferences)
        
        # Check that chicken was removed
        all_items = []
        for category in result["basket"]:
            for item in category["items"]:
                all_items.append(item["name"].lower())
        
        assert "chicken" not in " ".join(all_items)
    
    def test_validate_dietary_preferences_no_preferences(self, mock_llm_response_valid):
        """Test validation with no preferences leaves basket unchanged."""
        basket_data = json.loads(mock_llm_response_valid)
        original_count = sum(len(cat["items"]) for cat in basket_data["basket"])
        
        result = validate_dietary_preferences(basket_data, [])
        result_count = sum(len(cat["items"]) for cat in result["basket"])
        
        assert result_count == original_count


class TestFallbackLogic:
    """Tests for fallback basket generation."""
    
    def test_generate_fallback_basket(self, sample_basket_request):
        """Test fallback basket generation."""
        result = generate_fallback_basket(sample_basket_request)
        
        assert result is not None
        assert len(result.basket) > 0
        assert result.estimated_total > 0
        assert result.estimated_total <= sample_basket_request.budget
        assert any("fallback" in assumption.lower() for assumption in result.assumptions)
    
    def test_generate_fallback_basket_vegetarian(self, sample_basket_request):
        """Test fallback basket respects vegetarian preference."""
        result = generate_fallback_basket(sample_basket_request)
        
        # Check no meat items
        all_items = []
        for category in result.basket:
            for item in category.items:
                all_items.append(item.name.lower())
        
        meat_keywords = ["chicken", "beef", "pork", "meat"]
        assert not any(keyword in " ".join(all_items) for keyword in meat_keywords)
    
    def test_generate_fallback_basket_respects_categories(self, sample_basket_request):
        """Test fallback basket uses only available categories."""
        result = generate_fallback_basket(sample_basket_request)
        
        result_categories = [cat.category for cat in result.basket]
        available_categories = sample_basket_request.store_context.available_categories
        
        for category in result_categories:
            assert category in available_categories
    
    def test_is_basket_valid_true(self, mock_llm_response_valid):
        """Test basket validation for valid basket."""
        basket_data = json.loads(mock_llm_response_valid)
        
        is_valid = is_basket_valid(basket_data)
        
        assert is_valid is True
    
    def test_is_basket_valid_empty_basket(self):
        """Test basket validation for empty basket."""
        basket_data = {
            "basket": [],
            "estimated_total": 0.0
        }
        
        is_valid = is_basket_valid(basket_data)
        
        assert is_valid is False
    
    def test_is_basket_valid_none(self):
        """Test basket validation for None."""
        is_valid = is_basket_valid(None)
        
        assert is_valid is False
