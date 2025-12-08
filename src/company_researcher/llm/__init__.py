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
    get_factory,
    get_anthropic_client,
    get_tavily_client,
    create_message,
    calculate_cost,
    reset_clients,
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

__all__ = [
    # Client Factory (PRIMARY - use these for new code)
    "LLMClientFactory",
    "get_factory",
    "get_anthropic_client",
    "get_tavily_client",
    "create_message",
    "calculate_cost",
    "reset_clients",
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
]
