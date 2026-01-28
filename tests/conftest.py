"""
Pytest configuration and shared fixtures.

Provides reusable test fixtures for basket requests, mock LLM responses,
and test client setup.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.basket import BasketRequest, StoreContext


@pytest.fixture
def test_client():
    """
    FastAPI test client fixture.
    
    Returns:
        TestClient: Configured test client for API testing
    """
    return TestClient(app)


@pytest.fixture
def sample_basket_request():
    """
    Sample basket request for testing.
    
    Returns:
        BasketRequest: Valid basket request
    """
    return BasketRequest(
        user_intent="weekly grocery shopping for a vegetarian couple",
        budget=60.0,
        preferences=["vegetarian", "high-protein"],
        store_context=StoreContext(
            available_categories=["produce", "dairy", "grains", "snacks"],
            currency="GBP"
        )
    )


@pytest.fixture
def minimal_basket_request():
    """
    Minimal basket request with no preferences.
    
    Returns:
        BasketRequest: Minimal valid request
    """
    return BasketRequest(
        user_intent="quick lunch",
        budget=10.0,
        preferences=[],
        store_context=StoreContext(
            available_categories=["snacks", "beverages"],
            currency="USD"
        )
    )


@pytest.fixture
def mock_llm_response_valid():
    """
    Mock valid LLM response.
    
    Returns:
        str: Valid JSON response
    """
    return """{
        "basket": [
            {
                "category": "produce",
                "items": [
                    {
                        "name": "Spinach",
                        "reason": "High-protein vegetarian food"
                    },
                    {
                        "name": "Broccoli",
                        "reason": "Nutritious vegetable"
                    }
                ]
            },
            {
                "category": "dairy",
                "items": [
                    {
                        "name": "Greek Yogurt",
                        "reason": "High-protein dairy product"
                    }
                ]
            }
        ],
        "estimated_total": 45.50,
        "assumptions": ["Budget distributed across essential categories"]
    }"""


@pytest.fixture
def mock_llm_response_with_markdown():
    """
    Mock LLM response wrapped in markdown code blocks.
    
    Returns:
        str: JSON wrapped in markdown
    """
    return """```json
{
    "basket": [
        {
            "category": "snacks",
            "items": [
                {
                    "name": "Trail Mix",
                    "reason": "Healthy snack option"
                }
            ]
        }
    ],
    "estimated_total": 8.99,
    "assumptions": ["Quick snack selection"]
}
```"""


@pytest.fixture
def mock_llm_response_invalid():
    """
    Mock invalid LLM response (malformed JSON).
    
    Returns:
        str: Invalid JSON
    """
    return "This is not valid JSON at all!"


@pytest.fixture
def mock_llm_response_over_budget():
    """
    Mock LLM response that exceeds budget.
    
    Returns:
        str: Valid JSON with high total
    """
    return """{
        "basket": [
            {
                "category": "produce",
                "items": [
                    {"name": "Organic Vegetables", "reason": "Premium produce"}
                ]
            },
            {
                "category": "snacks",
                "items": [
                    {"name": "Premium Snacks", "reason": "High-quality snacks"}
                ]
            }
        ],
        "estimated_total": 75.00,
        "assumptions": ["Premium selection"]
    }"""


@pytest.fixture
def mock_llm_response_with_meat():
    """
    Mock LLM response containing meat items (for dietary testing).
    
    Returns:
        str: Valid JSON with meat items
    """
    return """{
        "basket": [
            {
                "category": "produce",
                "items": [
                    {"name": "Spinach", "reason": "Healthy vegetable"}
                ]
            },
            {
                "category": "protein",
                "items": [
                    {"name": "Chicken Breast", "reason": "Lean protein source"}
                ]
            }
        ],
        "estimated_total": 25.00,
        "assumptions": ["Balanced protein selection"]
    }"""
