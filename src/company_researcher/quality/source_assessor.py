"""
Source quality assessment system (Phase 5).

Automatically assesses source quality based on domain reputation,
provides quality scores, and assigns confidence levels.

Enhanced with AI-based relevance filtering to detect irrelevant sources
based on the research target (e.g., filtering out "Paraguay history" when
researching "Personal Paraguay telecom").
"""

import json
import re
from typing import Any, Dict, List, Optional, Tuple

from .models import ConfidenceLevel, ResearchFact, Source, SourceQuality

# ============================================================================
# AI Source Relevance Filter
# ============================================================================


class AISourceRelevanceFilter:
    """
    AI-powered filter to assess if sources are relevant to the research target.

    This addresses the issue where generic searches return irrelevant content
    (e.g., "Personal Paraguay" returning "History of Paraguay" articles).
    """

    # Keywords that indicate irrelevant content for common research types
    IRRELEVANCE_PATTERNS = {
        "telecom": [
            r"\bhistory of (?:the country|the nation)\b",
            r"\btourist|tourism|travel guide\b",
            r"\brecipe|cooking|food\b",
            r"\bsports team|football|soccer\b",
            r"\bweather forecast\b",
            r"\bpersonal (finance|loan|trainer|assistant|development)\b",  # "Personal" confusion
            r"\bNGO|non-profit|foundation\b(?!.*telecom)",  # NGOs unless telecom-related
            r"\bhistorical events|independence|colonial\b",
            # Enhanced patterns for country history confusion (Personal Paraguay issue)
            r"\borigen de \w+\b.*acontecimiento",  # "Origen de Paraguay"
            r"\bhistoria del? \w+:?\s*(antecedente|historia|origen)",  # "Historia del Paraguay: Antecedentes"
            r"\bfundaci[oó]n (?!.*(?:telecom|celular|m[oó]vil|telefon))",  # "Fundación X" unless telecom
            r"\bmicrofinance|microcr[eé]dito|poverty alleviation\b",  # Fundación Paraguaya is microfinance
            r"\bhistoria universal\b",  # Generic history sites
            r"\bcuriosfera|historiauniversal\.org\b",  # Specific junk domains
            r"\bgeograf[ií]a|geography\b.*\bcountry\b",  # Country geography
            r"\bcolonial period|conquest|conquista\b",  # Historical periods
            r"\bprecolombino|pre-columbian|indigenous history\b",  # Historical periods
        ],
        "finance": [
            r"\brecipe|cooking|food\b",
            r"\bsports|entertainment\b",
            r"\bweather\b",
        ],
        "general": [
            r"\brecipe|cooking\b",
            r"\bweather forecast\b",
        ],
    }

    # Keywords that indicate high relevance for specific industries
    RELEVANCE_BOOSTERS = {
        "telecom": [
            r"\b(mobile|cellular|wireless|spectrum|5G|4G|LTE)\b",
            r"\b(telecom|telecommunications|operator|carrier)\b",
            r"\b(subscribers|customers|users|ARPU)\b",
            r"\b(revenue|ingresos|earnings|EBITDA)\b",
            r"\b(CEO|CFO|director|ejecutivo|gerente)\b",
            r"\b(market share|cuota de mercado|participación)\b",
            r"\b(regulator|CONATEL|ANATEL|regulador)\b",
        ],
        "finance": [
            r"\b(revenue|profit|earnings|EBITDA)\b",
            r"\b(stock|share|market cap|valuation)\b",
            r"\b(CEO|CFO|executive|board)\b",
        ],
    }

    def __init__(self, llm_client=None):
        """
        Initialize the filter.

        Args:
            llm_client: Optional LLM client for advanced filtering.
                       If not provided, uses pattern-based filtering only.
        """
        self.llm_client = llm_client

    def quick_relevance_check(
        self, title: str, snippet: str, url: str, research_target: str, industry: str = "general"
    ) -> Tuple[bool, float, str]:
        """
        Quick pattern-based relevance check (no LLM call).

        Args:
            title: Source title
            snippet: Source snippet/description
            url: Source URL
            research_target: What we're researching (e.g., "Personal Paraguay")
            industry: Industry type for pattern matching

        Returns:
            Tuple of (is_relevant, confidence_score, reason)
        """
        combined_text = f"{title} {snippet} {url}".lower()
        research_lower = research_target.lower()

        # Check for irrelevance patterns
        irrelevance_patterns = self.IRRELEVANCE_PATTERNS.get(
            industry, self.IRRELEVANCE_PATTERNS["general"]
        )

        for pattern in irrelevance_patterns:
            if re.search(pattern, combined_text, re.IGNORECASE):
                # Check if research target is also present (might be false positive)
                if research_lower not in combined_text:
                    return False, 0.2, f"Matched irrelevance pattern: {pattern}"

        # Check for relevance boosters
        relevance_patterns = self.RELEVANCE_BOOSTERS.get(industry, [])
        relevance_score = 0.5  # Base score

        for pattern in relevance_patterns:
            if re.search(pattern, combined_text, re.IGNORECASE):
                relevance_score += 0.1  # Boost for each relevant keyword

        relevance_score = min(relevance_score, 1.0)

        # Check if research target appears in content
        if research_lower in combined_text:
            relevance_score += 0.2

        # URL-based checks
        url_lower = url.lower()
        if any(x in url_lower for x in ["wikipedia", "linkedin", "bloomberg", "reuters"]):
            relevance_score += 0.1

        # Penalize clearly irrelevant domains
        irrelevant_domains = [
            "tripadvisor",
            "booking.com",
            "expedia",
            "yelp",
            "pinterest",
            "instagram",
            "tiktok",
            "youtube.com/watch",
            # History/geography sites that pollute telecom research
            "curiosfera-historia.com",
            "historiauniversal.org",
            "historyextra.com",
            "worldhistory.org",
            "britannica.com/place",  # Country pages, not company
            "lonelyplanet.com",
            "roughguides.com",  # Travel guides
        ]
        if any(domain in url_lower for domain in irrelevant_domains):
            relevance_score -= 0.3

        is_relevant = relevance_score >= 0.4
        return is_relevant, relevance_score, "Pattern-based assessment"

    def ai_relevance_check(
        self,
        sources: List[Dict[str, Any]],
        research_target: str,
        industry: str = "telecom",
        company_context: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Use AI to filter sources for relevance to the research target.

        This is the main method to address source padding with irrelevant content.

        Args:
            sources: List of source dicts with 'title', 'snippet', 'url'
            research_target: Company/topic being researched
            industry: Industry type
            company_context: Additional context (legal_name, country, etc.)

        Returns:
            Filtered list of sources with relevance scores added
        """
        if not self.llm_client:
            # Fallback to pattern-based filtering
            filtered = []
            for source in sources:
                is_relevant, score, reason = self.quick_relevance_check(
                    source.get("title", ""),
                    source.get("snippet", source.get("content", "")),
                    source.get("url", ""),
                    research_target,
                    industry,
                )
                if is_relevant:
                    source["relevance_score"] = score
                    source["relevance_reason"] = reason
                    filtered.append(source)
            return filtered

        # AI-based filtering
        context_info = ""
        if company_context:
            context_info = f"""
Company Context:
- Legal Name: {company_context.get('legal_name', 'N/A')}
- Country: {company_context.get('country', 'N/A')}
- Industry: {company_context.get('industry', industry)}
- Parent Company: {company_context.get('parent_company', 'N/A')}
"""

        # Prepare sources for AI analysis
        source_summaries = []
        for i, src in enumerate(sources[:30]):  # Limit to 30 for token efficiency
            source_summaries.append(
                f"""
Source {i+1}:
- Title: {src.get('title', 'N/A')[:100]}
- URL: {src.get('url', 'N/A')}
- Snippet: {src.get('snippet', src.get('content', ''))[:200]}
"""
            )

        sources_text = "\n".join(source_summaries)

        prompt = f"""Analyze these sources for relevance to researching "{research_target}" ({industry} company).
{context_info}
SOURCES TO EVALUATE:
{sources_text}

TASK: For each source, determine if it's RELEVANT to researching this specific company.

IRRELEVANT sources include:
- General country history, tourism, travel guides
- Unrelated companies with similar names
- NGOs, foundations, or organizations that aren't the target company
- Sports, entertainment, or personal development content
- Generic articles that don't mention the specific company

RELEVANT sources include:
- Company profile, news, financial reports
- Industry analysis mentioning the company
- Regulatory/government sources about the company
- Executive appointments, leadership changes
- Market share, subscriber data, competitive analysis

Return JSON array with source numbers that are RELEVANT:
{{"relevant_sources": [1, 3, 5, ...]}}

Only include sources that are clearly about "{research_target}" the {industry} company."""

        try:
            result = self.llm_client.complete(
                prompt=prompt,
                system="You are a research quality analyst. Filter sources for relevance. Return valid JSON only.",
                task_type="extraction",
                max_tokens=500,
                json_mode=True,
            )

            # Parse response
            if isinstance(result, str):
                content = result
            elif hasattr(result, "content"):
                content = result.content
            elif isinstance(result, dict):
                content = result.get("content", "{}")
            else:
                content = "{}"

            parsed = json.loads(content)
            relevant_indices = set(parsed.get("relevant_sources", []))

            # Filter sources
            filtered = []
            for i, src in enumerate(sources[:30]):
                if (i + 1) in relevant_indices:
                    src["relevance_score"] = 0.9
                    src["relevance_reason"] = "AI verified as relevant"
                    filtered.append(src)
                else:
                    # Keep but mark as low relevance if it passes quick check
                    is_relevant, score, reason = self.quick_relevance_check(
                        src.get("title", ""),
                        src.get("snippet", ""),
                        src.get("url", ""),
                        research_target,
                        industry,
                    )
                    if is_relevant and score >= 0.6:
                        src["relevance_score"] = score * 0.8  # Reduce confidence
                        src["relevance_reason"] = f"Pattern match (AI excluded): {reason}"
                        filtered.append(src)

            # Add remaining sources (beyond 30) that weren't AI-checked
            for src in sources[30:]:
                is_relevant, score, reason = self.quick_relevance_check(
                    src.get("title", ""),
                    src.get("snippet", ""),
                    src.get("url", ""),
                    research_target,
                    industry,
                )
                if is_relevant:
                    src["relevance_score"] = score
                    src["relevance_reason"] = reason
                    filtered.append(src)

            return filtered

        except Exception as e:
            # Fallback to pattern-based on error
            filtered = []
            for source in sources:
                is_relevant, score, reason = self.quick_relevance_check(
                    source.get("title", ""),
                    source.get("snippet", source.get("content", "")),
                    source.get("url", ""),
                    research_target,
                    industry,
                )
                if is_relevant:
                    source["relevance_score"] = score
                    source["relevance_reason"] = f"{reason} (AI fallback: {e})"
                    filtered.append(source)
            return filtered


# ============================================================================
# Source Quality Assessor
# ============================================================================


class SourceQualityAssessor:
    """
    Automatically assess source quality from URL.

    Uses domain-based quality mapping to assign quality tiers
    and numerical scores (0-100) to sources.
    """

    # Quality mapping: domain pattern → (quality tier, score)
    QUALITY_MAP = {
        # Official sources (95-100)
        ".gov": (SourceQuality.OFFICIAL, 98),
        ".edu": (SourceQuality.OFFICIAL, 95),
        "sec.gov": (SourceQuality.OFFICIAL, 100),
        "investor.": (SourceQuality.OFFICIAL, 97),  # investor.tesla.com, investor.microsoft.com
        "ir.": (SourceQuality.OFFICIAL, 97),  # ir.tesla.com (investor relations)
        # Authoritative sources (80-94)
        "bloomberg.com": (SourceQuality.AUTHORITATIVE, 92),
        "reuters.com": (SourceQuality.AUTHORITATIVE, 90),
        "ft.com": (SourceQuality.AUTHORITATIVE, 88),
        "wsj.com": (SourceQuality.AUTHORITATIVE, 88),
        "apnews.com": (SourceQuality.AUTHORITATIVE, 85),
        "afp.com": (SourceQuality.AUTHORITATIVE, 85),
        # Reputable sources (65-79)
        "forbes.com": (SourceQuality.REPUTABLE, 75),
        "techcrunch.com": (SourceQuality.REPUTABLE, 72),
        "cnbc.com": (SourceQuality.REPUTABLE, 70),
        "businessinsider.com": (SourceQuality.REPUTABLE, 68),
        "theverge.com": (SourceQuality.REPUTABLE, 70),
        "wired.com": (SourceQuality.REPUTABLE, 72),
        "arstechnica.com": (SourceQuality.REPUTABLE, 73),
        # Community sources (40-64)
        "reddit.com": (SourceQuality.COMMUNITY, 50),
        "news.ycombinator.com": (SourceQuality.COMMUNITY, 55),
        "medium.com": (SourceQuality.COMMUNITY, 45),
        "substack.com": (SourceQuality.COMMUNITY, 45),
    }

    def assess(self, url: str) -> Tuple[SourceQuality, float]:
        """
        Assess source quality from URL.

        Args:
            url: Source URL to assess

        Returns:
            Tuple of (quality_tier, quality_score)
            - quality_tier: SourceQuality enum value
            - quality_score: Numerical score 0-100
        """
        url_lower = url.lower()

        # Check each domain pattern
        for domain_pattern, (quality, score) in self.QUALITY_MAP.items():
            if domain_pattern in url_lower:
                return quality, score

        # Default for unknown sources
        return SourceQuality.UNKNOWN, 30

    def assess_source(self, source: Source) -> Source:
        """
        Assess a Source object in-place.

        Args:
            source: Source object to assess

        Returns:
            Same source object with quality and quality_score updated
        """
        quality, score = self.assess(source.url)
        source.quality = quality
        source.quality_score = score
        return source

    def calculate_confidence(self, fact: ResearchFact) -> ConfidenceLevel:
        """
        Calculate confidence level for a fact based on its source quality.

        Args:
            fact: ResearchFact to assess

        Returns:
            ConfidenceLevel (HIGH/MEDIUM/LOW)

        Scoring:
        - HIGH: Official or Authoritative sources (score >= 80)
        - MEDIUM: Reputable sources (score >= 65)
        - LOW: Community or Unknown sources (score < 65)
        """
        score = fact.source.quality_score

        if score >= 80:
            return ConfidenceLevel.HIGH
        elif score >= 65:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW

    def assess_fact(self, fact: ResearchFact) -> ResearchFact:
        """
        Assess a ResearchFact in-place (quality + confidence).

        Args:
            fact: ResearchFact to assess

        Returns:
            Same fact with source quality and confidence updated
        """
        # Assess source quality
        self.assess_source(fact.source)

        # Calculate confidence level
        fact.confidence = self.calculate_confidence(fact)

        return fact


# ============================================================================
# Quality Tier Information
# ============================================================================


def get_quality_tier_info(quality: SourceQuality) -> dict:
    """
    Get information about a quality tier.

    Args:
        quality: SourceQuality enum value

    Returns:
        Dictionary with tier information:
        - name: Tier name
        - description: What this tier means
        - score_range: Typical score range
        - examples: Example domains
    """
    info = {
        SourceQuality.OFFICIAL: {
            "name": "Official",
            "description": "Government, educational, or official company sources",
            "score_range": (95, 100),
            "examples": [".gov", ".edu", "sec.gov", "investor.tesla.com"],
        },
        SourceQuality.AUTHORITATIVE: {
            "name": "Authoritative",
            "description": "Established news agencies and financial publications",
            "score_range": (80, 94),
            "examples": ["bloomberg.com", "reuters.com", "wsj.com", "ft.com"],
        },
        SourceQuality.REPUTABLE: {
            "name": "Reputable",
            "description": "Reputable tech and business publications",
            "score_range": (65, 79),
            "examples": ["forbes.com", "techcrunch.com", "cnbc.com", "wired.com"],
        },
        SourceQuality.COMMUNITY: {
            "name": "Community",
            "description": "Community-driven platforms and forums",
            "score_range": (40, 64),
            "examples": ["reddit.com", "news.ycombinator.com", "medium.com"],
        },
        SourceQuality.UNKNOWN: {
            "name": "Unknown",
            "description": "Unverified or unrecognized sources",
            "score_range": (0, 39),
            "examples": ["Unrecognized domains"],
        },
    }

    return info.get(
        quality,
        {
            "name": "Unknown",
            "description": "Quality tier information not available",
            "score_range": (0, 100),
            "examples": [],
        },
    )
