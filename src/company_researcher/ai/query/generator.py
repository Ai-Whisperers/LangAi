"""AI-powered query generator using LLM."""
from typing import List, Optional, Dict, Any
import logging

from ..base import AIComponent
from ..config import get_ai_config
from ..fallback import FallbackHandler
from ..utils import truncate_text
from ...llm.response_parser import parse_json_response

from .models import (
    CompanyContext,
    GeneratedQuery,
    QueryGenerationResult,
    QueryRefinementResult,
    QueryPurpose
)
from .prompts import (
    QUERY_GENERATION_PROMPT,
    QUERY_REFINEMENT_PROMPT,
    MULTILINGUAL_QUERY_PROMPT
)

logger = logging.getLogger(__name__)


# Legacy templates for fallback
LEGACY_TEMPLATES = {
    QueryPurpose.OVERVIEW: [
        "{company} company overview",
        "{company} about history founded",
        "{company} headquarters employees",
    ],
    QueryPurpose.FINANCIAL: [
        "{company} revenue financial performance",
        "{company} annual report",
        "{company} funding valuation",
    ],
    QueryPurpose.PRODUCTS: [
        "{company} products services offerings",
        "{company} technology platform",
    ],
    QueryPurpose.COMPETITORS: [
        "{company} competitors competition",
        "{company} vs comparison",
        "{company} market share",
    ],
    QueryPurpose.NEWS: [
        "{company} news latest",
        "{company} announcements 2024",
    ],
}


class AIQueryGenerator(AIComponent[QueryGenerationResult]):
    """
    AI-driven query generation replacing static templates.

    Generates contextually appropriate search queries based on
    company type, region, industry, and research needs.

    Example:
        generator = get_query_generator()
        context = CompanyContext(
            company_name="Grupo Bimbo",
            known_region="LATAM",
            is_public=True
        )
        result = generator.generate_queries(context, num_queries=10)
        for query in result.queries:
            print(f"{query.priority}: {query.query} ({query.language})")
    """

    component_name = "query_generation"
    default_task_type = "search_query"
    default_complexity = "medium"

    def __init__(self):
        super().__init__()
        self._fallback_handler = FallbackHandler("query_generation")

    def generate_queries(
        self,
        context: CompanyContext,
        num_queries: int = 10,
    ) -> QueryGenerationResult:
        """
        Generate optimal search queries using LLM.

        Args:
            context: Company context with known information
            num_queries: Number of queries to generate

        Returns:
            QueryGenerationResult with generated queries
        """
        # Infer languages if not provided
        languages = context.get_inferred_languages()

        prompt = QUERY_GENERATION_PROMPT.format(
            company_name=context.company_name,
            industry=context.known_industry or "Unknown",
            region=context.known_region or "Unknown",
            country=context.known_country or "Unknown",
            is_public=context.is_public if context.is_public is not None else "Unknown",
            ticker=context.stock_ticker or "Unknown",
            exchange=context.stock_exchange or "Unknown",
            products=", ".join(context.known_products) if context.known_products else "Unknown",
            competitors=", ".join(context.known_competitors) if context.known_competitors else "Unknown",
            executives=", ".join(context.known_executives) if context.known_executives else "Unknown",
            focus=", ".join(context.research_focus) if context.research_focus else "General research",
            depth=context.research_depth,
            languages=", ".join(languages),
            previous_queries="\n".join(context.previous_queries) if context.previous_queries else "None",
            gaps="\n".join(context.gaps_identified) if context.gaps_identified else "None",
            num_queries=num_queries
        )

        try:
            result = self._call_llm(
                prompt=prompt,
                task_type="search_query",
                complexity="medium",
                json_mode=True
            )

            parsed = parse_json_response(result, default={"queries": []})
            return self._parse_generation_result(parsed, languages)

        except Exception as e:
            logger.error(f"Query generation failed: {e}")
            # Fall back to legacy templates
            return self._generate_legacy_queries(context.company_name, num_queries)

    def refine_queries(
        self,
        original_result: QueryGenerationResult,
        coverage_scores: Dict[str, float],
        gaps: List[str],
        num_queries: int = 5
    ) -> QueryRefinementResult:
        """
        Refine queries based on search results quality.

        Args:
            original_result: Original query generation result
            coverage_scores: Coverage score per category (0.0-1.0)
            gaps: Identified information gaps
            num_queries: Number of refined queries to generate

        Returns:
            QueryRefinementResult with refined queries
        """
        # Format original queries with results
        original_summary = "\n".join([
            f"- {q.query} ({q.purpose}): Priority {q.priority}"
            for q in original_result.queries
        ])

        coverage_summary = "\n".join([
            f"- {cat}: {score:.1%}"
            for cat, score in coverage_scores.items()
        ])

        gaps_summary = "\n".join([f"- {gap}" for gap in gaps])

        prompt = QUERY_REFINEMENT_PROMPT.format(
            original_queries_with_results=original_summary,
            coverage_assessment=coverage_summary,
            gaps=gaps_summary,
            num_queries=num_queries
        )

        try:
            result = self._call_llm(
                prompt=prompt,
                task_type="search_query",
                complexity="low",
                json_mode=True
            )

            parsed = parse_json_response(result, default={"refined_queries": []})
            return self._parse_refinement_result(parsed)

        except Exception as e:
            logger.error(f"Query refinement failed: {e}")
            return QueryRefinementResult(confidence_in_refinement=0.0)

    def generate_multilingual_queries(
        self,
        company_name: str,
        region: str,
        languages: List[str],
        purpose: QueryPurpose
    ) -> Dict[str, List[str]]:
        """
        Generate queries in multiple languages.

        Args:
            company_name: Company to research
            region: Company's region
            languages: Languages to generate
            purpose: Query purpose/category

        Returns:
            Dict mapping language code to query list
        """
        purpose_value = purpose.value if isinstance(purpose, QueryPurpose) else purpose

        prompt = MULTILINGUAL_QUERY_PROMPT.format(
            company_name=company_name,
            region=region,
            country="",
            languages=", ".join(languages),
            purpose=purpose_value
        )

        try:
            result = self._call_llm(
                prompt=prompt,
                task_type="search_query",
                complexity="low",
                json_mode=True
            )

            parsed = parse_json_response(result, default={})
            return parsed.get("queries_by_language", {lang: [] for lang in languages})

        except Exception as e:
            logger.error(f"Multilingual query generation failed: {e}")
            return {lang: [f"{company_name}"] for lang in languages}

    def _parse_generation_result(
        self,
        data: Dict[str, Any],
        languages: List[str]
    ) -> QueryGenerationResult:
        """Parse LLM response into QueryGenerationResult."""
        queries = []

        for q_data in data.get("queries", []):
            try:
                purpose = q_data.get("purpose", "overview")
                if isinstance(purpose, str):
                    try:
                        purpose = QueryPurpose(purpose)
                    except ValueError:
                        purpose = QueryPurpose.OVERVIEW

                query = GeneratedQuery(
                    query=q_data.get("query", ""),
                    purpose=purpose,
                    expected_sources=q_data.get("expected_sources", []),
                    language=q_data.get("language", "en"),
                    priority=int(q_data.get("priority", 3)),
                    reasoning=q_data.get("reasoning", ""),
                    is_fallback=q_data.get("is_fallback", False)
                )
                if query.query:  # Only add non-empty queries
                    queries.append(query)
            except Exception as e:
                logger.warning(f"Failed to parse query: {e}")

        return QueryGenerationResult(
            queries=queries,
            company_context_inferred=data.get("company_context_inferred", {}),
            suggested_follow_ups=data.get("suggested_follow_ups", []),
            estimated_coverage=data.get("estimated_coverage", {}),
            total_queries=len(queries),
            languages_used=list(set(q.language for q in queries))
        )

    def _parse_refinement_result(self, data: Dict[str, Any]) -> QueryRefinementResult:
        """Parse LLM response into QueryRefinementResult."""
        queries = []

        for q_data in data.get("refined_queries", []):
            try:
                purpose = q_data.get("purpose", "overview")
                if isinstance(purpose, str):
                    try:
                        purpose = QueryPurpose(purpose)
                    except ValueError:
                        purpose = QueryPurpose.OVERVIEW

                query = GeneratedQuery(
                    query=q_data.get("query", ""),
                    purpose=purpose,
                    expected_sources=q_data.get("expected_sources", []),
                    language=q_data.get("language", "en"),
                    priority=int(q_data.get("priority", 1)),
                    reasoning=q_data.get("reasoning", ""),
                    is_fallback=q_data.get("is_fallback", False)
                )
                if query.query:
                    queries.append(query)
            except Exception as e:
                logger.warning(f"Failed to parse refined query: {e}")

        dropped = data.get("dropped_purposes", [])

        return QueryRefinementResult(
            refined_queries=queries,
            gaps_addressed=data.get("gaps_addressed", []),
            dropped_purposes=dropped,
            confidence_in_refinement=float(data.get("confidence_in_refinement", 0.5))
        )

    def _generate_legacy_queries(
        self,
        company_name: str,
        num_queries: int
    ) -> QueryGenerationResult:
        """Generate queries using legacy templates (fallback)."""
        queries = []
        priority = 1

        for purpose, templates in LEGACY_TEMPLATES.items():
            for template in templates[:2]:  # Limit per category
                if len(queries) >= num_queries:
                    break
                query = GeneratedQuery(
                    query=template.format(company=company_name),
                    purpose=purpose,
                    expected_sources=["news", "official"],
                    language="en",
                    priority=priority,
                    reasoning="Legacy template fallback",
                    is_fallback=True
                )
                queries.append(query)
            priority += 1

        return QueryGenerationResult(
            queries=queries[:num_queries],
            company_context_inferred={},
            suggested_follow_ups=[],
            estimated_coverage={},
            total_queries=len(queries[:num_queries]),
            languages_used=["en"]
        )

    def process(self, context: CompanyContext) -> QueryGenerationResult:
        """Main processing method (implements AIComponent interface)."""
        return self.generate_queries(context)


# Singleton instance
_generator_instance: Optional[AIQueryGenerator] = None


def get_query_generator() -> AIQueryGenerator:
    """Get singleton query generator instance."""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = AIQueryGenerator()
    return _generator_instance
