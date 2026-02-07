"""
Multi-Model Routing System

Routes tasks to optimal LLM models based on:
- Task complexity and type
- Cost vs quality tradeoffs
- Token usage optimization
- Fallback handling

Usage:
    from company_researcher.llm.model_router import ModelRouter, TaskType

    router = ModelRouter()
    model, config = router.select_model(
        task_type=TaskType.REASONING,
        complexity="high",
        max_cost=0.05
    )
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from ..utils import get_config, get_logger, utc_now

logger = get_logger(__name__)


class TaskType(Enum):
    """Types of tasks for model routing."""

    REASONING = "reasoning"  # Complex analysis, synthesis
    EXTRACTION = "extraction"  # Structured data extraction
    SEARCH_QUERY = "search_query"  # Query generation
    SUMMARIZATION = "summarization"  # Text summarization
    CLASSIFICATION = "classification"  # Categorization tasks
    REFLECTION = "reflection"  # Quality assessment
    SYNTHESIS = "synthesis"  # Report generation
    SIMPLE = "simple"  # Basic tasks


class ModelTier(Enum):
    """Model capability tiers."""

    PREMIUM = "premium"  # Best quality, highest cost
    STANDARD = "standard"  # Good balance
    ECONOMY = "economy"  # Cost-effective
    FAST = "fast"  # Low latency


@dataclass
class ModelConfig:
    """Configuration for a specific model."""

    model_id: str
    provider: str
    tier: ModelTier
    cost_per_1k_input: float
    cost_per_1k_output: float
    max_tokens: int
    context_window: int
    strengths: List[TaskType]
    latency_ms: int = 1000
    supports_vision: bool = False
    supports_tools: bool = True

    @property
    def avg_cost_per_1k(self) -> float:
        """Average cost assuming 2:1 output:input ratio."""
        return (self.cost_per_1k_input + 2 * self.cost_per_1k_output) / 3


@dataclass
class RoutingDecision:
    """Result of model routing decision."""

    model_config: ModelConfig
    task_type: TaskType
    complexity: str
    estimated_cost: float
    reasoning: str
    fallback_models: List[ModelConfig] = field(default_factory=list)
    timestamp: datetime = field(default_factory=utc_now)


class ModelRegistry:
    """Registry of available models and their configurations."""

    # Anthropic Models
    CLAUDE_OPUS = ModelConfig(
        model_id="claude-3-opus-20240229",
        provider="anthropic",
        tier=ModelTier.PREMIUM,
        cost_per_1k_input=0.015,
        cost_per_1k_output=0.075,
        max_tokens=4096,
        context_window=200000,
        strengths=[TaskType.REASONING, TaskType.SYNTHESIS, TaskType.REFLECTION],
        latency_ms=3000,
        supports_vision=True,
    )

    CLAUDE_SONNET = ModelConfig(
        model_id="claude-sonnet-4-20250514",
        provider="anthropic",
        tier=ModelTier.STANDARD,
        cost_per_1k_input=0.003,
        cost_per_1k_output=0.015,
        max_tokens=8192,
        context_window=200000,
        strengths=[TaskType.REASONING, TaskType.EXTRACTION, TaskType.SYNTHESIS],
        latency_ms=1500,
        supports_vision=True,
    )

    CLAUDE_HAIKU = ModelConfig(
        model_id="claude-3-5-haiku-20241022",
        provider="anthropic",
        tier=ModelTier.ECONOMY,
        cost_per_1k_input=0.001,
        cost_per_1k_output=0.005,
        max_tokens=8192,
        context_window=200000,
        strengths=[TaskType.EXTRACTION, TaskType.CLASSIFICATION, TaskType.SIMPLE],
        latency_ms=500,
        supports_vision=True,
    )

    # OpenAI Models
    GPT4_TURBO = ModelConfig(
        model_id="gpt-4-turbo",
        provider="openai",
        tier=ModelTier.PREMIUM,
        cost_per_1k_input=0.01,
        cost_per_1k_output=0.03,
        max_tokens=4096,
        context_window=128000,
        strengths=[TaskType.REASONING, TaskType.SYNTHESIS],
        latency_ms=2000,
        supports_vision=True,
    )

    GPT4O = ModelConfig(
        model_id="gpt-4o",
        provider="openai",
        tier=ModelTier.STANDARD,
        cost_per_1k_input=0.005,
        cost_per_1k_output=0.015,
        max_tokens=4096,
        context_window=128000,
        strengths=[TaskType.EXTRACTION, TaskType.SUMMARIZATION, TaskType.SEARCH_QUERY],
        latency_ms=1000,
        supports_vision=True,
    )

    GPT4O_MINI = ModelConfig(
        model_id="gpt-4o-mini",
        provider="openai",
        tier=ModelTier.ECONOMY,
        cost_per_1k_input=0.00015,
        cost_per_1k_output=0.0006,
        max_tokens=16384,
        context_window=128000,
        strengths=[TaskType.SIMPLE, TaskType.CLASSIFICATION, TaskType.SEARCH_QUERY],
        latency_ms=300,
        supports_vision=True,
    )

    GPT35_TURBO = ModelConfig(
        model_id="gpt-3.5-turbo",
        provider="openai",
        tier=ModelTier.FAST,
        cost_per_1k_input=0.0005,
        cost_per_1k_output=0.0015,
        max_tokens=4096,
        context_window=16385,
        strengths=[TaskType.SIMPLE, TaskType.SEARCH_QUERY],
        latency_ms=200,
    )

    # DeepSeek Models (ULTRA LOW COST)
    DEEPSEEK_V3 = ModelConfig(
        model_id="deepseek-chat",
        provider="deepseek",
        tier=ModelTier.ECONOMY,
        cost_per_1k_input=0.00014,  # $0.14/1M
        cost_per_1k_output=0.00027,  # $0.27/1M
        max_tokens=8000,
        context_window=128000,
        strengths=[
            TaskType.EXTRACTION,
            TaskType.SUMMARIZATION,
            TaskType.CLASSIFICATION,
            TaskType.SIMPLE,
        ],
        latency_ms=800,
        supports_tools=True,
    )

    DEEPSEEK_R1 = ModelConfig(
        model_id="deepseek-reasoner",
        provider="deepseek",
        tier=ModelTier.STANDARD,
        cost_per_1k_input=0.00055,  # $0.55/1M
        cost_per_1k_output=0.00219,  # $2.19/1M
        max_tokens=8000,
        context_window=128000,
        strengths=[TaskType.REASONING, TaskType.REFLECTION, TaskType.SYNTHESIS],
        latency_ms=2000,
        supports_tools=True,
    )

    # Groq (FAST + CHEAP)
    GROQ_LLAMA70B = ModelConfig(
        model_id="llama-3.3-70b-versatile",
        provider="groq",
        tier=ModelTier.FAST,
        cost_per_1k_input=0.00059,  # $0.59/1M
        cost_per_1k_output=0.00079,  # $0.79/1M
        max_tokens=32768,
        context_window=128000,
        strengths=[
            TaskType.EXTRACTION,
            TaskType.SUMMARIZATION,
            TaskType.SEARCH_QUERY,
            TaskType.SIMPLE,
        ],
        latency_ms=200,  # Very fast
        supports_tools=True,
    )

    @classmethod
    def get_all_models(cls) -> List[ModelConfig]:
        """Get all registered models."""
        return [
            cls.CLAUDE_OPUS,
            cls.CLAUDE_SONNET,
            cls.CLAUDE_HAIKU,
            cls.GPT4_TURBO,
            cls.GPT4O,
            cls.GPT4O_MINI,
            cls.GPT35_TURBO,
            cls.DEEPSEEK_V3,
            cls.DEEPSEEK_R1,
            cls.GROQ_LLAMA70B,
        ]

    @classmethod
    def get_by_tier(cls, tier: ModelTier) -> List[ModelConfig]:
        """Get models by tier."""
        return [m for m in cls.get_all_models() if m.tier == tier]

    @classmethod
    def get_by_provider(cls, provider: str) -> List[ModelConfig]:
        """Get models by provider."""
        return [m for m in cls.get_all_models() if m.provider == provider]


class ModelRouter:
    """
    Intelligent model routing based on task requirements.

    Selects optimal model considering:
    - Task type and complexity
    - Cost constraints
    - Quality requirements
    - Latency needs
    """

    # Complexity multipliers for cost estimation
    COMPLEXITY_MULTIPLIERS = {"low": 0.5, "medium": 1.0, "high": 2.0, "very_high": 3.0}

    # Task type to typical token counts
    TASK_TOKEN_ESTIMATES = {
        TaskType.REASONING: {"input": 2000, "output": 1500},
        TaskType.EXTRACTION: {"input": 3000, "output": 500},
        TaskType.SEARCH_QUERY: {"input": 500, "output": 200},
        TaskType.SUMMARIZATION: {"input": 4000, "output": 800},
        TaskType.CLASSIFICATION: {"input": 1000, "output": 100},
        TaskType.REFLECTION: {"input": 2500, "output": 1000},
        TaskType.SYNTHESIS: {"input": 5000, "output": 2000},
        TaskType.SIMPLE: {"input": 500, "output": 300},
    }

    def __init__(
        self,
        preferred_provider: Optional[str] = None,
        max_cost_per_call: float = 0.10,
        quality_priority: float = 0.5,  # 0 = cost focused, 1 = quality focused
        enable_fallbacks: bool = True,
    ):
        self.preferred_provider = preferred_provider or get_config(
            "PREFERRED_LLM_PROVIDER", default="groq"
        )
        self.max_cost_per_call = max_cost_per_call
        self.quality_priority = quality_priority
        self.enable_fallbacks = enable_fallbacks
        self.usage_stats: Dict[str, Dict[str, Any]] = {}

    def select_model(
        self,
        task_type: TaskType,
        complexity: str = "medium",
        max_cost: Optional[float] = None,
        require_vision: bool = False,
        require_tools: bool = False,
        prefer_low_latency: bool = False,
        context_size_needed: int = 0,
    ) -> RoutingDecision:
        """
        Select optimal model for a task.

        Args:
            task_type: Type of task to perform
            complexity: Task complexity (low, medium, high, very_high)
            max_cost: Maximum cost constraint (overrides default)
            require_vision: Whether vision capability is needed
            require_tools: Whether tool use is needed
            prefer_low_latency: Prioritize fast response
            context_size_needed: Minimum context window size

        Returns:
            RoutingDecision with selected model and reasoning
        """
        max_cost = max_cost or self.max_cost_per_call
        candidates = self._get_candidates(
            task_type=task_type,
            require_vision=require_vision,
            require_tools=require_tools,
            context_size_needed=context_size_needed,
        )

        if not candidates:
            # Fallback to any available model
            candidates = ModelRegistry.get_all_models()

        # Score each candidate
        scored = []
        for model in candidates:
            score, reasoning = self._score_model(
                model=model,
                task_type=task_type,
                complexity=complexity,
                max_cost=max_cost,
                prefer_low_latency=prefer_low_latency,
            )
            if score > 0:
                scored.append((model, score, reasoning))

        # Sort by score (highest first)
        scored.sort(key=lambda x: x[1], reverse=True)

        if not scored:
            # Use default fallback
            default = ModelRegistry.CLAUDE_SONNET
            return RoutingDecision(
                model_config=default,
                task_type=task_type,
                complexity=complexity,
                estimated_cost=self._estimate_cost(default, task_type, complexity),
                reasoning="No suitable model found, using default",
                fallback_models=[],
            )

        selected, _, reasoning = scored[0]
        fallbacks = [m for m, _, _ in scored[1:4]] if self.enable_fallbacks else []

        return RoutingDecision(
            model_config=selected,
            task_type=task_type,
            complexity=complexity,
            estimated_cost=self._estimate_cost(selected, task_type, complexity),
            reasoning=reasoning,
            fallback_models=fallbacks,
        )

    def _get_candidates(
        self,
        task_type: TaskType,
        require_vision: bool,
        require_tools: bool,
        context_size_needed: int,
    ) -> List[ModelConfig]:
        """Filter models that meet requirements."""
        candidates = []

        for model in ModelRegistry.get_all_models():
            # Check vision requirement
            if require_vision and not model.supports_vision:
                continue

            # Check tools requirement
            if require_tools and not model.supports_tools:
                continue

            # Check context size
            if context_size_needed > model.context_window:
                continue

            # Prefer models good at this task type
            if task_type in model.strengths:
                candidates.append(model)

        # If no specialists, include all that meet requirements
        if not candidates:
            for model in ModelRegistry.get_all_models():
                if require_vision and not model.supports_vision:
                    continue
                if require_tools and not model.supports_tools:
                    continue
                if context_size_needed > model.context_window:
                    continue
                candidates.append(model)

        return candidates

    def _score_model(
        self,
        model: ModelConfig,
        task_type: TaskType,
        complexity: str,
        max_cost: float,
        prefer_low_latency: bool,
    ) -> Tuple[float, str]:
        """Score a model for the given task."""
        score = 100.0
        reasons = []

        # Estimate cost
        estimated_cost = self._estimate_cost(model, task_type, complexity)

        # Cost check (hard constraint)
        if estimated_cost > max_cost:
            return 0.0, f"Exceeds cost limit (${estimated_cost:.4f} > ${max_cost:.4f})"

        # Quality score (based on tier)
        tier_scores = {
            ModelTier.PREMIUM: 40,
            ModelTier.STANDARD: 30,
            ModelTier.ECONOMY: 20,
            ModelTier.FAST: 10,
        }
        quality_score = tier_scores[model.tier] * self.quality_priority
        score += quality_score
        reasons.append(f"Quality: +{quality_score:.1f}")

        # Cost efficiency score
        cost_score = (1 - estimated_cost / max_cost) * 30 * (1 - self.quality_priority)
        score += cost_score
        reasons.append(f"Cost efficiency: +{cost_score:.1f}")

        # Task specialization bonus
        if task_type in model.strengths:
            score += 20
            reasons.append("Task specialist: +20")

        # Provider preference
        if model.provider == self.preferred_provider:
            score += 10
            reasons.append("Preferred provider: +10")

        # Latency preference
        if prefer_low_latency:
            latency_score = max(0, 20 - model.latency_ms / 100)
            score += latency_score
            reasons.append(f"Latency: +{latency_score:.1f}")

        # Complexity matching
        if complexity in ["high", "very_high"] and model.tier in [
            ModelTier.PREMIUM,
            ModelTier.STANDARD,
        ]:
            score += 15
            reasons.append("High complexity match: +15")
        elif complexity in ["low"] and model.tier in [ModelTier.ECONOMY, ModelTier.FAST]:
            score += 15
            reasons.append("Low complexity match: +15")

        return score, " | ".join(reasons)

    def _estimate_cost(self, model: ModelConfig, task_type: TaskType, complexity: str) -> float:
        """Estimate cost for a task."""
        tokens = self.TASK_TOKEN_ESTIMATES.get(task_type, {"input": 1000, "output": 500})
        multiplier = self.COMPLEXITY_MULTIPLIERS.get(complexity, 1.0)

        input_tokens = tokens["input"] * multiplier
        output_tokens = tokens["output"] * multiplier

        cost = (input_tokens / 1000) * model.cost_per_1k_input + (
            output_tokens / 1000
        ) * model.cost_per_1k_output

        return cost

    def record_usage(
        self,
        model_id: str,
        task_type: TaskType,
        input_tokens: int,
        output_tokens: int,
        latency_ms: int,
        success: bool,
    ):
        """Record model usage for analytics."""
        if model_id not in self.usage_stats:
            self.usage_stats[model_id] = {
                "total_calls": 0,
                "successful_calls": 0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "total_latency_ms": 0,
                "by_task_type": {},
            }

        stats = self.usage_stats[model_id]
        stats["total_calls"] += 1
        if success:
            stats["successful_calls"] += 1
        stats["total_input_tokens"] += input_tokens
        stats["total_output_tokens"] += output_tokens
        stats["total_latency_ms"] += latency_ms

        task_key = task_type.value
        if task_key not in stats["by_task_type"]:
            stats["by_task_type"][task_key] = {"calls": 0, "tokens": 0}
        stats["by_task_type"][task_key]["calls"] += 1
        stats["by_task_type"][task_key]["tokens"] += input_tokens + output_tokens

    def get_usage_report(self) -> Dict[str, Any]:
        """Get usage statistics report."""
        report = {
            "models": {},
            "totals": {"calls": 0, "input_tokens": 0, "output_tokens": 0, "estimated_cost": 0.0},
        }

        for model_id, stats in self.usage_stats.items():
            # Find model config
            model_config = None
            for m in ModelRegistry.get_all_models():
                if m.model_id == model_id:
                    model_config = m
                    break

            if model_config:
                cost = (stats["total_input_tokens"] / 1000) * model_config.cost_per_1k_input + (
                    stats["total_output_tokens"] / 1000
                ) * model_config.cost_per_1k_output
            else:
                cost = 0.0

            report["models"][model_id] = {
                **stats,
                "estimated_cost": cost,
                "avg_latency_ms": stats["total_latency_ms"] / max(stats["total_calls"], 1),
                "success_rate": stats["successful_calls"] / max(stats["total_calls"], 1),
            }

            report["totals"]["calls"] += stats["total_calls"]
            report["totals"]["input_tokens"] += stats["total_input_tokens"]
            report["totals"]["output_tokens"] += stats["total_output_tokens"]
            report["totals"]["estimated_cost"] += cost

        return report


# Convenience functions
def get_model_for_task(
    task_type: TaskType, complexity: str = "medium", **kwargs
) -> Tuple[str, str]:
    """
    Quick function to get model ID and provider for a task.

    Returns:
        Tuple of (model_id, provider)
    """
    router = ModelRouter()
    decision = router.select_model(task_type=task_type, complexity=complexity, **kwargs)
    return decision.model_config.model_id, decision.model_config.provider


def create_router_for_research() -> ModelRouter:
    """Create a router optimized for research tasks."""
    return ModelRouter(
        preferred_provider="groq",
        max_cost_per_call=0.15,
        quality_priority=0.7,  # Favor quality for research
        enable_fallbacks=True,
    )


def create_router_for_extraction() -> ModelRouter:
    """Create a router optimized for data extraction."""
    return ModelRouter(
        preferred_provider="openai",
        max_cost_per_call=0.05,
        quality_priority=0.3,  # Favor cost for extraction
        enable_fallbacks=True,
    )
