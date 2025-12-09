"""
Research Configuration Loader.

Loads configuration from research_config.yaml and provides
a unified interface for all research settings.
"""

import os
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


# Default config file path (relative to this module)
DEFAULT_CONFIG_PATH = Path(__file__).parent / "research_config.yaml"


@dataclass
class OutputConfig:
    """Output settings."""
    base_dir: str = "outputs/research"
    formats: List[str] = field(default_factory=lambda: ["md"])
    generate_comparison: bool = True


@dataclass
class SearchStrategyConfig:
    """Search strategy settings."""
    strategy: str = "free_first"  # free_first, free_only, auto, tavily_only
    min_free_sources: int = 100
    free_max_results_per_query: int = 10
    free_query_multiplier: float = 3.0
    tavily_refinement: bool = True
    max_tavily_refinement_queries: int = 5


@dataclass
class CacheConfig:
    """Cache and previous research reuse settings."""
    enabled: bool = True
    ttl_days: int = 7
    force_refresh: bool = False
    reuse_previous_research: bool = True
    verify_previous_content: bool = True
    max_previous_age_days: int = 30


@dataclass
class GapFillingConfig:
    """Gap-filling settings."""
    enabled: bool = True
    max_iterations: int = 3
    min_quality_score: float = 85.0
    max_gaps_allowed: int = 3


@dataclass
class DomainConfig:
    """Domain filtering settings."""
    include: List[str] = field(default_factory=list)
    exclude: List[str] = field(default_factory=list)


@dataclass
class RateLimitConfig:
    """Rate limiting settings."""
    max_retries: int = 3
    base_delay_seconds: float = 1.0
    duckduckgo_delay_seconds: float = 2.0


@dataclass
class ResearchConfig:
    """
    Complete research configuration.

    This is the main configuration object that contains all settings
    for the research system.
    """
    output: OutputConfig = field(default_factory=OutputConfig)
    depth: str = "comprehensive"
    search: SearchStrategyConfig = field(default_factory=SearchStrategyConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    gap_filling: GapFillingConfig = field(default_factory=GapFillingConfig)
    domains: DomainConfig = field(default_factory=DomainConfig)
    rate_limiting: RateLimitConfig = field(default_factory=RateLimitConfig)

    @classmethod
    def from_yaml(cls, yaml_data: Dict[str, Any]) -> "ResearchConfig":
        """Create config from YAML data."""
        output_data = yaml_data.get("output", {})
        search_data = yaml_data.get("search", {})
        cache_data = yaml_data.get("cache", {})
        gap_data = yaml_data.get("gap_filling", {})
        domain_data = yaml_data.get("domains", {})
        rate_data = yaml_data.get("rate_limiting", {})

        return cls(
            output=OutputConfig(
                base_dir=output_data.get("base_dir", "outputs/research"),
                formats=output_data.get("formats", ["md"]),
                generate_comparison=output_data.get("generate_comparison", True),
            ),
            depth=yaml_data.get("depth", "comprehensive"),
            search=SearchStrategyConfig(
                strategy=search_data.get("strategy", "free_first"),
                min_free_sources=search_data.get("min_free_sources", 100),
                free_max_results_per_query=search_data.get("free_max_results_per_query", 10),
                free_query_multiplier=search_data.get("free_query_multiplier", 3.0),
                tavily_refinement=search_data.get("tavily_refinement", True),
                max_tavily_refinement_queries=search_data.get("max_tavily_refinement_queries", 5),
            ),
            cache=CacheConfig(
                enabled=cache_data.get("enabled", True),
                ttl_days=cache_data.get("ttl_days", 7),
                force_refresh=cache_data.get("force_refresh", False),
                reuse_previous_research=cache_data.get("reuse_previous_research", True),
                verify_previous_content=cache_data.get("verify_previous_content", True),
                max_previous_age_days=cache_data.get("max_previous_age_days", 30),
            ),
            gap_filling=GapFillingConfig(
                enabled=gap_data.get("enabled", True),
                max_iterations=gap_data.get("max_iterations", 3),
                min_quality_score=gap_data.get("min_quality_score", 85.0),
                max_gaps_allowed=gap_data.get("max_gaps_allowed", 3),
            ),
            domains=DomainConfig(
                include=domain_data.get("include", []),
                exclude=domain_data.get("exclude", []),
            ),
            rate_limiting=RateLimitConfig(
                max_retries=rate_data.get("max_retries", 3),
                base_delay_seconds=rate_data.get("base_delay_seconds", 1.0),
                duckduckgo_delay_seconds=rate_data.get("duckduckgo_delay_seconds", 2.0),
            ),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "output": {
                "base_dir": self.output.base_dir,
                "formats": self.output.formats,
                "generate_comparison": self.output.generate_comparison,
            },
            "depth": self.depth,
            "search": {
                "strategy": self.search.strategy,
                "min_free_sources": self.search.min_free_sources,
                "free_max_results_per_query": self.search.free_max_results_per_query,
                "free_query_multiplier": self.search.free_query_multiplier,
                "tavily_refinement": self.search.tavily_refinement,
                "max_tavily_refinement_queries": self.search.max_tavily_refinement_queries,
            },
            "cache": {
                "enabled": self.cache.enabled,
                "ttl_days": self.cache.ttl_days,
                "force_refresh": self.cache.force_refresh,
                "reuse_previous_research": self.cache.reuse_previous_research,
                "verify_previous_content": self.cache.verify_previous_content,
                "max_previous_age_days": self.cache.max_previous_age_days,
            },
            "gap_filling": {
                "enabled": self.gap_filling.enabled,
                "max_iterations": self.gap_filling.max_iterations,
                "min_quality_score": self.gap_filling.min_quality_score,
                "max_gaps_allowed": self.gap_filling.max_gaps_allowed,
            },
            "domains": {
                "include": self.domains.include,
                "exclude": self.domains.exclude,
            },
            "rate_limiting": {
                "max_retries": self.rate_limiting.max_retries,
                "base_delay_seconds": self.rate_limiting.base_delay_seconds,
                "duckduckgo_delay_seconds": self.rate_limiting.duckduckgo_delay_seconds,
            },
        }


def load_config(config_path: Optional[Path] = None) -> ResearchConfig:
    """
    Load research configuration from YAML file.

    Args:
        config_path: Path to config file (defaults to research_config.yaml in this module's directory)

    Returns:
        ResearchConfig object with all settings
    """
    config_path = config_path or DEFAULT_CONFIG_PATH

    if not config_path.exists():
        print(f"[CONFIG] No config file found at {config_path}, using defaults")
        return ResearchConfig()

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            yaml_data = yaml.safe_load(f) or {}

        config = ResearchConfig.from_yaml(yaml_data)
        print(f"[CONFIG] Loaded configuration from {config_path}")
        return config

    except Exception as e:
        print(f"[CONFIG] Error loading config from {config_path}: {e}")
        print("[CONFIG] Using default configuration")
        return ResearchConfig()


def save_config(config: ResearchConfig, config_path: Optional[Path] = None) -> None:
    """
    Save research configuration to YAML file.

    Args:
        config: ResearchConfig object to save
        config_path: Path to save to (defaults to research_config.yaml)
    """
    config_path = config_path or DEFAULT_CONFIG_PATH

    try:
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config.to_dict(), f, default_flow_style=False, sort_keys=False)
        print(f"[CONFIG] Saved configuration to {config_path}")
    except Exception as e:
        print(f"[CONFIG] Error saving config to {config_path}: {e}")


# Global config instance (loaded on module import)
_global_config: Optional[ResearchConfig] = None


def get_config() -> ResearchConfig:
    """
    Get the global research configuration.

    Loads from file on first call, caches for subsequent calls.
    """
    global _global_config
    if _global_config is None:
        _global_config = load_config()
    return _global_config


def reload_config() -> ResearchConfig:
    """
    Reload the global configuration from file.

    Use this if the config file has been modified.
    """
    global _global_config
    _global_config = load_config()
    return _global_config
