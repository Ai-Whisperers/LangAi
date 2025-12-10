"""Integration layer for AI components in workflow."""
from typing import Dict, Any, Optional, List, TYPE_CHECKING
import logging

from .config import get_ai_config, AIConfig
from .utils import CostTracker

if TYPE_CHECKING:
    from ..state import OverallState

logger = logging.getLogger(__name__)


class AIIntegrationLayer:
    """
    Central integration layer for all AI components.

    Provides a unified interface for the research workflow to use
    AI-powered features with automatic fallback handling.

    Example:
        integration = get_ai_integration()

        # Generate queries
        queries = await integration.generate_search_queries(
            company_name="Tesla",
            context={"industry": "Automotive"}
        )

        # Analyze sentiment
        sentiment = await integration.analyze_news_sentiment(
            articles=news_articles,
            company_name="Tesla"
        )

        # Assess quality
        quality = await integration.assess_research_quality(state)
    """

    def __init__(self):
        self.config = get_ai_config()
        self.cost_tracker = CostTracker(
            warn_threshold=self.config.warn_at_cost,
            max_threshold=self.config.max_cost_per_research
        )
        self._sentiment = None
        self._query_gen = None
        self._quality = None
        self._extraction = None
        self._last_query_cost = 0.0
        self._last_sentiment_cost = 0.0
        self._last_quality_cost = 0.0
        self._last_extraction_cost = 0.0

    @property
    def sentiment_analyzer(self):
        """Lazy load sentiment analyzer."""
        if self._sentiment is None and self.config.sentiment.enabled:
            from company_researcher.ai.sentiment import get_sentiment_analyzer
            self._sentiment = get_sentiment_analyzer()
        return self._sentiment

    @property
    def query_generator(self):
        """Lazy load query generator."""
        if self._query_gen is None and self.config.query_generation.enabled:
            from company_researcher.ai.query import get_query_generator
            self._query_gen = get_query_generator()
        return self._query_gen

    @property
    def quality_assessor(self):
        """Lazy load quality assessor."""
        if self._quality is None and self.config.quality_assessment.enabled:
            from company_researcher.ai.quality import get_quality_assessor
            self._quality = get_quality_assessor()
        return self._quality

    @property
    def data_extractor(self):
        """Lazy load data extractor."""
        if self._extraction is None and self.config.data_extraction.enabled:
            from company_researcher.ai.extraction import get_data_extractor
            self._extraction = get_data_extractor()
        return self._extraction

    async def generate_search_queries(
        self,
        company_name: str,
        context: Optional[Dict] = None,
        num_queries: int = 10
    ) -> List[str]:
        """
        Generate AI-enhanced search queries.

        Args:
            company_name: Company to research
            context: Optional context dict with industry, region, etc.
            num_queries: Number of queries to generate

        Returns:
            List of query strings
        """
        if not self.query_generator:
            logger.debug("Query generator disabled, using legacy")
            return self._legacy_queries(company_name, num_queries)

        try:
            from company_researcher.ai.query import CompanyContext

            ctx = CompanyContext(
                company_name=company_name,
                known_industry=context.get("industry") if context else None,
                known_region=context.get("region") if context else None,
                is_public=context.get("is_public") if context else None,
                stock_ticker=context.get("ticker") if context else None,
                languages=context.get("languages", ["en"]) if context else ["en"]
            )

            result = await self.query_generator.generate_queries(ctx, num_queries)

            # Track cost
            stats = self.query_generator.get_stats()
            new_cost = stats.get("total_cost", 0) - self._last_query_cost
            if new_cost > 0:
                self.cost_tracker.add_cost(new_cost, "query_generation")
            self._last_query_cost = stats.get("total_cost", 0)

            return result.to_query_list()

        except Exception as e:
            logger.error(f"AI query generation failed: {e}")
            if self.config.query_generation.fallback_to_legacy:
                return self._legacy_queries(company_name, num_queries)
            raise

    async def analyze_news_sentiment(
        self,
        articles: List[Dict[str, Any]],
        company_name: str
    ) -> Dict[str, Any]:
        """
        Analyze sentiment of news articles.

        Args:
            articles: List of article dicts with 'content' or 'snippet' keys
            company_name: Target company

        Returns:
            Aggregated sentiment results
        """
        if not self.sentiment_analyzer:
            logger.debug("Sentiment analyzer disabled")
            return {"overall": "neutral", "confidence": 0.0, "source": "disabled"}

        try:
            results = await self.sentiment_analyzer.analyze_batch(articles, company_name)
            aggregation = self.sentiment_analyzer.aggregate_sentiment(results)

            # Track cost
            stats = self.sentiment_analyzer.get_stats()
            new_cost = stats.get("total_cost", 0) - self._last_sentiment_cost
            if new_cost > 0:
                self.cost_tracker.add_cost(new_cost, "sentiment")
            self._last_sentiment_cost = stats.get("total_cost", 0)

            return {
                "overall": aggregation.overall_sentiment.value,
                "score": aggregation.overall_score,
                "confidence": aggregation.confidence,
                "article_count": aggregation.article_count,
                "positive_ratio": aggregation.positive_ratio,
                "negative_ratio": aggregation.negative_ratio,
                "top_positive_factors": aggregation.top_positive_factors,
                "top_negative_factors": aggregation.top_negative_factors,
                "source": "ai"
            }

        except Exception as e:
            logger.error(f"AI sentiment analysis failed: {e}")
            return {"overall": "neutral", "confidence": 0.0, "source": "error", "error": str(e)}

    async def assess_research_quality(
        self,
        state: "OverallState"
    ) -> Dict[str, Any]:
        """
        Assess quality of research results.

        Args:
            state: Current workflow state dict

        Returns:
            Quality assessment results
        """
        if not self.quality_assessor:
            logger.debug("Quality assessor disabled")
            return self._legacy_quality_check(state)

        try:
            # Build sections dict from state
            sections = {}
            if state.get("company_overview"):
                sections["company_overview"] = state["company_overview"]
            if state.get("key_metrics"):
                sections["key_metrics"] = str(state["key_metrics"])
            if state.get("products_services"):
                sections["products_services"] = str(state["products_services"])
            if state.get("competitors"):
                sections["competitors"] = str(state["competitors"])
            if state.get("key_insights"):
                sections["key_insights"] = str(state["key_insights"])

            # Get sources
            sources = state.get("sources", [])

            # Run assessment
            report = await self.quality_assessor.process(
                company_name=state.get("company_name", "Unknown"),
                sections=sections,
                sources=sources
            )

            # Track cost
            stats = self.quality_assessor.get_stats()
            new_cost = stats.get("total_cost", 0) - self._last_quality_cost
            if new_cost > 0:
                self.cost_tracker.add_cost(new_cost, "quality")
            self._last_quality_cost = stats.get("total_cost", 0)

            return {
                "score": report.overall_score,
                "level": report.overall_level.value,
                "ready": report.ready_for_delivery,
                "iteration_needed": report.iteration_needed,
                "gaps": report.key_gaps,
                "issues": report.critical_issues,
                "recommendations": report.recommendations,
                "focus_areas": report.focus_areas_for_iteration,
                "section_scores": report.section_scores,
                "source": "ai"
            }

        except Exception as e:
            logger.error(f"AI quality assessment failed: {e}")
            if self.config.quality_assessment.fallback_to_legacy:
                return self._legacy_quality_check(state)
            raise

    async def extract_structured_data(
        self,
        company_name: str,
        search_results: List[Dict]
    ) -> Dict[str, Any]:
        """
        Extract structured data from search results.

        Args:
            company_name: Target company
            search_results: Search results with content

        Returns:
            Extracted data dict
        """
        if not self.data_extractor:
            logger.debug("Data extractor disabled")
            return {"source": "disabled"}

        try:
            result = await self.data_extractor.extract_all(company_name, search_results)

            # Track cost
            stats = self.data_extractor.get_stats()
            new_cost = stats.get("total_cost", 0) - self._last_extraction_cost
            if new_cost > 0:
                self.cost_tracker.add_cost(new_cost, "extraction")
            self._last_extraction_cost = stats.get("total_cost", 0)

            return {
                "classification": {
                    "company_type": result.company_classification.company_type.value,
                    "industry": result.company_classification.industry,
                    "country": result.company_classification.country,
                    "country_code": result.company_classification.country_code,
                    "region": result.company_classification.region,
                    "is_public": result.company_classification.is_listed,
                    "stock_ticker": result.company_classification.stock_ticker,
                },
                "financial": {
                    "revenue": result.financial_data.revenue if result.financial_data else None,
                    "profit": result.financial_data.profit if result.financial_data else None,
                    "market_cap": result.financial_data.market_cap if result.financial_data else None,
                    "employee_count": result.financial_data.employee_count if result.financial_data else None,
                },
                "coverage": result.data_coverage,
                "confidence": result.extraction_confidence,
                "facts_count": result.facts_extracted,
                "has_contradictions": result.has_critical_contradictions,
                "source": "ai"
            }

        except Exception as e:
            logger.error(f"AI data extraction failed: {e}")
            return {"source": "error", "error": str(e)}

    async def classify_company(
        self,
        company_name: str,
        context: str
    ) -> Dict[str, Any]:
        """
        Classify company type and details.

        Args:
            company_name: Company name
            context: Available context text

        Returns:
            Classification dict
        """
        if not self.data_extractor:
            return self._legacy_classify(company_name)

        try:
            classification = await self.data_extractor.classify_company(
                company_name, context
            )

            return {
                "company_type": classification.company_type.value,
                "industry": classification.industry,
                "country": classification.country,
                "country_code": classification.country_code,
                "region": classification.region,
                "is_public": classification.is_listed,
                "stock_ticker": classification.stock_ticker,
                "is_conglomerate": classification.is_conglomerate,
                "confidence": classification.confidence,
                "source": "ai"
            }

        except Exception as e:
            logger.error(f"AI classification failed: {e}")
            if self.config.classification.fallback_to_legacy:
                return self._legacy_classify(company_name)
            raise

    def get_cost_summary(self) -> Dict[str, Any]:
        """Get cost summary for current research."""
        return {
            "total_cost": self.cost_tracker.total_cost,
            "breakdown": self.cost_tracker.get_breakdown(),
            "warn_threshold": self.cost_tracker.warn_threshold,
            "max_threshold": self.cost_tracker.max_threshold
        }

    def reset_cost_tracking(self):
        """Reset cost tracking for new research."""
        self.cost_tracker.reset()
        self._last_query_cost = 0.0
        self._last_sentiment_cost = 0.0
        self._last_quality_cost = 0.0
        self._last_extraction_cost = 0.0

    def get_all_stats(self) -> Dict[str, Any]:
        """Get stats from all AI components."""
        stats = {}
        if self._sentiment:
            stats["sentiment"] = self._sentiment.get_stats()
        if self._query_gen:
            stats["query_generation"] = self._query_gen.get_stats()
        if self._quality:
            stats["quality"] = self._quality.get_stats()
        if self._extraction:
            stats["extraction"] = self._extraction.get_stats()
        stats["cost"] = self.get_cost_summary()
        return stats

    def is_ai_available(self) -> bool:
        """Check if any AI component is available."""
        return (
            self.config.global_enabled and
            any([
                self.config.sentiment.enabled,
                self.config.query_generation.enabled,
                self.config.quality_assessment.enabled,
                self.config.data_extraction.enabled,
            ])
        )

    # Legacy fallbacks

    def _legacy_queries(self, company_name: str, num: int) -> List[str]:
        """Generate queries using legacy templates."""
        templates = [
            "{company} company overview",
            "{company} revenue financial results",
            "{company} products services offerings",
            "{company} competitors market share",
            "{company} news latest developments",
            "{company} leadership management team",
            "{company} history founded",
            "{company} headquarters location",
            "{company} employees workforce",
            "{company} industry analysis",
        ]
        return [t.format(company=company_name) for t in templates[:num]]

    def _legacy_quality_check(self, state: Dict) -> Dict[str, Any]:
        """Legacy quality check based on content presence."""
        score = 50.0
        gaps = []

        if state.get("company_overview"):
            score += 10
        else:
            gaps.append("Missing company overview")

        if state.get("key_metrics"):
            score += 15
        else:
            gaps.append("Missing key metrics")

        if state.get("products_services"):
            score += 10
        else:
            gaps.append("Missing products/services info")

        if state.get("competitors"):
            score += 10
        else:
            gaps.append("Missing competitor analysis")

        sources = state.get("sources", [])
        if len(sources) >= 5:
            score += 5
        else:
            gaps.append(f"Only {len(sources)} sources (need 5+)")

        level = "good" if score >= 75 else "acceptable" if score >= 60 else "needs_improvement"

        return {
            "score": score,
            "level": level,
            "ready": score >= 75,
            "iteration_needed": score < 75,
            "gaps": gaps,
            "issues": [],
            "recommendations": [],
            "focus_areas": gaps[:3],
            "section_scores": {},
            "source": "legacy"
        }

    def _legacy_classify(self, company_name: str) -> Dict[str, Any]:
        """Legacy company classification."""
        return {
            "company_type": "unknown",
            "industry": "Unknown",
            "country": "Unknown",
            "country_code": "XX",
            "region": "Unknown",
            "is_public": None,
            "stock_ticker": None,
            "is_conglomerate": False,
            "confidence": 0.0,
            "source": "legacy"
        }


# Global integration layer singleton
_integration_layer: Optional[AIIntegrationLayer] = None


def get_ai_integration() -> AIIntegrationLayer:
    """Get AI integration layer singleton."""
    global _integration_layer
    if _integration_layer is None:
        _integration_layer = AIIntegrationLayer()
    return _integration_layer


def reset_ai_integration():
    """Reset integration layer (for testing)."""
    global _integration_layer
    _integration_layer = None
