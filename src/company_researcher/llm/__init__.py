"""
LangChain LLM Module for Company Researcher.

This module provides:
- Centralized LLM client factory (eliminates 22-file duplication)
- Response parsing utilities
- LangChain-wrapped LLM clients with LangSmith tracing
- Automatic cost tracking
- Session replay and debugging
- Performance monitoring

Usage:
    from company_researcher.llm import get_anthropic_client, create_message
    from company_researcher.llm import parse_json_response

    # Get shared client instance (recommended)
    client = get_anthropic_client()

    # Or use convenience function
    response = create_message(prompt="Analyze this company...")

    # Parse JSON from response
    data = parse_json_response(response.content[0].text, default={})
"""

# Batch Processing (50% cost reduction)
from .batch_processor import (
    BatchProcessor,
    BatchRequest,
    BatchResult,
    BatchStatus,
    get_batch_processor,
)

# Client Factory (centralized client management)
from .client_factory import (
    LLMClientFactory,
    LLMResponseError,
    calculate_cost,
    create_message,
    get_anthropic_client,
    get_factory,
    get_tavily_client,
    reset_clients,
    safe_extract_json,
    safe_extract_text,
)

# Cost Tracking (detailed metrics)
from .cost_tracker import APICall, CostSummary, CostTracker, get_cost_tracker

# DeepSeek (Ultra-low cost: $0.14/1M tokens, reasoning, FIM, tool use)
from .deepseek_client import (
    DEEPSEEK_PRICING,
    AsyncDeepSeekClient,
    DeepSeekClient,
    DeepSeekModelSelector,
    DeepSeekResponse,
    DeepSeekTaskType,
)
from .deepseek_client import (
    ToolDefinition as DeepSeekToolDefinition,  # Sync Client; Async Client (concurrent queries); Model Selection (task-based routing); Tool Use / Function Calling; Utilities
)
from .deepseek_client import (
    create_deepseek_research_tools,
    get_async_deepseek_client,
    get_deepseek_client,
    reset_deepseek_clients,
)

# Gemini (Search grounding + 2M context + caching + tool use)
from .gemini_client import (
    GEMINI_PRICING,
    AsyncGeminiClient,
    GeminiCache,
    GeminiClient,
    GeminiModelSelector,
    GeminiResponse,
    GeminiSource,
    GeminiTaskType,
)
from .gemini_client import (
    ToolDefinition as GeminiToolDefinition,  # Sync Client; Async Client (concurrent queries); Model Selection (task-based routing); Context Caching (75% cost savings); Tool Use / Function Calling; Utilities
)
from .gemini_client import (
    create_gemini_research_tools,
    get_async_gemini_client,
    get_gemini_client,
    reset_gemini_clients,
)

# Groq (Ultra-fast: 1,300 tok/sec, async, tool use, batch)
from .groq_client import AsyncGroqClient
from .groq_client import (
    BatchJob as GroqBatchJob,  # Sync Client; Async Client (10x faster batch); Batch Processing (50% cost savings); Model Selection; Tool Use / Function Calling; Utilities
)
from .groq_client import GroqBatchClient, GroqClient, GroqModelSelector, GroqResponse
from .groq_client import TaskType as GroqTaskType
from .groq_client import ToolDefinition as GroqToolDefinition
from .groq_client import create_research_tools as create_groq_research_tools
from .groq_client import create_tool as create_groq_tool
from .groq_client import get_async_groq_client
from .groq_client import get_batch_client as get_groq_batch_client
from .groq_client import get_groq_client, reset_groq_clients

# LangChain Client
from .langchain_client import (
    LangChainClient,
    TracedLLMResponse,
    ainvoke_with_tracing,
    get_chat_model,
    get_llm,
    invoke_with_tracing,
)

# LangSmith Setup
from .langsmith_setup import (
    create_run_tree,
    flush_traces,
    get_langsmith_url,
    init_langsmith,
    is_langsmith_enabled,
)

# Model Router
from .model_router import (
    ModelConfig,
    ModelRegistry,
    ModelRouter,
    ModelTier,
    RoutingDecision,
    TaskType,
    create_router_for_extraction,
    create_router_for_research,
    get_model_for_task,
)

# Prompt Caching (25% cost reduction)
from .prompt_cache import PromptCache, create_cached_analysis_request, get_prompt_cache

# Response Parser (centralized parsing utilities)
from .response_parser import (
    ParseResult,
    ResponseParser,
    extract_json_block,
    extract_list_from_response,
    extract_number_from_response,
    extract_sections_from_response,
    parse_json_response,
)

# Response Validation (safe API response handling)
from .response_validation import (
    ValidatedAnthropicResponse,
    ValidatedTavilyResponse,
    ValidatedTavilyResult,
    ValidationError,
    enforce_response_limits,
    extract_anthropic_content,
    extract_tavily_results,
    safe_get,
    validate_anthropic_response,
    validate_json_response,
    validate_required_fields,
    validate_tavily_response,
)

# Smart Client (Automatic model routing for cost optimization)
from .smart_client import (
    CompletionResult,
    SmartLLMClient,
    analyze_text,
    extract_data,
    generate_report,
    get_smart_client,
    print_llm_stats,
    smart_completion,
)

# Streaming (real-time responses)
from .streaming import (
    StreamingClient,
    StreamingProgressPrinter,
    StreamingResult,
    StreamingStats,
    get_streaming_client,
    stream_research_analysis,
)

# Tool Use (structured extraction)
from .tool_use import (
    FINANCIAL_EXTRACTION_TOOLS,
    ExtractionResult,
    StructuredExtractor,
    get_structured_extractor,
)

# Vision (image analysis)
from .vision import ImageAnalysisResult, VisionAnalyzer, get_vision_analyzer

# Web Search ($10/1K searches)
from .web_search import ClaudeWebSearch, WebSearchResult, get_claude_web_search

__all__ = [
    # Client Factory (PRIMARY - use these for new code)
    "LLMClientFactory",
    "LLMResponseError",
    "get_factory",
    "get_anthropic_client",
    "get_tavily_client",
    "create_message",
    "calculate_cost",
    "reset_clients",
    "safe_extract_text",
    "safe_extract_json",
    # Response Parser
    "ResponseParser",
    "ParseResult",
    "parse_json_response",
    "extract_json_block",
    "extract_list_from_response",
    "extract_sections_from_response",
    "extract_number_from_response",
    # LangChain Client
    "get_llm",
    "get_chat_model",
    "invoke_with_tracing",
    "ainvoke_with_tracing",
    "LangChainClient",
    "TracedLLMResponse",
    # LangSmith Setup
    "init_langsmith",
    "is_langsmith_enabled",
    "get_langsmith_url",
    "create_run_tree",
    "flush_traces",
    # Model Router
    "ModelRouter",
    "ModelRegistry",
    "TaskType",
    "ModelTier",
    "ModelConfig",
    "RoutingDecision",
    "get_model_for_task",
    "create_router_for_research",
    "create_router_for_extraction",
    # Prompt Caching
    "PromptCache",
    "get_prompt_cache",
    "create_cached_analysis_request",
    # Streaming
    "StreamingClient",
    "StreamingResult",
    "StreamingStats",
    "get_streaming_client",
    "StreamingProgressPrinter",
    "stream_research_analysis",
    # Cost Tracking
    "CostTracker",
    "APICall",
    "CostSummary",
    "get_cost_tracker",
    # Batch Processing
    "BatchProcessor",
    "BatchRequest",
    "BatchResult",
    "BatchStatus",
    "get_batch_processor",
    # Web Search
    "ClaudeWebSearch",
    "WebSearchResult",
    "get_claude_web_search",
    # DeepSeek (Ultra-low cost: $0.14/1M tokens, reasoning, FIM, tool use)
    "DeepSeekClient",
    "DeepSeekResponse",
    "get_deepseek_client",
    "DEEPSEEK_PRICING",
    # DeepSeek Async Client (concurrent queries)
    "AsyncDeepSeekClient",
    "get_async_deepseek_client",
    # DeepSeek Model Selection (task-based routing)
    "DeepSeekModelSelector",
    "DeepSeekTaskType",
    # DeepSeek Tool Use / Function Calling
    "DeepSeekToolDefinition",
    "create_deepseek_research_tools",
    # DeepSeek Utilities
    "reset_deepseek_clients",
    # Smart Client (Cost-optimized routing)
    "SmartLLMClient",
    "CompletionResult",
    "get_smart_client",
    "smart_completion",
    "extract_data",
    "analyze_text",
    "generate_report",
    "print_llm_stats",
    # Gemini (Search grounding + 2M context + caching + tool use)
    "GeminiClient",
    "GeminiResponse",
    "GeminiSource",
    "get_gemini_client",
    "GEMINI_PRICING",
    # Gemini Async Client (concurrent queries)
    "AsyncGeminiClient",
    "get_async_gemini_client",
    # Gemini Model Selection (task-based routing)
    "GeminiModelSelector",
    "GeminiTaskType",
    # Gemini Context Caching (75% cost savings)
    "GeminiCache",
    # Gemini Tool Use / Function Calling
    "GeminiToolDefinition",
    "create_gemini_research_tools",
    # Gemini Utilities
    "reset_gemini_clients",
    # Groq (Ultra-fast: 1,300 tok/sec, async, tool use, batch)
    "GroqClient",
    "GroqResponse",
    "get_groq_client",
    # Groq Async Client (10x faster batch operations)
    "AsyncGroqClient",
    "get_async_groq_client",
    # Groq Batch Processing (50% cost savings)
    "GroqBatchClient",
    "GroqBatchJob",
    "get_groq_batch_client",
    # Groq Model Selection (cost-optimized)
    "GroqModelSelector",
    "GroqTaskType",
    # Groq Tool Use / Function Calling
    "GroqToolDefinition",
    "create_groq_tool",
    "create_groq_research_tools",
    # Groq Utilities
    "reset_groq_clients",
    # Vision
    "VisionAnalyzer",
    "ImageAnalysisResult",
    "get_vision_analyzer",
    # Tool Use
    "StructuredExtractor",
    "ExtractionResult",
    "get_structured_extractor",
    "FINANCIAL_EXTRACTION_TOOLS",
    # Response Validation
    "ValidationError",
    "ValidatedAnthropicResponse",
    "ValidatedTavilyResponse",
    "ValidatedTavilyResult",
    "validate_anthropic_response",
    "validate_tavily_response",
    "extract_anthropic_content",
    "extract_tavily_results",
    "safe_get",
    "validate_required_fields",
    "validate_json_response",
    "enforce_response_limits",
]
