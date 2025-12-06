"""
Production Configuration (Phase 20.5).

Centralized configuration management:
- Environment-based config
- Validation
- Secure defaults
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import os
import logging


# ============================================================================
# Environment
# ============================================================================

class Environment(str, Enum):
    """Deployment environments."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


# ============================================================================
# Configuration Models
# ============================================================================

@dataclass
class LLMConfig:
    """LLM configuration."""
    provider: str = "anthropic"
    model: str = "claude-3-sonnet-20240229"
    api_key: str = ""
    max_tokens: int = 4096
    temperature: float = 0.1
    timeout_seconds: float = 60.0
    max_retries: int = 3

    @classmethod
    def from_env(cls) -> "LLMConfig":
        return cls(
            provider=os.getenv("LLM_PROVIDER", "anthropic"),
            model=os.getenv("LLM_MODEL", "claude-3-sonnet-20240229"),
            api_key=os.getenv("ANTHROPIC_API_KEY", ""),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "4096")),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")),
            timeout_seconds=float(os.getenv("LLM_TIMEOUT", "60")),
            max_retries=int(os.getenv("LLM_MAX_RETRIES", "3"))
        )


@dataclass
class SearchConfig:
    """Search API configuration."""
    provider: str = "tavily"
    api_key: str = ""
    max_results: int = 10
    timeout_seconds: float = 30.0

    @classmethod
    def from_env(cls) -> "SearchConfig":
        return cls(
            provider=os.getenv("SEARCH_PROVIDER", "tavily"),
            api_key=os.getenv("TAVILY_API_KEY", ""),
            max_results=int(os.getenv("SEARCH_MAX_RESULTS", "10")),
            timeout_seconds=float(os.getenv("SEARCH_TIMEOUT", "30"))
        )


@dataclass
class APIConfig:
    """API server configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    rate_limit_rpm: int = 60
    rate_limit_rph: int = 1000
    api_key_required: bool = False
    api_keys: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_env(cls) -> "APIConfig":
        cors = os.getenv("CORS_ORIGINS", "*").split(",")
        return cls(
            host=os.getenv("API_HOST", "0.0.0.0"),
            port=int(os.getenv("API_PORT", "8000")),
            workers=int(os.getenv("API_WORKERS", "4")),
            cors_origins=[o.strip() for o in cors],
            rate_limit_rpm=int(os.getenv("RATE_LIMIT_RPM", "60")),
            rate_limit_rph=int(os.getenv("RATE_LIMIT_RPH", "1000")),
            api_key_required=os.getenv("API_KEY_REQUIRED", "false").lower() == "true"
        )


@dataclass
class MonitoringConfig:
    """Monitoring configuration."""
    enabled: bool = True
    metrics_port: int = 9090
    log_level: str = "INFO"
    log_format: str = "json"
    alert_email: str = ""
    alert_slack_webhook: str = ""

    @classmethod
    def from_env(cls) -> "MonitoringConfig":
        return cls(
            enabled=os.getenv("MONITORING_ENABLED", "true").lower() == "true",
            metrics_port=int(os.getenv("METRICS_PORT", "9090")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_format=os.getenv("LOG_FORMAT", "json"),
            alert_email=os.getenv("ALERT_EMAIL", ""),
            alert_slack_webhook=os.getenv("ALERT_SLACK_WEBHOOK", "")
        )


@dataclass
class CostConfig:
    """Cost management configuration."""
    daily_budget: float = 10.0
    monthly_budget: float = 300.0
    alert_threshold: float = 0.8
    track_costs: bool = True

    @classmethod
    def from_env(cls) -> "CostConfig":
        return cls(
            daily_budget=float(os.getenv("DAILY_BUDGET", "10.0")),
            monthly_budget=float(os.getenv("MONTHLY_BUDGET", "300.0")),
            alert_threshold=float(os.getenv("COST_ALERT_THRESHOLD", "0.8")),
            track_costs=os.getenv("TRACK_COSTS", "true").lower() == "true"
        )


@dataclass
class ProductionConfig:
    """Complete production configuration."""
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    version: str = "1.0.0"
    service_name: str = "company-researcher"

    # Sub-configs
    llm: LLMConfig = field(default_factory=LLMConfig)
    search: SearchConfig = field(default_factory=SearchConfig)
    api: APIConfig = field(default_factory=APIConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    cost: CostConfig = field(default_factory=CostConfig)

    # Feature flags
    enable_caching: bool = True
    enable_quality_checks: bool = True
    enable_deep_research: bool = True
    max_parallel_agents: int = 4

    @classmethod
    def from_env(cls) -> "ProductionConfig":
        """Load configuration from environment variables."""
        env_str = os.getenv("ENVIRONMENT", "development").lower()
        try:
            environment = Environment(env_str)
        except ValueError:
            environment = Environment.DEVELOPMENT

        return cls(
            environment=environment,
            debug=os.getenv("DEBUG", "false").lower() == "true",
            version=os.getenv("SERVICE_VERSION", "1.0.0"),
            service_name=os.getenv("SERVICE_NAME", "company-researcher"),
            llm=LLMConfig.from_env(),
            search=SearchConfig.from_env(),
            api=APIConfig.from_env(),
            monitoring=MonitoringConfig.from_env(),
            cost=CostConfig.from_env(),
            enable_caching=os.getenv("ENABLE_CACHING", "true").lower() == "true",
            enable_quality_checks=os.getenv("ENABLE_QUALITY_CHECKS", "true").lower() == "true",
            enable_deep_research=os.getenv("ENABLE_DEEP_RESEARCH", "true").lower() == "true",
            max_parallel_agents=int(os.getenv("MAX_PARALLEL_AGENTS", "4"))
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (hiding secrets)."""
        return {
            "environment": self.environment.value,
            "debug": self.debug,
            "version": self.version,
            "service_name": self.service_name,
            "llm": {
                "provider": self.llm.provider,
                "model": self.llm.model,
                "api_key_set": bool(self.llm.api_key),
                "max_tokens": self.llm.max_tokens
            },
            "search": {
                "provider": self.search.provider,
                "api_key_set": bool(self.search.api_key)
            },
            "api": {
                "host": self.api.host,
                "port": self.api.port,
                "rate_limit_rpm": self.api.rate_limit_rpm
            },
            "features": {
                "caching": self.enable_caching,
                "quality_checks": self.enable_quality_checks,
                "deep_research": self.enable_deep_research,
                "max_parallel_agents": self.max_parallel_agents
            }
        }


# ============================================================================
# Configuration Validation
# ============================================================================

class ConfigValidationError(Exception):
    """Configuration validation error."""
    pass


def validate_config(config: ProductionConfig) -> List[str]:
    """
    Validate configuration.

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    # Check required API keys
    if not config.llm.api_key:
        errors.append("LLM API key not set (ANTHROPIC_API_KEY)")

    if not config.search.api_key:
        errors.append("Search API key not set (TAVILY_API_KEY)")

    # Check values
    if config.llm.max_tokens < 100:
        errors.append("LLM max_tokens too low (min 100)")

    if config.api.port < 1 or config.api.port > 65535:
        errors.append(f"Invalid API port: {config.api.port}")

    if config.cost.daily_budget <= 0:
        errors.append("Daily budget must be positive")

    if config.max_parallel_agents < 1:
        errors.append("max_parallel_agents must be at least 1")

    # Production-specific checks
    if config.environment == Environment.PRODUCTION:
        if config.debug:
            errors.append("Debug mode should be disabled in production")

        if "*" in config.api.cors_origins:
            errors.append("CORS should not allow all origins in production")

        if not config.api.api_key_required:
            errors.append("API key authentication recommended in production")

    return errors


def validate_or_raise(config: ProductionConfig):
    """Validate config and raise if invalid."""
    errors = validate_config(config)
    if errors:
        raise ConfigValidationError(
            f"Configuration validation failed:\n" +
            "\n".join(f"  - {e}" for e in errors)
        )


# ============================================================================
# Configuration Loading
# ============================================================================

_global_config: Optional[ProductionConfig] = None


def load_config(
    env_file: Optional[str] = None,
    validate: bool = True
) -> ProductionConfig:
    """
    Load configuration from environment.

    Args:
        env_file: Optional .env file path
        validate: Whether to validate config

    Returns:
        ProductionConfig instance
    """
    global _global_config

    # Load .env file if provided
    if env_file:
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
        except ImportError:
            pass

    config = ProductionConfig.from_env()

    # Validate
    if validate:
        errors = validate_config(config)
        if errors:
            logger = logging.getLogger("config")
            for error in errors:
                logger.warning(f"Config warning: {error}")

    _global_config = config
    return config


def get_config() -> ProductionConfig:
    """Get current configuration."""
    global _global_config
    if _global_config is None:
        _global_config = load_config(validate=False)
    return _global_config


def reload_config():
    """Reload configuration from environment."""
    global _global_config
    _global_config = None
    return load_config()


# ============================================================================
# Environment Helpers
# ============================================================================

def is_production() -> bool:
    """Check if running in production."""
    return get_config().environment == Environment.PRODUCTION


def is_development() -> bool:
    """Check if running in development."""
    return get_config().environment == Environment.DEVELOPMENT


def is_test() -> bool:
    """Check if running in test environment."""
    return get_config().environment == Environment.TEST


def get_environment() -> Environment:
    """Get current environment."""
    return get_config().environment
