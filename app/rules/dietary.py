"""
Dietary constraint validation.

Filters basket items to ensure compliance with dietary preferences
such as vegetarian, vegan, gluten-free, and dairy-free.
"""

import logging
from typing import Dict, Any, List, Set

logger = logging.getLogger(__name__)


# Keywords that indicate non-compliance with dietary preferences
DIETARY_FILTERS = {
    "vegetarian": {
        "exclude_keywords": ["meat", "chicken", "beef", "pork", "fish", "seafood", "lamb", "turkey", "bacon", "sausage"],
        "description": "vegetarian"
    },
    "vegan": {
        "exclude_keywords": ["meat", "chicken", "beef", "pork", "fish", "seafood", "lamb", "turkey", "bacon", "sausage",
                            "dairy", "milk", "cheese", "yogurt", "butter", "cream", "egg", "honey"],
        "description": "vegan"
    },
    "gluten-free": {
        "exclude_keywords": ["wheat", "bread", "pasta", "flour", "barley", "rye", "cereal", "couscous"],
        "description": "gluten-free"
    },
    "dairy-free": {
        "exclude_keywords": ["dairy", "milk", "cheese", "yogurt", "butter", "cream", "whey", "casein"],
        "description": "dairy-free"
    },
}


def check_item_compliance(item_name: str, item_reason: str, preference: str) -> bool:
    """
    Check if an item complies with a dietary preference.
    
    Args:
        item_name: Name of the item
        item_reason: Reason for including the item
        preference: Dietary preference (e.g., "vegetarian")
        
    Returns:
        bool: True if compliant, False if violates preference
    """
    filter_config = DIETARY_FILTERS.get(preference.lower())
    
    if not filter_config:
        # Unknown preference, assume compliant
        return True
    
    exclude_keywords = filter_config["exclude_keywords"]
    
    # Check both name and reason for excluded keywords
    combined_text = f"{item_name} {item_reason}".lower()
    
    for keyword in exclude_keywords:
        if keyword in combined_text:
            logger.debug(f"Item '{item_name}' violates {preference} due to keyword '{keyword}'")
            return False
    
    return True


def validate_dietary_preferences(
    basket_data: Dict[str, Any],
    preferences: List[str]
) -> Dict[str, Any]:
    """
    Validate and filter basket items based on dietary preferences.
    
    Removes items that violate any of the specified dietary preferences.
    
    Args:
        basket_data: Parsed basket dictionary
        preferences: List of dietary preferences (e.g., ["vegetarian", "gluten-free"])
        
    Returns:
        Dict[str, Any]: Filtered basket data
    """
    if not preferences:
        logger.info("No dietary preferences to validate")
        return basket_data
    
    logger.info(f"Validating dietary preferences: {preferences}")
    
    filtered_basket = []
    items_removed = 0
    
    for category in basket_data.get("basket", []):
        category_name = category.get("category", "unknown")
        items = category.get("items", [])
        
        filtered_items = []
        
        for item in items:
            item_name = item.get("name", "")
            item_reason = item.get("reason", "")
            
            # Check compliance with all preferences
            is_compliant = all(
                check_item_compliance(item_name, item_reason, pref)
                for pref in preferences
            )
            
            if is_compliant:
                filtered_items.append(item)
            else:
                items_removed += 1
                logger.info(f"Removed '{item_name}' from category '{category_name}' due to dietary preferences")
        
        # Only include category if it has items
        if filtered_items:
            filtered_basket.append({
                "category": category_name,
                "items": filtered_items
            })
    
    basket_data["basket"] = filtered_basket
    
    # Add assumption if items were removed
    if items_removed > 0:
        assumptions = basket_data.get("assumptions", [])
        pref_str = ", ".join(preferences)
        assumptions.append(f"Filtered {items_removed} items to comply with {pref_str} preferences")
        basket_data["assumptions"] = assumptions
        
        logger.info(f"Removed {items_removed} items total for dietary compliance")
    
    return basket_data


def get_supported_preferences() -> List[str]:
    """
    Get list of supported dietary preferences.
    
    Returns:
        List[str]: Supported preference names
    """
    return list(DIETARY_FILTERS.keys())
