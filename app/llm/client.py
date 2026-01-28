"""
LLM client for basket generation.

Handles all interactions with the OpenAI API including retry logic,
timeout handling, and deterministic settings.
"""

import asyncio
import logging
from typing import Optional

from openai import AsyncOpenAI, OpenAIError, APITimeoutError, RateLimitError
from app.config import get_settings

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Async LLM client with retry logic and error handling.
    
    Uses deterministic settings (temperature=0) for consistent outputs
    and enforces JSON-only responses.
    """
    
    def __init__(self):
        """Initialize the LLM client with settings from config."""
        settings = get_settings()
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            timeout=settings.llm_timeout
        )
        self.model = settings.openai_model
        self.temperature = settings.llm_temperature
        self.max_tokens = settings.llm_max_tokens
        self.max_retries = 3
        
    async def generate_basket(
        self,
        system_message: str,
        user_prompt: str
    ) -> Optional[str]:
        """
        Generate basket using LLM with retry logic.
        
        Args:
            system_message: System context for the LLM
            user_prompt: User prompt with intent and constraints
            
        Returns:
            Optional[str]: Raw LLM response as string, or None if all retries failed
        """
        for attempt in range(self.max_retries):
            try:
                logger.info(f"LLM request attempt {attempt + 1}/{self.max_retries}")
                
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    response_format={"type": "json_object"}  # Force JSON output
                )
                
                content = response.choices[0].message.content
                
                if content is None:
                    logger.warning("LLM returned None content")
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    return None
                
                logger.info("LLM request successful")
                return content
                
            except APITimeoutError:
                logger.warning(f"LLM request timeout on attempt {attempt + 1}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                logger.error("All retry attempts exhausted due to timeout")
                return None
                
            except RateLimitError:
                logger.warning(f"Rate limit hit on attempt {attempt + 1}")
                if attempt < self.max_retries - 1:
                    # Longer backoff for rate limits
                    await asyncio.sleep(5 * (2 ** attempt))
                    continue
                logger.error("All retry attempts exhausted due to rate limiting")
                return None
                
            except OpenAIError as e:
                logger.error(f"OpenAI API error on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                logger.error("All retry attempts exhausted due to API error")
                return None
                
            except Exception as e:
                logger.error(f"Unexpected error during LLM request: {e}")
                return None
        
        return None


# Singleton instance
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """
    Get LLM client singleton.
    
    Returns:
        LLMClient: Configured LLM client instance
    """
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
