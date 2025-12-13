"""
SELECT Strategy (Phase 12.2).

RAG (Retrieval Augmented Generation) and memory retrieval:
- Semantic search over stored research
- Context-aware retrieval
- Query expansion and rewriting
- Relevance ranking and filtering

The SELECT strategy retrieves the most relevant information
from memory to augment agent context.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re
from ..utils import utc_now


# ============================================================================
# Enums and Data Models
# ============================================================================

class RetrievalMode(str, Enum):
    """Retrieval modes."""
    SEMANTIC = "semantic"      # Embedding-based similarity
    KEYWORD = "keyword"        # Keyword matching
    HYBRID = "hybrid"          # Combined semantic + keyword
    TEMPORAL = "temporal"      # Time-based (recent first)
    STRUCTURED = "structured"  # Metadata-based


class RelevanceThreshold(str, Enum):
    """Relevance score thresholds."""
    STRICT = "strict"      # Only high relevance (>0.8)
    MODERATE = "moderate"  # Moderate relevance (>0.6)
    RELAXED = "relaxed"    # Low relevance (>0.4)
    ALL = "all"           # No filtering


@dataclass
class RetrievedChunk:
    """A retrieved chunk of information."""
    content: str
    source: str
    relevance_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    chunk_type: str = "text"
    retrieved_at: datetime = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "source": self.source,
            "relevance_score": self.relevance_score,
            "metadata": self.metadata,
            "chunk_type": self.chunk_type
        }


@dataclass
class RetrievalResult:
    """Result of a retrieval operation."""
    query: str
    chunks: List[RetrievedChunk]
    total_found: int
    retrieval_mode: RetrievalMode
    processing_time_ms: float = 0.0

    @property
    def top_chunk(self) -> Optional[RetrievedChunk]:
        return self.chunks[0] if self.chunks else None

    @property
    def average_relevance(self) -> float:
        if not self.chunks:
            return 0.0
        return sum(c.relevance_score for c in self.chunks) / len(self.chunks)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "chunks": [c.to_dict() for c in self.chunks],
            "total_found": self.total_found,
            "mode": self.retrieval_mode.value,
            "average_relevance": round(self.average_relevance, 3),
            "processing_time_ms": self.processing_time_ms
        }


# ============================================================================
# Query Processing
# ============================================================================

class QueryProcessor:
    """
    Process and expand queries for better retrieval.

    Supports:
    - Query expansion with synonyms
    - Query decomposition
    - Entity extraction
    - Intent classification
    """

    # Common business/finance synonyms
    SYNONYMS = {
        "revenue": ["sales", "income", "earnings", "turnover"],
        "profit": ["earnings", "net income", "bottom line"],
        "growth": ["increase", "expansion", "rise"],
        "market": ["industry", "sector", "space"],
        "competitor": ["rival", "competition", "alternative"],
        "product": ["offering", "solution", "service"],
        "customer": ["client", "user", "buyer"],
        "price": ["cost", "pricing", "rate"],
    }

    def __init__(self):
        self._query_cache: Dict[str, List[str]] = {}

    def expand_query(self, query: str) -> List[str]:
        """
        Expand query with synonyms and related terms.

        Args:
            query: Original query

        Returns:
            List of expanded queries
        """
        if query in self._query_cache:
            return self._query_cache[query]

        expanded = [query]
        query_lower = query.lower()

        for term, synonyms in self.SYNONYMS.items():
            if term in query_lower:
                for syn in synonyms[:2]:  # Limit synonyms
                    expanded.append(query_lower.replace(term, syn))

        self._query_cache[query] = expanded
        return expanded

    def decompose_query(self, query: str) -> List[str]:
        """
        Break complex query into simpler sub-queries.

        Args:
            query: Complex query

        Returns:
            List of sub-queries
        """
        # Split on common connectors
        connectors = [" and ", " or ", ", ", " also ", " including "]
        sub_queries = [query]

        for conn in connectors:
            if conn in query.lower():
                parts = query.lower().split(conn)
                sub_queries = [p.strip() for p in parts if len(p.strip()) > 10]
                break

        return sub_queries if len(sub_queries) > 1 else [query]

    def extract_entities(self, query: str) -> Dict[str, List[str]]:
        """
        Extract entities from query.

        Args:
            query: Query text

        Returns:
            Dictionary of entity types to values
        """
        entities = {
            "companies": [],
            "metrics": [],
            "time_periods": [],
            "topics": []
        }

        # Common company indicators
        company_patterns = [
            r"(?:about|for|of)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"([A-Z][a-z]+(?:'s|'s)?)\s+(?:revenue|profit|market|growth)"
        ]

        for pattern in company_patterns:
            matches = re.findall(pattern, query)
            entities["companies"].extend(matches)

        # Metric detection
        metrics = ["revenue", "profit", "growth", "margin", "share", "size", "cost"]
        for metric in metrics:
            if metric in query.lower():
                entities["metrics"].append(metric)

        # Time period detection
        time_patterns = [
            r"(20\d{2})",
            r"(Q[1-4]\s*20\d{2})",
            r"(last\s+(?:year|quarter|month))",
            r"(this\s+(?:year|quarter))"
        ]

        for pattern in time_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            entities["time_periods"].extend(matches)

        return entities

    def classify_intent(self, query: str) -> str:
        """
        Classify the intent of the query.

        Args:
            query: Query text

        Returns:
            Intent classification
        """
        query_lower = query.lower()

        intent_patterns = {
            "financial": ["revenue", "profit", "earnings", "financial", "cash", "debt"],
            "market": ["market", "industry", "tam", "sam", "som", "size", "share"],
            "competitive": ["competitor", "competition", "rival", "vs", "versus", "alternative"],
            "product": ["product", "feature", "technology", "innovation", "offering"],
            "general": ["overview", "about", "what is", "who is", "describe"]
        }

        for intent, keywords in intent_patterns.items():
            if any(kw in query_lower for kw in keywords):
                return intent

        return "general"


# ============================================================================
# Context Selector
# ============================================================================

class ContextSelector:
    """
    Select and retrieve relevant context for agents.

    Combines multiple retrieval strategies to find the most
    relevant information for a given query or task.

    Usage:
        selector = ContextSelector(memory=dual_layer_memory)

        # Retrieve for a query
        result = selector.retrieve(
            query="Tesla revenue growth 2024",
            mode=RetrievalMode.HYBRID,
            k=5
        )

        # Get formatted context
        context = selector.format_context(result, max_tokens=2000)
    """

    def __init__(
        self,
        memory=None,
        default_mode: RetrievalMode = RetrievalMode.HYBRID,
        default_threshold: RelevanceThreshold = RelevanceThreshold.MODERATE
    ):
        """
        Initialize context selector.

        Args:
            memory: DualLayerMemory instance (optional)
            default_mode: Default retrieval mode
            default_threshold: Default relevance threshold
        """
        self._memory = memory
        self._default_mode = default_mode
        self._default_threshold = default_threshold
        self._query_processor = QueryProcessor()

        # Threshold values
        self._thresholds = {
            RelevanceThreshold.STRICT: 0.8,
            RelevanceThreshold.MODERATE: 0.6,
            RelevanceThreshold.RELAXED: 0.4,
            RelevanceThreshold.ALL: 0.0
        }

    def set_memory(self, memory) -> None:
        """Set the memory backend."""
        self._memory = memory

    def retrieve(
        self,
        query: str,
        mode: Optional[RetrievalMode] = None,
        k: int = 5,
        threshold: Optional[RelevanceThreshold] = None,
        company_filter: Optional[str] = None,
        type_filter: Optional[str] = None,
        expand_query: bool = True
    ) -> RetrievalResult:
        """
        Retrieve relevant chunks for a query.

        Args:
            query: Search query
            mode: Retrieval mode
            k: Number of results
            threshold: Relevance threshold
            company_filter: Filter by company
            type_filter: Filter by data type
            expand_query: Whether to expand query

        Returns:
            RetrievalResult with matched chunks
        """
        import time
        start_time = time.time()

        mode = mode or self._default_mode
        threshold = threshold or self._default_threshold
        min_score = self._thresholds[threshold]

        chunks = []

        if mode == RetrievalMode.SEMANTIC:
            chunks = self._semantic_retrieve(
                query, k * 2, company_filter, type_filter
            )
        elif mode == RetrievalMode.KEYWORD:
            chunks = self._keyword_retrieve(
                query, k * 2, company_filter, type_filter
            )
        elif mode == RetrievalMode.HYBRID:
            # Combine semantic and keyword
            semantic_chunks = self._semantic_retrieve(
                query, k, company_filter, type_filter
            )
            keyword_chunks = self._keyword_retrieve(
                query, k, company_filter, type_filter
            )
            chunks = self._merge_results(semantic_chunks, keyword_chunks)
        elif mode == RetrievalMode.TEMPORAL:
            chunks = self._temporal_retrieve(
                k * 2, company_filter, type_filter
            )
        elif mode == RetrievalMode.STRUCTURED:
            chunks = self._structured_retrieve(
                company_filter, type_filter, k * 2
            )

        # Expand query if enabled
        if expand_query and len(chunks) < k:
            expanded_queries = self._query_processor.expand_query(query)
            for exp_query in expanded_queries[1:]:  # Skip original
                more_chunks = self._semantic_retrieve(
                    exp_query, k - len(chunks), company_filter, type_filter
                )
                chunks.extend(more_chunks)

        # Filter by threshold
        chunks = [c for c in chunks if c.relevance_score >= min_score]

        # Deduplicate
        seen_content = set()
        unique_chunks = []
        for chunk in chunks:
            content_hash = hash(chunk.content[:100])
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_chunks.append(chunk)

        # Sort by relevance and limit
        unique_chunks.sort(key=lambda c: c.relevance_score, reverse=True)
        final_chunks = unique_chunks[:k]

        processing_time = (time.time() - start_time) * 1000

        return RetrievalResult(
            query=query,
            chunks=final_chunks,
            total_found=len(unique_chunks),
            retrieval_mode=mode,
            processing_time_ms=processing_time
        )

    def _semantic_retrieve(
        self,
        query: str,
        k: int,
        company_filter: Optional[str],
        type_filter: Optional[str]
    ) -> List[RetrievedChunk]:
        """Retrieve using semantic similarity."""
        if not self._memory:
            return []

        try:
            results = self._memory.recall_similar(
                query=query,
                k=k,
                company_name=company_filter,
                data_type=type_filter
            )

            return [
                RetrievedChunk(
                    content=r.content,
                    source=r.metadata.get("source_url", "memory"),
                    relevance_score=r.score,
                    metadata=r.metadata,
                    chunk_type=r.metadata.get("data_type", "text")
                )
                for r in results
            ]
        except Exception:
            return []

    def _keyword_retrieve(
        self,
        query: str,
        k: int,
        company_filter: Optional[str],
        type_filter: Optional[str]
    ) -> List[RetrievedChunk]:
        """Retrieve using keyword matching."""
        if not self._memory:
            return []

        # Extract keywords
        words = query.lower().split()
        keywords = [w for w in words if len(w) > 3]

        if not keywords:
            return []

        try:
            # Use memory's recall with keyword-based approach
            if company_filter:
                results = self._memory.recall_company(
                    company_name=company_filter,
                    query=query,
                    data_type=type_filter,
                    k=k
                )
            else:
                results = self._memory.recall_similar(
                    query=" ".join(keywords),
                    k=k,
                    data_type=type_filter
                )

            chunks = []
            for r in results:
                # Calculate keyword match score
                content_lower = r.content.lower()
                match_count = sum(1 for kw in keywords if kw in content_lower)
                keyword_score = match_count / len(keywords) if keywords else 0

                # Combine with semantic score
                combined_score = (r.score + keyword_score) / 2

                chunks.append(RetrievedChunk(
                    content=r.content,
                    source=r.metadata.get("source_url", "memory"),
                    relevance_score=combined_score,
                    metadata=r.metadata,
                    chunk_type=r.metadata.get("data_type", "text")
                ))

            return chunks
        except Exception:
            return []

    def _temporal_retrieve(
        self,
        k: int,
        company_filter: Optional[str],
        type_filter: Optional[str]
    ) -> List[RetrievedChunk]:
        """Retrieve most recent items."""
        if not self._memory:
            return []

        try:
            if company_filter:
                results = self._memory.recall_company(
                    company_name=company_filter,
                    data_type=type_filter,
                    k=k
                )
            else:
                # Get from hot cache (most recent)
                results = self._memory.recall_similar("", k=k)

            # Sort by created_at in metadata
            chunks = [
                RetrievedChunk(
                    content=r.content,
                    source=r.metadata.get("source_url", "memory"),
                    relevance_score=0.7,  # Default score for temporal
                    metadata=r.metadata,
                    chunk_type=r.metadata.get("data_type", "text")
                )
                for r in results
            ]

            return chunks
        except Exception:
            return []

    def _structured_retrieve(
        self,
        company_filter: Optional[str],
        type_filter: Optional[str],
        k: int
    ) -> List[RetrievedChunk]:
        """Retrieve by structured metadata filters."""
        if not self._memory or not company_filter:
            return []

        try:
            results = self._memory.recall_company(
                company_name=company_filter,
                data_type=type_filter,
                k=k
            )

            return [
                RetrievedChunk(
                    content=r.content,
                    source=r.metadata.get("source_url", "memory"),
                    relevance_score=0.8,  # High score for exact match
                    metadata=r.metadata,
                    chunk_type=r.metadata.get("data_type", "text")
                )
                for r in results
            ]
        except Exception:
            return []

    def _merge_results(
        self,
        list1: List[RetrievedChunk],
        list2: List[RetrievedChunk]
    ) -> List[RetrievedChunk]:
        """Merge and deduplicate two result lists."""
        merged = {}

        for chunk in list1 + list2:
            key = hash(chunk.content[:100])
            if key not in merged:
                merged[key] = chunk
            else:
                # Keep higher score
                if chunk.relevance_score > merged[key].relevance_score:
                    merged[key] = chunk

        return list(merged.values())

    # ==========================================================================
    # Context Formatting
    # ==========================================================================

    def format_context(
        self,
        result: RetrievalResult,
        max_chars: int = 8000,
        include_metadata: bool = False,
        template: Optional[str] = None
    ) -> str:
        """
        Format retrieval results for LLM context.

        Args:
            result: RetrievalResult to format
            max_chars: Maximum characters
            include_metadata: Include source metadata
            template: Custom format template

        Returns:
            Formatted context string
        """
        if not result.chunks:
            return ""

        if template:
            return self._format_with_template(result, template, max_chars)

        lines = [f"## Retrieved Context for: {result.query}\n"]
        current_chars = len(lines[0])

        for i, chunk in enumerate(result.chunks, 1):
            header = f"\n### Source {i}"
            if include_metadata and chunk.source:
                header += f" ({chunk.source})"
            header += f" [Relevance: {chunk.relevance_score:.2f}]\n"

            content = chunk.content

            # Check length
            if current_chars + len(header) + len(content) > max_chars:
                # Truncate content
                remaining = max_chars - current_chars - len(header) - 50
                if remaining > 100:
                    content = content[:remaining] + "... (truncated)"
                else:
                    break

            lines.append(header)
            lines.append(content + "\n")
            current_chars += len(header) + len(content) + 1

        return "".join(lines)

    def _format_with_template(
        self,
        result: RetrievalResult,
        template: str,
        max_chars: int
    ) -> str:
        """Format using custom template."""
        chunks_text = ""
        for i, chunk in enumerate(result.chunks, 1):
            chunk_text = template.format(
                index=i,
                content=chunk.content[:1000],
                source=chunk.source,
                score=chunk.relevance_score,
                type=chunk.chunk_type
            )
            if len(chunks_text) + len(chunk_text) > max_chars:
                break
            chunks_text += chunk_text

        return chunks_text

    def select_for_task(
        self,
        task_type: str,
        company_name: str,
        additional_query: Optional[str] = None,
        k: int = 5
    ) -> RetrievalResult:
        """
        Select context optimized for a specific task type.

        Args:
            task_type: Type of task (financial, market, competitive, etc.)
            company_name: Company name
            additional_query: Additional search terms
            k: Number of results

        Returns:
            RetrievalResult optimized for task
        """
        # Build query based on task type
        task_queries = {
            "financial": f"{company_name} revenue profit financial performance earnings",
            "market": f"{company_name} market size TAM SAM SOM industry trends",
            "competitive": f"{company_name} competitors competition market share rivals",
            "product": f"{company_name} products technology features innovation",
            "overview": f"{company_name} company overview description business model"
        }

        base_query = task_queries.get(task_type, f"{company_name} {task_type}")
        if additional_query:
            base_query += f" {additional_query}"

        return self.retrieve(
            query=base_query,
            mode=RetrievalMode.HYBRID,
            k=k,
            company_filter=company_name,
            type_filter=task_type if task_type in ["financial", "market", "competitive", "product"] else None
        )


# ============================================================================
# Factory Functions
# ============================================================================

def create_selector(memory=None) -> ContextSelector:
    """Create a context selector."""
    return ContextSelector(memory=memory)


def retrieve_for_agent(
    memory,
    agent_type: str,
    company_name: str,
    k: int = 5
) -> str:
    """
    Retrieve and format context for a specific agent.

    Args:
        memory: DualLayerMemory instance
        agent_type: Type of agent (financial, market, etc.)
        company_name: Company being researched
        k: Number of results

    Returns:
        Formatted context string
    """
    selector = ContextSelector(memory=memory)
    result = selector.select_for_task(
        task_type=agent_type,
        company_name=company_name,
        k=k
    )
    return selector.format_context(result, max_chars=4000, include_metadata=True)
