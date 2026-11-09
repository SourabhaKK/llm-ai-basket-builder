"""
Configuration management for LLM AI Basket Builder.

Loads environment variables and provides centralized access to application settings.
Uses Pydantic Settings for validation and type safety.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI API Configuration
    openai_api_key: str = Field(..., description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o-mini", description="OpenAI model to use")
    
    # LLM Settings
    llm_temperature: float = Field(default=0.0, ge=0.0, le=2.0, description="LLM temperature for deterministic outputs")
    llm_max_tokens: int = Field(default=2000, gt=0, description="Maximum tokens for LLM response")
    llm_timeout: int = Field(default=30, gt=0, description="LLM API timeout in seconds")
    
    # Application Settings
    log_level: str = Field(default="INFO", description="Logging level")
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Singleton instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """
    Get application settings singleton.
    
    Returns:
        Settings: Application configuration instance
    """
    global _settings
    if _settings is None:
        # Required fields are read from the environment, which mypy cannot see.
        _settings = Settings()  # type: ignore[call-arg]
    return _settings
