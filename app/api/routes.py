"""
API routes for basket building.

Implements the /build-basket endpoint that orchestrates the full pipeline:
1. Build prompt from request
2. Call LLM
3. Parse and validate response
4. Apply business rules
5. Return validated basket
"""

import logging
from fastapi import APIRouter, HTTPException, status

from app.schemas.basket import BasketRequest, BasketResponse
from app.llm.prompt_builder import build_basket_prompt, build_system_message
from app.llm.client import get_llm_client
from app.llm.response_parser import parse_llm_response, validate_basket_structure
from app.rules.budget import enforce_budget_cap
from app.rules.dietary import validate_dietary_preferences
from app.rules.fallback import generate_fallback_basket, is_basket_valid

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/build-basket",
    response_model=BasketResponse,
    status_code=status.HTTP_200_OK,
    summary="Build a shopping basket from user intent",
    description="Generates a structured shopping basket using LLM reasoning based on user intent, budget, and preferences."
)
async def build_basket(request: BasketRequest) -> BasketResponse:
    """
    Build a shopping basket from natural language intent.
    
    This endpoint orchestrates the full basket building pipeline:
    1. Constructs a structured prompt from the request
    2. Calls the LLM to generate basket recommendations
    3. Parses and validates the LLM response
    4. Applies business rules (budget caps, dietary constraints)
    5. Returns a validated basket or falls back to a safe default
    
    Args:
        request: Basket request with user intent, budget, preferences, and store context
        
    Returns:
        BasketResponse: Structured basket with items, estimated total, and assumptions
        
    Raises:
        HTTPException: If request validation fails (handled by FastAPI automatically)
    """
    logger.info(f"Building basket for intent: '{request.user_intent}'")
    logger.debug(f"Budget: {request.budget}, Preferences: {request.preferences}")
    
    try:
        # Step 1: Build prompt
        system_message = build_system_message()
        user_prompt = build_basket_prompt(request)
        logger.debug("Prompt built successfully")
        
        # Step 2: Call LLM
        llm_client = get_llm_client()
        raw_response = await llm_client.generate_basket(system_message, user_prompt)
        
        # Step 3: Parse and validate response
        basket_data = None
        if raw_response:
            basket_data = parse_llm_response(raw_response)
        
        # Check if we need fallback
        if not basket_data or not is_basket_valid(basket_data):
            logger.warning("LLM response invalid or missing, using fallback")
            return generate_fallback_basket(request)
        
        # Step 4: Apply business rules
        
        # 4a. Validate dietary preferences
        basket_data = validate_dietary_preferences(basket_data, request.preferences)
        
        # Check if basket is still valid after dietary filtering
        if not is_basket_valid(basket_data):
            logger.warning("Basket empty after dietary filtering, using fallback")
            return generate_fallback_basket(request)
        
        # 4b. Enforce budget cap
        basket_data = enforce_budget_cap(basket_data, request.budget)
        
        # Final validation
        if not is_basket_valid(basket_data):
            logger.warning("Basket invalid after business rules, using fallback")
            return generate_fallback_basket(request)
        
        # Step 5: Return validated response
        response = BasketResponse(**basket_data)
        logger.info(f"Successfully built basket with {len(response.basket)} categories")
        
        return response
        
    except Exception as e:
        logger.error(f"Unexpected error during basket building: {e}", exc_info=True)
        # Return fallback instead of failing
        logger.info("Returning fallback basket due to error")
        return generate_fallback_basket(request)


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check endpoint",
    description="Returns service health status"
)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        dict: Service status
    """
    return {
        "status": "healthy",
        "service": "llm-ai-basket-builder"
    }
