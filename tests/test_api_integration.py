"""
API integration tests.

Tests the full /build-basket endpoint with mocked LLM responses.
"""

import pytest
from unittest.mock import AsyncMock, patch

from app.schemas.basket import BasketResponse


class TestBuildBasketAPI:
    """Integration tests for /build-basket endpoint."""
    
    @patch('app.api.routes.get_llm_client')
    def test_build_basket_success(
        self,
        mock_get_client,
        test_client,
        sample_basket_request,
        mock_llm_response_valid
    ):
        """Test successful basket building."""
        # Mock LLM client
        mock_client = AsyncMock()
        mock_client.generate_basket = AsyncMock(return_value=mock_llm_response_valid)
        mock_get_client.return_value = mock_client
        
        # Make request
        response = test_client.post(
            "/build-basket",
            json=sample_basket_request.model_dump()
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "basket" in data
        assert "estimated_total" in data
        assert "assumptions" in data
        assert len(data["basket"]) > 0
    
    @patch('app.api.routes.get_llm_client')
    def test_build_basket_llm_failure_uses_fallback(
        self,
        mock_get_client,
        test_client,
        sample_basket_request
    ):
        """Test that LLM failure triggers fallback basket."""
        # Mock LLM client to return None (failure)
        mock_client = AsyncMock()
        mock_client.generate_basket = AsyncMock(return_value=None)
        mock_get_client.return_value = mock_client
        
        # Make request
        response = test_client.post(
            "/build-basket",
            json=sample_basket_request.model_dump()
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have fallback assumption
        assert any("fallback" in assumption.lower() for assumption in data["assumptions"])
    
    @patch('app.api.routes.get_llm_client')
    def test_build_basket_invalid_json_uses_fallback(
        self,
        mock_get_client,
        test_client,
        sample_basket_request,
        mock_llm_response_invalid
    ):
        """Test that invalid LLM JSON triggers fallback."""
        # Mock LLM client to return invalid JSON
        mock_client = AsyncMock()
        mock_client.generate_basket = AsyncMock(return_value=mock_llm_response_invalid)
        mock_get_client.return_value = mock_client
        
        # Make request
        response = test_client.post(
            "/build-basket",
            json=sample_basket_request.model_dump()
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have fallback assumption
        assert any("fallback" in assumption.lower() for assumption in data["assumptions"])
    
    @patch('app.api.routes.get_llm_client')
    def test_build_basket_enforces_budget(
        self,
        mock_get_client,
        test_client,
        sample_basket_request,
        mock_llm_response_over_budget
    ):
        """Test that budget enforcement works in full pipeline."""
        # Mock LLM client to return over-budget basket
        mock_client = AsyncMock()
        mock_client.generate_basket = AsyncMock(return_value=mock_llm_response_over_budget)
        mock_get_client.return_value = mock_client
        
        # Make request
        response = test_client.post(
            "/build-basket",
            json=sample_basket_request.model_dump()
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should be within budget
        assert data["estimated_total"] <= sample_basket_request.budget
    
    @patch('app.api.routes.get_llm_client')
    def test_build_basket_enforces_dietary_preferences(
        self,
        mock_get_client,
        test_client,
        sample_basket_request,
        mock_llm_response_with_meat
    ):
        """Test that dietary preferences are enforced in full pipeline."""
        # Mock LLM client to return basket with meat
        mock_client = AsyncMock()
        mock_client.generate_basket = AsyncMock(return_value=mock_llm_response_with_meat)
        mock_get_client.return_value = mock_client
        
        # Make request (sample_basket_request has vegetarian preference)
        response = test_client.post(
            "/build-basket",
            json=sample_basket_request.model_dump()
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check no meat items in response
        all_items = []
        for category in data["basket"]:
            for item in category["items"]:
                all_items.append(item["name"].lower())
        
        assert "chicken" not in " ".join(all_items)
    
    def test_build_basket_invalid_request(self, test_client):
        """Test that invalid request returns 422."""
        # Missing required fields
        invalid_request = {
            "user_intent": "shopping"
            # Missing budget, store_context
        }
        
        response = test_client.post("/build-basket", json=invalid_request)
        
        assert response.status_code == 422
    
    def test_build_basket_negative_budget(self, test_client, sample_basket_request):
        """Test that negative budget is rejected."""
        request_data = sample_basket_request.model_dump()
        request_data["budget"] = -10.0
        
        response = test_client.post("/build-basket", json=request_data)
        
        assert response.status_code == 422


class TestHealthEndpoint:
    """Tests for health check endpoint."""
    
    def test_health_check(self, test_client):
        """Test health check endpoint."""
        response = test_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert "service" in data


class TestRootEndpoint:
    """Tests for root endpoint."""
    
    def test_root_endpoint(self, test_client):
        """Test root endpoint returns API info."""
        response = test_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "service" in data
        assert "version" in data
        assert "docs" in data
