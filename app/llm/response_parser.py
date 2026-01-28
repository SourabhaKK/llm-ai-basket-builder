"""
Response parser for LLM outputs.

Handles parsing, cleaning, and validation of LLM responses with
graceful error handling for malformed outputs.
"""

import json
import logging
import re
from typing import Optional, Dict, Any

from pydantic import ValidationError
from app.schemas.basket import BasketResponse

logger = logging.getLogger(__name__)


def clean_json_response(raw_response: str) -> str:
    """
    Clean LLM response to extract pure JSON.
    
    Removes markdown code blocks, extra whitespace, and other formatting
    that might prevent JSON parsing.
    
    Args:
        raw_response: Raw string response from LLM
        
    Returns:
        str: Cleaned JSON string
    """
    # Remove markdown code blocks if present
    cleaned = re.sub(r'^```json\s*', '', raw_response.strip())
    cleaned = re.sub(r'\s*```$', '', cleaned)
    cleaned = re.sub(r'^```\s*', '', cleaned)
    
    # Remove any leading/trailing whitespace
    cleaned = cleaned.strip()
    
    return cleaned


def parse_llm_response(raw_response: Optional[str]) -> Optional[Dict[str, Any]]:
    """
    Parse and validate LLM response.
    
    Args:
        raw_response: Raw string response from LLM
        
    Returns:
        Optional[Dict[str, Any]]: Parsed and validated basket data, or None if parsing failed
    """
    if raw_response is None:
        logger.error("Cannot parse None response")
        return None
    
    try:
        # Clean the response
        cleaned = clean_json_response(raw_response)
        logger.debug(f"Cleaned response: {cleaned[:200]}...")
        
        # Parse JSON
        parsed_data = json.loads(cleaned)
        logger.info("Successfully parsed JSON from LLM response")
        
        # Validate against Pydantic schema
        try:
            validated = BasketResponse(**parsed_data)
            logger.info("Response validated against schema")
            return validated.model_dump()
            
        except ValidationError as e:
            logger.error(f"Schema validation failed: {e}")
            logger.debug(f"Invalid data: {parsed_data}")
            return None
            
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}")
        logger.debug(f"Raw response: {raw_response[:500]}...")
        return None
        
    except Exception as e:
        logger.error(f"Unexpected error during response parsing: {e}")
        return None


def validate_basket_structure(basket_data: Dict[str, Any]) -> bool:
    """
    Perform additional structural validation on basket data.
    
    Checks for:
    - Non-empty basket
    - Valid estimated_total
    - All categories have items
    
    Args:
        basket_data: Parsed basket dictionary
        
    Returns:
        bool: True if structure is valid, False otherwise
    """
    try:
        # Check basket exists and is not empty
        if not basket_data.get("basket"):
            logger.warning("Basket is empty")
            return False
        
        # Check estimated_total is valid
        estimated_total = basket_data.get("estimated_total", -1)
        if estimated_total < 0:
            logger.warning(f"Invalid estimated_total: {estimated_total}")
            return False
        
        # Check all categories have items
        for category in basket_data["basket"]:
            if not category.get("items"):
                logger.warning(f"Category '{category.get('category')}' has no items")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error during structural validation: {e}")
        return False
