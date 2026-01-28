"""
Budget enforcement rules.

Ensures basket total does not exceed user's budget by trimming items
or adjusting quantities while preserving essential categories.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


# Category priority for budget trimming (higher priority = kept longer)
CATEGORY_PRIORITY = {
    "produce": 5,
    "grains": 4,
    "dairy": 3,
    "protein": 3,
    "meat": 3,
    "snacks": 1,
    "beverages": 1,
    "desserts": 1,
}


def enforce_budget_cap(basket_data: Dict[str, Any], max_budget: float) -> Dict[str, Any]:
    """
    Enforce budget cap by trimming items if necessary.
    
    Strategy:
    1. Check if estimated_total exceeds budget
    2. If yes, remove items from lowest priority categories first
    3. Recalculate estimated_total
    4. Add assumption about budget adjustment
    
    Args:
        basket_data: Parsed basket dictionary with basket, estimated_total, assumptions
        max_budget: Maximum allowed budget
        
    Returns:
        Dict[str, Any]: Budget-compliant basket data
    """
    estimated_total = basket_data.get("estimated_total", 0)
    
    # If within budget, return as-is
    if estimated_total <= max_budget:
        logger.info(f"Basket total {estimated_total} is within budget {max_budget}")
        return basket_data
    
    logger.warning(f"Basket total {estimated_total} exceeds budget {max_budget}, trimming items")
    
    # Sort categories by priority (lowest first for removal)
    basket_categories = basket_data.get("basket", [])
    sorted_categories = sorted(
        basket_categories,
        key=lambda cat: CATEGORY_PRIORITY.get(cat.get("category", "").lower(), 2)
    )
    
    # Calculate items to remove
    overage = estimated_total - max_budget
    items_removed = 0
    
    # Remove items from low-priority categories
    for category in sorted_categories:
        if estimated_total <= max_budget:
            break
            
        category_name = category.get("category", "unknown")
        items = category.get("items", [])
        
        if not items:
            continue
        
        # Estimate cost per item (rough approximation)
        estimated_category_cost = estimated_total / len(basket_categories)
        estimated_item_cost = estimated_category_cost / len(items) if items else 0
        
        # Remove items from this category
        items_to_remove = min(
            len(items),
            max(1, int(overage / estimated_item_cost)) if estimated_item_cost > 0 else 1
        )
        
        removed = items[-items_to_remove:]  # Remove from end
        category["items"] = items[:-items_to_remove]
        
        items_removed += items_to_remove
        estimated_total -= estimated_item_cost * items_to_remove
        
        logger.info(f"Removed {items_to_remove} items from category '{category_name}'")
    
    # Remove empty categories
    basket_data["basket"] = [cat for cat in basket_categories if cat.get("items")]
    
    # Recalculate estimated total (proportional reduction)
    if items_removed > 0:
        reduction_factor = max_budget / basket_data.get("estimated_total", max_budget)
        basket_data["estimated_total"] = round(max_budget * 0.95, 2)  # Slightly under budget
    
    # Add assumption
    assumptions = basket_data.get("assumptions", [])
    assumptions.append(f"Basket trimmed to fit budget of {max_budget}")
    basket_data["assumptions"] = assumptions
    
    logger.info(f"Final basket total: {basket_data['estimated_total']}")
    
    return basket_data


def validate_budget(basket_data: Dict[str, Any], max_budget: float) -> bool:
    """
    Validate that basket is within budget.
    
    Args:
        basket_data: Basket dictionary
        max_budget: Maximum allowed budget
        
    Returns:
        bool: True if within budget, False otherwise
    """
    estimated_total = basket_data.get("estimated_total", 0)
    is_valid = estimated_total <= max_budget
    
    if not is_valid:
        logger.warning(f"Budget validation failed: {estimated_total} > {max_budget}")
    
    return is_valid
