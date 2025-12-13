"""
Competitor Analysis Utilities (Phase 9).

Provides frameworks for:
- Competitor identification and classification
- Tech stack analysis
- GitHub repository metrics
- Competitive positioning assessment
- Patent and review analysis
"""

from typing import Dict, List, Tuple
from enum import Enum
from datetime import datetime, timedelta
from ..utils import utc_now


# ==============================================================================
# Enums and Constants
# ==============================================================================

class CompetitorType(str, Enum):
    """Competitor classification types."""
    DIRECT = "DIRECT"              # Same product/service, same market
    INDIRECT = "INDIRECT"          # Different approach, same problem
    POTENTIAL = "POTENTIAL"        # Could enter market
    SUBSTITUTE = "SUBSTITUTE"      # Alternative solution


class ThreatLevel(str, Enum):
    """Competitive threat assessment."""
    CRITICAL = "CRITICAL"          # Immediate major threat
    HIGH = "HIGH"                  # Significant threat
    MODERATE = "MODERATE"          # Manageable threat
    LOW = "LOW"                    # Minor threat
    EMERGING = "EMERGING"          # Future potential threat


# ==============================================================================
# Competitor Identification
# ==============================================================================

def classify_competitor(
    market_overlap: float,  # 0-100%
    product_similarity: float,  # 0-100%
    target_customer_overlap: float  # 0-100%
) -> CompetitorType:
    """
    Classify competitor type based on overlap metrics.

    Args:
        market_overlap: % of market overlap
        product_similarity: % of product/service similarity
        target_customer_overlap: % of customer base overlap

    Returns:
        CompetitorType classification

    Classification Rules:
    - DIRECT: High overlap in all dimensions (>70%)
    - INDIRECT: Moderate overlap (40-70%)
    - SUBSTITUTE: Different approach (<40% product similarity) but same customers
    - POTENTIAL: Low current overlap but potential future threat
    """
    avg_overlap = (market_overlap + product_similarity + target_customer_overlap) / 3

    if avg_overlap >= 70:
        return CompetitorType.DIRECT
    elif avg_overlap >= 40:
        if product_similarity < 40 and target_customer_overlap > 60:
            return CompetitorType.SUBSTITUTE
        else:
            return CompetitorType.INDIRECT
    else:
        return CompetitorType.POTENTIAL


def assess_threat_level(
    market_share: float,  # Competitor's market share %
    growth_rate: float,  # Competitor's growth rate %
    funding_strength: float,  # 0-10 scale
    product_quality: float,  # 0-10 scale
    brand_strength: float  # 0-10 scale
) -> ThreatLevel:
    """
    Assess competitive threat level.

    Args:
        market_share: Competitor's current market share (%)
        growth_rate: Competitor's YoY growth rate (%)
        funding_strength: Financial strength (0-10)
        product_quality: Product quality rating (0-10)
        brand_strength: Brand strength rating (0-10)

    Returns:
        ThreatLevel assessment
    """
    # Calculate threat score (weighted)
    threat_score = (
        market_share * 0.3 +      # Current position
        (growth_rate / 10) * 0.25 +  # Growth trajectory
        funding_strength * 0.15 +  # Resources
        product_quality * 0.15 +   # Product strength
        brand_strength * 0.15      # Brand power
    )

    # Normalize to 0-10
    normalized_score = min(threat_score / 10, 10)

    # Classify
    if normalized_score >= 8:
        return ThreatLevel.CRITICAL
    elif normalized_score >= 6:
        return ThreatLevel.HIGH
    elif normalized_score >= 4:
        return ThreatLevel.MODERATE
    elif normalized_score >= 2:
        return ThreatLevel.LOW
    else:
        return ThreatLevel.EMERGING


# ==============================================================================
# Tech Stack Analysis
# ==============================================================================

class TechStackAnalyzer:
    """
    Analyze competitor technology stacks.

    Categories:
    - Frontend: React, Vue, Angular, etc.
    - Backend: Node.js, Python, Java, etc.
    - Database: PostgreSQL, MongoDB, etc.
    - Infrastructure: AWS, GCP, Azure, Kubernetes
    - Analytics: Google Analytics, Mixpanel, etc.
    """

    # Technology category mappings
    TECH_CATEGORIES = {
        "frontend": ["React", "Vue", "Angular", "Svelte", "Next.js"],
        "backend": ["Node.js", "Python", "Java", "Go", "Ruby", "PHP"],
        "database": ["PostgreSQL", "MySQL", "MongoDB", "Redis", "Cassandra"],
        "cloud": ["AWS", "GCP", "Azure", "DigitalOcean", "Heroku"],
        "analytics": ["Google Analytics", "Mixpanel", "Amplitude", "Segment"],
        "cdn": ["Cloudflare", "Fastly", "Akamai", "CloudFront"],
        "monitoring": ["Datadog", "New Relic", "Sentry", "PagerDuty"]
    }

    def __init__(self):
        """Initialize tech stack analyzer."""
        self._cache = {}

    def analyze_stack(self, technologies: List[str]) -> Dict[str, List[str]]:
        """
        Categorize technologies into stack categories.

        Args:
            technologies: List of detected technologies

        Returns:
            Dictionary with categorized technologies
        """
        categorized = {category: [] for category in self.TECH_CATEGORIES.keys()}
        uncategorized = []

        for tech in technologies:
            categorized_flag = False

            for category, tech_list in self.TECH_CATEGORIES.items():
                if any(known_tech.lower() in tech.lower() for known_tech in tech_list):
                    categorized[category].append(tech)
                    categorized_flag = True
                    break

            if not categorized_flag:
                uncategorized.append(tech)

        if uncategorized:
            categorized["other"] = uncategorized

        return categorized

    def compare_stacks(
        self,
        stack_a: Dict[str, List[str]],
        stack_b: Dict[str, List[str]]
    ) -> Dict[str, any]:
        """
        Compare two technology stacks.

        Args:
            stack_a: First company's tech stack
            stack_b: Second company's tech stack

        Returns:
            Dictionary with comparison results:
            - similarity_score: 0-100%
            - common_technologies: Shared technologies
            - unique_to_a: Technologies only in A
            - unique_to_b: Technologies only in B
        """
        # Flatten stacks
        techs_a = set()
        techs_b = set()

        for techs in stack_a.values():
            techs_a.update(t.lower() for t in techs)

        for techs in stack_b.values():
            techs_b.update(t.lower() for t in techs)

        # Calculate overlap
        common = techs_a & techs_b
        unique_a = techs_a - techs_b
        unique_b = techs_b - techs_a

        # Similarity score (Jaccard index)
        union = techs_a | techs_b
        similarity = (len(common) / len(union) * 100) if union else 0

        return {
            "similarity_score": round(similarity, 2),
            "common_technologies": list(common),
            "unique_to_a": list(unique_a),
            "unique_to_b": list(unique_b),
            "total_technologies_a": len(techs_a),
            "total_technologies_b": len(techs_b)
        }


# ==============================================================================
# GitHub Activity Metrics
# ==============================================================================

class GitHubMetrics:
    """
    Calculate GitHub repository activity metrics.

    Metrics:
    - Commit frequency
    - Contributor count
    - Issue activity
    - Pull request activity
    - Repository health score
    """

    @staticmethod
    def calculate_commit_frequency(
        commits: List[datetime],
        period_days: int = 30
    ) -> float:
        """
        Calculate commit frequency (commits per day).

        Args:
            commits: List of commit timestamps
            period_days: Period to analyze (default: 30 days)

        Returns:
            Average commits per day
        """
        if not commits:
            return 0.0

        cutoff_date = utc_now() - timedelta(days=period_days)
        recent_commits = [c for c in commits if c >= cutoff_date]

        frequency = len(recent_commits) / period_days
        return round(frequency, 2)

    @staticmethod
    def calculate_repository_health(
        stars: int,
        forks: int,
        open_issues: int,
        closed_issues: int,
        last_commit_days_ago: int
    ) -> Dict[str, any]:
        """
        Calculate repository health score.

        Args:
            stars: Number of GitHub stars
            forks: Number of forks
            open_issues: Open issues count
            closed_issues: Closed issues count
            last_commit_days_ago: Days since last commit

        Returns:
            Dictionary with health metrics:
            - health_score: 0-100
            - popularity_score: Based on stars/forks
            - activity_score: Based on recent commits
            - maintenance_score: Based on issue resolution
        """
        # Popularity score (0-100)
        # Logarithmic scale for stars and forks
        import math
        if stars > 0 or forks > 0:
            popularity = min(
                (math.log10(max(stars, 1)) * 20 + math.log10(max(forks, 1)) * 10),
                100
            )
        else:
            popularity = 0

        # Activity score (0-100)
        # Recent commits are better
        if last_commit_days_ago <= 7:
            activity = 100
        elif last_commit_days_ago <= 30:
            activity = 80
        elif last_commit_days_ago <= 90:
            activity = 50
        elif last_commit_days_ago <= 180:
            activity = 25
        else:
            activity = 10

        # Maintenance score (0-100)
        # Based on issue resolution rate
        total_issues = open_issues + closed_issues
        if total_issues > 0:
            resolution_rate = closed_issues / total_issues
            maintenance = resolution_rate * 100
        else:
            maintenance = 50  # Neutral if no issues

        # Overall health score (weighted average)
        health_score = (
            popularity * 0.3 +
            activity * 0.4 +
            maintenance * 0.3
        )

        return {
            "health_score": round(health_score, 2),
            "popularity_score": round(popularity, 2),
            "activity_score": round(activity, 2),
            "maintenance_score": round(maintenance, 2)
        }

    @staticmethod
    def estimate_team_size(
        contributors: int,
        commit_frequency: float
    ) -> Tuple[int, int]:
        """
        Estimate team size from GitHub metrics.

        Args:
            contributors: Number of contributors
            commit_frequency: Commits per day

        Returns:
            Tuple of (min_estimate, max_estimate) for team size
        """
        # Heuristic: Active developers make 1-5 commits per day on average
        # Contributors may include occasional contributors

        # Core team estimate (frequent committers)
        if commit_frequency >= 10:
            min_core = 3
            max_core = 8
        elif commit_frequency >= 5:
            min_core = 2
            max_core = 5
        elif commit_frequency >= 1:
            min_core = 1
            max_core = 3
        else:
            min_core = 1
            max_core = 2

        # Total team (including occasional contributors)
        # Typically 20-40% of contributors are active
        min_total = int(contributors * 0.2) if contributors > 5 else contributors
        max_total = int(contributors * 0.4) if contributors > 5 else contributors

        # Sanity check
        min_estimate = max(min_core, min_total)
        max_estimate = max(max_core, max_total)

        return (min_estimate, max_estimate)


# ==============================================================================
# Competitive Positioning
# ==============================================================================

def analyze_competitive_positioning(
    company_strengths: List[str],
    company_weaknesses: List[str],
    competitor_strengths: List[str],
    competitor_weaknesses: List[str]
) -> Dict[str, any]:
    """
    Analyze competitive positioning between company and competitor.

    Args:
        company_strengths: List of company strengths
        company_weaknesses: List of company weaknesses
        competitor_strengths: List of competitor strengths
        competitor_weaknesses: List of competitor weaknesses

    Returns:
        Dictionary with positioning analysis:
        - advantages: Company advantages over competitor
        - disadvantages: Competitor advantages over company
        - opportunities: Competitor weaknesses to exploit
        - threats: Competitor strengths to defend against
    """
    # Find unique strengths (advantages)
    advantages = [s for s in company_strengths if s not in competitor_strengths]

    # Find where competitor is stronger (disadvantages)
    disadvantages = [s for s in competitor_strengths if s not in company_strengths]

    # Opportunities (competitor weaknesses company can exploit)
    opportunities = [w for w in competitor_weaknesses if w not in company_weaknesses]

    # Threats (competitor strengths that exploit company weaknesses)
    threats = [
        s for s in competitor_strengths
        if any(w in s for w in company_weaknesses)
    ]

    return {
        "advantages": advantages,
        "disadvantages": disadvantages,
        "opportunities": opportunities,
        "threats": threats
    }


# ==============================================================================
# Patent and Review Analysis
# ==============================================================================

def analyze_patent_portfolio(
    patent_count: int,
    recent_filings: int,  # Last 12 months
    key_categories: List[str]
) -> Dict[str, any]:
    """
    Analyze patent portfolio strength.

    Args:
        patent_count: Total patent count
        recent_filings: Patents filed in last 12 months
        key_categories: Key patent categories

    Returns:
        Dictionary with patent analysis:
        - portfolio_strength: LOW/MODERATE/STRONG/DOMINANT
        - innovation_velocity: Based on recent filings
        - key_areas: Key technology areas
    """
    # Portfolio strength assessment
    if patent_count >= 10000:
        strength = "DOMINANT"
    elif patent_count >= 1000:
        strength = "STRONG"
    elif patent_count >= 100:
        strength = "MODERATE"
    else:
        strength = "LOW"

    # Innovation velocity (patents per month)
    velocity = round(recent_filings / 12, 1)

    return {
        "portfolio_strength": strength,
        "total_patents": patent_count,
        "recent_filings": recent_filings,
        "innovation_velocity": velocity,  # patents per month
        "key_areas": key_categories
    }


def aggregate_review_sentiment(
    reviews: List[Dict[str, any]]
) -> Dict[str, any]:
    """
    Aggregate customer review sentiment.

    Args:
        reviews: List of reviews with 'rating' and 'text' keys

    Returns:
        Dictionary with sentiment analysis:
        - average_rating: Mean rating
        - rating_distribution: Count by rating
        - sentiment: POSITIVE/NEUTRAL/NEGATIVE
    """
    if not reviews:
        return {
            "available": False,
            "reason": "No reviews available"
        }

    # Calculate average rating
    ratings = [r.get("rating", 0) for r in reviews]
    avg_rating = sum(ratings) / len(ratings)

    # Distribution
    distribution = {
        "5_star": sum(1 for r in ratings if r == 5),
        "4_star": sum(1 for r in ratings if r == 4),
        "3_star": sum(1 for r in ratings if r == 3),
        "2_star": sum(1 for r in ratings if r == 2),
        "1_star": sum(1 for r in ratings if r == 1)
    }

    # Sentiment
    if avg_rating >= 4.0:
        sentiment = "POSITIVE"
    elif avg_rating >= 3.0:
        sentiment = "NEUTRAL"
    else:
        sentiment = "NEGATIVE"

    return {
        "available": True,
        "average_rating": round(avg_rating, 2),
        "total_reviews": len(reviews),
        "rating_distribution": distribution,
        "sentiment": sentiment
    }
