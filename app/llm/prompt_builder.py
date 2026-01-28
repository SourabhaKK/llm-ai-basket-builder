"""
Prompt builder for LLM basket generation.

Constructs structured prompts that force JSON-only outputs from the LLM
and include all necessary context for basket building.
"""

from app.schemas.basket import BasketRequest


def build_basket_prompt(request: BasketRequest) -> str:
    """
    Build a structured prompt for basket generation.
    
    The prompt is designed to:
    - Force JSON-only output (no markdown, no explanations)
    - Include explicit schema definition
    - Inject all user constraints (budget, preferences, categories)
    - Guide the LLM to respect business rules
    
    Args:
        request: Validated basket request with user intent and constraints
        
    Returns:
        str: Formatted prompt for LLM
    """
    
    # Format preferences for readability
    preferences_str = ", ".join(request.preferences) if request.preferences else "none specified"
    
    # Format categories
    categories_str = ", ".join(request.store_context.available_categories)
    
    prompt = f"""You are a shopping assistant that helps build grocery baskets based on user intent.

USER INTENT: {request.user_intent}

CONSTRAINTS:
- Budget: {request.budget} {request.store_context.currency}
- Dietary/Shopping Preferences: {preferences_str}
- Available Categories: {categories_str}

INSTRUCTIONS:
1. Recommend products that match the user's intent and preferences
2. Organize items by category (only use the available categories listed above)
3. Ensure the estimated total does NOT exceed the budget
4. If preferences include dietary restrictions (vegetarian, vegan, gluten-free, dairy-free), only recommend appropriate items
5. Distribute the budget sensibly across categories based on the user intent
6. For each item, provide a brief reason explaining why it was chosen

CRITICAL: You MUST respond with ONLY valid JSON matching this exact schema. Do not include markdown formatting, code blocks, or any text outside the JSON structure.

{{
  "basket": [
    {{
      "category": "category_name",
      "items": [
        {{
          "name": "Product Name",
          "reason": "Brief explanation"
        }}
      ]
    }}
  ],
  "estimated_total": 0.0,
  "assumptions": ["List any assumptions you made"]
}}

Return ONLY the JSON object, nothing else."""

    return prompt


def build_system_message() -> str:
    """
    Build the system message for LLM context.
    
    Returns:
        str: System message defining the assistant's role
    """
    return """You are a professional shopping assistant AI that helps users build grocery baskets. 
You always respond with valid JSON only, never with markdown formatting or explanations outside the JSON structure.
You are precise, helpful, and respect all user constraints including budget and dietary preferences."""
