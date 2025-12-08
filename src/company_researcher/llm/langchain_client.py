"""
LangChain LLM Client with Full LangSmith Tracing.

This module provides LangChain-wrapped LLM clients that enable automatic
LangSmith tracing for all LLM calls. Use these instead of direct Anthropic SDK
calls to get full observability.

Features:
- Automatic trace capture to LangSmith
- Cost tracking per call
- Latency monitoring
- Token usage tracking
- Callbacks for custom processing

Usage:
    from company_researcher.llm import get_llm, invoke_with_tracing

    # Simple usage
    llm = get_llm()
    response = llm.invoke("Analyze Tesla's financial health")

    # With tracing metadata
    response = invoke_with_tracing(
        llm=llm,
        prompt="Analyze Tesla's financials",
        run_name="financial_analysis",
        tags=["tesla", "financial"],
        metadata={"agent": "financial_agent"}
    )
"""

import os
import time
import logging
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass
from datetime import datetime

from ..config import get_config
from .client_factory import safe_extract_text

logger = logging.getLogger(__name__)

# LangChain imports with graceful fallback
try:
    from langchain_anthropic import ChatAnthropic
    from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.callbacks import BaseCallbackHandler
    from langchain_core.runnables import RunnableConfig
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    ChatAnthropic = None
    HumanMessage = None
    SystemMessage = None
    AIMessage = None
    ChatPromptTemplate = None
    StrOutputParser = None
    BaseCallbackHandler = None
    RunnableConfig = None

# Fallback to direct Anthropic if LangChain not available
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    Anthropic = None


@dataclass
class TracedLLMResponse:
    """Response from a traced LLM call."""
    content: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_usd: float
    latency_ms: float
    model: str
    run_id: Optional[str] = None
    trace_url: Optional[str] = None


class CostTrackingCallback(BaseCallbackHandler if LANGCHAIN_AVAILABLE else object):
    """Callback handler for tracking costs and tokens."""

    def __init__(self):
        self.input_tokens = 0
        self.output_tokens = 0
        self.total_cost = 0.0
        self.start_time = None
        self.end_time = None
        self.runs = []

    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs):
        """Called when LLM starts processing."""
        self.start_time = time.time()

    def on_llm_end(self, response, **kwargs):
        """Called when LLM finishes processing."""
        self.end_time = time.time()

        # Extract token usage from response
        if hasattr(response, 'llm_output') and response.llm_output:
            usage = response.llm_output.get('usage', {})
            self.input_tokens += usage.get('input_tokens', 0)
            self.output_tokens += usage.get('output_tokens', 0)

        # Store run info if available
        if hasattr(response, 'run') and response.run:
            self.runs.append({
                'run_id': str(response.run.id) if hasattr(response.run, 'id') else None,
                'latency_ms': (self.end_time - self.start_time) * 1000 if self.start_time else 0
            })

    @property
    def latency_ms(self) -> float:
        """Get latency in milliseconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time) * 1000
        return 0.0


def get_llm(
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    streaming: bool = False,
    **kwargs
) -> "ChatAnthropic":
    """
    Get a LangChain-wrapped Anthropic LLM with tracing enabled.

    This is the primary way to get an LLM instance that will be
    automatically traced by LangSmith.

    Args:
        model: Model name (default: from config)
        temperature: Temperature setting (default: from config)
        max_tokens: Max output tokens (default: from config)
        streaming: Enable streaming responses
        **kwargs: Additional arguments passed to ChatAnthropic

    Returns:
        ChatAnthropic instance with tracing enabled

    Raises:
        ImportError: If langchain-anthropic is not installed
    """
    if not LANGCHAIN_AVAILABLE:
        raise ImportError(
            "langchain-anthropic is required for traced LLM calls. "
            "Install with: pip install langchain-anthropic"
        )

    config = get_config()

    return ChatAnthropic(
        model=model or config.llm_model,
        temperature=temperature if temperature is not None else config.llm_temperature,
        max_tokens=max_tokens or config.llm_max_tokens,
        anthropic_api_key=config.anthropic_api_key,
        streaming=streaming,
        **kwargs
    )


def get_chat_model(
    model: Optional[str] = None,
    system_prompt: Optional[str] = None,
    **kwargs
) -> "ChatAnthropic":
    """
    Get a chat model with optional system prompt.

    Args:
        model: Model name
        system_prompt: System prompt to prepend
        **kwargs: Additional arguments

    Returns:
        Configured ChatAnthropic instance
    """
    llm = get_llm(model=model, **kwargs)

    if system_prompt:
        # Bind system message
        return llm.bind(system=system_prompt)

    return llm


def invoke_with_tracing(
    prompt: str,
    llm: Optional["ChatAnthropic"] = None,
    system_prompt: Optional[str] = None,
    run_name: Optional[str] = None,
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    **kwargs
) -> TracedLLMResponse:
    """
    Invoke LLM with full LangSmith tracing.

    This function ensures the LLM call is traced with:
    - Custom run name for easy identification
    - Tags for filtering
    - Metadata for context
    - Token and cost tracking

    Args:
        prompt: The prompt to send to the LLM
        llm: Optional LLM instance (creates one if not provided)
        system_prompt: Optional system prompt
        run_name: Name for this run in LangSmith
        tags: Tags for filtering in LangSmith
        metadata: Additional metadata to attach
        **kwargs: Additional invoke arguments

    Returns:
        TracedLLMResponse with content and metrics
    """
    if not LANGCHAIN_AVAILABLE:
        # Fallback to direct Anthropic call
        return _invoke_anthropic_direct(prompt, system_prompt)

    config = get_config()
    llm = llm or get_llm()

    # Set up callbacks
    cost_callback = CostTrackingCallback()

    # Build runnable config
    run_config = RunnableConfig(
        callbacks=[cost_callback],
        tags=tags or [],
        metadata={
            **(metadata or {}),
            "timestamp": datetime.now().isoformat(),
            "model": config.llm_model,
        },
        run_name=run_name or "llm_invoke",
    )

    # Build messages
    messages = []
    if system_prompt:
        messages.append(SystemMessage(content=system_prompt))
    messages.append(HumanMessage(content=prompt))

    # Invoke with timing
    start_time = time.time()
    response = llm.invoke(messages, config=run_config, **kwargs)
    latency_ms = (time.time() - start_time) * 1000

    # Extract content
    content = response.content if hasattr(response, 'content') else str(response)

    # Get token counts from response metadata
    input_tokens = 0
    output_tokens = 0

    if hasattr(response, 'response_metadata'):
        usage = response.response_metadata.get('usage', {})
        input_tokens = usage.get('input_tokens', 0)
        output_tokens = usage.get('output_tokens', 0)

    # Fallback to callback tracking
    if input_tokens == 0:
        input_tokens = cost_callback.input_tokens
    if output_tokens == 0:
        output_tokens = cost_callback.output_tokens

    # Calculate cost
    cost_usd = config.calculate_llm_cost(input_tokens, output_tokens)

    # Get run ID if available
    run_id = None
    if cost_callback.runs:
        run_id = cost_callback.runs[-1].get('run_id')

    # Build trace URL
    trace_url = None
    if run_id:
        project = os.environ.get("LANGCHAIN_PROJECT", "langai-research")
        trace_url = f"https://smith.langchain.com/o/default/projects/p/{project}/r/{run_id}"

    return TracedLLMResponse(
        content=content,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=input_tokens + output_tokens,
        cost_usd=cost_usd,
        latency_ms=latency_ms,
        model=config.llm_model,
        run_id=run_id,
        trace_url=trace_url,
    )


async def ainvoke_with_tracing(
    prompt: str,
    llm: Optional["ChatAnthropic"] = None,
    system_prompt: Optional[str] = None,
    run_name: Optional[str] = None,
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    **kwargs
) -> TracedLLMResponse:
    """
    Async version of invoke_with_tracing.

    Args:
        prompt: The prompt to send to the LLM
        llm: Optional LLM instance
        system_prompt: Optional system prompt
        run_name: Name for this run in LangSmith
        tags: Tags for filtering
        metadata: Additional metadata
        **kwargs: Additional invoke arguments

    Returns:
        TracedLLMResponse with content and metrics
    """
    if not LANGCHAIN_AVAILABLE:
        return _invoke_anthropic_direct(prompt, system_prompt)

    config = get_config()
    llm = llm or get_llm()

    # Set up callbacks
    cost_callback = CostTrackingCallback()

    # Build runnable config
    run_config = RunnableConfig(
        callbacks=[cost_callback],
        tags=tags or [],
        metadata={
            **(metadata or {}),
            "timestamp": datetime.now().isoformat(),
            "model": config.llm_model,
        },
        run_name=run_name or "llm_ainvoke",
    )

    # Build messages
    messages = []
    if system_prompt:
        messages.append(SystemMessage(content=system_prompt))
    messages.append(HumanMessage(content=prompt))

    # Invoke with timing
    start_time = time.time()
    response = await llm.ainvoke(messages, config=run_config, **kwargs)
    latency_ms = (time.time() - start_time) * 1000

    # Extract content
    content = response.content if hasattr(response, 'content') else str(response)

    # Get token counts
    input_tokens = 0
    output_tokens = 0

    if hasattr(response, 'response_metadata'):
        usage = response.response_metadata.get('usage', {})
        input_tokens = usage.get('input_tokens', 0)
        output_tokens = usage.get('output_tokens', 0)

    # Calculate cost
    cost_usd = config.calculate_llm_cost(input_tokens, output_tokens)

    return TracedLLMResponse(
        content=content,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=input_tokens + output_tokens,
        cost_usd=cost_usd,
        latency_ms=latency_ms,
        model=config.llm_model,
    )


def _invoke_anthropic_direct(
    prompt: str,
    system_prompt: Optional[str] = None
) -> TracedLLMResponse:
    """
    Fallback to direct Anthropic SDK (not traced).

    Used when LangChain is not available.
    """
    if not ANTHROPIC_AVAILABLE:
        raise ImportError(
            "Neither langchain-anthropic nor anthropic is installed. "
            "Install with: pip install langchain-anthropic"
        )

    config = get_config()
    client = Anthropic(api_key=config.anthropic_api_key)

    start_time = time.time()

    kwargs = {
        "model": config.llm_model,
        "max_tokens": config.llm_max_tokens,
        "temperature": config.llm_temperature,
        "messages": [{"role": "user", "content": prompt}]
    }

    if system_prompt:
        kwargs["system"] = system_prompt

    response = client.messages.create(**kwargs)

    latency_ms = (time.time() - start_time) * 1000

    content = safe_extract_text(response, agent_name="langchain_client")
    input_tokens = response.usage.input_tokens
    output_tokens = response.usage.output_tokens
    cost_usd = config.calculate_llm_cost(input_tokens, output_tokens)

    logger.warning(
        "[LLM] Using direct Anthropic SDK (not traced). "
        "Install langchain-anthropic for LangSmith tracing."
    )

    return TracedLLMResponse(
        content=content,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=input_tokens + output_tokens,
        cost_usd=cost_usd,
        latency_ms=latency_ms,
        model=config.llm_model,
    )


class LangChainClient:
    """
    High-level LangChain client for common operations.

    Provides convenient methods for different types of LLM calls
    with automatic tracing.
    """

    def __init__(
        self,
        model: Optional[str] = None,
        default_tags: Optional[List[str]] = None
    ):
        """
        Initialize LangChain client.

        Args:
            model: Model to use (default: from config)
            default_tags: Tags to apply to all calls
        """
        self.model = model
        self.default_tags = default_tags or []
        self._llm: Optional[ChatAnthropic] = None

    @property
    def llm(self) -> "ChatAnthropic":
        """Get or create the LLM instance."""
        if self._llm is None:
            self._llm = get_llm(model=self.model)
        return self._llm

    def analyze(
        self,
        prompt: str,
        context: Optional[str] = None,
        run_name: str = "analysis",
        **kwargs
    ) -> TracedLLMResponse:
        """
        Perform an analysis task.

        Args:
            prompt: Analysis prompt
            context: Additional context to include
            run_name: Name for the run
            **kwargs: Additional arguments

        Returns:
            TracedLLMResponse
        """
        full_prompt = prompt
        if context:
            full_prompt = f"Context:\n{context}\n\nTask:\n{prompt}"

        return invoke_with_tracing(
            prompt=full_prompt,
            llm=self.llm,
            run_name=run_name,
            tags=self.default_tags + ["analysis"],
            **kwargs
        )

    def extract(
        self,
        text: str,
        extraction_prompt: str,
        run_name: str = "extraction",
        **kwargs
    ) -> TracedLLMResponse:
        """
        Extract information from text.

        Args:
            text: Text to extract from
            extraction_prompt: What to extract
            run_name: Name for the run
            **kwargs: Additional arguments

        Returns:
            TracedLLMResponse
        """
        prompt = f"{extraction_prompt}\n\nText:\n{text}"

        return invoke_with_tracing(
            prompt=prompt,
            llm=self.llm,
            run_name=run_name,
            tags=self.default_tags + ["extraction"],
            **kwargs
        )

    def summarize(
        self,
        text: str,
        max_length: Optional[int] = None,
        run_name: str = "summarization",
        **kwargs
    ) -> TracedLLMResponse:
        """
        Summarize text.

        Args:
            text: Text to summarize
            max_length: Optional maximum length hint
            run_name: Name for the run
            **kwargs: Additional arguments

        Returns:
            TracedLLMResponse
        """
        prompt = f"Summarize the following text"
        if max_length:
            prompt += f" in approximately {max_length} words"
        prompt += f":\n\n{text}"

        return invoke_with_tracing(
            prompt=prompt,
            llm=self.llm,
            run_name=run_name,
            tags=self.default_tags + ["summarization"],
            **kwargs
        )
