"""
LangChain LLM Module for Company Researcher.

This module provides LangChain-wrapped LLM clients that enable:
- Full LangSmith tracing for all LLM calls
- Automatic cost tracking
- Session replay and debugging
- Performance monitoring

Usage:
    from company_researcher.llm import get_llm, invoke_with_tracing

    # Get a traced LLM instance
    llm = get_llm()

    # Invoke with automatic tracing
    response = invoke_with_tracing(
        llm=llm,
        prompt="Analyze this company...",
        run_name="financial_analysis"
    )
"""

from .langchain_client import (
    get_llm,
    get_chat_model,
    invoke_with_tracing,
    ainvoke_with_tracing,
    LangChainClient,
    TracedLLMResponse,
)

from .langsmith_setup import (
    init_langsmith,
    is_langsmith_enabled,
    get_langsmith_url,
    create_run_tree,
    flush_traces,
)

__all__ = [
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
]
