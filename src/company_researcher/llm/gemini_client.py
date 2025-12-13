"""
Google Gemini API integration - Full-featured client with all API capabilities.

Features:
- Native Google Search grounding with citations
- Up to 2M token context (largest available)
- Context caching (75% savings on repeated content)
- Async support for concurrent operations
- Streaming responses
- Tool Use / Function Calling
- Task-based model selection
- Vision support (image analysis)

Pricing (per 1M tokens):
- Flash-8B: $0.04 input, $0.15 output (best value, fast)
- 1.5 Flash: $0.08 input, $0.30 output (balanced)
- 1.5 Pro: $1.25 input, $5.00 output (2M context)
- 2.0 Flash: $0.10 input, $0.40 output (latest)
- Grounding: $35/1K queries (free during preview)
- Context Cache: 75% discount on cached tokens

Usage:
    from company_researcher.llm.gemini_client import (
        get_gemini_client,
        get_async_gemini_client,
        GeminiTaskType,
    )

    # Sync client with task-based routing
    client = get_gemini_client()
    result = client.query("Analyze Tesla", task_type=GeminiTaskType.ANALYSIS)

    # Search with grounding (returns citations)
    result = client.search_with_grounding("Tesla Q4 2024 earnings")
    print(result.sources)

    # Context caching for repeated queries
    cache = client.create_cache(
        content=large_document,
        system_instruction="You are a document analyst"
    )
    result = client.query_with_cache("Summarize key points", cache_name=cache.name)

    # Async concurrent queries
    async_client = await get_async_gemini_client()
    results = await async_client.concurrent_queries([...])

    # Tool use / function calling
    tools = create_gemini_research_tools()
    result = client.query_with_tools("Get financial data for Apple", tools=tools)
"""

from typing import Optional, Dict, Any, List, Callable, Union, AsyncGenerator, Generator
from dataclasses import dataclass, field
from threading import Lock
from enum import Enum
import asyncio
import json
from ..utils import get_config, get_logger

logger = get_logger(__name__)

# Try to import google-generativeai
try:
    import google.generativeai as genai
    from google.generativeai import types as genai_types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None
    genai_types = None
    logger.warning("google-generativeai not installed. Run: pip install google-generativeai")


# =============================================================================
# Pricing Configuration
# =============================================================================

GEMINI_PRICING = {
    "gemini-1.5-flash-8b": {
        "input": 0.0375,
        "output": 0.15,
        "input_long": 0.075,  # >128K tokens
        "output_long": 0.30,
        "context_window": 1_000_000,
        "cache_discount": 0.75,  # 75% off for cached
        "speed": 1000,  # tokens/sec
    },
    "gemini-1.5-flash": {
        "input": 0.075,
        "output": 0.30,
        "input_long": 0.15,
        "output_long": 0.60,
        "context_window": 1_000_000,
        "cache_discount": 0.75,
        "speed": 800,
    },
    "gemini-1.5-pro": {
        "input": 1.25,
        "output": 5.00,
        "input_long": 2.50,
        "output_long": 10.00,
        "context_window": 2_000_000,
        "cache_discount": 0.75,
        "speed": 300,
    },
    "gemini-2.0-flash": {
        "input": 0.10,
        "output": 0.40,
        "input_long": 0.20,
        "output_long": 0.80,
        "context_window": 1_000_000,
        "cache_discount": 0.75,
        "speed": 900,
    },
    "gemini-2.0-flash-001": {
        "input": 0.10,
        "output": 0.40,
        "input_long": 0.20,
        "output_long": 0.80,
        "context_window": 1_000_000,
        "cache_discount": 0.75,
        "speed": 900,
    },
    "grounding": {
        "per_1k_queries": 35.00  # Free during preview
    }
}


# =============================================================================
# Task Types for Model Selection
# =============================================================================

class GeminiTaskType(Enum):
    """Task types for intelligent model selection."""
    SPEED = "speed"                # Fast responses - use Flash-8B
    BALANCED = "balanced"          # General purpose - use 1.5 Flash
    QUALITY = "quality"            # Best quality - use 1.5 Pro
    LONG_CONTEXT = "long_context"  # Large documents - use 1.5 Pro (2M)
    GROUNDING = "grounding"        # Search with citations
    EXTRACTION = "extraction"      # Data extraction - use Flash-8B
    ANALYSIS = "analysis"          # Analysis - use 1.5 Flash
    LATEST = "latest"              # Use 2.0 Flash


class GeminiModelSelector:
    """Intelligent model selection based on task type."""

    TASK_MODEL_MAP = {
        GeminiTaskType.SPEED: "gemini-1.5-flash-8b",
        GeminiTaskType.BALANCED: "gemini-1.5-flash",
        GeminiTaskType.QUALITY: "gemini-1.5-pro",
        GeminiTaskType.LONG_CONTEXT: "gemini-1.5-pro",
        GeminiTaskType.GROUNDING: "gemini-1.5-flash",
        GeminiTaskType.EXTRACTION: "gemini-1.5-flash-8b",
        GeminiTaskType.ANALYSIS: "gemini-1.5-flash",
        GeminiTaskType.LATEST: "gemini-2.0-flash",
    }

    @classmethod
    def select_model(
        cls,
        task_type: GeminiTaskType = GeminiTaskType.BALANCED,
        context_length: int = 0,
        require_grounding: bool = False,
        max_cost_per_1m: Optional[float] = None
    ) -> str:
        """
        Select optimal model based on task type and constraints.

        Args:
            task_type: Type of task
            context_length: Approximate context length in tokens
            require_grounding: Need Google Search grounding
            max_cost_per_1m: Maximum cost per 1M tokens

        Returns:
            Model ID string
        """
        # Long context requires Pro
        if context_length > 1_000_000:
            return "gemini-1.5-pro"

        # Cost constraint check
        if max_cost_per_1m is not None:
            if max_cost_per_1m < 0.10:
                return "gemini-1.5-flash-8b"
            elif max_cost_per_1m < 1.0:
                return "gemini-1.5-flash"

        return cls.TASK_MODEL_MAP.get(task_type, "gemini-1.5-flash")

    @classmethod
    def get_model_for_research_task(cls, task: str) -> str:
        """Map research task description to optimal model."""
        task_lower = task.lower()

        # Speed tasks
        if any(word in task_lower for word in ["quick", "fast", "simple", "classify"]):
            return "gemini-1.5-flash-8b"

        # Quality tasks
        if any(word in task_lower for word in ["complex", "detailed", "comprehensive", "deep"]):
            return "gemini-1.5-pro"

        # Long context tasks
        if any(word in task_lower for word in ["document", "report", "annual", "long"]):
            return "gemini-1.5-pro"

        # Default to balanced
        return "gemini-1.5-flash"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class GeminiSource:
    """Source from grounding."""
    title: str
    uri: str
    snippet: Optional[str] = None


@dataclass
class GeminiCache:
    """Cached content reference."""
    name: str
    model: str
    display_name: Optional[str] = None
    token_count: int = 0
    expire_time: Optional[str] = None


@dataclass
class GeminiResponse:
    """Response from Gemini API."""
    content: str
    sources: List[GeminiSource] = field(default_factory=list)
    grounding_used: bool = False
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    model: str = ""
    cost: float = 0.0
    tool_calls: Optional[List[Dict[str, Any]]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "sources": [{"title": s.title, "uri": s.uri, "snippet": s.snippet} for s in self.sources],
            "grounding_used": self.grounding_used,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cached_tokens": self.cached_tokens,
            "model": self.model,
            "cost": self.cost,
            "tool_calls": self.tool_calls
        }


@dataclass
class ToolDefinition:
    """Definition of a tool for function calling."""
    name: str
    description: str
    parameters: Dict[str, Any]
    function: Optional[Callable] = None

    def to_gemini_format(self) -> Dict[str, Any]:
        """Convert to Gemini function declaration format."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }


# =============================================================================
# Sync Client
# =============================================================================

class GeminiClient:
    """
    Full-featured Gemini API client.

    Features:
    - Task-based model selection
    - Google Search grounding with citations
    - Context caching (75% cost savings)
    - Tool use / function calling
    - Streaming responses
    - Long document analysis (up to 2M tokens)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = "gemini-1.5-flash"
    ):
        """
        Initialize Gemini client.

        Args:
            api_key: Google API key (or GOOGLE_API_KEY env var)
            default_model: Default model to use
        """
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai not installed. Run: pip install google-generativeai")

        self.api_key = api_key or get_config("GOOGLE_API_KEY")
        if not self.api_key:
            logger.warning("Google API key not found. Set GOOGLE_API_KEY env var.")
        else:
            genai.configure(api_key=self.api_key)

        self.default_model = default_model
        self._total_cost = 0.0
        self._total_calls = 0
        self._grounding_queries = 0
        self._cache_hits = 0
        self._lock = Lock()

        # Cache storage
        self._caches: Dict[str, GeminiCache] = {}

    def _calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cached_tokens: int = 0,
        grounding_used: bool = False
    ) -> float:
        """Calculate cost for a request."""
        pricing = GEMINI_PRICING.get(model, GEMINI_PRICING["gemini-1.5-flash"])

        # Check if long context pricing applies (>128K tokens)
        if input_tokens > 128_000:
            input_price = pricing.get("input_long", pricing["input"])
            output_price = pricing.get("output_long", pricing["output"])
        else:
            input_price = pricing["input"]
            output_price = pricing["output"]

        # Regular input cost
        uncached_input = input_tokens - cached_tokens
        cost = (uncached_input / 1_000_000) * input_price

        # Cached tokens at discount
        if cached_tokens > 0:
            cache_discount = pricing.get("cache_discount", 0.75)
            cost += (cached_tokens / 1_000_000) * input_price * (1 - cache_discount)

        # Output cost
        cost += (output_tokens / 1_000_000) * output_price

        return cost

    def query(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        task_type: GeminiTaskType = GeminiTaskType.BALANCED,
        max_tokens: int = 4000,
        temperature: float = 0.0,
        json_mode: bool = False
    ) -> GeminiResponse:
        """
        Query Gemini with task-based model selection.

        Args:
            prompt: User prompt
            system: System instruction
            model: Override model selection
            task_type: Task type for automatic model selection
            max_tokens: Maximum output tokens
            temperature: Sampling temperature
            json_mode: Request JSON output

        Returns:
            GeminiResponse with content and usage
        """
        model_name = model or GeminiModelSelector.select_model(task_type)

        generation_config = {
            "max_output_tokens": max_tokens,
            "temperature": temperature
        }

        if json_mode:
            generation_config["response_mime_type"] = "application/json"

        model_instance = genai.GenerativeModel(
            model_name,
            system_instruction=system,
            generation_config=generation_config
        )

        response = model_instance.generate_content(prompt)

        # Get usage
        input_tokens = getattr(response.usage_metadata, 'prompt_token_count', len(prompt) // 4) if hasattr(response, 'usage_metadata') else len(prompt) // 4
        output_tokens = getattr(response.usage_metadata, 'candidates_token_count', len(response.text) // 4) if hasattr(response, 'usage_metadata') else len(response.text) // 4

        cost = self._calculate_cost(model_name, input_tokens, output_tokens)

        with self._lock:
            self._total_cost += cost
            self._total_calls += 1

        return GeminiResponse(
            content=response.text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model_name,
            cost=cost
        )

    def search_with_grounding(
        self,
        query: str,
        context: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 4000
    ) -> GeminiResponse:
        """
        Search with Google grounding - returns citations.

        Best for:
        - Getting latest information
        - Fact-checking with sources
        - News and current events

        Args:
            query: Search query
            context: Additional context
            model: Model to use
            max_tokens: Maximum output tokens

        Returns:
            GeminiResponse with sources
        """
        model_name = model or "gemini-1.5-flash"

        # Create model with Google Search tool
        model_instance = genai.GenerativeModel(
            model_name,
            tools=[genai.Tool(google_search=genai.GoogleSearch())],
            generation_config={"max_output_tokens": max_tokens}
        )

        prompt = query
        if context:
            prompt = f"{context}\n\nSearch for: {query}"

        prompt += "\n\nProvide your answer based on the search results. Cite your sources."

        response = model_instance.generate_content(prompt)

        # Extract grounding sources
        sources = []
        grounding_used = False

        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                grounding_used = True
                grounding = candidate.grounding_metadata

                if hasattr(grounding, 'grounding_chunks'):
                    for chunk in grounding.grounding_chunks:
                        if hasattr(chunk, 'web'):
                            sources.append(GeminiSource(
                                title=getattr(chunk.web, 'title', 'Unknown'),
                                uri=getattr(chunk.web, 'uri', ''),
                                snippet=getattr(chunk, 'text', None)
                            ))

        # Get usage
        input_tokens = getattr(response.usage_metadata, 'prompt_token_count', len(prompt) // 4) if hasattr(response, 'usage_metadata') else len(prompt) // 4
        output_tokens = getattr(response.usage_metadata, 'candidates_token_count', len(response.text) // 4) if hasattr(response, 'usage_metadata') else len(response.text) // 4

        cost = self._calculate_cost(model_name, input_tokens, output_tokens, grounding_used=grounding_used)

        with self._lock:
            self._total_cost += cost
            self._total_calls += 1
            if grounding_used:
                self._grounding_queries += 1

        return GeminiResponse(
            content=response.text,
            sources=sources,
            grounding_used=grounding_used,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model_name,
            cost=cost
        )

    def create_cache(
        self,
        content: Union[str, List[str]],
        system_instruction: Optional[str] = None,
        model: str = "gemini-2.0-flash-001",
        display_name: Optional[str] = None,
        ttl_seconds: int = 300
    ) -> GeminiCache:
        """
        Create a context cache for repeated queries.

        Caching saves 75% on input token costs for repeated content.

        Args:
            content: Content to cache (text or list of texts)
            system_instruction: System instruction to cache
            model: Model to use (must be explicit version like -001)
            display_name: Optional display name for the cache
            ttl_seconds: Time-to-live in seconds (default 5 minutes)

        Returns:
            GeminiCache reference for use in queries
        """
        from google import genai as genai_new
        from google.genai import types

        # Use new client for caching
        client = genai_new.Client(api_key=self.api_key)

        # Prepare content
        if isinstance(content, str):
            contents = [content]
        else:
            contents = content

        cache_config = types.CreateCachedContentConfig(
            display_name=display_name,
            system_instruction=system_instruction,
            contents=contents,
            ttl=f"{ttl_seconds}s"
        )

        cache = client.caches.create(
            model=f"models/{model}",
            config=cache_config
        )

        gemini_cache = GeminiCache(
            name=cache.name,
            model=model,
            display_name=display_name,
            token_count=getattr(cache.usage_metadata, 'total_token_count', 0) if hasattr(cache, 'usage_metadata') else 0,
            expire_time=str(cache.expire_time) if hasattr(cache, 'expire_time') else None
        )

        # Store locally
        self._caches[cache.name] = gemini_cache

        logger.info(f"Created cache: {cache.name} with {gemini_cache.token_count} tokens")

        return gemini_cache

    def query_with_cache(
        self,
        prompt: str,
        cache_name: str,
        model: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 0.0
    ) -> GeminiResponse:
        """
        Query using cached content.

        Args:
            prompt: User prompt
            cache_name: Name of the cache to use
            model: Model override
            max_tokens: Maximum output tokens
            temperature: Sampling temperature

        Returns:
            GeminiResponse with cached token usage
        """
        from google import genai as genai_new
        from google.genai import types

        client = genai_new.Client(api_key=self.api_key)

        # Get cache info
        cache_info = self._caches.get(cache_name)
        model_name = model or (cache_info.model if cache_info else "gemini-2.0-flash-001")

        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                cached_content=cache_name,
                max_output_tokens=max_tokens,
                temperature=temperature
            )
        )

        # Extract usage with cached tokens
        usage = response.usage_metadata if hasattr(response, 'usage_metadata') else None
        input_tokens = getattr(usage, 'prompt_token_count', len(prompt) // 4) if usage else len(prompt) // 4
        output_tokens = getattr(usage, 'candidates_token_count', len(response.text) // 4) if usage else len(response.text) // 4
        cached_tokens = getattr(usage, 'cached_content_token_count', 0) if usage else 0

        cost = self._calculate_cost(model_name, input_tokens, output_tokens, cached_tokens)

        with self._lock:
            self._total_cost += cost
            self._total_calls += 1
            if cached_tokens > 0:
                self._cache_hits += 1

        return GeminiResponse(
            content=response.text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_tokens=cached_tokens,
            model=model_name,
            cost=cost
        )

    def query_with_tools(
        self,
        prompt: str,
        tools: List[ToolDefinition],
        system: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 0.0,
        auto_execute: bool = False
    ) -> GeminiResponse:
        """
        Query with tool use / function calling.

        Args:
            prompt: User prompt
            tools: List of tool definitions
            system: System instruction
            model: Model to use
            max_tokens: Maximum output tokens
            temperature: Sampling temperature
            auto_execute: Automatically execute tool functions

        Returns:
            GeminiResponse with tool_calls
        """
        model_name = model or "gemini-1.5-flash"

        # Convert tools to Gemini format
        function_declarations = [t.to_gemini_format() for t in tools]
        gemini_tools = [genai.Tool(function_declarations=function_declarations)]

        model_instance = genai.GenerativeModel(
            model_name,
            system_instruction=system,
            tools=gemini_tools,
            generation_config={
                "max_output_tokens": max_tokens,
                "temperature": temperature
            }
        )

        response = model_instance.generate_content(prompt)

        # Extract function calls
        tool_calls = None
        content = ""

        if response.candidates:
            candidate = response.candidates[0]
            for part in candidate.content.parts:
                if hasattr(part, 'function_call') and part.function_call:
                    fc = part.function_call
                    if tool_calls is None:
                        tool_calls = []

                    tool_call = {
                        "name": fc.name,
                        "arguments": dict(fc.args) if fc.args else {}
                    }

                    # Auto-execute if enabled
                    if auto_execute:
                        for tool in tools:
                            if tool.name == fc.name and tool.function:
                                try:
                                    result = tool.function(**tool_call["arguments"])
                                    tool_call["result"] = result
                                except Exception as e:
                                    tool_call["error"] = str(e)

                    tool_calls.append(tool_call)
                elif hasattr(part, 'text') and part.text:
                    content += part.text

        # Get usage
        input_tokens = getattr(response.usage_metadata, 'prompt_token_count', len(prompt) // 4) if hasattr(response, 'usage_metadata') else len(prompt) // 4
        output_tokens = getattr(response.usage_metadata, 'candidates_token_count', len(content) // 4) if hasattr(response, 'usage_metadata') else len(content) // 4

        cost = self._calculate_cost(model_name, input_tokens, output_tokens)

        with self._lock:
            self._total_cost += cost
            self._total_calls += 1

        return GeminiResponse(
            content=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model_name,
            cost=cost,
            tool_calls=tool_calls
        )

    def stream_query(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        task_type: GeminiTaskType = GeminiTaskType.BALANCED,
        max_tokens: int = 4000,
        temperature: float = 0.0
    ) -> Generator[str, None, GeminiResponse]:
        """
        Stream response tokens in real-time.

        Args:
            prompt: User prompt
            system: System instruction
            model: Model to use
            task_type: Task type for model selection
            max_tokens: Maximum output tokens
            temperature: Sampling temperature

        Yields:
            Text chunks as they arrive

        Returns:
            Final GeminiResponse with stats
        """
        model_name = model or GeminiModelSelector.select_model(task_type)

        model_instance = genai.GenerativeModel(
            model_name,
            system_instruction=system,
            generation_config={
                "max_output_tokens": max_tokens,
                "temperature": temperature
            }
        )

        response = model_instance.generate_content(prompt, stream=True)

        full_content = ""
        for chunk in response:
            if chunk.text:
                full_content += chunk.text
                yield chunk.text

        # Estimate tokens
        input_tokens = len(prompt) // 4
        output_tokens = len(full_content) // 4
        cost = self._calculate_cost(model_name, input_tokens, output_tokens)

        with self._lock:
            self._total_cost += cost
            self._total_calls += 1

        return GeminiResponse(
            content=full_content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model_name,
            cost=cost
        )

    def analyze_long_document(
        self,
        document: str,
        analysis_prompt: str,
        model: str = "gemini-1.5-pro"
    ) -> GeminiResponse:
        """
        Analyze documents up to 2M tokens.

        Best for: Annual reports, large document sets, multiple files.

        Args:
            document: Document text (up to 2M tokens)
            analysis_prompt: What to analyze
            model: Model to use (default: 1.5 Pro for 2M context)

        Returns:
            GeminiResponse with analysis
        """
        model_instance = genai.GenerativeModel(
            model,
            generation_config={"max_output_tokens": 8000}
        )

        full_prompt = f"""{analysis_prompt}

Document:
{document}"""

        response = model_instance.generate_content(full_prompt)

        input_tokens = getattr(response.usage_metadata, 'prompt_token_count', len(full_prompt) // 4) if hasattr(response, 'usage_metadata') else len(full_prompt) // 4
        output_tokens = getattr(response.usage_metadata, 'candidates_token_count', len(response.text) // 4) if hasattr(response, 'usage_metadata') else len(response.text) // 4

        cost = self._calculate_cost(model, input_tokens, output_tokens)

        with self._lock:
            self._total_cost += cost
            self._total_calls += 1

        return GeminiResponse(
            content=response.text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model,
            cost=cost
        )

    # Convenience methods for research
    def research_company_news(
        self,
        company_name: str,
        topics: Optional[List[str]] = None,
        days_back: int = 30
    ) -> GeminiResponse:
        """Get latest news for a company with citations."""
        topics_str = ", ".join(topics) if topics else "latest news and developments"
        query = f"{company_name} {topics_str} news last {days_back} days"

        context = f"""Research {company_name} focusing on recent news.
Include:
1. Recent announcements and press releases
2. Financial results or guidance updates
3. Product launches or updates
4. Leadership changes
5. Market reactions

Prioritize information from the past {days_back} days.
Include specific dates for all news items."""

        return self.search_with_grounding(query, context)

    def get_competitive_intelligence(
        self,
        company_name: str,
        competitors: List[str]
    ) -> GeminiResponse:
        """Get competitive analysis with citations."""
        competitors_str = ", ".join(competitors)
        query = f"{company_name} vs {competitors_str} market share competition analysis"

        context = f"""Compare {company_name} with {competitors_str}:
1. Market Position (market share, trends)
2. Product/Service Comparison
3. Financial Comparison (if available)
4. Recent Strategic Moves
5. Analyst Perspectives

Use the most recent data available and cite all sources."""

        return self.search_with_grounding(query, context)

    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        with self._lock:
            return {
                "total_calls": self._total_calls,
                "total_cost": self._total_cost,
                "grounding_queries": self._grounding_queries,
                "cache_hits": self._cache_hits,
                "active_caches": len(self._caches),
                "avg_cost_per_call": self._total_cost / self._total_calls if self._total_calls > 0 else 0
            }

    def reset_stats(self) -> None:
        """Reset usage statistics."""
        with self._lock:
            self._total_cost = 0.0
            self._total_calls = 0
            self._grounding_queries = 0
            self._cache_hits = 0


# =============================================================================
# Async Client
# =============================================================================

class AsyncGeminiClient:
    """
    Async Gemini client for concurrent operations.

    Use when:
    - Processing multiple queries in parallel
    - Building async applications
    - Need non-blocking I/O
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = "gemini-1.5-flash"
    ):
        """Initialize async client."""
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai not installed.")

        self.api_key = api_key or get_config("GOOGLE_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)

        self.default_model = default_model
        self._total_cost = 0.0
        self._total_calls = 0
        self._lock = asyncio.Lock()

    async def query(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        task_type: GeminiTaskType = GeminiTaskType.BALANCED,
        max_tokens: int = 4000,
        temperature: float = 0.0,
        json_mode: bool = False
    ) -> GeminiResponse:
        """Async query with task-based model selection."""
        model_name = model or GeminiModelSelector.select_model(task_type)

        generation_config = {
            "max_output_tokens": max_tokens,
            "temperature": temperature
        }

        if json_mode:
            generation_config["response_mime_type"] = "application/json"

        model_instance = genai.GenerativeModel(
            model_name,
            system_instruction=system,
            generation_config=generation_config
        )

        # Use async generate
        response = await model_instance.generate_content_async(prompt)

        input_tokens = getattr(response.usage_metadata, 'prompt_token_count', len(prompt) // 4) if hasattr(response, 'usage_metadata') else len(prompt) // 4
        output_tokens = getattr(response.usage_metadata, 'candidates_token_count', len(response.text) // 4) if hasattr(response, 'usage_metadata') else len(response.text) // 4

        pricing = GEMINI_PRICING.get(model_name, GEMINI_PRICING["gemini-1.5-flash"])
        input_price = pricing["input_long"] if input_tokens > 128_000 else pricing["input"]
        output_price = pricing["output_long"] if input_tokens > 128_000 else pricing["output"]
        cost = (input_tokens / 1_000_000) * input_price + (output_tokens / 1_000_000) * output_price

        async with self._lock:
            self._total_cost += cost
            self._total_calls += 1

        return GeminiResponse(
            content=response.text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model_name,
            cost=cost
        )

    async def concurrent_queries(
        self,
        prompts: List[str],
        system: Optional[str] = None,
        model: Optional[str] = None,
        task_type: GeminiTaskType = GeminiTaskType.BALANCED,
        max_tokens: int = 4000
    ) -> List[GeminiResponse]:
        """
        Execute multiple queries concurrently.

        Args:
            prompts: List of prompts
            system: Shared system instruction
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
                max_tokens=max_tokens
            )
            for prompt in prompts
        ]

        return await asyncio.gather(*tasks)

    async def stream_query(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        task_type: GeminiTaskType = GeminiTaskType.BALANCED,
        max_tokens: int = 4000,
        temperature: float = 0.0
    ) -> AsyncGenerator[str, None]:
        """Async streaming query."""
        model_name = model or GeminiModelSelector.select_model(task_type)

        model_instance = genai.GenerativeModel(
            model_name,
            system_instruction=system,
            generation_config={
                "max_output_tokens": max_tokens,
                "temperature": temperature
            }
        )

        response = await model_instance.generate_content_async(prompt, stream=True)

        async for chunk in response:
            if chunk.text:
                yield chunk.text

    async def search_with_grounding(
        self,
        query: str,
        context: Optional[str] = None,
        model: Optional[str] = None
    ) -> GeminiResponse:
        """Async search with Google grounding."""
        model_name = model or "gemini-1.5-flash"

        model_instance = genai.GenerativeModel(
            model_name,
            tools=[genai.Tool(google_search=genai.GoogleSearch())]
        )

        prompt = f"{context}\n\nSearch for: {query}" if context else query
        prompt += "\n\nProvide your answer based on the search results. Cite your sources."

        response = await model_instance.generate_content_async(prompt)

        sources = []
        grounding_used = False

        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                grounding_used = True
                grounding = candidate.grounding_metadata

                if hasattr(grounding, 'grounding_chunks'):
                    for chunk in grounding.grounding_chunks:
                        if hasattr(chunk, 'web'):
                            sources.append(GeminiSource(
                                title=getattr(chunk.web, 'title', 'Unknown'),
                                uri=getattr(chunk.web, 'uri', ''),
                                snippet=getattr(chunk, 'text', None)
                            ))

        input_tokens = len(prompt) // 4
        output_tokens = len(response.text) // 4
        pricing = GEMINI_PRICING.get(model_name, GEMINI_PRICING["gemini-1.5-flash"])
        cost = (input_tokens / 1_000_000) * pricing["input"] + (output_tokens / 1_000_000) * pricing["output"]

        async with self._lock:
            self._total_cost += cost
            self._total_calls += 1

        return GeminiResponse(
            content=response.text,
            sources=sources,
            grounding_used=grounding_used,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model_name,
            cost=cost
        )

    async def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        async with self._lock:
            return {
                "total_calls": self._total_calls,
                "total_cost": self._total_cost,
                "avg_cost_per_call": self._total_cost / self._total_calls if self._total_calls > 0 else 0
            }


# =============================================================================
# Tool Creation Helpers
# =============================================================================

def create_tool(
    name: str,
    description: str,
    parameters: Dict[str, Any],
    function: Optional[Callable] = None
) -> ToolDefinition:
    """Create a tool definition for function calling."""
    return ToolDefinition(
        name=name,
        description=description,
        parameters=parameters,
        function=function
    )


def create_gemini_research_tools() -> List[ToolDefinition]:
    """Create research-specific tools for Gemini function calling."""
    return [
        ToolDefinition(
            name="search_company_info",
            description="Search for company information from the web",
            parameters={
                "type": "object",
                "properties": {
                    "company_name": {"type": "string", "description": "Company name to search"},
                    "info_type": {
                        "type": "string",
                        "enum": ["financial", "news", "products", "leadership", "competitors"],
                        "description": "Type of information to find"
                    }
                },
                "required": ["company_name"]
            }
        ),
        ToolDefinition(
            name="extract_metrics",
            description="Extract financial metrics from text",
            parameters={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text containing metrics"},
                    "metric_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Types of metrics to extract"
                    }
                },
                "required": ["text"]
            }
        ),
        ToolDefinition(
            name="compare_companies",
            description="Compare multiple companies on specific dimensions",
            parameters={
                "type": "object",
                "properties": {
                    "companies": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of company names"
                    },
                    "dimensions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Comparison dimensions"
                    }
                },
                "required": ["companies"]
            }
        )
    ]


# =============================================================================
# Singleton Instances
# =============================================================================

_gemini_client: Optional[GeminiClient] = None
_async_gemini_client: Optional[AsyncGeminiClient] = None
_client_lock = Lock()


def get_gemini_client() -> GeminiClient:
    """Get singleton Gemini client instance."""
    global _gemini_client
    if _gemini_client is None:
        with _client_lock:
            if _gemini_client is None:
                _gemini_client = GeminiClient()
    return _gemini_client


async def get_async_gemini_client() -> AsyncGeminiClient:
    """Get singleton async Gemini client instance."""
    global _async_gemini_client
    if _async_gemini_client is None:
        _async_gemini_client = AsyncGeminiClient()
    return _async_gemini_client


def reset_gemini_clients() -> None:
    """Reset all Gemini client instances."""
    global _gemini_client, _async_gemini_client
    _gemini_client = None
    _async_gemini_client = None
