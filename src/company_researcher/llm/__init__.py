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

# Client Factory (centralized client management)
from .client_factory import (
    LLMClientFactory,
    LLMResponseError,
    get_factory,
    get_anthropic_client,
    get_tavily_client,
    create_message,
    calculate_cost,
    reset_clients,
    safe_extract_text,
    safe_extract_json,
)

# Response Parser (centralized parsing utilities)
from .response_parser import (
    ResponseParser,
    ParseResult,
    parse_json_response,
    extract_json_block,
    extract_list_from_response,
    extract_sections_from_response,
    extract_number_from_response,
)

# LangChain Client
from .langchain_client import (
    get_llm,
    get_chat_model,
    invoke_with_tracing,
    ainvoke_with_tracing,
    LangChainClient,
    TracedLLMResponse,
)

# LangSmith Setup
from .langsmith_setup import (
    init_langsmith,
    is_langsmith_enabled,
    get_langsmith_url,
    create_run_tree,
    flush_traces,
)

# Model Router
from .model_router import (
    ModelRouter,
    ModelRegistry,
    TaskType,
    ModelTier,
    ModelConfig,
    RoutingDecision,
    get_model_for_task,
    create_router_for_research,
    create_router_for_extraction,
)

# Prompt Caching (25% cost reduction)
from .prompt_cache import (
    PromptCache,
    get_prompt_cache,
    create_cached_analysis_request,
)

# Streaming (real-time responses)
from .streaming import (
    StreamingClient,
    StreamingResult,
    StreamingStats,
    get_streaming_client,
    StreamingProgressPrinter,
    stream_research_analysis,
)

# Cost Tracking (detailed metrics)
from .cost_tracker import (
    CostTracker,
    APICall,
    CostSummary,
    get_cost_tracker,
)

# Batch Processing (50% cost reduction)
from .batch_processor import (
    BatchProcessor,
    BatchRequest,
    BatchResult,
    BatchStatus,
    get_batch_processor,
)

# Web Search ($10/1K searches)
from .web_search import (
    ClaudeWebSearch,
    WebSearchResult,
    get_claude_web_search,
)

# DeepSeek (Ultra-low cost: $0.14/1M tokens, reasoning, FIM, tool use)
from .deepseek_client import (
    # Sync Client
    DeepSeekClient,
    DeepSeekResponse,
    get_deepseek_client,
    DEEPSEEK_PRICING,
    # Async Client (concurrent queries)
    AsyncDeepSeekClient,
    get_async_deepseek_client,
    # Model Selection (task-based routing)
    DeepSeekModelSelector,
    DeepSeekTaskType,
    # Tool Use / Function Calling
    ToolDefinition as DeepSeekToolDefinition,
    create_deepseek_research_tools,
    # Utilities
    reset_deepseek_clients,
)

# Smart Client (Automatic model routing for cost optimization)
from .smart_client import (
    SmartLLMClient,
    CompletionResult,
    get_smart_client,
    smart_completion,
    extract_data,
    analyze_text,
    generate_report,
    print_llm_stats,
)

# Gemini (Search grounding + 2M context + caching + tool use)
from .gemini_client import (
    # Sync Client
    GeminiClient,
    GeminiResponse,
    GeminiSource,
    get_gemini_client,
    GEMINI_PRICING,
    # Async Client (concurrent queries)
    AsyncGeminiClient,
    get_async_gemini_client,
    # Model Selection (task-based routing)
    GeminiModelSelector,
    GeminiTaskType,
    # Context Caching (75% cost savings)
    GeminiCache,
    # Tool Use / Function Calling
    ToolDefinition as GeminiToolDefinition,
    create_gemini_research_tools,
    # Utilities
    reset_gemini_clients,
)

# Groq (Ultra-fast: 1,300 tok/sec, async, tool use, batch)
from .groq_client import (
    # Sync Client
    GroqClient,
    GroqResponse,
    get_groq_client,
    # Async Client (10x faster batch)
    AsyncGroqClient,
    get_async_groq_client,
    # Batch Processing (50% cost savings)
    GroqBatchClient,
    BatchJob as GroqBatchJob,
    get_batch_client as get_groq_batch_client,
    # Model Selection
    GroqModelSelector,
    TaskType as GroqTaskType,
    # Tool Use / Function Calling
    ToolDefinition as GroqToolDefinition,
    create_tool as create_groq_tool,
    create_research_tools as create_groq_research_tools,
    # Utilities
    reset_groq_clients,
)

# Vision (image analysis)
from .vision import (
    VisionAnalyzer,
    ImageAnalysisResult,
    get_vision_analyzer,
)

# Tool Use (structured extraction)
from .tool_use import (
    StructuredExtractor,
    ExtractionResult,
    get_structured_extractor,
    FINANCIAL_EXTRACTION_TOOLS,
)

# Response Validation (safe API response handling)
from .response_validation import (
    ValidationError,
    ValidatedAnthropicResponse,
    ValidatedTavilyResponse,
    ValidatedTavilyResult,
    validate_anthropic_response,
    validate_tavily_response,
    extract_anthropic_content,
    extract_tavily_results,
    safe_get,
    validate_required_fields,
    validate_json_response,
    enforce_response_limits,
)

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
