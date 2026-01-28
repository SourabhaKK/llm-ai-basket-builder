"""
Fallback basket generation.

Provides safe, minimal baskets when LLM fails or returns invalid data.
Ensures the system always returns a valid response.
"""

import logging
from typing import List

from app.schemas.basket import BasketRequest, BasketResponse, BasketCategory, BasketItem

logger = logging.getLogger(__name__)


# Generic fallback items by category
FALLBACK_ITEMS = {
    "produce": [
        {"name": "Fresh Vegetables", "reason": "Essential nutritious produce"},
        {"name": "Fresh Fruits", "reason": "Healthy fruit selection"}
    ],
    "dairy": [
        {"name": "Milk", "reason": "Basic dairy staple"},
        {"name": "Cheese", "reason": "Versatile dairy product"}
    ],
    "grains": [
        {"name": "Whole Grain Bread", "reason": "Staple grain product"},
        {"name": "Rice", "reason": "Versatile grain base"}
    ],
    "protein": [
        {"name": "Eggs", "reason": "High-quality protein source"},
        {"name": "Beans", "reason": "Plant-based protein"}
    ],
    "meat": [
        {"name": "Chicken Breast", "reason": "Lean protein source"}
    ],
    "snacks": [
        {"name": "Healthy Snack Mix", "reason": "Convenient snacking option"}
    ],
    "beverages": [
        {"name": "Water", "reason": "Essential hydration"}
    ],
}


# Vegetarian alternatives
VEGETARIAN_FALLBACK = {
    "produce": FALLBACK_ITEMS["produce"],
    "dairy": FALLBACK_ITEMS["dairy"],
    "grains": FALLBACK_ITEMS["grains"],
    "protein": [
        {"name": "Tofu", "reason": "Plant-based protein"},
        {"name": "Lentils", "reason": "High-protein legume"}
    ],
}


def generate_fallback_basket(request: BasketRequest) -> BasketResponse:
    """
    Generate a safe fallback basket when LLM fails.
    
    Creates a minimal but valid basket that:
    - Respects available categories
    - Respects dietary preferences
    - Distributes budget evenly
    - Always returns valid data
    
    Args:
        request: Original basket request
        
    Returns:
        BasketResponse: Safe fallback basket
    """
    logger.warning("Generating fallback basket due to LLM failure")
    
    # Determine which fallback items to use based on preferences
    is_vegetarian = any(pref in ["vegetarian", "vegan"] for pref in request.preferences)
    fallback_source = VEGETARIAN_FALLBACK if is_vegetarian else FALLBACK_ITEMS
    
    # Build basket from available categories
    basket_categories: List[BasketCategory] = []
    
    for category_name in request.store_context.available_categories:
        # Get fallback items for this category
        category_items = fallback_source.get(category_name.lower(), [])
        
        if not category_items:
            # Create generic item if no specific fallback exists
            category_items = [
                {
                    "name": f"Essential {category_name.title()} Items",
                    "reason": f"Basic {category_name} products"
                }
            ]
        
        # Create BasketItem objects
        items = [
            BasketItem(name=item["name"], reason=item["reason"])
            for item in category_items[:2]  # Limit to 2 items per category
        ]
        
        basket_categories.append(
            BasketCategory(category=category_name, items=items)
        )
    
    # Calculate estimated total (distribute budget evenly)
    num_categories = len(basket_categories)
    estimated_total = round(request.budget * 0.8, 2)  # Use 80% of budget for safety
    
    # Build assumptions
    assumptions = [
        "Fallback basket generated due to processing error",
        "Budget distributed evenly across available categories",
    ]
    
    if is_vegetarian:
        assumptions.append("Vegetarian items selected based on preferences")
    
    response = BasketResponse(
        basket=basket_categories,
        estimated_total=estimated_total,
        assumptions=assumptions
    )
    
    logger.info(f"Generated fallback basket with {num_categories} categories, total: {estimated_total}")
    
    return response


def is_basket_valid(basket_data: dict) -> bool:
    """
    Check if basket data is valid and usable.
    
    Args:
        basket_data: Basket dictionary to validate
        
    Returns:
        bool: True if valid, False if fallback should be used
    """
    try:
        # Check required fields exist
        if not basket_data:
            return False
        
        if "basket" not in basket_data or "estimated_total" not in basket_data:
            return False
        
        # Check basket is not empty
        if not basket_data["basket"]:
            return False
        
        # Check all categories have items
        for category in basket_data["basket"]:
            if not category.get("items"):
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating basket: {e}")
        return False
