"""
Social Media Agent (Phase 14.2).

Social media analysis capabilities:
- Social presence evaluation
- Engagement metrics analysis
- Content strategy assessment
- Audience analysis
- Platform performance comparison
- Influencer/partnership identification

This agent analyzes company social media presence and strategy.

Refactored to use BaseSpecialistAgent for:
- Reduced code duplication
- Consistent agent interface
- Centralized LLM calling and cost tracking
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List

from ...config import get_config
from ...llm.client_factory import calculate_cost
from ...state import OverallState
from ...types import ContentStrategy, EngagementLevel, SocialPlatform  # Centralized enums
from ..base import create_empty_result, get_agent_logger
from ..base.specialist import BaseSpecialistAgent, ParsingMixin

# ============================================================================
# Data Models
# ============================================================================
# Note: SocialPlatform, EngagementLevel, ContentStrategy imported from types.py


@dataclass
class PlatformMetrics:
    """Metrics for a single platform."""

    platform: SocialPlatform
    followers: int = 0
    engagement_rate: float = 0.0
    posting_frequency: str = ""  # daily, weekly, etc.
    content_types: List[str] = field(default_factory=list)
    top_performing_content: str = ""
    sentiment: str = "neutral"
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "platform": self.platform.value,
            "followers": self.followers,
            "engagement_rate": round(self.engagement_rate, 2),
            "posting_frequency": self.posting_frequency,
            "content_types": self.content_types,
            "sentiment": self.sentiment,
        }


@dataclass
class AudienceInsight:
    """Insight about the social media audience."""

    segment: str
    percentage: float
    engagement_level: EngagementLevel
    interests: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "segment": self.segment,
            "percentage": round(self.percentage, 1),
            "engagement_level": self.engagement_level.value,
            "interests": self.interests,
        }


@dataclass
class SocialMediaResult:
    """Complete social media analysis result."""

    company_name: str
    overall_presence: EngagementLevel = EngagementLevel.MODERATE
    social_score: float = 50.0
    platform_metrics: List[PlatformMetrics] = field(default_factory=list)
    audience_insights: List[AudienceInsight] = field(default_factory=list)
    content_strategy: ContentStrategy = ContentStrategy.MIXED
    top_platforms: List[str] = field(default_factory=list)
    viral_content: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    analysis: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "company_name": self.company_name,
            "overall_presence": self.overall_presence.value,
            "social_score": round(self.social_score, 1),
            "platform_metrics": [p.to_dict() for p in self.platform_metrics],
            "audience_insights": [a.to_dict() for a in self.audience_insights],
            "content_strategy": self.content_strategy.value,
            "top_platforms": self.top_platforms,
            "strengths": self.strengths,
            "opportunities": self.opportunities,
            "recommendations": self.recommendations,
        }


# ============================================================================
# Prompts
# ============================================================================

SOCIAL_MEDIA_PROMPT = """You are an expert social media analyst evaluating a company's social presence.

**COMPANY:** {company_name}

**AVAILABLE DATA:**
{search_results}

**TASK:** Perform comprehensive social media analysis.

**STRUCTURE YOUR ANALYSIS:**

### 1. Social Media Overview
- **Overall Presence:** [EXCEPTIONAL/HIGH/MODERATE/LOW/MINIMAL]
- **Primary Platforms:** [List main platforms]
- **Content Strategy:** [THOUGHT_LEADERSHIP/PRODUCT_FOCUSED/COMMUNITY_BUILDING/ENTERTAINMENT/EDUCATIONAL/MIXED]
- **Brand Voice:** [Description of tone and style]

### 2. Platform-by-Platform Analysis

**Twitter/X:**
- Followers: [Estimated count]
- Engagement Rate: [X%]
- Posting Frequency: [daily/weekly/etc.]
- Content Types: [List types]
- Sentiment: [POSITIVE/NEUTRAL/NEGATIVE]
- Notable: [Any notable observations]

**LinkedIn:**
- Followers: [Estimated count]
- Engagement Rate: [X%]
- Content Focus: [Description]
- Notable: [Any notable observations]

**Other Platforms:** (Instagram, YouTube, TikTok, etc.)
[Similar structure for each relevant platform]

### 3. Engagement Analysis
- **Average Engagement Rate:** [X%]
- **Best Performing Content Types:** [List]
- **Peak Engagement Times:** [If known]
- **Community Interaction:** [Description]

### 4. Audience Insights
| Segment | Percentage | Engagement | Key Interests |
|---------|------------|------------|---------------|
| [Segment 1] | [X%] | [HIGH/MED/LOW] | [Interests] |
| [Segment 2] | [X%] | [HIGH/MED/LOW] | [Interests] |
...

### 5. Content Strategy Evaluation
- **Content Pillars:** [Main content themes]
- **Content Mix:** [Types and ratios]
- **Viral/Top Performing Content:** [Examples]
- **Content Gaps:** [What's missing]

### 6. Competitive Social Position
- How does their social presence compare to competitors?
- Unique differentiators on social media
- Areas where competitors outperform

### 7. Influencer & Partnership Activity
- Notable partnerships
- Influencer collaborations
- User-generated content strategy

### 8. Strengths
1. [Strength 1]
2. [Strength 2]
...

### 9. Opportunities
1. [Opportunity 1]
2. [Opportunity 2]
...

### 10. Overall Social Score
**Social Score:** [0-100]

### 11. Recommendations
1. [Recommendation 1]
2. [Recommendation 2]
...

**REQUIREMENTS:**
- Be specific with estimates where data allows
- Note data limitations
- Provide actionable recommendations
- Consider platform-specific best practices

Begin your social media analysis:"""


# ============================================================================
# Social Media Agent
# ============================================================================


class SocialMediaAgent(BaseSpecialistAgent[SocialMediaResult], ParsingMixin):
    """
    Social Media Agent for presence analysis.

    Inherits from:
    - BaseSpecialistAgent: Common agent functionality (LLM calls, formatting, cost tracking)
    - ParsingMixin: Standardized extraction methods

    Analyzes:
    - Platform presence and metrics
    - Engagement patterns
    - Content strategy
    - Audience demographics
    - Competitive positioning

    Usage:
        agent = SocialMediaAgent()
        result = agent.analyze(  # Uses base class analyze() method
            company_name="Tesla",
            search_results=results
        )
    """

    # Class attributes for BaseSpecialistAgent
    agent_name = "social_media"

    def _get_prompt(self, company_name: str, formatted_results: str) -> str:
        """Build the social media analysis prompt."""
        return SOCIAL_MEDIA_PROMPT.format(
            company_name=company_name, search_results=formatted_results
        )

    def _format_search_results(self, results: List[Dict[str, Any]]) -> str:
        """Format search results for prompt."""
        if not results:
            return "No search results available"

        # Prioritize social media related results
        social_keywords = [
            "twitter",
            "linkedin",
            "instagram",
            "facebook",
            "youtube",
            "tiktok",
            "social",
            "followers",
            "engagement",
        ]

        scored_results = []
        for r in results:
            content = (r.get("content", "") + r.get("title", "")).lower()
            score = sum(1 for kw in social_keywords if kw in content)
            scored_results.append((score, r))

        scored_results.sort(key=lambda x: x[0], reverse=True)

        formatted = []
        for _, r in scored_results[:12]:
            formatted.append(
                f"Source: {r.get('title', 'N/A')}\n" f"Content: {r.get('content', '')[:400]}...\n"
            )

        return "\n".join(formatted)

    def _parse_analysis(self, company_name: str, analysis: str) -> SocialMediaResult:
        """Parse LLM analysis into structured result."""
        result = SocialMediaResult(company_name=company_name)

        # Extract platform metrics
        result.platform_metrics = self._extract_platform_metrics(analysis)

        # Extract overall presence
        result.overall_presence = self._extract_presence_level(analysis)

        # Extract content strategy
        result.content_strategy = self._extract_content_strategy(analysis)

        # Extract audience insights
        result.audience_insights = self._extract_audience_insights(analysis)

        # Extract lists
        result.strengths = self._extract_list_section(analysis, "Strength")
        result.opportunities = self._extract_list_section(analysis, "Opportunit")
        result.recommendations = self._extract_list_section(analysis, "Recommendation")

        # Extract top platforms
        result.top_platforms = self._extract_top_platforms(analysis)

        # Extract score
        result.social_score = self._extract_score(analysis)

        return result

    def _extract_platform_metrics(self, analysis: str) -> List[PlatformMetrics]:
        """Extract metrics for each platform."""
        metrics = []
        platforms = {
            "twitter": SocialPlatform.TWITTER,
            "linkedin": SocialPlatform.LINKEDIN,
            "facebook": SocialPlatform.FACEBOOK,
            "instagram": SocialPlatform.INSTAGRAM,
            "youtube": SocialPlatform.YOUTUBE,
            "tiktok": SocialPlatform.TIKTOK,
        }

        for name, platform in platforms.items():
            if name in analysis.lower():
                # Try to extract follower count
                followers = 0
                followers_pattern = (
                    rf"{name}[:\s]*.*?(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:M|K|million|thousand|followers)"
                )
                match = re.search(followers_pattern, analysis, re.IGNORECASE)
                if match:
                    num_str = match.group(1).replace(",", "")
                    try:
                        followers = int(float(num_str))
                        if "M" in match.group(0) or "million" in match.group(0).lower():
                            followers *= 1000000
                        elif "K" in match.group(0) or "thousand" in match.group(0).lower():
                            followers *= 1000
                    except ValueError:
                        pass

                # Try to extract engagement rate
                engagement = 0.0
                eng_pattern = rf"{name}.*?engagement.*?(\d+(?:\.\d+)?)\s*%"
                eng_match = re.search(eng_pattern, analysis, re.IGNORECASE)
                if eng_match:
                    try:
                        engagement = float(eng_match.group(1))
                    except ValueError:
                        pass

                metrics.append(
                    PlatformMetrics(
                        platform=platform,
                        followers=followers,
                        engagement_rate=engagement,
                        posting_frequency="regular" if name in analysis.lower() else "unknown",
                    )
                )

        return metrics

    def _extract_presence_level(self, analysis: str) -> EngagementLevel:
        """Extract overall presence level."""
        analysis_lower = analysis.lower()

        if "exceptional" in analysis_lower:
            return EngagementLevel.EXCEPTIONAL
        elif "high" in analysis_lower and "presence" in analysis_lower:
            return EngagementLevel.HIGH
        elif "low" in analysis_lower and "presence" in analysis_lower:
            return EngagementLevel.LOW
        elif "minimal" in analysis_lower:
            return EngagementLevel.MINIMAL

        return EngagementLevel.MODERATE

    def _extract_content_strategy(self, analysis: str) -> ContentStrategy:
        """Extract content strategy type."""
        analysis_lower = analysis.lower()

        if "thought leadership" in analysis_lower:
            return ContentStrategy.THOUGHT_LEADERSHIP
        elif "product" in analysis_lower and (
            "focus" in analysis_lower or "centric" in analysis_lower
        ):
            return ContentStrategy.PRODUCT_FOCUSED
        elif "community" in analysis_lower:
            return ContentStrategy.COMMUNITY_BUILDING
        elif "entertainment" in analysis_lower:
            return ContentStrategy.ENTERTAINMENT
        elif "educational" in analysis_lower or "education" in analysis_lower:
            return ContentStrategy.EDUCATIONAL

        return ContentStrategy.MIXED

    def _extract_audience_insights(self, analysis: str) -> List[AudienceInsight]:
        """Extract audience insights."""
        insights = []
        common_segments = [
            "tech enthusiasts",
            "professionals",
            "millennials",
            "gen z",
            "investors",
            "industry experts",
            "consumers",
        ]

        for segment in common_segments:
            if segment.lower() in analysis.lower():
                insights.append(
                    AudienceInsight(
                        segment=segment.title(),
                        percentage=20.0,  # Default estimate
                        engagement_level=EngagementLevel.MODERATE,
                    )
                )

        return insights[:4]

    def _extract_top_platforms(self, analysis: str) -> List[str]:
        """Extract top performing platforms."""
        platforms = []
        platform_names = ["Twitter", "LinkedIn", "Instagram", "YouTube", "TikTok", "Facebook"]

        for name in platform_names:
            if name.lower() in analysis.lower():
                # Check if mentioned positively
                if any(
                    word in analysis.lower() for word in ["strong", "active", "popular", "primary"]
                ):
                    platforms.append(name)

        return platforms[:3] if platforms else ["Unknown"]

    def _extract_list_section(self, analysis: str, section_keyword: str) -> List[str]:
        """Extract items from a list section using ParsingMixin."""
        # Delegate to ParsingMixin.extract_list_items for standardized extraction
        return self.extract_list_items(analysis, section_keyword, max_items=5)

    def _extract_score(self, analysis: str) -> float:
        """Extract social score using ParsingMixin."""
        # Delegate to ParsingMixin.extract_score for standardized extraction
        return self.extract_score(analysis, "Social Score", default=50.0)


# ============================================================================
# Agent Node Function
# ============================================================================


def social_media_agent_node(state: OverallState) -> Dict[str, Any]:
    """
    Social Media Agent Node for workflow integration.

    Args:
        state: Current workflow state

    Returns:
        State update with social media analysis
    """
    logger = get_agent_logger("social_media")
    config = get_config()
    company_name = state["company_name"]
    search_results = state.get("search_results", [])

    with logger.agent_run(company_name):
        if not search_results:
            logger.no_data()
            return create_empty_result("social_media")

        logger.analyzing(len(search_results))

        # Run analysis
        agent = SocialMediaAgent(config)
        result = agent.analyze(company_name=company_name, search_results=search_results)

        cost = calculate_cost(500, 1500)

        logger.info(f"Social Score: {result.social_score}")
        logger.info(f"Presence: {result.overall_presence.value}")
        logger.info(f"Top Platforms: {result.top_platforms}")
        logger.complete(cost=cost)

        return {
            "agent_outputs": {
                "social_media": {**result.to_dict(), "analysis": result.analysis, "cost": cost}
            },
            "total_cost": cost,
        }


# ============================================================================
# Factory Function
# ============================================================================


def create_social_media_agent() -> SocialMediaAgent:
    """Create a Social Media Agent instance."""
    return SocialMediaAgent()
