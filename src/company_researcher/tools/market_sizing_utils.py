"""
Market Sizing and Analysis Utilities (Phase 8).

Provides frameworks and calculations for:
- TAM/SAM/SOM market sizing
- Market penetration analysis
- Growth potential estimation
- Industry trend classification
- Competitive dynamics assessment
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum


# ==============================================================================
# Enums and Constants
# ==============================================================================

class MarketTrend(str, Enum):
    """Market trend direction classification."""
    GROWING = "GROWING"          # Positive growth trajectory
    DECLINING = "DECLINING"      # Negative growth trajectory
    STABLE = "STABLE"            # Flat growth (~0-5%)
    EMERGING = "EMERGING"        # New market, high growth potential
    MATURE = "MATURE"            # Established market, low growth
    DISRUPTING = "DISRUPTING"    # Undergoing major transformation


class CompetitiveIntensity(str, Enum):
    """Competitive intensity levels."""
    LOW = "LOW"                  # Few competitors, high barriers
    MODERATE = "MODERATE"        # Balanced competition
    HIGH = "HIGH"                # Many competitors, price pressure
    INTENSE = "INTENSE"          # Highly fragmented, low margins


# ==============================================================================
# TAM/SAM/SOM Calculations
# ==============================================================================

def calculate_tam(
    total_potential_customers: float,
    average_revenue_per_customer: float
) -> float:
    """
    Calculate Total Addressable Market (TAM).

    TAM = Total number of potential customers × Average revenue per customer

    Args:
        total_potential_customers: Total number of potential customers globally
        average_revenue_per_customer: Average annual revenue per customer

    Returns:
        TAM in same currency units as average revenue

    Example:
        >>> # Electric vehicle market
        >>> calculate_tam(
        ...     total_potential_customers=1_400_000_000,  # Global car buyers
        ...     average_revenue_per_customer=50_000       # Average car price
        ... )
        70000000000000.0  # $70 trillion
    """
    return total_potential_customers * average_revenue_per_customer


def calculate_sam(
    tam: float,
    addressable_percentage: float
) -> float:
    """
    Calculate Serviceable Available Market (SAM).

    SAM = TAM × Percentage of market that product/service can address

    Args:
        tam: Total Addressable Market
        addressable_percentage: Percentage of TAM that can be realistically addressed (0-100)

    Returns:
        SAM in same units as TAM

    Example:
        >>> # EV market (subset of total automotive)
        >>> calculate_sam(
        ...     tam=70_000_000_000_000,  # Total automotive
        ...     addressable_percentage=15  # 15% EVs
        ... )
        10500000000000.0  # $10.5 trillion
    """
    return tam * (addressable_percentage / 100)


def calculate_som(
    sam: float,
    market_share_percentage: float
) -> float:
    """
    Calculate Serviceable Obtainable Market (SOM).

    SOM = SAM × Realistic market share percentage

    Args:
        sam: Serviceable Available Market
        market_share_percentage: Realistic market share company can capture (0-100)

    Returns:
        SOM in same units as SAM

    Example:
        >>> # Tesla's addressable market
        >>> calculate_som(
        ...     sam=10_500_000_000_000,  # EV market
        ...     market_share_percentage=2  # 2% market share
        ... )
        210000000000.0  # $210 billion
    """
    return sam * (market_share_percentage / 100)


def calculate_market_sizing(
    total_potential_customers: float,
    average_revenue_per_customer: float,
    addressable_percentage: float,
    market_share_percentage: float
) -> Dict[str, float]:
    """
    Calculate complete TAM/SAM/SOM market sizing.

    Args:
        total_potential_customers: Total global potential customers
        average_revenue_per_customer: Average revenue per customer
        addressable_percentage: % of TAM addressable (0-100)
        market_share_percentage: Realistic market share % (0-100)

    Returns:
        Dictionary with TAM, SAM, SOM values
    """
    tam = calculate_tam(total_potential_customers, average_revenue_per_customer)
    sam = calculate_sam(tam, addressable_percentage)
    som = calculate_som(sam, market_share_percentage)

    return {
        "tam": tam,
        "sam": sam,
        "som": som,
        "addressable_percentage": addressable_percentage,
        "market_share_percentage": market_share_percentage
    }


# ==============================================================================
# Market Penetration Analysis
# ==============================================================================

def calculate_penetration_rate(
    current_customers: float,
    total_addressable_customers: float
) -> float:
    """
    Calculate market penetration rate.

    Penetration Rate = (Current Customers / Total Addressable Customers) × 100

    Args:
        current_customers: Current number of customers
        total_addressable_customers: Total addressable customer base

    Returns:
        Penetration rate as percentage

    Example:
        >>> calculate_penetration_rate(
        ...     current_customers=5_000_000,      # 5M Tesla customers
        ...     total_addressable_customers=250_000_000  # 250M EV buyers
        ... )
        2.0  # 2% penetration
    """
    if total_addressable_customers == 0:
        return 0.0

    penetration = (current_customers / total_addressable_customers) * 100
    return round(penetration, 2)


def calculate_growth_potential(
    current_market_size: float,
    projected_market_size: float,
    years: int
) -> Dict[str, float]:
    """
    Calculate market growth potential.

    Args:
        current_market_size: Current market size
        projected_market_size: Projected future market size
        years: Number of years for projection

    Returns:
        Dictionary with growth metrics:
        - total_growth: Total growth amount
        - growth_rate: Percentage growth
        - cagr: Compound annual growth rate
    """
    if current_market_size == 0:
        return {
            "total_growth": 0.0,
            "growth_rate": 0.0,
            "cagr": 0.0
        }

    total_growth = projected_market_size - current_market_size
    growth_rate = (total_growth / current_market_size) * 100

    # Calculate CAGR
    if years > 0:
        cagr = (((projected_market_size / current_market_size) ** (1 / years)) - 1) * 100
    else:
        cagr = 0.0

    return {
        "total_growth": round(total_growth, 2),
        "growth_rate": round(growth_rate, 2),
        "cagr": round(cagr, 2)
    }


# ==============================================================================
# Industry Trend Analysis
# ==============================================================================

def classify_trend(
    historical_growth_rate: float,
    market_maturity: str = "mature"
) -> MarketTrend:
    """
    Classify market trend based on growth rate and maturity.

    Args:
        historical_growth_rate: Historical CAGR percentage
        market_maturity: Market maturity stage ("emerging", "growth", "mature", "decline")

    Returns:
        MarketTrend classification

    Classification:
    - EMERGING: >30% growth or new market
    - GROWING: 10-30% growth in mature market, >15% in established
    - STABLE: 0-10% growth
    - DECLINING: Negative growth
    - DISRUPTING: Major technology/business model shift
    """
    if market_maturity.lower() == "emerging":
        return MarketTrend.EMERGING

    if historical_growth_rate < 0:
        return MarketTrend.DECLINING
    elif historical_growth_rate < 5:
        return MarketTrend.STABLE
    elif historical_growth_rate < 10:
        return MarketTrend.MATURE if market_maturity.lower() == "mature" else MarketTrend.GROWING
    elif historical_growth_rate < 30:
        return MarketTrend.GROWING
    else:
        return MarketTrend.EMERGING


def analyze_industry_trend(
    historical_data: List[Tuple[str, float]],
    market_maturity: str = "mature"
) -> Dict[str, any]:
    """
    Analyze industry trend from historical data.

    Args:
        historical_data: List of (year, market_size) tuples
        market_maturity: Market maturity stage

    Returns:
        Dictionary with trend analysis:
        - trend: MarketTrend classification
        - cagr: Compound annual growth rate
        - direction: "accelerating", "stable", or "decelerating"
        - outlook: Qualitative assessment
    """
    if len(historical_data) < 2:
        return {
            "available": False,
            "reason": "Insufficient historical data"
        }

    # Sort by year
    sorted_data = sorted(historical_data, key=lambda x: x[0])

    # Calculate CAGR
    years = len(sorted_data) - 1
    initial_size = sorted_data[0][1]
    final_size = sorted_data[-1][1]

    if initial_size > 0 and years > 0:
        cagr = (((final_size / initial_size) ** (1 / years)) - 1) * 100
    else:
        cagr = 0.0

    # Classify trend
    trend = classify_trend(cagr, market_maturity)

    # Analyze direction (acceleration/deceleration)
    if len(sorted_data) >= 3:
        # Compare recent growth vs earlier growth
        mid_point = len(sorted_data) // 2
        early_data = sorted_data[:mid_point + 1]
        recent_data = sorted_data[mid_point:]

        early_cagr = (((early_data[-1][1] / early_data[0][1]) ** (1 / len(early_data))) - 1) * 100
        recent_cagr = (((recent_data[-1][1] / recent_data[0][1]) ** (1 / len(recent_data))) - 1) * 100

        if abs(recent_cagr - early_cagr) < 3:
            direction = "stable"
        elif recent_cagr > early_cagr:
            direction = "accelerating"
        else:
            direction = "decelerating"
    else:
        direction = "insufficient data"

    # Generate outlook
    outlook = generate_outlook(trend, cagr, direction)

    return {
        "available": True,
        "trend": trend.value,
        "cagr": round(cagr, 2),
        "direction": direction,
        "outlook": outlook,
        "historical_data": sorted_data
    }


def generate_outlook(
    trend: MarketTrend,
    cagr: float,
    direction: str
) -> str:
    """Generate qualitative market outlook."""
    if trend == MarketTrend.EMERGING:
        return "High-growth emerging market with significant expansion potential"
    elif trend == MarketTrend.GROWING:
        if direction == "accelerating":
            return f"Growing market ({cagr:.1f}% CAGR) with accelerating momentum"
        else:
            return f"Steady growth market ({cagr:.1f}% CAGR)"
    elif trend == MarketTrend.STABLE:
        return "Mature, stable market with limited growth opportunities"
    elif trend == MarketTrend.DECLINING:
        return f"Declining market ({cagr:.1f}% CAGR) - consider pivoting"
    else:
        return "Market undergoing transformation"


# ==============================================================================
# Competitive Analysis
# ==============================================================================

def assess_competitive_intensity(
    number_of_competitors: int,
    market_concentration_hhi: Optional[float] = None,
    barriers_to_entry: str = "moderate"
) -> CompetitiveIntensity:
    """
    Assess competitive intensity of market.

    Args:
        number_of_competitors: Number of significant competitors
        market_concentration_hhi: Herfindahl-Hirschman Index (0-10000)
            - <1500: Unconcentrated (low intensity)
            - 1500-2500: Moderate concentration
            - >2500: High concentration (high intensity if many players)
        barriers_to_entry: "low", "moderate", "high"

    Returns:
        CompetitiveIntensity assessment

    HHI Calculation:
        HHI = sum of (market_share_i)^2 for all competitors
        - 10000 = monopoly
        - 2500+ = concentrated
        - <1500 = competitive
    """
    # If HHI provided, use it
    if market_concentration_hhi is not None:
        if market_concentration_hhi > 5000:
            # High concentration (monopoly/duopoly)
            return CompetitiveIntensity.LOW
        elif market_concentration_hhi > 2500:
            # Moderate concentration
            return CompetitiveIntensity.MODERATE
        elif market_concentration_hhi > 1500:
            # Competitive market
            return CompetitiveIntensity.HIGH
        else:
            # Highly fragmented
            return CompetitiveIntensity.INTENSE

    # Otherwise, use competitor count and barriers
    if barriers_to_entry == "high":
        if number_of_competitors < 5:
            return CompetitiveIntensity.LOW
        elif number_of_competitors < 15:
            return CompetitiveIntensity.MODERATE
        else:
            return CompetitiveIntensity.HIGH

    elif barriers_to_entry == "moderate":
        if number_of_competitors < 10:
            return CompetitiveIntensity.MODERATE
        elif number_of_competitors < 25:
            return CompetitiveIntensity.HIGH
        else:
            return CompetitiveIntensity.INTENSE

    else:  # low barriers
        if number_of_competitors < 15:
            return CompetitiveIntensity.HIGH
        else:
            return CompetitiveIntensity.INTENSE


def calculate_market_share_distribution(
    competitor_revenues: Dict[str, float]
) -> Dict[str, any]:
    """
    Calculate market share distribution and concentration.

    Args:
        competitor_revenues: Dictionary of {company_name: revenue}

    Returns:
        Dictionary with:
        - market_shares: {company: percentage}
        - hhi: Herfindahl-Hirschman Index
        - top_4_concentration: CR4 ratio (top 4 market share)
        - market_leader: Company with highest share
    """
    if not competitor_revenues:
        return {"available": False}

    total_revenue = sum(competitor_revenues.values())

    if total_revenue == 0:
        return {"available": False}

    # Calculate market shares
    market_shares = {
        company: (revenue / total_revenue) * 100
        for company, revenue in competitor_revenues.items()
    }

    # Calculate HHI
    hhi = sum(share ** 2 for share in market_shares.values())

    # Calculate CR4 (top 4 concentration)
    top_4_shares = sorted(market_shares.values(), reverse=True)[:4]
    cr4 = sum(top_4_shares)

    # Identify market leader
    market_leader = max(market_shares, key=market_shares.get)

    return {
        "available": True,
        "market_shares": {k: round(v, 2) for k, v in market_shares.items()},
        "hhi": round(hhi, 2),
        "top_4_concentration": round(cr4, 2),
        "market_leader": market_leader,
        "market_leader_share": round(market_shares[market_leader], 2)
    }


# ==============================================================================
# Helper Functions
# ==============================================================================

def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format currency amount for display.

    Args:
        amount: Amount to format
        currency: Currency code (USD, EUR, etc.)

    Returns:
        Formatted string (e.g., "$1.5T", "$250M", "$50K")
    """
    if currency == "USD":
        symbol = "$"
    elif currency == "EUR":
        symbol = "€"
    elif currency == "GBP":
        symbol = "£"
    else:
        symbol = currency + " "

    # Determine scale
    if amount >= 1_000_000_000_000:  # Trillions
        return f"{symbol}{amount / 1_000_000_000_000:.1f}T"
    elif amount >= 1_000_000_000:  # Billions
        return f"{symbol}{amount / 1_000_000_000:.1f}B"
    elif amount >= 1_000_000:  # Millions
        return f"{symbol}{amount / 1_000_000:.1f}M"
    elif amount >= 1_000:  # Thousands
        return f"{symbol}{amount / 1_000:.1f}K"
    else:
        return f"{symbol}{amount:.0f}"
