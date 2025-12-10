"""Configuration for AI components."""
from pydantic import BaseModel, Field
from typing import Dict, Optional
import os
import logging

logger = logging.getLogger(__name__)


class AIComponentConfig(BaseModel):
    """Configuration for an individual AI component."""

    enabled: bool = True
    fallback_to_legacy: bool = True  # Use old logic if AI fails
    max_retries: int = 2
    timeout_seconds: float = 30.0
    cost_limit_per_call: float = 0.10
    preferred_model: Optional[str] = None

    class Config:
        extra = "allow"  # Allow additional fields


class AIConfig(BaseModel):
    """
    Global AI configuration.

    Controls which AI components are enabled and their behavior.
    Can be loaded from environment variables or set programmatically.

    Example:
        config = get_ai_config()

        # Check if sentiment is enabled
        if config.sentiment.enabled:
            # Use AI sentiment
            pass

        # Disable a component at runtime
        config.query_generation.enabled = False
    """

    # Component-specific configs
    sentiment: AIComponentConfig = Field(default_factory=AIComponentConfig)
    query_generation: AIComponentConfig = Field(default_factory=AIComponentConfig)
    quality_assessment: AIComponentConfig = Field(default_factory=AIComponentConfig)
    data_extraction: AIComponentConfig = Field(default_factory=AIComponentConfig)
    classification: AIComponentConfig = Field(default_factory=AIComponentConfig)
    contradiction_detection: AIComponentConfig = Field(default_factory=AIComponentConfig)

    # Global settings
    global_enabled: bool = True  # Master switch for all AI components
    log_prompts: bool = False  # Log all prompts (verbose)
    log_responses: bool = False  # Log all responses (verbose)
    track_costs: bool = True  # Track costs per call

    # Cost controls
    max_cost_per_research: float = 1.00  # Max cost for entire research
    warn_at_cost: float = 0.50  # Warn when cost exceeds this

    # Performance
    parallel_calls: bool = True  # Allow parallel AI calls
    cache_responses: bool = True  # Cache identical prompts

    @classmethod
    def from_env(cls) -> "AIConfig":
        """Load configuration from environment variables."""

        def get_bool(key: str, default: bool = True) -> bool:
            return os.getenv(key, str(default)).lower() in ("true", "1", "yes")

        def get_float(key: str, default: float) -> float:
            try:
                return float(os.getenv(key, default))
            except ValueError:
                return default

        config = cls(
            global_enabled=get_bool("AI_COMPONENTS_ENABLED", True),
            log_prompts=get_bool("AI_LOG_PROMPTS", False),
            log_responses=get_bool("AI_LOG_RESPONSES", False),
            track_costs=get_bool("AI_TRACK_COSTS", True),
            max_cost_per_research=get_float("AI_MAX_COST_PER_RESEARCH", 1.00),
            warn_at_cost=get_float("AI_WARN_AT_COST", 0.50),

            sentiment=AIComponentConfig(
                enabled=get_bool("AI_SENTIMENT_ENABLED", True),
                fallback_to_legacy=get_bool("AI_SENTIMENT_FALLBACK", True)
            ),
            query_generation=AIComponentConfig(
                enabled=get_bool("AI_QUERY_GEN_ENABLED", True),
                fallback_to_legacy=get_bool("AI_QUERY_GEN_FALLBACK", True)
            ),
            quality_assessment=AIComponentConfig(
                enabled=get_bool("AI_QUALITY_ENABLED", True),
                fallback_to_legacy=get_bool("AI_QUALITY_FALLBACK", True)
            ),
            data_extraction=AIComponentConfig(
                enabled=get_bool("AI_EXTRACTION_ENABLED", True),
                fallback_to_legacy=get_bool("AI_EXTRACTION_FALLBACK", True)
            ),
            classification=AIComponentConfig(
                enabled=get_bool("AI_CLASSIFICATION_ENABLED", True),
                fallback_to_legacy=get_bool("AI_CLASSIFICATION_FALLBACK", True)
            ),
            contradiction_detection=AIComponentConfig(
                enabled=get_bool("AI_CONTRADICTION_ENABLED", True),
                fallback_to_legacy=get_bool("AI_CONTRADICTION_FALLBACK", True)
            )
        )

        logger.info(f"AI Config loaded: global_enabled={config.global_enabled}")
        return config

    def is_component_enabled(self, component_name: str) -> bool:
        """Check if a specific component is enabled."""
        if not self.global_enabled:
            return False

        component_config = getattr(self, component_name.replace("-", "_"), None)
        if component_config and hasattr(component_config, 'enabled'):
            return component_config.enabled

        return False

    def get_component_config(self, component_name: str) -> Optional[AIComponentConfig]:
        """Get configuration for a specific component."""
        return getattr(self, component_name.replace("-", "_"), None)


# Global config instance
_ai_config: Optional[AIConfig] = None


def get_ai_config() -> AIConfig:
    """Get global AI configuration."""
    global _ai_config
    if _ai_config is None:
        _ai_config = AIConfig.from_env()
    return _ai_config


def set_ai_config(config: AIConfig):
    """Set global AI configuration."""
    global _ai_config
    _ai_config = config
    logger.info("AI Config updated programmatically")


def reset_ai_config():
    """Reset AI configuration to reload from environment."""
    global _ai_config
    _ai_config = None
