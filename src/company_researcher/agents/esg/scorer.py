"""
ESG Scorer Module.

Scoring logic for ESG metrics and ratings.
"""

from typing import List

from .models import (
    ESGCategory,
    ESGRating,
    ESGMetric,
    Controversy,
    ControversySeverity,
    ESGScore,
)


class ESGScorer:
    """
    ESG scoring calculator.

    Calculates overall and category-specific ESG scores
    based on metrics and controversies.
    """

    # Weight distribution for overall score
    CATEGORY_WEIGHTS = {
        ESGCategory.ENVIRONMENTAL: 0.33,
        ESGCategory.SOCIAL: 0.33,
        ESGCategory.GOVERNANCE: 0.34,
    }

    # Controversy penalties by severity
    CONTROVERSY_PENALTIES = {
        ControversySeverity.SEVERE: 15,
        ControversySeverity.HIGH: 10,
        ControversySeverity.MODERATE: 5,
        ControversySeverity.LOW: 2,
        ControversySeverity.NONE: 0,
    }

    # Rating thresholds
    RATING_THRESHOLDS = [
        (85, ESGRating.AAA),
        (75, ESGRating.AA),
        (65, ESGRating.A),
        (55, ESGRating.BBB),
        (45, ESGRating.BB),
        (35, ESGRating.B),
        (25, ESGRating.CCC),
        (15, ESGRating.CC),
        (0, ESGRating.C),
    ]

    def __init__(self, base_score: float = 50.0):
        """
        Initialize scorer.

        Args:
            base_score: Starting score for each category (0-100)
        """
        self.base_score = base_score

    def calculate_score(
        self,
        metrics: List[ESGMetric],
        controversies: List[Controversy]
    ) -> ESGScore:
        """
        Calculate ESG scores from metrics and controversies.

        Args:
            metrics: List of ESG metrics
            controversies: List of ESG controversies

        Returns:
            ESGScore with category and overall scores
        """
        # Initialize category scores
        env_score = self.base_score
        social_score = self.base_score
        gov_score = self.base_score

        # Adjust based on metrics
        for metric in metrics:
            adjustment = self._metric_to_adjustment(metric)
            if metric.category == ESGCategory.ENVIRONMENTAL:
                env_score += adjustment
            elif metric.category == ESGCategory.SOCIAL:
                social_score += adjustment
            elif metric.category == ESGCategory.GOVERNANCE:
                gov_score += adjustment

        # Apply controversy penalties
        for controversy in controversies:
            penalty = self.CONTROVERSY_PENALTIES.get(controversy.severity, 0)

            # Reduce penalty if resolved
            if controversy.resolved:
                penalty = penalty // 2

            if controversy.category == ESGCategory.ENVIRONMENTAL:
                env_score -= penalty
            elif controversy.category == ESGCategory.SOCIAL:
                social_score -= penalty
            elif controversy.category == ESGCategory.GOVERNANCE:
                gov_score -= penalty

        # Clamp scores to valid range
        env_score = self._clamp_score(env_score)
        social_score = self._clamp_score(social_score)
        gov_score = self._clamp_score(gov_score)

        # Calculate weighted overall score
        overall = (
            env_score * self.CATEGORY_WEIGHTS[ESGCategory.ENVIRONMENTAL] +
            social_score * self.CATEGORY_WEIGHTS[ESGCategory.SOCIAL] +
            gov_score * self.CATEGORY_WEIGHTS[ESGCategory.GOVERNANCE]
        )

        # Determine rating
        rating = self._score_to_rating(overall)

        # Calculate confidence based on data availability
        confidence = self._calculate_confidence(metrics, controversies)

        return ESGScore(
            overall_score=round(overall, 1),
            overall_rating=rating,
            environmental_score=round(env_score, 1),
            social_score=round(social_score, 1),
            governance_score=round(gov_score, 1),
            confidence=confidence
        )

    def _metric_to_adjustment(self, metric: ESGMetric) -> float:
        """
        Convert metric to score adjustment.

        Args:
            metric: ESG metric

        Returns:
            Score adjustment value
        """
        adjustment = 0.0

        # Trend-based adjustment
        if metric.trend == "improving":
            adjustment += 5
        elif metric.trend == "declining":
            adjustment -= 5

        # Benchmark comparison
        if metric.benchmark is not None and isinstance(metric.value, (int, float)):
            if metric.value > metric.benchmark:
                adjustment += 3
            elif metric.value < metric.benchmark:
                adjustment -= 3

        return adjustment

    def _clamp_score(self, score: float) -> float:
        """Clamp score to 0-100 range."""
        return max(0, min(100, score))

    def _score_to_rating(self, score: float) -> ESGRating:
        """
        Convert numeric score to ESG rating.

        Args:
            score: Overall ESG score (0-100)

        Returns:
            ESGRating enum value
        """
        for threshold, rating in self.RATING_THRESHOLDS:
            if score >= threshold:
                return rating
        return ESGRating.C

    def _calculate_confidence(
        self,
        metrics: List[ESGMetric],
        controversies: List[Controversy]
    ) -> float:
        """
        Calculate confidence level based on data availability.

        Args:
            metrics: List of ESG metrics
            controversies: List of controversies

        Returns:
            Confidence score (0-1)
        """
        confidence = 0.3  # Base confidence

        # More metrics = higher confidence
        if len(metrics) >= 10:
            confidence += 0.3
        elif len(metrics) >= 5:
            confidence += 0.2
        elif len(metrics) >= 1:
            confidence += 0.1

        # Category coverage improves confidence
        categories_covered = set(m.category for m in metrics)
        confidence += 0.1 * len(categories_covered)

        # Source quality (metrics with sources)
        sourced_metrics = sum(1 for m in metrics if m.source)
        if sourced_metrics > 0:
            confidence += 0.1 * min(1.0, sourced_metrics / len(metrics))

        return min(1.0, confidence)

    def identify_strengths_risks(
        self,
        metrics: List[ESGMetric],
        controversies: List[Controversy]
    ) -> tuple:
        """
        Identify ESG strengths and risks.

        Args:
            metrics: List of ESG metrics
            controversies: List of controversies

        Returns:
            Tuple of (strengths, risks) lists
        """
        strengths = []
        risks = []

        # Check metrics for strengths/risks
        for metric in metrics:
            if metric.trend == "improving":
                strengths.append(f"Improving {metric.name}")
            elif metric.trend == "declining":
                risks.append(f"Declining {metric.name}")

            # Benchmark comparison
            if metric.benchmark is not None and isinstance(metric.value, (int, float)):
                if metric.value > metric.benchmark * 1.2:
                    strengths.append(f"Above benchmark: {metric.name}")
                elif metric.value < metric.benchmark * 0.8:
                    risks.append(f"Below benchmark: {metric.name}")

        # Add controversies as risks
        for controversy in controversies:
            if controversy.severity in [ControversySeverity.SEVERE, ControversySeverity.HIGH]:
                risks.append(
                    f"{controversy.category.value.title()}: {controversy.title}"
                )

        return strengths[:5], risks[:5]

    def generate_recommendations(
        self,
        metrics: List[ESGMetric],
        score: ESGScore,
        risks: List[str]
    ) -> List[str]:
        """
        Generate ESG improvement recommendations.

        Args:
            metrics: List of ESG metrics
            score: Calculated ESG score
            risks: Identified risks

        Returns:
            List of recommendations
        """
        recommendations = []

        # Category coverage recommendations
        categories_covered = set(m.category for m in metrics)
        for category in ESGCategory:
            if category not in categories_covered:
                recommendations.append(
                    f"Improve {category.value} disclosure and tracking"
                )

        # Score-based recommendations
        if score.environmental_score < 50:
            recommendations.append(
                "Strengthen environmental initiatives and reporting"
            )
        if score.social_score < 50:
            recommendations.append(
                "Enhance social responsibility programs"
            )
        if score.governance_score < 50:
            recommendations.append(
                "Improve governance practices and transparency"
            )

        # Risk-based recommendations
        for risk in risks[:3]:
            risk_lower = risk.lower()
            if "environmental" in risk_lower:
                recommendations.append("Address environmental risk factors")
            elif "social" in risk_lower:
                recommendations.append("Mitigate social responsibility concerns")
            elif "governance" in risk_lower:
                recommendations.append("Strengthen governance controls")

        # Remove duplicates while preserving order
        seen = set()
        unique_recs = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recs.append(rec)

        return unique_recs[:5]
