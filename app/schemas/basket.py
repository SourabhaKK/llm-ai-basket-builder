"""
Pydantic schemas for basket building API.

Defines request/response models with validation rules for type safety
and automatic API documentation.
"""

from typing import List
from pydantic import BaseModel, Field, field_validator


class StoreContext(BaseModel):
    """Store-specific context for basket building."""
    
    available_categories: List[str] = Field(
        ...,
        description="List of product categories available in the store",
        min_length=1,
        examples=[["produce", "dairy", "grains", "snacks"]]
    )
    currency: str = Field(
        default="GBP",
        description="Currency code for pricing",
        examples=["GBP", "USD", "EUR"]
    )


class BasketRequest(BaseModel):
    """Request schema for basket building endpoint."""
    
    user_intent: str = Field(
        ...,
        description="Natural language description of shopping intent",
        min_length=5,
        examples=["weekly grocery shopping for a vegetarian couple"]
    )
    budget: float = Field(
        ...,
        description="Maximum budget for the basket",
        gt=0,
        examples=[60.0]
    )
    preferences: List[str] = Field(
        default_factory=list,
        description="Dietary or shopping preferences",
        examples=[["vegetarian", "high-protein"]]
    )
    store_context: StoreContext = Field(
        ...,
        description="Store-specific context and constraints"
    )
    
    @field_validator('preferences')
    @classmethod
    def normalize_preferences(cls, v: List[str]) -> List[str]:
        """Normalize preferences to lowercase for consistent matching."""
        return [pref.lower().strip() for pref in v]


class BasketItem(BaseModel):
    """Individual item in a basket category."""
    
    name: str = Field(
        ...,
        description="Product name",
        min_length=1,
        examples=["Spinach"]
    )
    reason: str = Field(
        ...,
        description="Reason for including this item",
        min_length=1,
        examples=["High-protein vegetarian food"]
    )


class BasketCategory(BaseModel):
    """Category grouping of basket items."""
    
    category: str = Field(
        ...,
        description="Product category name",
        min_length=1,
        examples=["produce"]
    )
    items: List[BasketItem] = Field(
        ...,
        description="Items in this category",
        min_length=1
    )


class BasketResponse(BaseModel):
    """Response schema for basket building endpoint."""
    
    basket: List[BasketCategory] = Field(
        ...,
        description="Organized basket with categorized items",
        min_length=1
    )
    estimated_total: float = Field(
        ...,
        description="Estimated total cost of the basket",
        ge=0,
        examples=[57.20]
    )
    assumptions: List[str] = Field(
        default_factory=list,
        description="Assumptions made during basket building",
        examples=[["Budget distributed evenly across categories"]]
    )
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "basket": [
                    {
                        "category": "produce",
                        "items": [
                            {
                                "name": "Spinach",
                                "reason": "High-protein vegetarian food"
                            }
                        ]
                    }
                ],
                "estimated_total": 57.20,
                "assumptions": ["Budget distributed evenly across categories"]
            }
        }
