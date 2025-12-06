"""
Context Engineering Module (Phase 12).

Four strategies for managing agent context:
- WRITE: Scratchpad and working memory
- SELECT: RAG and memory retrieval
- COMPRESS: Summarization and distillation
- ISOLATE: Multi-agent context separation

Usage:
    from src.company_researcher.context import (
        Scratchpad, ContextSelector, TextCompressor,
        ContextIsolationManager, AgentContextBuilder
    )

    # WRITE: Create scratchpad
    scratchpad = Scratchpad(company_name="Tesla")
    scratchpad.write_finding("Revenue grew 8%", "financial_agent")

    # SELECT: Retrieve context
    selector = ContextSelector(memory=dual_layer_memory)
    result = selector.retrieve("Tesla revenue", k=5)

    # COMPRESS: Compress content
    compressor = TextCompressor()
    result = compressor.compress(long_text, level=CompressionLevel.MODERATE)

    # ISOLATE: Manage agent contexts
    manager = ContextIsolationManager()
    ctx = manager.create_context("financial_agent", "financial")
"""

# WRITE Strategy
from .write_strategy import (
    Scratchpad,
    ScratchpadNote,
    WorkingMemory,
    NoteType,
    NotePriority,
    create_scratchpad,
    scratchpad_from_state,
)

# SELECT Strategy
from .select_strategy import (
    ContextSelector,
    QueryProcessor,
    RetrievalResult,
    RetrievedChunk,
    RetrievalMode,
    RelevanceThreshold,
    create_selector,
    retrieve_for_agent,
)

# COMPRESS Strategy
from .compress_strategy import (
    TextCompressor,
    KeyPointExtractor,
    ProgressiveSummarizer,
    ContextWindowOptimizer,
    CompressionResult,
    CompressionLevel,
    ContentType,
    KeyPoint,
    compress_text,
    extract_key_points,
    optimize_for_context,
)

# ISOLATE Strategy
from .isolate_strategy import (
    ContextIsolationManager,
    ContextFilter,
    AgentContextBuilder,
    AgentContext,
    ContextItem,
    IsolationLevel,
    SharePolicy,
    ContextVisibility,
    create_isolation_manager,
    build_agent_context,
)

__all__ = [
    # WRITE
    "Scratchpad",
    "ScratchpadNote",
    "WorkingMemory",
    "NoteType",
    "NotePriority",
    "create_scratchpad",
    "scratchpad_from_state",
    # SELECT
    "ContextSelector",
    "QueryProcessor",
    "RetrievalResult",
    "RetrievedChunk",
    "RetrievalMode",
    "RelevanceThreshold",
    "create_selector",
    "retrieve_for_agent",
    # COMPRESS
    "TextCompressor",
    "KeyPointExtractor",
    "ProgressiveSummarizer",
    "ContextWindowOptimizer",
    "CompressionResult",
    "CompressionLevel",
    "ContentType",
    "KeyPoint",
    "compress_text",
    "extract_key_points",
    "optimize_for_context",
    # ISOLATE
    "ContextIsolationManager",
    "ContextFilter",
    "AgentContextBuilder",
    "AgentContext",
    "ContextItem",
    "IsolationLevel",
    "SharePolicy",
    "ContextVisibility",
    "create_isolation_manager",
    "build_agent_context",
]
