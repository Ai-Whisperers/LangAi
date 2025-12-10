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

# DeepSeek (Ultra-low cost: $0.14/1M tokens)
from .deepseek_client import (
    DeepSeekClient,
    DeepSeekResponse,
    get_deepseek_client,
    DEEPSEEK_PRICING,
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

# Gemini (Search grounding + 2M context)
from .gemini_client import (
    GeminiClient,
    GeminiResponse,
    GeminiSource,
    get_gemini_client,
    GEMINI_PRICING,
)

# Groq (Ultra-fast: 1,300 tok/sec)
from .groq_client import (
    GroqClient,
    GroqResponse,
    get_groq_client,
    GROQ_PRICING,
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
    # DeepSeek
    "DeepSeekClient",
    "DeepSeekResponse",
    "get_deepseek_client",
    "DEEPSEEK_PRICING",
    # Smart Client (Cost-optimized routing)
    "SmartLLMClient",
    "CompletionResult",
    "get_smart_client",
    "smart_completion",
    "extract_data",
    "analyze_text",
    "generate_report",
    "print_llm_stats",
    # Gemini
    "GeminiClient",
    "GeminiResponse",
    "GeminiSource",
    "get_gemini_client",
    "GEMINI_PRICING",
    # Groq
    "GroqClient",
    "GroqResponse",
    "get_groq_client",
    "GROQ_PRICING",
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
