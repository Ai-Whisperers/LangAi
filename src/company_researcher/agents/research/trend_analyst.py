"""
Trend Analysis & Forecasting Agent

Analyzes historical data to:
- Identify trends over time
- Provide simple forecasting
- Detect emerging patterns
- Spot growth opportunities and threats

Usage:
    from company_researcher.agents.research.trend_analyst import (
        TrendAnalystAgent,
        trend_analyst_agent_node,
        create_trend_analyst
    )

    analyst = create_trend_analyst()
    trends = await analyst.analyze_trends(data_points)
    forecast = await analyst.forecast(metric, periods=4)
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
from ...utils import get_logger, utc_now

logger = get_logger(__name__)


class TrendDirection(Enum):
    """Direction of a trend."""
    STRONG_UP = "strong_up"
    UP = "up"
    STABLE = "stable"
    DOWN = "down"
    STRONG_DOWN = "strong_down"
    VOLATILE = "volatile"


class TrendStrength(Enum):
    """Strength/confidence of a trend."""
    VERY_STRONG = "very_strong"
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    UNCLEAR = "unclear"


class SignalType(Enum):
    """Types of trend signals."""
    BREAKOUT = "breakout"           # Breaking above resistance
    BREAKDOWN = "breakdown"          # Breaking below support
    REVERSAL = "reversal"           # Trend reversal
    ACCELERATION = "acceleration"    # Trend speeding up
    DECELERATION = "deceleration"    # Trend slowing down
    CONSOLIDATION = "consolidation"  # Flat/sideways movement
    SEASONALITY = "seasonality"      # Seasonal pattern detected


@dataclass
class DataPoint:
    """A single data point in a time series."""
    timestamp: datetime
    value: float
    metric: str
    source: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Trend:
    """A detected trend."""
    metric: str
    direction: TrendDirection
    strength: TrendStrength
    start_date: datetime
    end_date: datetime
    start_value: float
    end_value: float
    change_percent: float
    data_points: int
    r_squared: float              # Fit quality
    signals: List[SignalType] = field(default_factory=list)
    description: str = ""


@dataclass
class Forecast:
    """A forecasted value."""
    metric: str
    period: datetime
    predicted_value: float
    confidence_lower: float
    confidence_upper: float
    confidence_level: float       # 0-1
    method: str
    assumptions: List[str] = field(default_factory=list)


@dataclass
class TrendAnalysis:
    """Complete trend analysis result."""
    company_name: str
    analysis_date: datetime
    trends: List[Trend]
    forecasts: List[Forecast]
    signals: List[Dict[str, Any]]
    opportunities: List[str]
    threats: List[str]
    summary: str
    confidence: float


class TrendAnalystAgent:
    """
    Agent for analyzing trends and forecasting.

    Uses statistical methods to identify patterns in
    historical data and project future values.
    """

    # Thresholds for trend classification
    STRONG_TREND_THRESHOLD = 0.15   # 15% change
    TREND_THRESHOLD = 0.05          # 5% change
    VOLATILITY_THRESHOLD = 0.20     # 20% standard deviation

    def __init__(
        self,
        company_name: str,
        forecast_confidence: float = 0.8,
        min_data_points: int = 3
    ):
        self.company_name = company_name
        self.forecast_confidence = forecast_confidence
        self.min_data_points = min_data_points
        self.data_store: Dict[str, List[DataPoint]] = defaultdict(list)

    def add_data_point(
        self,
        metric: str,
        value: float,
        timestamp: datetime,
        source: Optional[str] = None
    ):
        """Add a data point for analysis."""
        point = DataPoint(
            timestamp=timestamp,
            value=value,
            metric=metric,
            source=source
        )
        self.data_store[metric].append(point)
        # Keep sorted by timestamp
        self.data_store[metric].sort(key=lambda x: x.timestamp)

    def add_historical_data(self, metric: str, data: List[Dict[str, Any]]):
        """Add multiple historical data points."""
        for item in data:
            timestamp = item.get("date") or item.get("timestamp") or item.get("period")
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

            value = item.get("value") or item.get(metric)
            if value is not None and timestamp is not None:
                self.add_data_point(
                    metric=metric,
                    value=float(value),
                    timestamp=timestamp,
                    source=item.get("source")
                )

    def analyze_trends(self, metrics: Optional[List[str]] = None) -> TrendAnalysis:
        """
        Analyze trends across all or specified metrics.

        Args:
            metrics: List of metrics to analyze (None = all)

        Returns:
            TrendAnalysis with trends, forecasts, and insights
        """
        metrics_to_analyze = metrics or list(self.data_store.keys())
        trends = []
        forecasts = []
        all_signals = []
        opportunities = []
        threats = []

        for metric in metrics_to_analyze:
            data = self.data_store.get(metric, [])

            if len(data) < self.min_data_points:
                logger.warning(f"Insufficient data for {metric}: {len(data)} points")
                continue

            # Analyze trend
            trend = self._analyze_metric_trend(metric, data)
            if trend:
                trends.append(trend)

                # Generate signals
                signals = self._detect_signals(metric, data, trend)
                all_signals.extend(signals)

                # Identify opportunities and threats
                if trend.direction in [TrendDirection.STRONG_UP, TrendDirection.UP]:
                    opportunities.append(
                        f"{metric}: Positive trend ({trend.change_percent:+.1f}% over period)"
                    )
                elif trend.direction in [TrendDirection.STRONG_DOWN, TrendDirection.DOWN]:
                    threats.append(
                        f"{metric}: Declining trend ({trend.change_percent:+.1f}% over period)"
                    )

                # Generate forecast
                forecast = self._generate_forecast(metric, data, periods=4)
                forecasts.extend(forecast)

        # Generate summary
        summary = self._generate_summary(trends, forecasts, opportunities, threats)

        # Calculate overall confidence
        if trends:
            confidence = sum(t.r_squared for t in trends) / len(trends)
        else:
            confidence = 0.0

        return TrendAnalysis(
            company_name=self.company_name,
            analysis_date=utc_now(),
            trends=trends,
            forecasts=forecasts,
            signals=all_signals,
            opportunities=opportunities,
            threats=threats,
            summary=summary,
            confidence=confidence
        )

    def _analyze_metric_trend(self, metric: str, data: List[DataPoint]) -> Optional[Trend]:
        """Analyze trend for a single metric."""
        if len(data) < 2:
            return None

        values = [d.value for d in data]
        timestamps = [d.timestamp for d in data]

        # Calculate basic statistics
        start_value = values[0]
        end_value = values[-1]

        if start_value == 0:
            change_percent = 100 if end_value > 0 else 0
        else:
            change_percent = ((end_value - start_value) / abs(start_value)) * 100

        # Calculate linear regression for trend line
        slope, intercept, r_squared = self._linear_regression(
            list(range(len(values))), values
        )

        # Determine direction
        direction = self._classify_direction(change_percent, values)

        # Determine strength
        strength = self._classify_strength(r_squared, abs(change_percent))

        # Generate description
        description = self._generate_trend_description(
            metric, direction, change_percent, timestamps[0], timestamps[-1]
        )

        return Trend(
            metric=metric,
            direction=direction,
            strength=strength,
            start_date=timestamps[0],
            end_date=timestamps[-1],
            start_value=start_value,
            end_value=end_value,
            change_percent=change_percent,
            data_points=len(data),
            r_squared=r_squared,
            description=description
        )

    def _linear_regression(
        self,
        x: List[float],
        y: List[float]
    ) -> Tuple[float, float, float]:
        """Calculate linear regression and R-squared."""
        n = len(x)
        if n < 2:
            return 0, y[0] if y else 0, 0

        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi ** 2 for xi in x)

        denominator = n * sum_x2 - sum_x ** 2
        if denominator == 0:
            return 0, sum_y / n, 0

        slope = (n * sum_xy - sum_x * sum_y) / denominator
        intercept = (sum_y - slope * sum_x) / n

        # Calculate R-squared
        y_mean = sum_y / n
        ss_tot = sum((yi - y_mean) ** 2 for yi in y)
        ss_res = sum((yi - (slope * xi + intercept)) ** 2 for xi, yi in zip(x, y))

        if ss_tot == 0:
            r_squared = 1.0 if ss_res == 0 else 0.0
        else:
            r_squared = 1 - (ss_res / ss_tot)

        return slope, intercept, max(0, r_squared)

    def _classify_direction(
        self,
        change_percent: float,
        values: List[float]
    ) -> TrendDirection:
        """Classify trend direction."""
        # Check for volatility
        if len(values) > 2:
            mean = statistics.mean(values)
            if mean != 0:
                std_ratio = statistics.stdev(values) / abs(mean)
                if std_ratio > self.VOLATILITY_THRESHOLD:
                    return TrendDirection.VOLATILE

        # Classify by change
        if change_percent >= self.STRONG_TREND_THRESHOLD * 100:
            return TrendDirection.STRONG_UP
        elif change_percent >= self.TREND_THRESHOLD * 100:
            return TrendDirection.UP
        elif change_percent <= -self.STRONG_TREND_THRESHOLD * 100:
            return TrendDirection.STRONG_DOWN
        elif change_percent <= -self.TREND_THRESHOLD * 100:
            return TrendDirection.DOWN
        else:
            return TrendDirection.STABLE

    def _classify_strength(self, r_squared: float, change_magnitude: float) -> TrendStrength:
        """Classify trend strength."""
        if r_squared >= 0.9 and change_magnitude >= 10:
            return TrendStrength.VERY_STRONG
        elif r_squared >= 0.7 and change_magnitude >= 5:
            return TrendStrength.STRONG
        elif r_squared >= 0.5:
            return TrendStrength.MODERATE
        elif r_squared >= 0.3:
            return TrendStrength.WEAK
        else:
            return TrendStrength.UNCLEAR

    def _detect_signals(
        self,
        metric: str,
        data: List[DataPoint],
        trend: Trend
    ) -> List[Dict[str, Any]]:
        """Detect trend signals."""
        signals = []
        values = [d.value for d in data]

        if len(values) < 4:
            return signals

        # Check for acceleration/deceleration
        first_half_change = (values[len(values)//2] - values[0]) / max(abs(values[0]), 1)
        second_half_change = (values[-1] - values[len(values)//2]) / max(abs(values[len(values)//2]), 1)

        if second_half_change > first_half_change * 1.5:
            signals.append({
                "metric": metric,
                "signal": SignalType.ACCELERATION.value,
                "description": f"{metric} trend is accelerating"
            })
        elif second_half_change < first_half_change * 0.5:
            signals.append({
                "metric": metric,
                "signal": SignalType.DECELERATION.value,
                "description": f"{metric} trend is decelerating"
            })

        # Check for reversal (last few points opposite to overall trend)
        recent_change = (values[-1] - values[-3]) / max(abs(values[-3]), 1)
        if (trend.direction in [TrendDirection.UP, TrendDirection.STRONG_UP] and
            recent_change < -self.TREND_THRESHOLD):
            signals.append({
                "metric": metric,
                "signal": SignalType.REVERSAL.value,
                "description": f"{metric} may be reversing from uptrend"
            })
        elif (trend.direction in [TrendDirection.DOWN, TrendDirection.STRONG_DOWN] and
              recent_change > self.TREND_THRESHOLD):
            signals.append({
                "metric": metric,
                "signal": SignalType.REVERSAL.value,
                "description": f"{metric} may be reversing from downtrend"
            })

        return signals

    def _generate_forecast(
        self,
        metric: str,
        data: List[DataPoint],
        periods: int = 4
    ) -> List[Forecast]:
        """Generate forecasts for future periods."""
        forecasts = []
        values = [d.value for d in data]
        timestamps = [d.timestamp for d in data]

        if len(values) < 2:
            return forecasts

        # Calculate trend line
        x = list(range(len(values)))
        slope, intercept, r_squared = self._linear_regression(x, values)

        # Calculate standard error
        predicted = [slope * xi + intercept for xi in x]
        residuals = [yi - pred for yi, pred in zip(values, predicted)]
        if len(residuals) > 2:
            std_error = statistics.stdev(residuals)
        else:
            std_error = abs(values[-1] - values[0]) * 0.1

        # Determine period duration
        if len(timestamps) >= 2:
            avg_period = (timestamps[-1] - timestamps[0]) / (len(timestamps) - 1)
        else:
            avg_period = timedelta(days=90)  # Default to quarterly

        # Generate forecasts
        for i in range(1, periods + 1):
            future_x = len(values) - 1 + i
            predicted_value = slope * future_x + intercept

            # Confidence interval widens with time
            confidence_multiplier = 1.96 * (1 + i * 0.1)  # ~95% confidence
            margin = std_error * confidence_multiplier

            # Calculate period date
            period_date = timestamps[-1] + avg_period * i

            # Confidence decreases with forecast horizon
            forecast_confidence = max(
                r_squared * (1 - i * 0.1),
                0.1
            )

            forecasts.append(Forecast(
                metric=metric,
                period=period_date,
                predicted_value=predicted_value,
                confidence_lower=predicted_value - margin,
                confidence_upper=predicted_value + margin,
                confidence_level=forecast_confidence,
                method="linear_regression",
                assumptions=[
                    "Historical trend continues",
                    "No major market disruptions",
                    f"Based on {len(data)} historical data points"
                ]
            ))

        return forecasts

    def _generate_trend_description(
        self,
        metric: str,
        direction: TrendDirection,
        change_percent: float,
        start_date: datetime,
        end_date: datetime
    ) -> str:
        """Generate human-readable trend description."""
        direction_words = {
            TrendDirection.STRONG_UP: "showing strong growth",
            TrendDirection.UP: "increasing",
            TrendDirection.STABLE: "relatively stable",
            TrendDirection.DOWN: "declining",
            TrendDirection.STRONG_DOWN: "showing significant decline",
            TrendDirection.VOLATILE: "showing high volatility"
        }

        period = f"from {start_date.strftime('%b %Y')} to {end_date.strftime('%b %Y')}"
        direction_text = direction_words.get(direction, "changing")

        return f"{metric} is {direction_text} ({change_percent:+.1f}%) {period}"

    def _generate_summary(
        self,
        trends: List[Trend],
        forecasts: List[Forecast],
        opportunities: List[str],
        threats: List[str]
    ) -> str:
        """Generate executive summary of analysis."""
        if not trends:
            return "Insufficient data for trend analysis."

        # Count trend directions
        direction_counts = defaultdict(int)
        for trend in trends:
            direction_counts[trend.direction] += 1

        # Build summary
        summary_parts = []

        # Overall sentiment
        positive = direction_counts[TrendDirection.STRONG_UP] + direction_counts[TrendDirection.UP]
        negative = direction_counts[TrendDirection.STRONG_DOWN] + direction_counts[TrendDirection.DOWN]

        if positive > negative:
            summary_parts.append(f"Overall positive trends observed across {positive} metrics.")
        elif negative > positive:
            summary_parts.append(f"Caution: {negative} metrics showing declining trends.")
        else:
            summary_parts.append("Mixed trends across analyzed metrics.")

        # Highlight key findings
        strong_trends = [t for t in trends if t.strength in [TrendStrength.VERY_STRONG, TrendStrength.STRONG]]
        if strong_trends:
            summary_parts.append(
                f"{len(strong_trends)} strong trends identified: " +
                ", ".join(t.metric for t in strong_trends[:3])
            )

        # Opportunities and threats
        if opportunities:
            summary_parts.append(f"Key opportunities: {len(opportunities)}")
        if threats:
            summary_parts.append(f"Areas of concern: {len(threats)}")

        return " ".join(summary_parts)

    def forecast_single_metric(
        self,
        metric: str,
        periods: int = 4
    ) -> List[Forecast]:
        """Generate forecast for a single metric."""
        data = self.data_store.get(metric, [])
        if len(data) < self.min_data_points:
            return []
        return self._generate_forecast(metric, data, periods)

    def get_latest_values(self) -> Dict[str, float]:
        """Get the most recent value for each metric."""
        return {
            metric: data[-1].value if data else None
            for metric, data in self.data_store.items()
        }


async def trend_analyst_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """LangGraph node for trend analysis."""
    company_name = state.get("company_name", "Unknown")
    historical_data = state.get("historical_data", {})

    analyst = TrendAnalystAgent(company_name=company_name)

    # Load historical data
    for metric, data in historical_data.items():
        analyst.add_historical_data(metric, data)

    # Perform analysis
    analysis = analyst.analyze_trends()

    return {
        "trend_analysis": {
            "summary": analysis.summary,
            "confidence": analysis.confidence,
            "trends": [
                {
                    "metric": t.metric,
                    "direction": t.direction.value,
                    "strength": t.strength.value,
                    "change_percent": t.change_percent,
                    "description": t.description
                }
                for t in analysis.trends
            ],
            "forecasts": [
                {
                    "metric": f.metric,
                    "period": f.period.isoformat(),
                    "predicted_value": f.predicted_value,
                    "confidence_range": [f.confidence_lower, f.confidence_upper],
                    "confidence_level": f.confidence_level
                }
                for f in analysis.forecasts
            ],
            "opportunities": analysis.opportunities,
            "threats": analysis.threats,
            "signals": analysis.signals
        }
    }


def create_trend_analyst(company_name: str = "Unknown") -> TrendAnalystAgent:
    """Factory function to create a trend analyst."""
    return TrendAnalystAgent(company_name=company_name)
