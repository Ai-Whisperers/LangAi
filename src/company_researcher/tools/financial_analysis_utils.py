"""
Financial Analysis Utilities (Phase 7).

Provides calculation functions for financial metrics and analysis:
- Revenue trends and growth rates
- Profitability margins
- Financial health ratios
- Valuation metrics
- Trend analysis
"""

from typing import List, Tuple, Dict, Optional


# ==============================================================================
# Revenue Analysis
# ==============================================================================

def calculate_yoy_growth(current: float, previous: float) -> float:
    """
    Calculate year-over-year growth rate.

    Args:
        current: Current period value
        previous: Previous period value

    Returns:
        Growth rate as percentage (e.g., 25.5 for 25.5% growth)
    """
    if previous == 0:
        return 0.0

    growth = ((current - previous) / previous) * 100
    return round(growth, 2)


def calculate_cagr(
    initial_value: float,
    final_value: float,
    num_years: int
) -> float:
    """
    Calculate Compound Annual Growth Rate.

    Args:
        initial_value: Starting value
        final_value: Ending value
        num_years: Number of years

    Returns:
        CAGR as percentage
    """
    if initial_value == 0 or num_years == 0:
        return 0.0

    cagr = (((final_value / initial_value) ** (1 / num_years)) - 1) * 100
    return round(cagr, 2)


def analyze_revenue_trend(
    revenue_history: List[Tuple[str, float]]
) -> Dict[str, any]:
    """
    Analyze revenue trend over time.

    Args:
        revenue_history: List of (period, revenue) tuples
          E.g., [("2021", 50.0), ("2022", 65.0), ("2023", 81.5)]

    Returns:
        Dictionary with trend analysis:
        - yoy_growth: List of year-over-year growth rates
        - average_growth: Average YoY growth
        - cagr: CAGR over the period
        - trend: "accelerating", "decelerating", or "stable"
    """
    if len(revenue_history) < 2:
        return {
            "available": False,
            "reason": "Insufficient data (need at least 2 periods)"
        }

    # Sort by period
    sorted_history = sorted(revenue_history, key=lambda x: x[0])

    # Calculate YoY growth for each period
    yoy_growth = []
    for i in range(1, len(sorted_history)):
        prev_revenue = sorted_history[i-1][1]
        curr_revenue = sorted_history[i][1]
        growth = calculate_yoy_growth(curr_revenue, prev_revenue)
        yoy_growth.append({
            "period": sorted_history[i][0],
            "growth": growth
        })

    # Calculate CAGR
    num_years = len(sorted_history) - 1
    initial_revenue = sorted_history[0][1]
    final_revenue = sorted_history[-1][1]
    cagr = calculate_cagr(initial_revenue, final_revenue, num_years)

    # Determine trend (accelerating vs decelerating)
    if len(yoy_growth) >= 2:
        recent_growth = yoy_growth[-1]["growth"]
        previous_growth = yoy_growth[-2]["growth"]

        if abs(recent_growth - previous_growth) < 5:
            trend = "stable"
        elif recent_growth > previous_growth:
            trend = "accelerating"
        else:
            trend = "decelerating"
    else:
        trend = "insufficient data"

    return {
        "available": True,
        "revenue_history": sorted_history,
        "yoy_growth": yoy_growth,
        "average_growth": round(sum(g["growth"] for g in yoy_growth) / len(yoy_growth), 2),
        "cagr": cagr,
        "trend": trend
    }


# ==============================================================================
# Profitability Analysis
# ==============================================================================

def calculate_gross_margin(revenue: float, cogs: float) -> float:
    """
    Calculate gross profit margin.

    Args:
        revenue: Total revenue
        cogs: Cost of goods sold

    Returns:
        Gross margin as percentage
    """
    if revenue == 0:
        return 0.0

    gross_profit = revenue - cogs
    margin = (gross_profit / revenue) * 100
    return round(margin, 2)


def calculate_operating_margin(revenue: float, operating_income: float) -> float:
    """
    Calculate operating profit margin.

    Args:
        revenue: Total revenue
        operating_income: Operating income (EBIT)

    Returns:
        Operating margin as percentage
    """
    if revenue == 0:
        return 0.0

    margin = (operating_income / revenue) * 100
    return round(margin, 2)


def calculate_net_margin(revenue: float, net_income: float) -> float:
    """
    Calculate net profit margin.

    Args:
        revenue: Total revenue
        net_income: Net income

    Returns:
        Net margin as percentage
    """
    if revenue == 0:
        return 0.0

    margin = (net_income / revenue) * 100
    return round(margin, 2)


def calculate_ebitda_margin(revenue: float, ebitda: float) -> float:
    """
    Calculate EBITDA margin.

    Args:
        revenue: Total revenue
        ebitda: EBITDA (Earnings Before Interest, Taxes, Depreciation, Amortization)

    Returns:
        EBITDA margin as percentage
    """
    if revenue == 0:
        return 0.0

    margin = (ebitda / revenue) * 100
    return round(margin, 2)


def analyze_profitability(
    revenue: float,
    gross_profit: Optional[float] = None,
    operating_income: Optional[float] = None,
    net_income: Optional[float] = None,
    ebitda: Optional[float] = None,
    cogs: Optional[float] = None
) -> Dict[str, any]:
    """
    Comprehensive profitability analysis.

    Args:
        revenue: Total revenue
        gross_profit: Gross profit (or will calculate from cogs)
        operating_income: Operating income (EBIT)
        net_income: Net income
        ebitda: EBITDA
        cogs: Cost of goods sold (if gross_profit not provided)

    Returns:
        Dictionary with all calculated margins
    """
    profitability = {
        "revenue": revenue,
        "gross_margin": None,
        "operating_margin": None,
        "net_margin": None,
        "ebitda_margin": None
    }

    # Gross margin
    if gross_profit is not None:
        profitability["gross_margin"] = calculate_gross_margin(
            revenue, revenue - gross_profit
        )
    elif cogs is not None:
        profitability["gross_margin"] = calculate_gross_margin(revenue, cogs)

    # Operating margin
    if operating_income is not None:
        profitability["operating_margin"] = calculate_operating_margin(
            revenue, operating_income
        )

    # Net margin
    if net_income is not None:
        profitability["net_margin"] = calculate_net_margin(revenue, net_income)

    # EBITDA margin
    if ebitda is not None:
        profitability["ebitda_margin"] = calculate_ebitda_margin(revenue, ebitda)

    return profitability


# ==============================================================================
# Financial Health Ratios
# ==============================================================================

def calculate_debt_to_equity(total_debt: float, total_equity: float) -> float:
    """
    Calculate debt-to-equity ratio.

    Args:
        total_debt: Total debt
        total_equity: Total shareholder equity

    Returns:
        Debt-to-equity ratio
    """
    if total_equity == 0:
        return float('inf')

    ratio = total_debt / total_equity
    return round(ratio, 2)


def calculate_current_ratio(current_assets: float, current_liabilities: float) -> float:
    """
    Calculate current ratio (liquidity measure).

    Args:
        current_assets: Total current assets
        current_liabilities: Total current liabilities

    Returns:
        Current ratio
    """
    if current_liabilities == 0:
        return float('inf')

    ratio = current_assets / current_liabilities
    return round(ratio, 2)


def calculate_quick_ratio(
    current_assets: float,
    inventory: float,
    current_liabilities: float
) -> float:
    """
    Calculate quick ratio (acid-test ratio).

    Args:
        current_assets: Total current assets
        inventory: Inventory value
        current_liabilities: Total current liabilities

    Returns:
        Quick ratio
    """
    if current_liabilities == 0:
        return float('inf')

    quick_assets = current_assets - inventory
    ratio = quick_assets / current_liabilities
    return round(ratio, 2)


def calculate_free_cash_flow(
    operating_cash_flow: float,
    capital_expenditures: float
) -> float:
    """
    Calculate free cash flow.

    Args:
        operating_cash_flow: Cash flow from operations
        capital_expenditures: Capital expenditures (CapEx)

    Returns:
        Free cash flow
    """
    fcf = operating_cash_flow - capital_expenditures
    return round(fcf, 2)


def analyze_financial_health(
    cash: float,
    total_debt: float,
    total_equity: float,
    current_assets: float,
    current_liabilities: float,
    inventory: Optional[float] = None,
    operating_cash_flow: Optional[float] = None,
    capex: Optional[float] = None
) -> Dict[str, any]:
    """
    Comprehensive financial health analysis.

    Args:
        cash: Cash and cash equivalents
        total_debt: Total debt
        total_equity: Total shareholder equity
        current_assets: Current assets
        current_liabilities: Current liabilities
        inventory: Inventory value (for quick ratio)
        operating_cash_flow: Operating cash flow
        capex: Capital expenditures

    Returns:
        Dictionary with all health metrics
    """
    health = {
        "cash": cash,
        "total_debt": total_debt,
        "debt_to_equity": calculate_debt_to_equity(total_debt, total_equity),
        "current_ratio": calculate_current_ratio(current_assets, current_liabilities),
        "quick_ratio": None,
        "free_cash_flow": None,
        "assessment": None
    }

    # Quick ratio
    if inventory is not None:
        health["quick_ratio"] = calculate_quick_ratio(
            current_assets, inventory, current_liabilities
        )

    # Free cash flow
    if operating_cash_flow is not None and capex is not None:
        health["free_cash_flow"] = calculate_free_cash_flow(
            operating_cash_flow, capex
        )

    # Overall assessment
    health["assessment"] = assess_financial_health(health)

    return health


def assess_financial_health(health_metrics: Dict) -> str:
    """
    Assess overall financial health based on metrics.

    Args:
        health_metrics: Dictionary of financial health metrics

    Returns:
        Assessment: "Strong", "Healthy", "Moderate", "Weak", or "Concerning"
    """
    score = 0
    max_score = 0

    # Debt-to-equity (lower is better)
    if health_metrics.get("debt_to_equity") is not None:
        max_score += 2
        ratio = health_metrics["debt_to_equity"]
        if ratio < 0.3:
            score += 2  # Very low debt
        elif ratio < 0.7:
            score += 1  # Moderate debt
        # else: 0 points (high debt)

    # Current ratio (>1.0 is healthy, >2.0 is strong)
    if health_metrics.get("current_ratio") is not None:
        max_score += 2
        ratio = health_metrics["current_ratio"]
        if ratio >= 2.0:
            score += 2  # Strong liquidity
        elif ratio >= 1.0:
            score += 1  # Adequate liquidity
        # else: 0 points (liquidity concern)

    # Free cash flow (positive is good)
    if health_metrics.get("free_cash_flow") is not None:
        max_score += 1
        if health_metrics["free_cash_flow"] > 0:
            score += 1

    # Calculate percentage
    if max_score == 0:
        return "Insufficient data"

    percentage = (score / max_score) * 100

    if percentage >= 80:
        return "Strong"
    elif percentage >= 60:
        return "Healthy"
    elif percentage >= 40:
        return "Moderate"
    elif percentage >= 20:
        return "Weak"
    else:
        return "Concerning"


# ==============================================================================
# Valuation Metrics
# ==============================================================================

def calculate_pe_ratio(stock_price: float, earnings_per_share: float) -> float:
    """
    Calculate Price-to-Earnings ratio.

    Args:
        stock_price: Current stock price
        earnings_per_share: EPS

    Returns:
        P/E ratio
    """
    if earnings_per_share == 0:
        return float('inf')

    pe = stock_price / earnings_per_share
    return round(pe, 2)


def calculate_pb_ratio(stock_price: float, book_value_per_share: float) -> float:
    """
    Calculate Price-to-Book ratio.

    Args:
        stock_price: Current stock price
        book_value_per_share: Book value per share

    Returns:
        P/B ratio
    """
    if book_value_per_share == 0:
        return float('inf')

    pb = stock_price / book_value_per_share
    return round(pb, 2)


def calculate_ev_to_ebitda(
    market_cap: float,
    total_debt: float,
    cash: float,
    ebitda: float
) -> float:
    """
    Calculate EV/EBITDA ratio.

    Args:
        market_cap: Market capitalization
        total_debt: Total debt
        cash: Cash and cash equivalents
        ebitda: EBITDA

    Returns:
        EV/EBITDA ratio
    """
    if ebitda == 0:
        return float('inf')

    enterprise_value = market_cap + total_debt - cash
    ev_ebitda = enterprise_value / ebitda
    return round(ev_ebitda, 2)
