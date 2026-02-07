"""
DeepSeek API integration - Full-featured client with all API capabilities.

Features:
- DeepSeek-V3: General chat ($0.14/1M input, $0.27/1M output)
- DeepSeek-R1: Reasoning model with chain-of-thought ($0.55/1M input, $2.19/1M output)
- Async support for concurrent operations
- Streaming responses
- Tool Use / Function Calling
- FIM (Fill-in-the-Middle) completion for code
- Context caching (automatic, 90% discount on cache hits)
- Prefix completion (Beta)
- Task-based model selection

Pricing (per 1M tokens):
- DeepSeek-V3 (deepseek-chat):
  - Input: $0.14 (cache hit: $0.014)
  - Output: $0.27
- DeepSeek-R1 (deepseek-reasoner):
  - Input: $0.55 (cache hit: $0.14)
  - Output: $2.19

Usage:
    from company_researcher.llm.deepseek_client import (
        get_deepseek_client,
        get_async_deepseek_client,
        DeepSeekTaskType,
    )

    # Sync client with task-based routing
    client = get_deepseek_client()
    result = client.query("Analyze Tesla", task_type=DeepSeekTaskType.ANALYSIS)

    # Async client for concurrent operations
    async_client = await get_async_deepseek_client()
    results = await async_client.concurrent_queries([...])

    # Tool use / function calling
    tools = create_deepseek_research_tools()
    result = client.query_with_tools("Get weather in Tokyo", tools=tools)

    # FIM completion for code
    result = client.fim_completion(
        prefix="def fibonacci(n):",
        suffix="    return fib(n-1) + fib(n-2)"
    )

    # Reasoning with chain-of-thought
    result = client.reason("Solve: 9.11 vs 9.8 which is larger?")
"""

import asyncio
import json
from dataclasses import dataclass, field
from enum import Enum
from threading import Lock
from typing import Any, AsyncGenerator, Callable, Dict, Generator, List, Optional, Union

from openai import AsyncOpenAI, OpenAI

from ..utils import get_config, get_logger

logger = get_logger(__name__)


# =============================================================================
# Pricing Configuration
# =============================================================================

DEEPSEEK_PRICING = {
    "deepseek-chat": {  # V3
        "input": 0.14,
        "output": 0.27,
        "cache_hit": 0.014,  # 90% discount for cached
        "context_window": 128000,
        "max_output": 8000,
        "speed": 60,  # tokens/sec estimate
    },
    "deepseek-reasoner": {  # R1 - reasoning model
        "input": 0.55,
        "output": 2.19,
        "cache_hit": 0.14,
        "context_window": 64000,  # 64K for reasoner
        "max_output": 64000,
        "speed": 30,  # slower due to reasoning
    },
}


# =============================================================================
# Task Types for Model Selection
# =============================================================================


class DeepSeekTaskType(Enum):
    """Task types for intelligent model selection."""

    EXTRACTION = "extraction"  # Data extraction - use V3 (cheap)
    CLASSIFICATION = "classification"  # Quick classification - use V3 (cheap)
    ANALYSIS = "analysis"  # General analysis - use V3
    SYNTHESIS = "synthesis"  # Report synthesis - use V3
    REASONING = "reasoning"  # Complex reasoning - use R1
    MATH = "math"  # Math problems - use R1
    CODE = "code"  # Code generation - use V3 with FIM
    CONVERSATION = "conversation"  # Multi-turn chat - use V3


class DeepSeekModelSelector:
    """Intelligent model selection based on task type."""

    TASK_MODEL_MAP = {
        DeepSeekTaskType.EXTRACTION: "deepseek-chat",
        DeepSeekTaskType.CLASSIFICATION: "deepseek-chat",
        DeepSeekTaskType.ANALYSIS: "deepseek-chat",
        DeepSeekTaskType.SYNTHESIS: "deepseek-chat",
        DeepSeekTaskType.REASONING: "deepseek-reasoner",
        DeepSeekTaskType.MATH: "deepseek-reasoner",
        DeepSeekTaskType.CODE: "deepseek-chat",
        DeepSeekTaskType.CONVERSATION: "deepseek-chat",
    }

    @classmethod
    def select_model(
        cls,
        task_type: DeepSeekTaskType = DeepSeekTaskType.ANALYSIS,
        require_reasoning: bool = False,
        max_cost_per_1m: Optional[float] = None,
    ) -> str:
        """
        Select optimal model based on task type.

        Args:
            task_type: Type of task
            require_reasoning: Force reasoning model
            max_cost_per_1m: Maximum cost per 1M tokens

        Returns:
            Model ID string
        """
        if require_reasoning:
            return "deepseek-reasoner"

        # Cost constraint check
        if max_cost_per_1m is not None:
            if max_cost_per_1m < DEEPSEEK_PRICING["deepseek-reasoner"]["input"]:
                return "deepseek-chat"

        return cls.TASK_MODEL_MAP.get(task_type, "deepseek-chat")

    @classmethod
    def get_model_for_research_task(cls, task: str) -> str:
        """Map research task description to optimal model."""
        task_lower = task.lower()

        # Reasoning tasks
        if any(
            word in task_lower
            for word in ["reason", "think", "analyze deeply", "complex", "math", "calculate"]
        ):
            return "deepseek-reasoner"

        # Default to V3 for cost efficiency
        return "deepseek-chat"


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class DeepSeekResponse:
    """Response from DeepSeek API."""

    content: str
    input_tokens: int
    output_tokens: int
    model: str
    cost: float
    cached_tokens: int = 0
    reasoning_content: Optional[str] = None  # For R1 model
    reasoning_tokens: int = 0
    tool_calls: Optional[List[Dict[str, Any]]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "model": self.model,
            "cost": self.cost,
            "cached_tokens": self.cached_tokens,
            "reasoning_content": self.reasoning_content,
            "reasoning_tokens": self.reasoning_tokens,
            "tool_calls": self.tool_calls,
        }


@dataclass
class ToolDefinition:
    """Definition of a tool for function calling."""

    name: str
    description: str
    parameters: Dict[str, Any]
    function: Optional[Callable] = None  # Optional auto-execute function

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


# =============================================================================
# Sync Client
# =============================================================================


class DeepSeekClient:
    """
    Full-featured DeepSeek API client.

    Features:
    - Task-based model selection
    - Tool use / function calling
    - FIM completion for code
    - Streaming responses
    - Reasoning model support
    - Cost tracking with cache awareness
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.deepseek.com",
        beta_base_url: str = "https://api.deepseek.com/beta",
        default_model: str = "deepseek-chat",
    ):
        """
        Initialize DeepSeek client.

        Args:
            api_key: DeepSeek API key (or DEEPSEEK_API_KEY env var)
            base_url: API base URL
            beta_base_url: Beta API base URL (for FIM, prefix completion)
            default_model: Default model to use
        """
        self.api_key = api_key or get_config("DEEPSEEK_API_KEY")
        if not self.api_key:
            logger.warning("DeepSeek API key not found. Set DEEPSEEK_API_KEY env var.")

        # Standard client
        self.client = OpenAI(api_key=self.api_key, base_url=base_url) if self.api_key else None

        # Beta client for FIM and prefix completion
        self.beta_client = (
            OpenAI(api_key=self.api_key, base_url=beta_base_url) if self.api_key else None
        )

        self.default_model = default_model
        self._total_cost = 0.0
        self._total_calls = 0
        self._cache_hits = 0
        self._lock = Lock()

    def _calculate_cost(
        self, model: str, input_tokens: int, output_tokens: int, cached_tokens: int = 0
    ) -> float:
        """Calculate cost for a request."""
        pricing = DEEPSEEK_PRICING.get(model, DEEPSEEK_PRICING["deepseek-chat"])

        uncached_input = input_tokens - cached_tokens
        cost = (uncached_input / 1_000_000) * pricing["input"]
        cost += (cached_tokens / 1_000_000) * pricing["cache_hit"]
        cost += (output_tokens / 1_000_000) * pricing["output"]

        return cost

    def query(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        task_type: DeepSeekTaskType = DeepSeekTaskType.ANALYSIS,
        max_tokens: int = 4000,
        temperature: float = 0.0,
        json_mode: bool = False,
    ) -> DeepSeekResponse:
        """
        Query DeepSeek with task-based model selection.

        Args:
            prompt: User prompt
            system: System prompt
            model: Override model selection
            task_type: Task type for automatic model selection
            max_tokens: Maximum output tokens
            temperature: Sampling temperature
            json_mode: Enable JSON output mode

        Returns:
            DeepSeekResponse with content and usage
        """
        if not self.client:
            raise ValueError("DeepSeek client not initialized. Set DEEPSEEK_API_KEY.")

        # Auto-select model based on task type
        model = model or DeepSeekModelSelector.select_model(task_type)

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        kwargs: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = self.client.chat.completions.create(**kwargs)

        # Extract usage
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        cached_tokens = getattr(response.usage, "prompt_cache_hit_tokens", 0)

        # Extract reasoning content for R1
        reasoning_content = None
        if model == "deepseek-reasoner":
            reasoning_content = getattr(response.choices[0].message, "reasoning_content", None)

        cost = self._calculate_cost(model, input_tokens, output_tokens, cached_tokens)

        # Track stats
        with self._lock:
            self._total_cost += cost
            self._total_calls += 1
            if cached_tokens > 0:
                self._cache_hits += 1

        return DeepSeekResponse(
            content=response.choices[0].message.content or "",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=response.model,
            cost=cost,
            cached_tokens=cached_tokens,
            reasoning_content=reasoning_content,
        )

    def reason(
        self, prompt: str, system: Optional[str] = None, max_tokens: int = 8000
    ) -> DeepSeekResponse:
        """
        Use DeepSeek R1 reasoning model with chain-of-thought.

        Best for:
        - Complex reasoning tasks
        - Math problems
        - Multi-step logic

        Args:
            prompt: Problem to reason about
            system: Optional system prompt
            max_tokens: Maximum output tokens

        Returns:
            DeepSeekResponse with reasoning_content and final answer
        """
        return self.query(
            prompt=prompt,
            system=system,
            model="deepseek-reasoner",
            max_tokens=max_tokens,
            temperature=0.0,
        )

    def query_with_tools(
        self,
        prompt: str,
        tools: List[ToolDefinition],
        system: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 0.0,
        auto_execute: bool = False,
    ) -> DeepSeekResponse:
        """
        Query with tool use / function calling.

        Args:
            prompt: User prompt
            tools: List of tool definitions
            system: System prompt
            model: Model to use
            max_tokens: Maximum output tokens
            temperature: Sampling temperature
            auto_execute: Automatically execute tool functions

        Returns:
            DeepSeekResponse with tool_calls or final content
        """
        if not self.client:
            raise ValueError("DeepSeek client not initialized.")

        model = model or "deepseek-chat"
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        tools_list = [t.to_dict() for t in tools]

        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools_list,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        message = response.choices[0].message
        tool_calls_raw = message.tool_calls

        # Process tool calls
        tool_calls = None
        if tool_calls_raw:
            tool_calls = []
            for tc in tool_calls_raw:
                tool_call = {
                    "id": tc.id,
                    "name": tc.function.name,
                    "arguments": json.loads(tc.function.arguments),
                }
                tool_calls.append(tool_call)

                # Auto-execute if enabled
                if auto_execute:
                    for tool in tools:
                        if tool.name == tc.function.name and tool.function:
                            try:
                                result = tool.function(**tool_call["arguments"])
                                tool_call["result"] = result
                            except Exception as e:
                                tool_call["error"] = str(e)

        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        cached_tokens = getattr(response.usage, "prompt_cache_hit_tokens", 0)
        cost = self._calculate_cost(model, input_tokens, output_tokens, cached_tokens)

        with self._lock:
            self._total_cost += cost
            self._total_calls += 1

        return DeepSeekResponse(
            content=message.content or "",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model,
            cost=cost,
            cached_tokens=cached_tokens,
            tool_calls=tool_calls,
        )

    def stream_query(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        task_type: DeepSeekTaskType = DeepSeekTaskType.ANALYSIS,
        max_tokens: int = 4000,
        temperature: float = 0.0,
    ) -> Generator[str, None, DeepSeekResponse]:
        """
        Stream response tokens in real-time.

        Args:
            prompt: User prompt
            system: System prompt
            model: Model to use
            task_type: Task type for model selection
            max_tokens: Maximum output tokens
            temperature: Sampling temperature

        Yields:
            Text chunks as they arrive

        Returns:
            Final DeepSeekResponse with full content and stats
        """
        if not self.client:
            raise ValueError("DeepSeek client not initialized.")

        model = model or DeepSeekModelSelector.select_model(task_type)

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
        )

        full_content = ""
        reasoning_content = ""

        for chunk in response:
            if chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                full_content += text
                yield text
            # For R1 model, capture reasoning
            if hasattr(chunk.choices[0].delta, "reasoning_content"):
                rc = chunk.choices[0].delta.reasoning_content
                if rc:
                    reasoning_content += rc

        # Estimate tokens (streaming doesn't provide usage)
        input_tokens = len(prompt) // 4
        output_tokens = len(full_content) // 4
        cost = self._calculate_cost(model, input_tokens, output_tokens)

        with self._lock:
            self._total_cost += cost
            self._total_calls += 1

        return DeepSeekResponse(
            content=full_content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model,
            cost=cost,
            reasoning_content=reasoning_content if reasoning_content else None,
        )

    def fim_completion(
        self,
        prefix: str,
        suffix: Optional[str] = None,
        model: str = "deepseek-chat",
        max_tokens: int = 256,
    ) -> DeepSeekResponse:
        """
        Fill-in-the-Middle completion for code.

        Best for:
        - Code completion
        - Filling gaps in code
        - Generating function bodies

        Args:
            prefix: Code before the insertion point
            suffix: Code after the insertion point
            model: Model to use
            max_tokens: Maximum tokens to generate

        Returns:
            DeepSeekResponse with generated code
        """
        if not self.beta_client:
            raise ValueError("DeepSeek beta client not initialized.")

        kwargs: Dict[str, Any] = {"model": model, "prompt": prefix, "max_tokens": max_tokens}

        if suffix:
            kwargs["suffix"] = suffix

        response = self.beta_client.completions.create(**kwargs)

        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        cost = self._calculate_cost(model, input_tokens, output_tokens)

        with self._lock:
            self._total_cost += cost
            self._total_calls += 1

        return DeepSeekResponse(
            content=response.choices[0].text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model,
            cost=cost,
        )

    def prefix_completion(
        self,
        messages: List[Dict[str, str]],
        assistant_prefix: str,
        model: str = "deepseek-chat",
        max_tokens: int = 1000,
        stop: Optional[List[str]] = None,
    ) -> DeepSeekResponse:
        """
        Continue from an assistant prefix (Beta).

        Useful for:
        - Structured output generation
        - Code generation with specific format
        - Constrained completions

        Args:
            messages: Conversation history
            assistant_prefix: Text to continue from
            model: Model to use
            max_tokens: Maximum tokens to generate
            stop: Stop sequences

        Returns:
            DeepSeekResponse with completion
        """
        if not self.beta_client:
            raise ValueError("DeepSeek beta client not initialized.")

        # Add assistant prefix message
        all_messages = messages.copy()
        all_messages.append({"role": "assistant", "content": assistant_prefix, "prefix": True})

        kwargs: Dict[str, Any] = {
            "model": model,
            "messages": all_messages,
            "max_tokens": max_tokens,
        }

        if stop:
            kwargs["stop"] = stop

        response = self.beta_client.chat.completions.create(**kwargs)

        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        cost = self._calculate_cost(model, input_tokens, output_tokens)

        with self._lock:
            self._total_cost += cost
            self._total_calls += 1

        return DeepSeekResponse(
            content=assistant_prefix + response.choices[0].message.content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model,
            cost=cost,
        )

    # Convenience methods for research
    def extract_company_data(
        self, company_name: str, search_results: str, fields: List[str]
    ) -> Dict[str, Any]:
        """Extract structured company data."""
        fields_list = "\n".join(f"- {field}" for field in fields)

        prompt = f"""Extract the following fields for {company_name}:
{fields_list}

Search Results:
{search_results}

Return valid JSON with the extracted fields. Use null for missing data.
Include a "confidence" field (0-1) for each extracted value."""

        response = self.query(
            prompt=prompt,
            system="You are a data extraction specialist. Return valid JSON only.",
            task_type=DeepSeekTaskType.EXTRACTION,
            json_mode=True,
        )

        try:
            data = json.loads(response.content)
            data["_meta"] = {
                "model": response.model,
                "cost": response.cost,
                "tokens": response.input_tokens + response.output_tokens,
            }
            return data
        except json.JSONDecodeError:
            return {
                "error": "Failed to parse JSON",
                "raw_content": response.content,
                "_meta": {"model": response.model, "cost": response.cost},
            }

    def analyze_financials(
        self, company_name: str, financial_data: str, use_reasoning: bool = False
    ) -> DeepSeekResponse:
        """Analyze company financials with optional deep reasoning."""
        prompt = f"""Analyze the financial data for {company_name}:

{financial_data}

Provide:
1. Revenue analysis (trends, growth rates)
2. Profitability assessment (margins, efficiency)
3. Key financial metrics
4. Notable concerns or highlights
5. Comparison to industry if data available

Be specific with numbers and cite sources."""

        if use_reasoning:
            return self.reason(prompt)
        else:
            return self.query(
                prompt=prompt,
                system="You are a senior financial analyst. Provide objective, data-driven analysis.",
                task_type=DeepSeekTaskType.ANALYSIS,
            )

    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        with self._lock:
            return {
                "total_calls": self._total_calls,
                "total_cost": self._total_cost,
                "cache_hits": self._cache_hits,
                "cache_hit_rate": (
                    self._cache_hits / self._total_calls if self._total_calls > 0 else 0
                ),
                "avg_cost_per_call": (
                    self._total_cost / self._total_calls if self._total_calls > 0 else 0
                ),
            }

    def reset_stats(self) -> None:
        """Reset usage statistics."""
        with self._lock:
            self._total_cost = 0.0
            self._total_calls = 0
            self._cache_hits = 0


# =============================================================================
# Async Client
# =============================================================================


class AsyncDeepSeekClient:
    """
    Async DeepSeek client for concurrent operations.

    Use when:
    - Processing multiple queries in parallel
    - Building async applications
    - Need non-blocking I/O
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.deepseek.com",
        beta_base_url: str = "https://api.deepseek.com/beta",
    ):
        """Initialize async client."""
        self.api_key = api_key or get_config("DEEPSEEK_API_KEY")
        if not self.api_key:
            logger.warning("DeepSeek API key not found.")

        self.client = AsyncOpenAI(api_key=self.api_key, base_url=base_url) if self.api_key else None

        self.beta_client = (
            AsyncOpenAI(api_key=self.api_key, base_url=beta_base_url) if self.api_key else None
        )

        self._total_cost = 0.0
        self._total_calls = 0
        self._lock = asyncio.Lock()

    async def query(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        task_type: DeepSeekTaskType = DeepSeekTaskType.ANALYSIS,
        max_tokens: int = 4000,
        temperature: float = 0.0,
        json_mode: bool = False,
    ) -> DeepSeekResponse:
        """Async query with task-based model selection."""
        if not self.client:
            raise ValueError("DeepSeek client not initialized.")

        model = model or DeepSeekModelSelector.select_model(task_type)

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        kwargs: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = await self.client.chat.completions.create(**kwargs)

        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        cached_tokens = getattr(response.usage, "prompt_cache_hit_tokens", 0)

        pricing = DEEPSEEK_PRICING.get(model, DEEPSEEK_PRICING["deepseek-chat"])
        uncached_input = input_tokens - cached_tokens
        cost = (uncached_input / 1_000_000) * pricing["input"]
        cost += (cached_tokens / 1_000_000) * pricing["cache_hit"]
        cost += (output_tokens / 1_000_000) * pricing["output"]

        reasoning_content = None
        if model == "deepseek-reasoner":
            reasoning_content = getattr(response.choices[0].message, "reasoning_content", None)

        async with self._lock:
            self._total_cost += cost
            self._total_calls += 1

        return DeepSeekResponse(
            content=response.choices[0].message.content or "",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=response.model,
            cost=cost,
            cached_tokens=cached_tokens,
            reasoning_content=reasoning_content,
        )

    async def concurrent_queries(
        self,
        prompts: List[str],
        system: Optional[str] = None,
        model: Optional[str] = None,
        task_type: DeepSeekTaskType = DeepSeekTaskType.ANALYSIS,
        max_tokens: int = 4000,
    ) -> List[DeepSeekResponse]:
        """
        Execute multiple queries concurrently.

        10x faster than sequential processing.

        Args:
            prompts: List of prompts
            system: Shared system prompt
            model: Model to use
            task_type: Task type for model selection
            max_tokens: Maximum tokens per response

        Returns:
            List of responses in same order as prompts
        """
        tasks = [
            self.query(
                prompt=prompt,
                system=system,
                model=model,
                task_type=task_type,
                max_tokens=max_tokens,
            )
            for prompt in prompts
        ]

        return await asyncio.gather(*tasks)

    async def stream_query(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        task_type: DeepSeekTaskType = DeepSeekTaskType.ANALYSIS,
        max_tokens: int = 4000,
        temperature: float = 0.0,
    ) -> AsyncGenerator[str, None]:
        """Async streaming query."""
        if not self.client:
            raise ValueError("DeepSeek client not initialized.")

        model = model or DeepSeekModelSelector.select_model(task_type)

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
        )

        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def query_with_tools(
        self,
        prompt: str,
        tools: List[ToolDefinition],
        system: Optional[str] = None,
        model: str = "deepseek-chat",
        max_tokens: int = 4000,
        auto_execute: bool = False,
    ) -> DeepSeekResponse:
        """Async tool use / function calling."""
        if not self.client:
            raise ValueError("DeepSeek client not initialized.")

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        tools_list = [t.to_dict() for t in tools]

        response = await self.client.chat.completions.create(
            model=model, messages=messages, tools=tools_list, max_tokens=max_tokens
        )

        message = response.choices[0].message
        tool_calls_raw = message.tool_calls

        tool_calls = None
        if tool_calls_raw:
            tool_calls = []
            for tc in tool_calls_raw:
                tool_call = {
                    "id": tc.id,
                    "name": tc.function.name,
                    "arguments": json.loads(tc.function.arguments),
                }
                tool_calls.append(tool_call)

                if auto_execute:
                    for tool in tools:
                        if tool.name == tc.function.name and tool.function:
                            try:
                                result = tool.function(**tool_call["arguments"])
                                tool_call["result"] = result
                            except Exception as e:
                                tool_call["error"] = str(e)

        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        cached_tokens = getattr(response.usage, "prompt_cache_hit_tokens", 0)

        pricing = DEEPSEEK_PRICING["deepseek-chat"]
        cost = ((input_tokens - cached_tokens) / 1_000_000) * pricing["input"]
        cost += (cached_tokens / 1_000_000) * pricing["cache_hit"]
        cost += (output_tokens / 1_000_000) * pricing["output"]

        async with self._lock:
            self._total_cost += cost
            self._total_calls += 1

        return DeepSeekResponse(
            content=message.content or "",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model,
            cost=cost,
            cached_tokens=cached_tokens,
            tool_calls=tool_calls,
        )

    async def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        async with self._lock:
            return {
                "total_calls": self._total_calls,
                "total_cost": self._total_cost,
                "avg_cost_per_call": (
                    self._total_cost / self._total_calls if self._total_calls > 0 else 0
                ),
            }


# =============================================================================
# Tool Creation Helpers
# =============================================================================


def create_tool(
    name: str, description: str, parameters: Dict[str, Any], function: Optional[Callable] = None
) -> ToolDefinition:
    """Create a tool definition for function calling."""
    return ToolDefinition(
        name=name, description=description, parameters=parameters, function=function
    )


def create_deepseek_research_tools() -> List[ToolDefinition]:
    """Create research-specific tools for DeepSeek function calling."""
    return [
        ToolDefinition(
            name="extract_financial_data",
            description="Extract financial metrics from text",
            parameters={
                "type": "object",
                "properties": {
                    "company_name": {"type": "string", "description": "Company name"},
                    "metric_type": {
                        "type": "string",
                        "enum": ["revenue", "profit", "margin", "growth"],
                    },
                    "time_period": {"type": "string", "description": "Time period (e.g., Q1 2024)"},
                },
                "required": ["company_name", "metric_type"],
            },
        ),
        ToolDefinition(
            name="analyze_competitor",
            description="Analyze competitive landscape",
            parameters={
                "type": "object",
                "properties": {
                    "company_name": {"type": "string", "description": "Target company"},
                    "competitors": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Competitor names",
                    },
                    "dimensions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Analysis dimensions",
                    },
                },
                "required": ["company_name"],
            },
        ),
        ToolDefinition(
            name="calculate_metrics",
            description="Calculate financial metrics",
            parameters={
                "type": "object",
                "properties": {
                    "metric": {"type": "string", "enum": ["cagr", "margin", "ratio", "growth"]},
                    "values": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Numeric values",
                    },
                    "periods": {"type": "integer", "description": "Number of periods"},
                },
                "required": ["metric", "values"],
            },
        ),
    ]


# =============================================================================
# Singleton Instances
# =============================================================================

_deepseek_client: Optional[DeepSeekClient] = None
_async_deepseek_client: Optional[AsyncDeepSeekClient] = None
_client_lock = Lock()


def get_deepseek_client() -> DeepSeekClient:
    """Get singleton DeepSeek client instance."""
    global _deepseek_client
    if _deepseek_client is None:
        with _client_lock:
            if _deepseek_client is None:
                _deepseek_client = DeepSeekClient()
    return _deepseek_client


async def get_async_deepseek_client() -> AsyncDeepSeekClient:
    """Get singleton async DeepSeek client instance."""
    global _async_deepseek_client
    if _async_deepseek_client is None:
        _async_deepseek_client = AsyncDeepSeekClient()
    return _async_deepseek_client


def reset_deepseek_clients() -> None:
    """Reset all DeepSeek client instances."""
    global _deepseek_client, _async_deepseek_client
    _deepseek_client = None
    _async_deepseek_client = None
