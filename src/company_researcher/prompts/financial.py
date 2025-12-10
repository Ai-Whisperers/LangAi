"""
Financial analysis prompts for investment and financial evaluation.

This module contains prompts used for:
- Financial data extraction
- Enhanced financial analysis
- Investment due diligence
"""

# ============================================================================
# Financial Analysis Prompts
# ============================================================================

FINANCIAL_ANALYSIS_PROMPT = """You are a financial analyst reviewing search results about a company.

Company: {company_name}

Search Results:
{search_results}

Task: Extract ALL financial data and metrics from these search results.

Focus on:
1. **Revenue**: Annual revenue, quarterly revenue, revenue growth
2. **Funding**: Total funding raised, valuation, recent rounds
3. **Profitability**: Operating income, net income, profit margins
4. **Market Value**: Market cap (if public), valuation (if private)
5. **Financial Metrics**: R&D spending, cash flow, any other metrics

Requirements:
- Be specific with numbers and dates
- Include sources for each data point
- Note if data is missing or unavailable
- Format as bullet points

Output format:
- Revenue: [specific figures with years]
- Funding: [total raised, rounds, investors if mentioned]
- Valuation/Market Cap: [amount and date]
- Profitability: [operating income, net income, etc.]
- Other Metrics: [any additional financial data]

Extract the financial data now:"""


ENHANCED_FINANCIAL_PROMPT = """You are an expert financial analyst with access to comprehensive financial data.

Company: {company_name}

**FINANCIAL DATA:**
{financial_data}

**SEARCH RESULTS:**
{search_results}

**TASK:**
Provide a comprehensive financial analysis combining both financial data and search results.

**STRUCTURE YOUR ANALYSIS:**

### 1. Revenue Analysis
- Historical revenue figures (cite specific years)
- Year-over-year growth rates
- Revenue breakdown by segment/region if available
- Revenue growth trends and projections

### 2. Profitability Analysis
- Gross margin trends
- Operating margin trends
- Net profit margin
- EBITDA if available
- Comparison to industry averages

### 3. Financial Health Indicators
**Balance Sheet Strength:**
- Current ratio (Current Assets / Current Liabilities)
- Debt-to-equity ratio
- Total debt levels
- Cash position

**Cash Flow Analysis:**
- Operating cash flow trends
- Free cash flow
- Capital expenditure patterns
- Dividend policy (if applicable)

### 4. Valuation Assessment
**For Public Companies:**
- Current market cap
- P/E ratio vs industry average
- P/S ratio
- EV/EBITDA if available

**For Private Companies:**
- Last known valuation
- Funding rounds and valuations over time
- Comparable company analysis

### 5. Risk Assessment
- Financial risks identified
- Debt maturity concerns
- Currency/market exposure
- Operational risks with financial impact

### 6. Financial Summary
Provide 3-4 key financial takeaways:
- Financial health rating (STRONG/MODERATE/WEAK)
- Growth trajectory
- Risk level
- Investment considerations

**REQUIREMENTS:**
- Cite specific numbers with dates/sources
- Note any data gaps or uncertainties
- Be objective and balanced
- Highlight both strengths and concerns

Provide your comprehensive financial analysis:"""


INVESTMENT_ANALYSIS_PROMPT = """You are an expert investment analyst performing due diligence on a company.

Company: {company_name}

**AVAILABLE RESEARCH DATA:**
{research_data}

**TASK:**
Provide a comprehensive investment analysis suitable for institutional investors.

**STRUCTURE YOUR ANALYSIS:**

### 1. Investment Thesis
Provide a clear, concise investment thesis (2-3 sentences) answering:
- What does this company do well?
- Why might it be a good/bad investment?
- What is the primary value driver?

### 2. Business Quality Assessment

**Competitive Moat Analysis:**
Rate moat strength: [WIDE/NARROW/NONE]
- Brand value
- Network effects
- Cost advantages
- Switching costs
- Intangible assets (patents, licenses)

**Management Quality:**
- Track record
- Capital allocation history
- Insider ownership
- Corporate governance

**Business Model:**
- Recurring revenue percentage
- Customer concentration risk
- Pricing power evidence

### 3. Growth Assessment

**Historical Growth:**
- Revenue CAGR (3-5 years)
- Earnings/profit growth
- Market share gains

**Future Growth Drivers:**
- New products/markets
- Geographic expansion
- M&A strategy
- Industry tailwinds

**Growth Stage:** [EARLY/GROWTH/MATURE/DECLINING]

### 4. Risk Analysis

**Business Risks:**
- Competition threats
- Technology disruption
- Regulatory risks
- Customer concentration

**Financial Risks:**
- Leverage concerns
- Cash flow sustainability
- Capital intensity

**Risk Level:** [LOW/MODERATE/HIGH/CRITICAL]

### 5. Valuation Assessment

**Current Valuation:**
- Key multiples (P/E, P/S, EV/EBITDA)
- Comparison to peers
- Historical valuation range

**Valuation Verdict:**
- Appears [UNDERVALUED/FAIRLY VALUED/OVERVALUED]
- Supporting rationale

### 6. Investment Recommendation

**Rating:** [STRONG BUY/BUY/HOLD/SELL/STRONG SELL]

**Key Factors:**
- Top 3 reasons supporting this rating
- Key catalysts to watch
- Main risks that could change thesis

### 7. Monitoring Checklist
List 3-5 specific metrics/events to monitor

**REQUIREMENTS:**
- Be balanced and objective
- Support opinions with data
- Acknowledge uncertainties
- Provide actionable conclusions

Provide your investment analysis:"""
