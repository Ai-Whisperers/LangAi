"""
Source quality assessment system (Phase 5).

Automatically assesses source quality based on domain reputation,
provides quality scores, and assigns confidence levels.
"""

from typing import Tuple
from .models import Source, SourceQuality, ConfidenceLevel, ResearchFact


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

    return info.get(quality, {
        "name": "Unknown",
        "description": "Quality tier information not available",
        "score_range": (0, 100),
        "examples": [],
    })
