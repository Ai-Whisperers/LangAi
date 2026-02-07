"""
Semantic Source Selector Module.

Implements RAG (Retrieval Augmented Generation) for intelligent source selection.
Instead of sending all sources to the LLM, selects the most relevant and diverse ones.

Key features:
1. Embedding-based relevance scoring
2. Diversity-aware selection
3. Authority-weighted ranking
4. Query-specific filtering
"""

from dataclasses import dataclass
from typing import Any, Dict, List

from ..utils import get_logger

logger = get_logger(__name__)


@dataclass
class RankedSource:
    """A source with relevance and diversity scores."""

    source: Dict[str, Any]
    relevance_score: float
    authority_score: float
    diversity_score: float
    combined_score: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = dict(self.source)
        result.update(
            {
                "relevance_score": round(self.relevance_score, 3),
                "authority_score": round(self.authority_score, 3),
                "diversity_score": round(self.diversity_score, 3),
                "combined_score": round(self.combined_score, 3),
            }
        )
        return result


class SemanticSourceSelector:
    """
    Select most relevant and diverse sources for LLM context.

    Instead of sending first N sources, selects sources that:
    1. Are most relevant to the specific task/query
    2. Provide diverse information (not redundant)
    3. Come from authoritative sources
    4. Cover different aspects of the topic

    Usage:
        selector = SemanticSourceSelector()
        selected = selector.select_sources(
            query="financial analysis",
            sources=all_sources,
            max_sources=5
        )
    """

    # Authority tiers for scoring
    AUTHORITY_SCORES = {
        "sec.gov": 1.0,
        "investor.": 0.95,
        "ir.": 0.95,
        "bloomberg.com": 0.90,
        "reuters.com": 0.90,
        "wsj.com": 0.85,
        "ft.com": 0.85,
        "yahoo.com/finance": 0.80,
        "cnbc.com": 0.75,
        "forbes.com": 0.70,
        "techcrunch.com": 0.70,
        "businessinsider.com": 0.65,
        ".edu": 0.75,
        ".gov": 0.80,
    }

    def __init__(self):
        """Initialize selector with optional embedding model."""
        self._encoder = None
        self._use_embeddings = False

        try:
            from sentence_transformers import SentenceTransformer

            self._encoder = SentenceTransformer("all-MiniLM-L6-v2")
            self._use_embeddings = True
            logger.info("SemanticSourceSelector initialized with embedding model")
        except ImportError:
            logger.warning(
                "sentence-transformers not installed. "
                "Using keyword-based selection. Install with: pip install sentence-transformers"
            )

    def select_sources(
        self,
        query: str,
        sources: List[Dict],
        max_sources: int = 5,
        diversity_threshold: float = 0.7,
        authority_weight: float = 0.3,
        relevance_weight: float = 0.5,
        diversity_weight: float = 0.2,
    ) -> List[Dict]:
        """
        Select most relevant and diverse sources.

        Args:
            query: The analysis task/question
            sources: List of source dictionaries
            max_sources: Maximum sources to return
            diversity_threshold: Minimum dissimilarity between selected sources
            authority_weight: Weight for source authority (0-1)
            relevance_weight: Weight for query relevance (0-1)
            diversity_weight: Weight for diversity (0-1)

        Returns:
            List of selected source dictionaries
        """
        if not sources:
            return []

        if len(sources) <= max_sources:
            return sources

        # Score all sources
        ranked_sources = self._rank_sources(query, sources)

        # Greedy selection with diversity constraint
        selected = self._select_diverse(ranked_sources, max_sources, diversity_threshold)

        # Recompute combined scores
        for rs in selected:
            rs.combined_score = (
                rs.relevance_score * relevance_weight
                + rs.authority_score * authority_weight
                + rs.diversity_score * diversity_weight
            )

        # Sort by combined score
        selected.sort(key=lambda x: x.combined_score, reverse=True)

        return [rs.to_dict() for rs in selected]

    def select_for_task(self, task: str, sources: List[Dict], max_sources: int = 5) -> List[Dict]:
        """
        Select sources optimized for a specific task type.

        Args:
            task: Task type (financial, market, product, company)
            sources: All available sources
            max_sources: Maximum to select

        Returns:
            Selected sources optimized for the task
        """
        # Task-specific query expansion
        task_queries = {
            "financial": "revenue profit margin earnings financial performance",
            "market": "market share competitive position industry trends",
            "product": "products services offerings technology features",
            "company": "company overview history headquarters leadership",
            "competitive": "competitors comparison competitive advantage",
        }

        query = task_queries.get(task, task)

        # Task-specific authority preferences
        task_domains = {
            "financial": ["sec.gov", "yahoo.com", "bloomberg.com"],
            "market": ["statista.com", "ibisworld.com", "gartner.com"],
            "company": ["linkedin.com", "crunchbase.com"],
        }

        # Boost sources from preferred domains
        preferred = task_domains.get(task, [])
        boosted_sources = []

        for source in sources:
            url = source.get("url", "").lower()
            boost = any(d in url for d in preferred)
            source_copy = dict(source)
            source_copy["_task_boost"] = 1.2 if boost else 1.0
            boosted_sources.append(source_copy)

        return self.select_sources(query, boosted_sources, max_sources)

    def _rank_sources(self, query: str, sources: List[Dict]) -> List[RankedSource]:
        """Rank sources by relevance and authority."""
        ranked = []

        # Get query embedding if available
        query_embedding = None
        if self._use_embeddings:
            try:
                query_embedding = self._encoder.encode([query])[0]
            except Exception as e:
                logger.warning(f"Failed to encode query: {e}")

        for source in sources:
            # Calculate relevance
            if query_embedding is not None:
                relevance = self._calculate_semantic_relevance(query_embedding, source)
            else:
                relevance = self._calculate_keyword_relevance(query, source)

            # Apply task boost if present
            boost = source.get("_task_boost", 1.0)
            relevance *= boost

            # Calculate authority
            authority = self._calculate_authority(source)

            ranked.append(
                RankedSource(
                    source=source,
                    relevance_score=relevance,
                    authority_score=authority,
                    diversity_score=1.0,  # Will be updated during selection
                    combined_score=0.0,
                )
            )

        return ranked

    def _calculate_semantic_relevance(self, query_embedding, source: Dict) -> float:
        """Calculate semantic relevance using embeddings."""
        content = source.get("content", "") or source.get("snippet", "") or source.get("body", "")
        title = source.get("title", "")

        text = f"{title} {content}"[:1000]  # Limit length

        if not text.strip():
            return 0.3

        try:
            import numpy as np

            source_embedding = self._encoder.encode([text])[0]

            similarity = np.dot(query_embedding, source_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(source_embedding)
            )

            # Convert similarity (-1 to 1) to score (0 to 1)
            return max(0, (similarity + 1) / 2)

        except Exception as e:
            logger.debug(f"Embedding calculation failed: {e}")
            return 0.5

    def _calculate_keyword_relevance(self, query: str, source: Dict) -> float:
        """Calculate relevance using keyword matching."""
        content = source.get("content", "") or source.get("snippet", "") or source.get("body", "")
        title = source.get("title", "")

        text = f"{title} {content}".lower()
        query_terms = set(query.lower().split())

        # Remove stopwords
        stopwords = {
            "the",
            "a",
            "an",
            "is",
            "are",
            "was",
            "were",
            "to",
            "of",
            "and",
            "in",
            "for",
            "on",
            "with",
            "at",
            "by",
            "this",
            "that",
        }
        query_terms -= stopwords

        if not query_terms:
            return 0.5

        # Count matches
        matches = sum(1 for term in query_terms if term in text)
        return matches / len(query_terms)

    def _calculate_authority(self, source: Dict) -> float:
        """Calculate source authority based on domain."""
        url = source.get("url", "").lower()

        for domain, score in self.AUTHORITY_SCORES.items():
            if domain in url:
                return score

        return 0.5  # Default for unknown domains

    def _select_diverse(
        self, ranked_sources: List[RankedSource], max_sources: int, diversity_threshold: float
    ) -> List[RankedSource]:
        """
        Select diverse sources using greedy algorithm.

        At each step, select the source with highest combined score
        that is sufficiently different from already selected sources.
        """
        if not ranked_sources:
            return []

        # Sort by relevance + authority first
        sorted_sources = sorted(
            ranked_sources,
            key=lambda x: x.relevance_score * 0.7 + x.authority_score * 0.3,
            reverse=True,
        )

        selected: List[RankedSource] = []
        selected_embeddings = []

        for rs in sorted_sources:
            if len(selected) >= max_sources:
                break

            # Check diversity against already selected
            if selected and self._use_embeddings:
                is_diverse = self._check_diversity(
                    rs.source, selected_embeddings, diversity_threshold
                )

                if not is_diverse:
                    continue

                # Update diversity score
                rs.diversity_score = self._calculate_diversity_score(rs.source, selected_embeddings)

            selected.append(rs)

            # Add embedding for diversity check
            if self._use_embeddings:
                content = rs.source.get("content", "") or rs.source.get("snippet", "")
                if content:
                    try:
                        emb = self._encoder.encode([content[:1000]])[0]
                        selected_embeddings.append(emb)
                    except:
                        pass

        return selected

    def _check_diversity(self, source: Dict, selected_embeddings: List, threshold: float) -> bool:
        """Check if source is sufficiently different from selected."""
        content = source.get("content", "") or source.get("snippet", "")

        if not content or not selected_embeddings:
            return True

        try:
            import numpy as np

            emb = self._encoder.encode([content[:1000]])[0]

            for sel_emb in selected_embeddings:
                similarity = np.dot(emb, sel_emb) / (np.linalg.norm(emb) * np.linalg.norm(sel_emb))

                if similarity > threshold:
                    return False

            return True

        except:
            return True

    def _calculate_diversity_score(self, source: Dict, selected_embeddings: List) -> float:
        """Calculate how different this source is from selected ones."""
        if not selected_embeddings:
            return 1.0

        content = source.get("content", "") or source.get("snippet", "")
        if not content:
            return 0.5

        try:
            import numpy as np

            emb = self._encoder.encode([content[:1000]])[0]

            # Average dissimilarity
            dissimilarities = []
            for sel_emb in selected_embeddings:
                sim = np.dot(emb, sel_emb) / (np.linalg.norm(emb) * np.linalg.norm(sel_emb))
                dissimilarities.append(1 - sim)

            return sum(dissimilarities) / len(dissimilarities)

        except:
            return 0.5

    def get_coverage_analysis(
        self, selected_sources: List[Dict], all_sources: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze coverage of selected sources."""
        # Domain coverage
        selected_domains = set()
        for s in selected_sources:
            url = s.get("url", "")
            domain = self._extract_domain(url)
            selected_domains.add(domain)

        all_domains = set()
        for s in all_sources:
            url = s.get("url", "")
            domain = self._extract_domain(url)
            all_domains.add(domain)

        # Authority coverage
        authority_tiers = {"tier_1": 0, "tier_2": 0, "tier_3": 0}
        for s in selected_sources:
            url = s.get("url", "").lower()
            if any(d in url for d in ["sec.gov", "investor.", "ir."]):
                authority_tiers["tier_1"] += 1
            elif any(d in url for d in ["bloomberg", "reuters", "wsj", "ft.com"]):
                authority_tiers["tier_2"] += 1
            else:
                authority_tiers["tier_3"] += 1

        return {
            "selected_count": len(selected_sources),
            "total_available": len(all_sources),
            "selection_ratio": len(selected_sources) / len(all_sources) if all_sources else 0,
            "domain_coverage": len(selected_domains) / len(all_domains) if all_domains else 0,
            "selected_domains": list(selected_domains),
            "authority_distribution": authority_tiers,
        }

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse

            parsed = urlparse(url)
            return parsed.netloc or url
        except:
            return url
