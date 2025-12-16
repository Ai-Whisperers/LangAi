"""
Enhanced Groq API integration with full feature support.

Features:
- Ultra-fast inference (1,300+ tokens/second)
- Async support for concurrent operations
- Streaming responses for real-time output
- Tool use / Function calling for autonomous agents
- Batch API for 50% cost savings
- Intelligent model selection by task type

Speed: 1,300+ tokens/second (Llama 3.1 8B)

Model Selection Strategy:
- SPEED: llama-3.2-1b-preview (2,000 tok/s) - Simple classification, quick lookups
- BALANCED: llama-3.1-8b-instant (1,300 tok/s) - General tasks, extraction
- QUALITY: llama-3.3-70b-versatile (275 tok/s) - Complex analysis, reasoning
- TOOL_USE: llama-3.3-70b-versatile - Best for function calling
- VISION: llama-4-scout-17b-16e-instruct - Image analysis
- LONG_CONTEXT: llama-4-maverick-17b-128e-instruct - Large documents

Usage:
    from company_researcher.llm.groq_client import (
        get_groq_client,
        get_async_groq_client,
        GroqModelSelector,
        TaskType,
    )

    # Sync client
    client = get_groq_client()
    result = client.fast_query("What is Tesla's market cap?")

    # Async client (10x faster for batch)
    async_client = await get_async_groq_client()
    results = await async_client.concurrent_queries([
        "Tesla revenue",
        "Apple revenue",
        "Microsoft revenue"
    ])

    # Tool use
    result = client.query_with_tools(
        "Get weather in NYC",
        tools=[weather_tool]
    )

    # Streaming
    async for chunk in client.stream_query("Explain quantum computing"):
        print(chunk, end="")
"""

import asyncio
import json
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from threading import Lock
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Union

from ..utils import get_config, get_logger

logger = get_logger(__name__)

# Try to import groq
try:
    import httpx
    from groq import AsyncGroq, Groq

    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    logger.warning("groq not installed. Run: pip install groq")


# =============================================================================
# Task Types and Model Selection
# =============================================================================


class TaskType(Enum):
    """Task types for intelligent model selection."""

    SPEED = "speed"  # Simple tasks, classification
    BALANCED = "balanced"  # General purpose
    QUALITY = "quality"  # Complex analysis
    TOOL_USE = "tool_use"  # Function calling
    VISION = "vision"  # Image analysis
    LONG_CONTEXT = "long_context"  # Large documents
    REASONING = "reasoning"  # Deep reasoning tasks
    EXTRACTION = "extraction"  # Data extraction
    CLASSIFICATION = "classification"  # Quick classification


class GroqModelSelector:
    """
    Intelligent model selection based on task type and cost optimization.

    Selects the best model considering:
    - Task complexity
    - Speed requirements
    - Cost constraints
    - Context length needs
    """

    # Model configurations with pricing and capabilities
    MODELS = {
        # Ultra-fast models (best for simple tasks)
        "llama-3.2-1b-preview": {
            "input": 0.04,
            "output": 0.04,
            "speed": 2000,
            "context": 128000,
            "tasks": [TaskType.SPEED, TaskType.CLASSIFICATION],
            "quality": 0.6,
        },
        "llama-3.2-3b-preview": {
            "input": 0.06,
            "output": 0.06,
            "speed": 1800,
            "context": 128000,
            "tasks": [TaskType.SPEED, TaskType.EXTRACTION],
            "quality": 0.7,
        },
        # Fast balanced models
        "llama-3.1-8b-instant": {
            "input": 0.05,
            "output": 0.08,
            "speed": 1300,
            "context": 128000,
            "tasks": [TaskType.BALANCED, TaskType.EXTRACTION],
            "quality": 0.75,
        },
        # High quality models
        "llama-3.3-70b-versatile": {
            "input": 0.59,
            "output": 0.79,
            "speed": 275,
            "context": 128000,
            "tasks": [TaskType.QUALITY, TaskType.TOOL_USE, TaskType.REASONING],
            "quality": 0.95,
        },
        "llama-3.1-70b-versatile": {
            "input": 0.59,
            "output": 0.79,
            "speed": 250,
            "context": 128000,
            "tasks": [TaskType.QUALITY, TaskType.TOOL_USE],
            "quality": 0.9,
        },
        # Vision models
        "meta-llama/llama-4-scout-17b-16e-instruct": {
            "input": 0.11,
            "output": 0.34,
            "speed": 500,
            "context": 131072,
            "tasks": [TaskType.VISION, TaskType.BALANCED],
            "quality": 0.85,
            "vision": True,
        },
        # Long context models
        "meta-llama/llama-4-maverick-17b-128e-instruct": {
            "input": 0.20,
            "output": 0.60,
            "speed": 400,
            "context": 1048576,  # 1M tokens
            "tasks": [TaskType.LONG_CONTEXT, TaskType.QUALITY],
            "quality": 0.88,
        },
        # Reasoning models
        "deepseek-r1-distill-llama-70b": {
            "input": 0.75,
            "output": 0.99,
            "speed": 200,
            "context": 128000,
            "tasks": [TaskType.REASONING, TaskType.QUALITY],
            "quality": 0.92,
        },
        # Mixtral (good balance)
        "mixtral-8x7b-32768": {
            "input": 0.24,
            "output": 0.24,
            "speed": 500,
            "context": 32768,
            "tasks": [TaskType.BALANCED],
            "quality": 0.8,
        },
        # Gemma (efficient)
        "gemma2-9b-it": {
            "input": 0.20,
            "output": 0.20,
            "speed": 600,
            "context": 8192,
            "tasks": [TaskType.BALANCED, TaskType.EXTRACTION],
            "quality": 0.78,
        },
    }

    # Default models by task type
    TASK_DEFAULTS = {
        TaskType.SPEED: "llama-3.2-3b-preview",
        TaskType.BALANCED: "llama-3.1-8b-instant",
        TaskType.QUALITY: "llama-3.3-70b-versatile",
        TaskType.TOOL_USE: "llama-3.3-70b-versatile",
        TaskType.VISION: "meta-llama/llama-4-scout-17b-16e-instruct",
        TaskType.LONG_CONTEXT: "meta-llama/llama-4-maverick-17b-128e-instruct",
        TaskType.REASONING: "deepseek-r1-distill-llama-70b",
        TaskType.EXTRACTION: "llama-3.1-8b-instant",
        TaskType.CLASSIFICATION: "llama-3.2-1b-preview",
    }

    @classmethod
    def select_model(
        cls,
        task_type: TaskType = TaskType.BALANCED,
        context_length: int = 0,
        require_vision: bool = False,
        max_cost_per_1m: float = 1.0,
        prefer_speed: bool = False,
    ) -> str:
        """
        Select optimal model based on requirements.

        Args:
            task_type: Type of task to perform
            context_length: Required context window
            require_vision: Whether vision capability is needed
            max_cost_per_1m: Maximum cost per 1M tokens
            prefer_speed: Prioritize speed over quality

        Returns:
            Model name string
        """
        # Filter models by requirements
        candidates = []

        for model_name, config in cls.MODELS.items():
            # Check vision requirement
            if require_vision and not config.get("vision", False):
                continue

            # Check context length
            if context_length > config["context"]:
                continue

            # Check cost constraint
            avg_cost = (config["input"] + config["output"]) / 2
            if avg_cost > max_cost_per_1m:
                continue

            # Check task compatibility
            if task_type in config["tasks"]:
                candidates.append((model_name, config))

        if not candidates:
            # Fallback to default for task type
            return cls.TASK_DEFAULTS.get(task_type, "llama-3.1-8b-instant")

        # Sort by preference
        if prefer_speed:
            candidates.sort(key=lambda x: -x[1]["speed"])
        else:
            candidates.sort(key=lambda x: -x[1]["quality"])

        return candidates[0][0]

    @classmethod
    def get_model_for_research_task(cls, task: str) -> str:
        """
        Get optimal model for specific research tasks.

        Args:
            task: Research task name

        Returns:
            Model name
        """
        task_mapping = {
            # Fast tasks
            "company_classification": TaskType.CLASSIFICATION,
            "query_generation": TaskType.SPEED,
            "quick_lookup": TaskType.SPEED,
            # Balanced tasks
            "data_extraction": TaskType.EXTRACTION,
            "summarization": TaskType.BALANCED,
            "news_analysis": TaskType.BALANCED,
            # Quality tasks
            "financial_analysis": TaskType.QUALITY,
            "market_analysis": TaskType.QUALITY,
            "competitive_analysis": TaskType.QUALITY,
            "esg_analysis": TaskType.QUALITY,
            "investment_thesis": TaskType.REASONING,
            "risk_assessment": TaskType.REASONING,
            # Tool use tasks
            "data_retrieval": TaskType.TOOL_USE,
            "api_orchestration": TaskType.TOOL_USE,
            # Special tasks
            "chart_analysis": TaskType.VISION,
            "document_analysis": TaskType.LONG_CONTEXT,
            "earnings_call": TaskType.LONG_CONTEXT,
        }

        task_type = task_mapping.get(task.lower(), TaskType.BALANCED)
        return cls.select_model(task_type)

    @classmethod
    def get_pricing(cls, model: str) -> Dict[str, float]:
        """Get pricing for a model."""
        config = cls.MODELS.get(model, cls.MODELS["llama-3.1-8b-instant"])
        return {"input": config["input"], "output": config["output"]}


# =============================================================================
# Response Models
# =============================================================================


@dataclass
class GroqResponse:
    """Response from Groq API."""

    content: str
    input_tokens: int
    output_tokens: int
    model: str
    cost: float
    latency_ms: Optional[float] = None
    tokens_per_second: Optional[float] = None
    tool_calls: Optional[List[Dict]] = None
    finish_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "model": self.model,
            "cost": self.cost,
            "latency_ms": self.latency_ms,
            "tokens_per_second": self.tokens_per_second,
            "tool_calls": self.tool_calls,
            "finish_reason": self.finish_reason,
        }


@dataclass
class ToolDefinition:
    """Definition of a tool for function calling."""

    name: str
    description: str
    parameters: Dict[str, Any]
    function: Optional[Callable] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


@dataclass
class BatchJob:
    """Batch processing job."""

    job_id: str
    status: str
    input_file_id: str
    output_file_id: Optional[str] = None
    created_at: Optional[float] = None
    completed_at: Optional[float] = None
    request_counts: Optional[Dict[str, int]] = None
    error: Optional[str] = None


# =============================================================================
# Main Groq Client
# =============================================================================


class GroqClient:
    """
    Enhanced Groq API client with full feature support.

    Features:
    - Ultra-fast inference
    - Intelligent model selection
    - Tool use / function calling
    - JSON mode
    - Cost tracking
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: Optional[str] = None,
        max_retries: int = 3,
        timeout: float = 60.0,
    ):
        """
        Initialize Groq client.

        Args:
            api_key: Groq API key (or GROQ_API_KEY env var)
            default_model: Default model (auto-selects if None)
            max_retries: Max retry attempts
            timeout: Request timeout in seconds
        """
        if not GROQ_AVAILABLE:
            raise ImportError("groq not installed. Run: pip install groq")

        self.api_key = api_key or get_config("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            logger.warning("Groq API key not found. Set GROQ_API_KEY env var.")

        # Configure timeout
        self._timeout = httpx.Timeout(timeout=timeout, connect=10.0) if GROQ_AVAILABLE else None

        self.client = (
            Groq(api_key=self.api_key, max_retries=max_retries, timeout=self._timeout)
            if self.api_key
            else None
        )

        self.default_model = default_model or GroqModelSelector.TASK_DEFAULTS[TaskType.BALANCED]
        self._total_cost = 0.0
        self._total_calls = 0
        self._total_latency_ms = 0.0
        self._lock = Lock()

    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for API call."""
        pricing = GroqModelSelector.get_pricing(model)
        cost = (input_tokens / 1_000_000) * pricing["input"]
        cost += (output_tokens / 1_000_000) * pricing["output"]
        return cost

    def _track_usage(self, cost: float, latency_ms: float) -> None:
        """Track usage statistics."""
        with self._lock:
            self._total_cost += cost
            self._total_calls += 1
            self._total_latency_ms += latency_ms

    def fast_query(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        task_type: TaskType = TaskType.BALANCED,
        max_tokens: int = 2000,
        temperature: float = 0.0,
        json_mode: bool = False,
    ) -> GroqResponse:
        """
        Ultra-fast completion with intelligent model selection.

        Args:
            prompt: User prompt
            system: System prompt
            model: Model to use (auto-selects if None)
            task_type: Task type for model selection
            max_tokens: Maximum output tokens
            temperature: Sampling temperature
            json_mode: Enable JSON output mode

        Returns:
            GroqResponse with content and metrics
        """
        if not self.client:
            raise ValueError("Groq client not initialized. Set GROQ_API_KEY.")

        # Auto-select model if not specified
        model = model or GroqModelSelector.select_model(task_type)

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        kwargs = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        start_time = time.time()
        response = self.client.chat.completions.create(**kwargs)
        latency_ms = (time.time() - start_time) * 1000

        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        cost = self._calculate_cost(model, input_tokens, output_tokens)

        total_tokens = input_tokens + output_tokens
        tokens_per_second = (total_tokens / latency_ms) * 1000 if latency_ms > 0 else 0

        self._track_usage(cost, latency_ms)

        return GroqResponse(
            content=response.choices[0].message.content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model,
            cost=cost,
            latency_ms=latency_ms,
            tokens_per_second=tokens_per_second,
            finish_reason=response.choices[0].finish_reason,
        )

    def query_with_tools(
        self,
        prompt: str,
        tools: List[ToolDefinition],
        system: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.0,
        tool_choice: str = "auto",
        auto_execute: bool = True,
    ) -> GroqResponse:
        """
        Query with tool use / function calling.

        Args:
            prompt: User prompt
            tools: List of tool definitions
            system: System prompt
            model: Model (defaults to tool-optimized model)
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            tool_choice: "auto", "none", "required", or specific tool
            auto_execute: Automatically execute tools and get final response

        Returns:
            GroqResponse with content and/or tool calls
        """
        if not self.client:
            raise ValueError("Groq client not initialized.")

        # Use tool-optimized model
        model = model or GroqModelSelector.select_model(TaskType.TOOL_USE)

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        tools_schema = [t.to_dict() for t in tools]

        start_time = time.time()

        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools_schema,
            tool_choice=tool_choice,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        # If tools were called and auto_execute is enabled
        if tool_calls and auto_execute:
            # Build tool lookup
            tool_funcs = {t.name: t.function for t in tools if t.function}

            # Add assistant message
            messages.append(response_message)

            # Execute each tool call
            for tool_call in tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)

                if func_name in tool_funcs and tool_funcs[func_name]:
                    try:
                        func_result = tool_funcs[func_name](**func_args)
                        result_str = (
                            json.dumps(func_result)
                            if not isinstance(func_result, str)
                            else func_result
                        )
                    except Exception as e:
                        result_str = json.dumps({"error": str(e)})
                else:
                    result_str = json.dumps({"error": f"Function {func_name} not available"})

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": func_name,
                        "content": result_str,
                    }
                )

            # Get final response
            final_response = self.client.chat.completions.create(
                model=model, messages=messages, max_tokens=max_tokens
            )

            latency_ms = (time.time() - start_time) * 1000

            total_input = response.usage.prompt_tokens + final_response.usage.prompt_tokens
            total_output = response.usage.completion_tokens + final_response.usage.completion_tokens
            cost = self._calculate_cost(model, total_input, total_output)

            self._track_usage(cost, latency_ms)

            return GroqResponse(
                content=final_response.choices[0].message.content,
                input_tokens=total_input,
                output_tokens=total_output,
                model=model,
                cost=cost,
                latency_ms=latency_ms,
                tool_calls=[
                    {"name": tc.function.name, "arguments": json.loads(tc.function.arguments)}
                    for tc in tool_calls
                ],
                finish_reason=final_response.choices[0].finish_reason,
            )

        # No tool calls or auto_execute disabled
        latency_ms = (time.time() - start_time) * 1000
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        cost = self._calculate_cost(model, input_tokens, output_tokens)

        self._track_usage(cost, latency_ms)

        return GroqResponse(
            content=response_message.content or "",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model,
            cost=cost,
            latency_ms=latency_ms,
            tool_calls=(
                [
                    {"name": tc.function.name, "arguments": json.loads(tc.function.arguments)}
                    for tc in tool_calls
                ]
                if tool_calls
                else None
            ),
            finish_reason=response.choices[0].finish_reason,
        )

    def stream_query(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        task_type: TaskType = TaskType.BALANCED,
        max_tokens: int = 2000,
        temperature: float = 0.0,
    ):
        """
        Stream response tokens in real-time.

        Args:
            prompt: User prompt
            system: System prompt
            model: Model to use
            task_type: Task type for model selection
            max_tokens: Maximum tokens
            temperature: Sampling temperature

        Yields:
            String chunks as they arrive
        """
        if not self.client:
            raise ValueError("Groq client not initialized.")

        model = model or GroqModelSelector.select_model(task_type)

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        stream = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

            # Track usage from final chunk
            if hasattr(chunk, "x_groq") and chunk.x_groq and hasattr(chunk.x_groq, "usage"):
                usage = chunk.x_groq.usage
                cost = self._calculate_cost(model, usage.prompt_tokens, usage.completion_tokens)
                self._track_usage(cost, 0)

    def quick_company_info(
        self, company_name: str, fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Quick company information lookup using fastest model.

        Args:
            company_name: Company to look up
            fields: Specific fields to return

        Returns:
            Dict with company info
        """
        default_fields = [
            "full_name",
            "industry",
            "founded",
            "headquarters",
            "ceo",
            "employees",
            "description",
        ]
        fields = fields or default_fields

        prompt = f"""Provide brief information about {company_name}:
Return JSON with these fields: {', '.join(fields)}
Use null for unknown fields. Be concise."""

        response = self.fast_query(
            prompt=prompt,
            system="You are a company database. Return valid JSON only.",
            task_type=TaskType.SPEED,
            max_tokens=500,
            json_mode=True,
        )

        try:
            data = json.loads(response.content)
            data["_meta"] = {
                "latency_ms": response.latency_ms,
                "tokens_per_second": response.tokens_per_second,
                "cost": response.cost,
                "model": response.model,
            }
            return data
        except json.JSONDecodeError:
            return {
                "error": "Failed to parse JSON",
                "raw_content": response.content,
                "_meta": {"latency_ms": response.latency_ms},
            }

    def fast_classify(self, text: str, categories: List[str]) -> Dict[str, Any]:
        """
        Ultra-fast text classification.

        Args:
            text: Text to classify
            categories: List of possible categories

        Returns:
            Dict with category and confidence
        """
        categories_str = ", ".join(categories)

        prompt = f"""Classify this text into one of these categories: {categories_str}

Text: {text}

Return JSON with:
- category: one of the categories above
- confidence: 0-1 score
- reasoning: brief explanation"""

        response = self.fast_query(
            prompt=prompt, task_type=TaskType.CLASSIFICATION, max_tokens=200, json_mode=True
        )

        try:
            result = json.loads(response.content)
            result["_meta"] = {
                "latency_ms": response.latency_ms,
                "cost": response.cost,
                "model": response.model,
            }
            return result
        except json.JSONDecodeError:
            return {
                "category": "unknown",
                "confidence": 0,
                "error": "Failed to parse response",
                "_meta": {"latency_ms": response.latency_ms},
            }

    def get_stats(self) -> Dict[str, Any]:
        """Get usage and performance statistics."""
        with self._lock:
            avg_latency = self._total_latency_ms / self._total_calls if self._total_calls > 0 else 0
            return {
                "total_calls": self._total_calls,
                "total_cost": self._total_cost,
                "total_latency_ms": self._total_latency_ms,
                "avg_latency_ms": avg_latency,
                "avg_cost_per_call": (
                    self._total_cost / self._total_calls if self._total_calls > 0 else 0
                ),
            }

    def reset_stats(self) -> None:
        """Reset usage statistics."""
        with self._lock:
            self._total_cost = 0.0
            self._total_calls = 0
            self._total_latency_ms = 0.0


# =============================================================================
# Async Groq Client
# =============================================================================


class AsyncGroqClient:
    """
    Async Groq client for concurrent operations.

    10x faster than sync for batch processing.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: Optional[str] = None,
        max_retries: int = 3,
        timeout: float = 60.0,
    ):
        """Initialize async client."""
        if not GROQ_AVAILABLE:
            raise ImportError("groq not installed. Run: pip install groq")

        self.api_key = api_key or get_config("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")

        self._timeout = httpx.Timeout(timeout=timeout, connect=10.0) if GROQ_AVAILABLE else None

        self.client = (
            AsyncGroq(api_key=self.api_key, max_retries=max_retries, timeout=self._timeout)
            if self.api_key
            else None
        )

        self.default_model = default_model or GroqModelSelector.TASK_DEFAULTS[TaskType.BALANCED]
        self._total_cost = 0.0
        self._total_calls = 0
        self._lock = asyncio.Lock()

    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for API call."""
        pricing = GroqModelSelector.get_pricing(model)
        cost = (input_tokens / 1_000_000) * pricing["input"]
        cost += (output_tokens / 1_000_000) * pricing["output"]
        return cost

    async def _track_usage(self, cost: float) -> None:
        """Track usage statistics."""
        async with self._lock:
            self._total_cost += cost
            self._total_calls += 1

    async def query(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        task_type: TaskType = TaskType.BALANCED,
        max_tokens: int = 2000,
        temperature: float = 0.0,
        json_mode: bool = False,
    ) -> GroqResponse:
        """
        Async query with intelligent model selection.

        Args:
            prompt: User prompt
            system: System prompt
            model: Model to use
            task_type: Task type for model selection
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            json_mode: Enable JSON mode

        Returns:
            GroqResponse
        """
        if not self.client:
            raise ValueError("Groq client not initialized.")

        model = model or GroqModelSelector.select_model(task_type)

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        kwargs = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        start_time = time.time()
        response = await self.client.chat.completions.create(**kwargs)
        latency_ms = (time.time() - start_time) * 1000

        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        cost = self._calculate_cost(model, input_tokens, output_tokens)

        await self._track_usage(cost)

        return GroqResponse(
            content=response.choices[0].message.content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model,
            cost=cost,
            latency_ms=latency_ms,
            tokens_per_second=(
                (input_tokens + output_tokens) / latency_ms * 1000 if latency_ms > 0 else 0
            ),
            finish_reason=response.choices[0].finish_reason,
        )

    async def concurrent_queries(
        self,
        prompts: List[str],
        system: Optional[str] = None,
        model: Optional[str] = None,
        task_type: TaskType = TaskType.BALANCED,
        max_tokens: int = 1000,
    ) -> List[GroqResponse]:
        """
        Execute multiple queries concurrently (10x faster than sequential).

        Args:
            prompts: List of prompts to process
            system: Shared system prompt
            model: Model to use
            task_type: Task type for model selection
            max_tokens: Max tokens per response

        Returns:
            List of GroqResponse objects
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
        task_type: TaskType = TaskType.BALANCED,
        max_tokens: int = 2000,
        temperature: float = 0.0,
    ) -> AsyncGenerator[str, None]:
        """
        Async streaming response.

        Args:
            prompt: User prompt
            system: System prompt
            model: Model to use
            task_type: Task type for model selection
            max_tokens: Maximum tokens
            temperature: Sampling temperature

        Yields:
            String chunks as they arrive
        """
        if not self.client:
            raise ValueError("Groq client not initialized.")

        model = model or GroqModelSelector.select_model(task_type)

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        stream = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def query_with_tools(
        self,
        prompt: str,
        tools: List[ToolDefinition],
        system: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.0,
        tool_choice: str = "auto",
    ) -> GroqResponse:
        """
        Async query with tool use.

        Args:
            prompt: User prompt
            tools: List of tool definitions
            system: System prompt
            model: Model to use
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            tool_choice: Tool choice strategy

        Returns:
            GroqResponse with tool calls
        """
        if not self.client:
            raise ValueError("Groq client not initialized.")

        model = model or GroqModelSelector.select_model(TaskType.TOOL_USE)

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        tools_schema = [t.to_dict() for t in tools]

        start_time = time.time()

        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools_schema,
            tool_choice=tool_choice,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        latency_ms = (time.time() - start_time) * 1000

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        cost = self._calculate_cost(model, input_tokens, output_tokens)

        await self._track_usage(cost)

        return GroqResponse(
            content=response_message.content or "",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model,
            cost=cost,
            latency_ms=latency_ms,
            tool_calls=(
                [
                    {"name": tc.function.name, "arguments": json.loads(tc.function.arguments)}
                    for tc in tool_calls
                ]
                if tool_calls
                else None
            ),
            finish_reason=response.choices[0].finish_reason,
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

    async def close(self) -> None:
        """Close the async client."""
        if self.client:
            await self.client.close()


# =============================================================================
# Batch Processing Client
# =============================================================================


class GroqBatchClient:
    """
    Batch processing client for 50% cost savings.

    Best for:
    - Bulk company research
    - Historical analysis
    - Non-time-sensitive tasks
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize batch client."""
        self.api_key = api_key or get_config("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
        self.base_url = "https://api.groq.com/openai/v1"

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    def create_batch_file(
        self, requests: List[Dict[str, Any]], output_path: str = "batch_input.jsonl"
    ) -> str:
        """
        Create JSONL file for batch processing.

        Args:
            requests: List of request dictionaries
            output_path: Output file path

        Returns:
            Path to created file
        """
        with open(output_path, "w") as f:
            for i, req in enumerate(requests):
                batch_req = {
                    "custom_id": req.get("custom_id", f"request-{i}"),
                    "method": "POST",
                    "url": "/v1/chat/completions",
                    "body": {
                        "model": req.get("model", "llama-3.1-8b-instant"),
                        "messages": req.get("messages", []),
                        "max_tokens": req.get("max_tokens", 1000),
                        "temperature": req.get("temperature", 0.0),
                    },
                }
                if req.get("json_mode"):
                    batch_req["body"]["response_format"] = {"type": "json_object"}

                f.write(json.dumps(batch_req) + "\n")

        return output_path

    def upload_batch_file(self, file_path: str) -> str:
        """
        Upload batch file to Groq.

        Args:
            file_path: Path to JSONL file

        Returns:
            File ID
        """
        import requests

        url = f"{self.base_url}/files"

        with open(file_path, "rb") as f:
            response = requests.post(
                url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                files={"file": f},
                data={"purpose": "batch"},
            )

        response.raise_for_status()
        return response.json()["id"]

    def submit_batch(self, input_file_id: str, completion_window: str = "24h") -> BatchJob:
        """
        Submit batch job.

        Args:
            input_file_id: Uploaded file ID
            completion_window: Completion window (24h)

        Returns:
            BatchJob with job details
        """
        import requests

        url = f"{self.base_url}/batches"

        response = requests.post(
            url,
            headers=self._get_headers(),
            json={
                "input_file_id": input_file_id,
                "endpoint": "/v1/chat/completions",
                "completion_window": completion_window,
            },
        )

        response.raise_for_status()
        data = response.json()

        return BatchJob(
            job_id=data["id"],
            status=data["status"],
            input_file_id=input_file_id,
            created_at=data.get("created_at"),
        )

    def get_batch_status(self, job_id: str) -> BatchJob:
        """
        Get batch job status.

        Args:
            job_id: Batch job ID

        Returns:
            BatchJob with current status
        """
        import requests

        url = f"{self.base_url}/batches/{job_id}"

        response = requests.get(url, headers={"Authorization": f"Bearer {self.api_key}"})

        response.raise_for_status()
        data = response.json()

        return BatchJob(
            job_id=data["id"],
            status=data["status"],
            input_file_id=data["input_file_id"],
            output_file_id=data.get("output_file_id"),
            created_at=data.get("created_at"),
            completed_at=data.get("completed_at"),
            request_counts=data.get("request_counts"),
            error=data.get("errors"),
        )

    def download_results(self, output_file_id: str) -> List[Dict[str, Any]]:
        """
        Download batch results.

        Args:
            output_file_id: Output file ID from completed batch

        Returns:
            List of result dictionaries
        """
        import requests

        url = f"{self.base_url}/files/{output_file_id}/content"

        response = requests.get(url, headers={"Authorization": f"Bearer {self.api_key}"})

        response.raise_for_status()

        results = []
        for line in response.text.strip().split("\n"):
            if line:
                results.append(json.loads(line))

        return results

    def process_batch(
        self,
        requests: List[Dict[str, Any]],
        wait_for_completion: bool = True,
        poll_interval: int = 30,
    ) -> Union[BatchJob, List[Dict[str, Any]]]:
        """
        Process batch end-to-end.

        Args:
            requests: List of request dictionaries
            wait_for_completion: Wait for results
            poll_interval: Polling interval in seconds

        Returns:
            BatchJob if not waiting, results if waiting
        """
        import os as os_module
        import tempfile

        # Create temp file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            temp_path = f.name

        try:
            # Create and upload batch file
            self.create_batch_file(requests, temp_path)
            file_id = self.upload_batch_file(temp_path)

            # Submit batch
            job = self.submit_batch(file_id)

            if not wait_for_completion:
                return job

            # Poll for completion
            while True:
                job = self.get_batch_status(job.job_id)

                if job.status == "completed":
                    if job.output_file_id:
                        return self.download_results(job.output_file_id)
                    return []
                elif job.status in ["failed", "cancelled", "expired"]:
                    raise RuntimeError(f"Batch job {job.status}: {job.error}")

                time.sleep(poll_interval)

        finally:
            # Cleanup temp file
            if os_module.path.exists(temp_path):
                os_module.remove(temp_path)


# =============================================================================
# Singleton Instances
# =============================================================================

_groq_client: Optional[GroqClient] = None
_async_groq_client: Optional[AsyncGroqClient] = None
_batch_client: Optional[GroqBatchClient] = None
_client_lock = Lock()


def get_groq_client() -> GroqClient:
    """Get singleton Groq client instance."""
    global _groq_client
    if _groq_client is None:
        with _client_lock:
            if _groq_client is None:
                _groq_client = GroqClient()
    return _groq_client


async def get_async_groq_client() -> AsyncGroqClient:
    """Get singleton async Groq client instance."""
    global _async_groq_client
    if _async_groq_client is None:
        _async_groq_client = AsyncGroqClient()
    return _async_groq_client


def get_batch_client() -> GroqBatchClient:
    """Get singleton batch client instance."""
    global _batch_client
    if _batch_client is None:
        with _client_lock:
            if _batch_client is None:
                _batch_client = GroqBatchClient()
    return _batch_client


def reset_groq_clients() -> None:
    """Reset all Groq client instances (for testing)."""
    global _groq_client, _async_groq_client, _batch_client
    _groq_client = None
    _async_groq_client = None
    _batch_client = None


# =============================================================================
# Convenience Functions
# =============================================================================


def create_tool(
    name: str, description: str, parameters: Dict[str, Any], function: Optional[Callable] = None
) -> ToolDefinition:
    """
    Create a tool definition for function calling.

    Args:
        name: Tool name
        description: Tool description
        parameters: JSON schema for parameters
        function: Optional callable to execute

    Returns:
        ToolDefinition

    Example:
        weather_tool = create_tool(
            name="get_weather",
            description="Get weather for a location",
            parameters={
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"}
                },
                "required": ["location"]
            },
            function=lambda location: {"temp": 72, "condition": "sunny"}
        )
    """
    return ToolDefinition(
        name=name, description=description, parameters=parameters, function=function
    )


# =============================================================================
# Research-Specific Tools
# =============================================================================


def create_research_tools() -> List[ToolDefinition]:
    """
    Create standard tools for company research.

    Returns:
        List of ToolDefinition objects for research tasks
    """
    return [
        ToolDefinition(
            name="search_company_data",
            description="Search for company information from various data sources",
            parameters={
                "type": "object",
                "properties": {
                    "company_name": {
                        "type": "string",
                        "description": "Name of the company to search",
                    },
                    "data_type": {
                        "type": "string",
                        "enum": ["financial", "market", "news", "sec_filings", "competitors"],
                        "description": "Type of data to retrieve",
                    },
                },
                "required": ["company_name", "data_type"],
            },
        ),
        ToolDefinition(
            name="analyze_sentiment",
            description="Analyze sentiment of text content",
            parameters={
                "type": "object",
                "properties": {"text": {"type": "string", "description": "Text to analyze"}},
                "required": ["text"],
            },
        ),
        ToolDefinition(
            name="extract_metrics",
            description="Extract financial or business metrics from text",
            parameters={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text containing metrics"},
                    "metric_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Types of metrics to extract (revenue, profit, growth, etc.)",
                    },
                },
                "required": ["text"],
            },
        ),
        ToolDefinition(
            name="compare_companies",
            description="Compare two or more companies on specific criteria",
            parameters={
                "type": "object",
                "properties": {
                    "companies": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of company names to compare",
                    },
                    "criteria": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Comparison criteria (market_share, revenue, innovation, etc.)",
                    },
                },
                "required": ["companies"],
            },
        ),
    ]
