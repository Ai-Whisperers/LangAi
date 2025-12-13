"""
Smart LLM Client - Automatic model routing for cost optimization.

Routes tasks to optimal models based on:
- Task type (extraction, reasoning, synthesis, etc.)
- Complexity level
- Cost constraints
- Quality requirements

Cost hierarchy:
- DRAFTS/EXTRACTION: DeepSeek V3 ($0.14/1M) or GPT-4o-mini ($0.15/1M)
- ANALYSIS: DeepSeek R1 ($0.55/1M) or Groq Llama-70B ($0.59/1M)
- FINAL OUTPUT: Claude 3.5 Sonnet ($3/1M) or Claude Haiku ($1/1M)

Usage:
    from company_researcher.llm.smart_client import (
        get_smart_client,
        smart_completion,
        extract_data,
        analyze_text,
        generate_report
    )

    client = get_smart_client()

    # Automatic routing based on task
    result = client.complete(
        prompt="Extract financial data...",
        task_type="extraction"
    )

    # Or use convenience functions
    data = extract_data("Tesla", search_results)  # Uses DeepSeek
    report = generate_report(analysis)  # Uses Claude
"""

from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass
from threading import Lock

from anthropic import Anthropic
from openai import OpenAI

from .model_router import ModelRouter, TaskType
from .deepseek_client import DeepSeekClient
from ..utils import get_config, get_logger, utc_now

logger = get_logger(__name__)


@dataclass
class CompletionResult:
    """Result from smart completion."""
    content: str
    model: str
    provider: str
    input_tokens: int
    output_tokens: int
    cost: float
    task_type: str
    routing_reason: str
    latency_ms: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "model": self.model,
            "provider": self.provider,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cost": self.cost,
            "task_type": self.task_type,
            "routing_reason": self.routing_reason,
            "latency_ms": self.latency_ms
        }


class SmartLLMClient:
    """
    Smart LLM client with automatic model routing.

    Automatically selects the most cost-effective model for each task
    while maintaining quality requirements.

    Routing strategy:
    - Simple/extraction tasks → DeepSeek V3, GPT-4o-mini, Groq
    - Complex reasoning → DeepSeek R1, Claude Haiku
    - Final outputs → Claude Sonnet
    """

    def __init__(
        self,
        anthropic_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        deepseek_api_key: Optional[str] = None,
        groq_api_key: Optional[str] = None,
        quality_priority: float = 0.5,
        max_cost_per_call: float = 0.10,
        enable_fallbacks: bool = True
    ):
        """
        Initialize smart client with available providers.

        Args:
            anthropic_api_key: Anthropic API key
            openai_api_key: OpenAI API key
            deepseek_api_key: DeepSeek API key
            groq_api_key: Groq API key
            quality_priority: Balance between quality (1.0) and cost (0.0)
            max_cost_per_call: Maximum cost per API call
            enable_fallbacks: Enable automatic fallbacks on error
        """
        # Initialize clients
        self._anthropic = None
        self._openai = None
        self._deepseek = None
        self._groq = None

        # Anthropic
        anthropic_key = anthropic_api_key or get_config("ANTHROPIC_API_KEY")
        if anthropic_key:
            self._anthropic = Anthropic(api_key=anthropic_key)
            logger.info("Anthropic client initialized")

        # OpenAI
        openai_key = openai_api_key or get_config("OPENAI_API_KEY")
        if openai_key:
            self._openai = OpenAI(api_key=openai_key)
            logger.info("OpenAI client initialized")

        # DeepSeek
        deepseek_key = deepseek_api_key or get_config("DEEPSEEK_API_KEY")
        if deepseek_key:
            self._deepseek = DeepSeekClient(api_key=deepseek_key)
            logger.info("DeepSeek client initialized")

        # Groq
        groq_key = groq_api_key or get_config("GROQ_API_KEY")
        if groq_key:
            self._groq = OpenAI(
                api_key=groq_key,
                base_url="https://api.groq.com/openai/v1"
            )
            logger.info("Groq client initialized")

        # Model router
        self._router = ModelRouter(
            quality_priority=quality_priority,
            max_cost_per_call=max_cost_per_call,
            enable_fallbacks=enable_fallbacks
        )

        # Usage tracking
        self._total_cost = 0.0
        self._total_calls = 0
        self._usage_by_provider: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()

    def _get_available_providers(self) -> List[str]:
        """Get list of available providers."""
        providers = []
        if self._anthropic:
            providers.append("anthropic")
        if self._openai:
            providers.append("openai")
        if self._deepseek:
            providers.append("deepseek")
        if self._groq:
            providers.append("groq")
        return providers

    def complete(
        self,
        prompt: str,
        task_type: Union[str, TaskType] = "simple",
        system: Optional[str] = None,
        complexity: str = "medium",
        max_tokens: int = 4000,
        temperature: float = 0.0,
        force_provider: Optional[str] = None,
        force_model: Optional[str] = None,
        json_mode: bool = False
    ) -> CompletionResult:
        """
        Create completion with automatic model routing.

        Args:
            prompt: User prompt
            task_type: Type of task (extraction, reasoning, synthesis, etc.)
            system: System prompt
            complexity: Task complexity (low, medium, high, very_high)
            max_tokens: Maximum output tokens
            temperature: Sampling temperature
            force_provider: Override provider selection
            force_model: Override model selection
            json_mode: Enable JSON output mode

        Returns:
            CompletionResult with content and metadata
        """
        # Convert string to TaskType
        if isinstance(task_type, str):
            try:
                task_type = TaskType(task_type)
            except ValueError:
                task_type = TaskType.SIMPLE

        # Select model
        if force_model:
            model_id = force_model
            provider = force_provider or self._infer_provider(force_model)
            routing_reason = f"Forced: {model_id}"
        else:
            decision = self._router.select_model(
                task_type=task_type,
                complexity=complexity
            )
            model_id = decision.model_config.model_id
            provider = force_provider or decision.model_config.provider
            routing_reason = decision.reasoning

        # Check provider availability
        available = self._get_available_providers()
        if provider not in available:
            # Fallback to available provider - prioritize Groq (fast, cheap, no rate limits)
            if "groq" in available:
                provider = "groq"
                model_id = "llama-3.3-70b-versatile"
            elif "deepseek" in available:
                provider = "deepseek"
                model_id = "deepseek-chat"
            elif "openai" in available:
                provider = "openai"
                model_id = "gpt-4o-mini"
            elif "anthropic" in available:
                provider = "anthropic"
                model_id = "claude-sonnet-4-20250514"
            else:
                raise ValueError("No LLM providers available")
            routing_reason = f"Fallback to {provider}/{model_id}"

        logger.info(f"Routing: {task_type.value} -> {provider}/{model_id}")

        # Execute completion with automatic fallback on rate limit errors
        start_time = utc_now()
        try:
            result = self._execute_completion(
                provider=provider,
                model=model_id,
                prompt=prompt,
                system=system,
                max_tokens=max_tokens,
                temperature=temperature,
                json_mode=json_mode
            )
        except Exception as e:
            error_msg = str(e).lower()
            # Check for rate limit, billing, authentication, or API errors
            # 400 = billing/credit issues, 401 = auth issues, 429 = rate limit
            is_recoverable = (
                "rate" in error_msg or
                "limit" in error_msg or
                "429" in str(e) or
                "400" in str(e) or  # Billing/credit exhausted
                "401" in str(e) or  # Authentication errors (invalid/expired key)
                "authentication" in error_msg or
                "invalid" in error_msg or  # Invalid API key
                "credit" in error_msg or
                "quota" in error_msg or
                "billing" in error_msg or
                "payment" in error_msg or
                "insufficient" in error_msg
            )
            if is_recoverable:
                logger.warning(f"API error for {provider} ({str(e)[:100]}), falling back to alternative provider")
                # Try Groq as fallback
                if provider != "groq" and self._groq:
                    provider = "groq"
                    model_id = "llama-3.3-70b-versatile"
                    routing_reason = f"Fallback to {provider}/{model_id} (rate limit)"
                    result = self._execute_completion(
                        provider=provider,
                        model=model_id,
                        prompt=prompt,
                        system=system,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        json_mode=json_mode
                    )
                # Try DeepSeek as second fallback
                elif provider != "deepseek" and self._deepseek:
                    provider = "deepseek"
                    model_id = "deepseek-chat"
                    routing_reason = f"Fallback to {provider}/{model_id} (rate limit)"
                    result = self._execute_completion(
                        provider=provider,
                        model=model_id,
                        prompt=prompt,
                        system=system,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        json_mode=json_mode
                    )
                else:
                    raise  # Re-raise if no fallback available
            else:
                raise  # Re-raise non-rate-limit errors
        latency_ms = int((utc_now() - start_time).total_seconds() * 1000)

        # Track usage
        self._track_usage(provider, result["cost"], result["input_tokens"], result["output_tokens"])

        return CompletionResult(
            content=result["content"],
            model=model_id,
            provider=provider,
            input_tokens=result["input_tokens"],
            output_tokens=result["output_tokens"],
            cost=result["cost"],
            task_type=task_type.value,
            routing_reason=routing_reason,
            latency_ms=latency_ms
        )

    def _infer_provider(self, model_id: str) -> str:
        """Infer provider from model ID."""
        if "claude" in model_id:
            return "anthropic"
        elif "gpt" in model_id:
            return "openai"
        elif "deepseek" in model_id:
            return "deepseek"
        elif "llama" in model_id or "mixtral" in model_id:
            return "groq"
        return "anthropic"  # Default

    def _execute_completion(
        self,
        provider: str,
        model: str,
        prompt: str,
        system: Optional[str],
        max_tokens: int,
        temperature: float,
        json_mode: bool
    ) -> Dict[str, Any]:
        """Execute completion with specific provider."""

        if provider == "anthropic":
            return self._anthropic_completion(model, prompt, system, max_tokens, temperature)
        elif provider == "openai":
            return self._openai_completion(model, prompt, system, max_tokens, temperature, json_mode)
        elif provider == "deepseek":
            return self._deepseek_completion(model, prompt, system, max_tokens, temperature, json_mode)
        elif provider == "groq":
            return self._groq_completion(model, prompt, system, max_tokens, temperature, json_mode)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def _anthropic_completion(
        self,
        model: str,
        prompt: str,
        system: Optional[str],
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """Execute Anthropic completion."""
        kwargs = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}]
        }
        if system:
            kwargs["system"] = system

        response = self._anthropic.messages.create(**kwargs)

        # Calculate cost
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens

        # Pricing (per 1K tokens)
        if "opus" in model:
            cost = (input_tokens * 0.015 + output_tokens * 0.075) / 1000
        elif "sonnet" in model:
            cost = (input_tokens * 0.003 + output_tokens * 0.015) / 1000
        else:  # haiku
            cost = (input_tokens * 0.001 + output_tokens * 0.005) / 1000

        return {
            "content": response.content[0].text,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost
        }

    def _openai_completion(
        self,
        model: str,
        prompt: str,
        system: Optional[str],
        max_tokens: int,
        temperature: float,
        json_mode: bool
    ) -> Dict[str, Any]:
        """Execute OpenAI completion."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        kwargs = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = self._openai.chat.completions.create(**kwargs)

        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens

        # Pricing
        if "gpt-4o-mini" in model:
            cost = (input_tokens * 0.00015 + output_tokens * 0.0006) / 1000
        elif "gpt-4o" in model:
            cost = (input_tokens * 0.005 + output_tokens * 0.015) / 1000
        elif "gpt-4-turbo" in model:
            cost = (input_tokens * 0.01 + output_tokens * 0.03) / 1000
        else:  # gpt-3.5
            cost = (input_tokens * 0.0005 + output_tokens * 0.0015) / 1000

        return {
            "content": response.choices[0].message.content,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost
        }

    def _deepseek_completion(
        self,
        model: str,
        prompt: str,
        system: Optional[str],
        max_tokens: int,
        temperature: float,
        json_mode: bool
    ) -> Dict[str, Any]:
        """Execute DeepSeek completion using the query method."""
        response = self._deepseek.query(
            prompt=prompt,
            system=system,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            json_mode=json_mode
        )

        return {
            "content": response.content,
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
            "cost": response.cost
        }

    def _groq_completion(
        self,
        model: str,
        prompt: str,
        system: Optional[str],
        max_tokens: int,
        temperature: float,
        json_mode: bool
    ) -> Dict[str, Any]:
        """Execute Groq completion."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        kwargs = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = self._groq.chat.completions.create(**kwargs)

        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens

        # Groq pricing (Llama 70B)
        cost = (input_tokens * 0.00059 + output_tokens * 0.00079) / 1000

        return {
            "content": response.choices[0].message.content,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost
        }

    def _track_usage(self, provider: str, cost: float, input_tokens: int, output_tokens: int):
        """Track usage statistics."""
        with self._lock:
            self._total_cost += cost
            self._total_calls += 1

            if provider not in self._usage_by_provider:
                self._usage_by_provider[provider] = {
                    "calls": 0,
                    "cost": 0.0,
                    "input_tokens": 0,
                    "output_tokens": 0
                }

            self._usage_by_provider[provider]["calls"] += 1
            self._usage_by_provider[provider]["cost"] += cost
            self._usage_by_provider[provider]["input_tokens"] += input_tokens
            self._usage_by_provider[provider]["output_tokens"] += output_tokens

    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        with self._lock:
            return {
                "total_calls": self._total_calls,
                "total_cost": self._total_cost,
                "by_provider": dict(self._usage_by_provider),
                "available_providers": self._get_available_providers()
            }

    def reset_stats(self):
        """Reset usage statistics."""
        with self._lock:
            self._total_cost = 0.0
            self._total_calls = 0
            self._usage_by_provider = {}


# Singleton instance
_smart_client: Optional[SmartLLMClient] = None
_client_lock = Lock()


def get_smart_client(**kwargs) -> SmartLLMClient:
    """Get singleton smart client instance."""
    global _smart_client
    if _smart_client is None:
        with _client_lock:
            if _smart_client is None:
                _smart_client = SmartLLMClient(**kwargs)
    return _smart_client


# Convenience functions
def smart_completion(
    prompt: str,
    task_type: str = "simple",
    **kwargs
) -> CompletionResult:
    """Quick smart completion."""
    return get_smart_client().complete(prompt, task_type=task_type, **kwargs)


def extract_data(
    context: str,
    extraction_prompt: str,
    fields: Optional[List[str]] = None
) -> CompletionResult:
    """Extract structured data (uses cheapest model)."""
    if fields:
        prompt = f"{extraction_prompt}\n\nFields to extract: {', '.join(fields)}\n\nContext:\n{context}"
    else:
        prompt = f"{extraction_prompt}\n\nContext:\n{context}"

    return get_smart_client().complete(
        prompt=prompt,
        task_type="extraction",
        complexity="low",
        json_mode=True
    )


def analyze_text(text: str, analysis_prompt: str) -> CompletionResult:
    """Analyze text (uses mid-tier model)."""
    return get_smart_client().complete(
        prompt=f"{analysis_prompt}\n\nText:\n{text}",
        task_type="reasoning",
        complexity="medium"
    )


def generate_report(content: str, report_type: str = "summary") -> CompletionResult:
    """Generate report (uses high-quality model)."""
    return get_smart_client().complete(
        prompt=f"Generate a {report_type} report:\n\n{content}",
        task_type="synthesis",
        complexity="high"
    )


def print_llm_stats() -> None:
    """Print LLM usage statistics."""
    stats = get_smart_client().get_stats()
    print("\n=== Smart LLM Client Stats ===")
    print(f"Total calls: {stats['total_calls']}")
    print(f"Total cost: ${stats['total_cost']:.4f}")
    print(f"Available providers: {', '.join(stats['available_providers'])}")
    print("\nBy provider:")
    for provider, data in stats.get("by_provider", {}).items():
        print(f"  {provider}:")
        print(f"    Calls: {data['calls']}")
        print(f"    Cost: ${data['cost']:.4f}")
        print(f"    Tokens: {data['input_tokens']:,} in, {data['output_tokens']:,} out")
