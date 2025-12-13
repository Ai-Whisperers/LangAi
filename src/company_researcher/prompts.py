"""
Prompt templates for the Company Researcher workflow.

This module contains all prompts used by the LLM at different stages
of the research workflow.
"""


# ============================================================================
# Query Generation
# ============================================================================

GENERATE_QUERIES_PROMPT = """You are a research assistant tasked with gathering comprehensive information about a company.

Company: {company_name}

Generate {num_queries} specific, targeted search queries that will help research this company thoroughly.

IMPORTANT INSTRUCTIONS:
1. If this appears to be a LATAM company (Brazilian, Mexican, etc.), include queries in BOTH English AND the local language
2. For Brazilian companies: include Portuguese queries ("receita", "lucro", "empresa")
3. For Spanish-speaking countries: include Spanish queries ("ingresos", "empleados", "empresa")
4. Include the stock ticker if you know it (e.g., GGBR4, AMX, COPEL)
5. If this might be a subsidiary, search for the parent company too

Your queries should cover:
1. Company overview and background
2. Financial performance and metrics (annual report, earnings)
3. Products and services
4. Market position and competitors
5. Recent news and developments
6. Leadership team and executives

Requirements:
- Each query should be specific and focused
- Queries should complement each other (no redundancy)
- Use exact company name in queries
- Keep queries concise (3-10 words each)
- For non-US companies, mix English and local language queries

Output format:
Return ONLY a JSON array of query strings, nothing else.

Example output for a Brazilian company:
["Gerdau empresa overview", "Gerdau receita 2024", "Gerdau GGBR4 stock price", "Gerdau revenue annual report", "Gerdau competitors ArcelorMittal"]

Example output for a Mexican company:
["América Móvil empresa historia", "América Móvil ingresos 2024", "AMX stock telcel Claro", "América Móvil competitors", "América Móvil Carlos Slim"]

Now generate {num_queries} queries for {company_name}:"""


# ============================================================================
# Analysis and Summarization
# ============================================================================

ANALYZE_RESULTS_PROMPT = """You are an expert research analyst reviewing web search results about a company.

Company: {company_name}

Search Results:
{search_results}

Task: Perform THOROUGH analysis of these search results. Extract EVERY piece of useful information.

CRITICAL INSTRUCTIONS:
1. Process content in ANY language (English, Spanish, Portuguese, etc.)
2. Translate key findings to English while preserving original terms for accuracy
3. Extract ALL numerical data: revenue, employees, funding, market share, etc.
4. Note the SOURCE and YEAR for each data point when available
5. For LATAM companies, pay special attention to:
   - "receita" / "ingresos" / "faturamento" = revenue
   - "lucro" / "beneficio" = profit
   - "funcionários" / "empleados" = employees
   - Stock tickers on B3, BMV, BVL, etc.

Create comprehensive notes covering:

## 1. Company Identity
- Official company name and any DBA/trade names
- Legal structure (S.A., Ltda, Inc, etc.)
- Parent company (if subsidiary)
- Country and headquarters location
- Year founded
- Stock ticker and exchange (if public)

## 2. Financial Data (EXTRACT ALL NUMBERS FOUND)
- Annual revenue (specify year, currency)
- Net income/profit
- EBITDA
- Market capitalization
- Total funding raised
- Latest funding round details
- Debt levels
- Any other financial metrics mentioned

## 3. Operational Data
- Employee count
- Number of locations/offices
- Countries of operation
- Production capacity
- Customer count (if B2B)

## 4. Products & Services
- List all products/services mentioned
- Key product lines
- Technology/platform details
- Patents or IP mentioned

## 5. Market Position
- Market share percentages
- Industry ranking
- Key competitors mentioned
- Competitive advantages

## 6. Recent Developments (last 2 years)
- News and announcements
- Leadership changes
- Acquisitions or partnerships
- Strategic initiatives
- Challenges or controversies

## 7. Regulatory Environment (CRITICAL for LATAM)
- **Regulatory Body**: Name of telecom/industry regulator
  - Paraguay: CONATEL
  - Brazil: ANATEL
  - Mexico: IFT
  - Colombia: CRC
  - Chile: SUBTEL
- **License Status**: Any spectrum or operating licenses mentioned
- **Regulatory Actions**: Fines, investigations, compliance issues
- **Industry Rules**: Key regulations affecting the company

## 8. Data Confidence Assessment
- List which data points are well-sourced
- Note any conflicting information
- Identify gaps in the research

## CRITICAL DATA CHECKLIST (Verify these are extracted if present):
- [ ] CEO/General Manager name
- [ ] Exact subscriber/customer count
- [ ] Market share percentage
- [ ] Annual revenue with year
- [ ] Employee count
- [ ] Competitor names with their market shares
- [ ] Regulatory body overseeing the company

Requirements:
- Be exhaustive - extract EVERY data point
- Cite the source for significant facts
- Note the language of original source
- Flag any conflicting information
- Be factual and objective
- PRIORITIZE: CEO name, subscriber count, market share, revenue

Format your analysis as detailed bullet points with section headers."""


# ============================================================================
# Structured Data Extraction
# ============================================================================

EXTRACT_DATA_PROMPT = """You are an expert data extraction specialist analyzing research notes about a company.

Company: {company_name}

Research Notes:
{notes}

Search Sources:
{sources}

Task: Extract ALL available structured information. Be thorough and extract every data point you can find.

CRITICAL INSTRUCTIONS:
1. Extract data in ANY language found (Spanish, Portuguese, English)
2. Convert currencies to USD where possible (1 BRL ≈ 0.20 USD, 1 MXN ≈ 0.06 USD, 1 PYG ≈ 0.00013 USD)
3. For LATAM companies: look for "receita", "ingresos", "faturamento" (revenue), "lucro" (profit)
4. Include BOTH local currency AND USD equivalent when available
5. If the company is a subsidiary, mention the parent company
6. Extract ANY numerical data points mentioned (backlog, projects, employees, etc.)
7. VALIDATE: Flag any conflicting numbers found (e.g., different subscriber counts)

## REQUIRED FIELDS (Must extract if ANY evidence exists)
These fields are CRITICAL - search thoroughly for each:

### Leadership (CRITICAL)
- **CEO/General Manager**: Name and title (look for "CEO", "Director General", "Gerente General", "Chief Executive")
- **Executive Team**: Other C-suite executives mentioned
- **Founders/Owners**: Key shareholders or parent company leadership

### Financial Data (CRITICAL)
- **Revenue**: Annual revenue with year and currency
- **Profit/Loss**: Net income, EBITDA, or profitability status
- **Market Share**: Percentage in primary market

### Operational Data (CRITICAL)
- **Subscribers/Customers**: EXACT number if telecom/services (look for "abonados", "suscriptores", "clientes", "usuarios")
- **Employees**: Number with year
- **Network Coverage**: For telecom (4G/5G coverage percentage)

### Regulatory Environment (Important for LATAM)
- **Regulatory Body**: (e.g., CONATEL Paraguay, ANATEL Brazil, IFT Mexico)
- **License Status**: Spectrum licenses, operating permits
- **Compliance Issues**: Any regulatory challenges mentioned

## Company Overview
A 2-3 sentence summary of the company, its purpose, industry, and what it does.
Include: Country of origin, parent company (if subsidiary), key business areas.

## Key Metrics
Extract ALL available metrics. Be specific with years and sources:

**Leadership:**
- CEO: [FULL NAME and title - THIS IS CRITICAL]
- Key Executives: [Names and roles]
- Board Chair: [if available]

**Financial Metrics:**
- Revenue: [amount in local currency AND USD, specify year]
- Net Income/Profit: [amount, year]
- EBITDA: [if available]
- Market Cap: [amount, date] (for public companies)
- Valuation: [amount, date] (for private companies)
- Debt: [if mentioned]

**Operational Metrics:**
- Employees: [number, year if specified]
- Subscribers/Customers: [EXACT number if telecom - CRITICAL]
- Founded: [year]
- Headquarters: [city, country]
- Operating Countries: [list if available]

**Business Metrics:**
- Market Share: [percentage if mentioned - CRITICAL]
- Customer Growth: [YoY growth rate if available]
- ARPU: [Average Revenue Per User if telecom]
- Churn Rate: [if available]

**Regulatory:**
- Regulator: [e.g., CONATEL, ANATEL]
- Key Licenses: [spectrum, operating permits]

## Main Products/Services
List ALL products and services mentioned (bullet points):
- Be specific with product names and categories
- Include business divisions/segments
- Note any flagship or key products

## Competitors
List ALL competitors mentioned WITH their metrics:
- **Competitor 1**: [Name, Market Share %, Revenue if available]
- **Competitor 2**: [Name, Market Share %, Revenue if available]
- Include regional and global competitors

## Key Insights
List 3-5 most important insights:
- Recent developments and news
- Strategic initiatives
- Growth trends
- Challenges or risks mentioned
- Industry position

## Data Validation
IMPORTANT: Check for and note any conflicting data:
- **Conflicting Numbers**: List any metrics with multiple different values found
- **Resolution**: Which value is likely correct and why (prefer official sources)

## Data Quality Notes
- Confidence level: [HIGH/MEDIUM/LOW]
- Data gaps identified: [list any missing CRITICAL fields from above]
- Data freshness: [most recent data year found]
- Missing CRITICAL fields: [List which required fields couldn't be found]

Requirements:
- Extract EVERY data point found, even partial information
- NEVER say "Not available" if ANY related information exists
- For missing sections, provide what partial data you have, then note gaps
- Include source references where possible
- Format as clean markdown with clear sections
- FLAG CONTRADICTIONS - if you find conflicting numbers, list all versions

Extract ALL available data now:"""


# ============================================================================
# Report Generation
# ============================================================================

GENERATE_REPORT_TEMPLATE = """# {company_name} - Research Report

*Generated on {date}*

---

## Company Overview

{company_overview}

---

## Key Metrics

{key_metrics}

---

## Main Products & Services

{products_services}

---

## Competitive Landscape

{competitors}

---

## Key Insights

{key_insights}

---

## Sources

{sources}

---

*This report was automatically generated by the Company Researcher System*
*Research completed in {duration:.1f} seconds | Cost: ${cost:.4f} | Sources: {source_count}*
"""


# ============================================================================
# Quality Check (Phase 2)
# ============================================================================

QUALITY_CHECK_PROMPT = """You are a quality assurance specialist reviewing company research.

Company: {company_name}

Extracted Information:
{extracted_data}

Available Sources:
{sources}

Task: Evaluate the quality and completeness of this research.

Please assess:

1. **Completeness** (0-40 points):
   - Does it have company overview? (10 points)
   - Does it have key financial metrics? (10 points)
   - Does it have products/services? (10 points)
   - Does it have competitive analysis? (10 points)

2. **Accuracy** (0-30 points):
   - Are facts supported by sources? (15 points)
   - Are numbers/dates specific and verifiable? (15 points)

3. **Depth** (0-30 points):
   - Is the analysis insightful? (15 points)
   - Does it go beyond surface-level information? (15 points)

Provide your assessment in this exact JSON format:
{{
  "quality_score": <number 0-100>,
  "missing_information": [
    "Specific information that's missing or incomplete",
    "Another missing piece",
    ...
  ],
  "strengths": [
    "What's good about this research",
    ...
  ],
  "recommended_queries": [
    "Specific search query to fill gap 1",
    "Specific search query to fill gap 2",
    ...
  ]
}}

Be strict: Only score 85+ if the research is truly comprehensive and well-sourced."""


# ============================================================================
# Helper Functions
# ============================================================================

def format_search_results_for_analysis(results: list) -> str:
    """
    Format search results for the analysis prompt.

    Args:
        results: List of search result dictionaries

    Returns:
        Formatted string of search results
    """
    formatted = []
    for i, result in enumerate(results, 1):
        formatted.append(f"""
Result {i}:
Title: {result.get('title', 'N/A')}
URL: {result.get('url', 'N/A')}
Content: {result.get('content', 'N/A')}
Score: {result.get('score', 0):.0%}
---
""")
    return "\n".join(formatted)


def format_sources_for_extraction(sources: list) -> str:
    """
    Format sources for the extraction prompt.

    Args:
        sources: List of source dictionaries

    Returns:
        Formatted string of sources
    """
    formatted = []
    for i, source in enumerate(sources, 1):
        formatted.append(
            f"{i}. [{source.get('title', 'N/A')}]({source.get('url', 'N/A')}) "
            f"(Relevance: {source.get('score', 0):.0%})"
        )
    return "\n".join(formatted)


def format_sources_for_report(sources: list) -> str:
    """
    Format sources for the final report.

    Args:
        sources: List of source dictionaries

    Returns:
        Formatted markdown list of sources
    """
    formatted = []
    for i, source in enumerate(sources, 1):
        formatted.append(
            f"{i}. [{source.get('title', 'N/A')}]({source.get('url', 'N/A')})"
        )
    return "\n".join(formatted)


# ============================================================================
# Agent Prompts - Financial
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


# ============================================================================
# Agent Prompts - Market
# ============================================================================

MARKET_ANALYSIS_PROMPT = """You are a market analyst reviewing search results about a company.

Company: {company_name}

Search Results:
{search_results}

Task: Extract ALL market position and competitive information from these search results.

Focus on:
1. **Market Share**: Domestic market share, global market share, market position
2. **Competitors**: Main competitors, their market shares, competitive dynamics
3. **Positioning**: How the company positions itself, unique value proposition
4. **Market Trends**: Industry trends, market growth, shifts in competition
5. **Competitive Advantages**: What makes the company different or better

Requirements:
- Be specific with percentages and rankings
- Name specific competitors
- Include market context (growing/declining, etc.)
- Format as bullet points

Output format:
- Market Share: [domestic %, global %, ranking]
- Main Competitors: [list competitors with their positions]
- Positioning: [how company positions itself]
- Market Trends: [key trends affecting the company]
- Competitive Advantages: [unique strengths]

Extract the market data now:"""


ENHANCED_MARKET_PROMPT = """You are an expert market analyst with deep expertise in industry analysis and market sizing.

Company: {company_name}

**SEARCH RESULTS:**
{search_results}

**TASK:**
Provide comprehensive market analysis covering all critical strategic dimensions.

**STRUCTURE YOUR ANALYSIS:**

### 1. Market Sizing (TAM/SAM/SOM)
**TAM (Total Addressable Market)**: Global market size for the entire industry
**SAM (Serviceable Available Market)**: Portion of TAM the company's product/service addresses
**SOM (Serviceable Obtainable Market)**: Realistic market share company can capture
**Market Penetration**: Current market share percentage and growth runway

### 2. Industry Trends
**Growing Trends** [GROWING]: Trends with positive momentum
**Declining Trends** [DECLINING]: Trends losing momentum
**Emerging Opportunities** [EMERGING]: New market segments and technological shifts

### 3. Regulatory Landscape
**Current Regulations**: Existing laws and compliance requirements
**Upcoming Changes**: Proposed regulations and expected timeline
**Regional Variations**: Differences by geography

### 4. Competitive Dynamics
**Market Structure**: Number of competitors, concentration, competitive intensity
**Key Players**: Top 3-5 competitors with market share estimates

### 5. Customer Intelligence
**Customer Segments**: Primary customer types and segment sizes
**Buying Behavior**: Decision factors, purchase cycle, switching costs

### 6. Market Summary
- Overall market health rating
- Company's market position strength
- Key opportunities and main threats

Provide your market analysis:"""


COMPETITOR_SCOUT_PROMPT = """You are an expert competitive intelligence analyst specializing in deep competitor research.

Company: {company_name}

**SEARCH RESULTS:**
{search_results}

**TASK:**
Provide comprehensive competitive intelligence analysis.

**STRUCTURE YOUR ANALYSIS:**

### 1. Competitive Landscape Overview
- Industry/market definition
- Total number of competitors
- Competitive intensity level: [LOW/MODERATE/HIGH/INTENSE]

### 2. Direct Competitors (Same Product/Market)
For each major competitor:
- Market position/share
- Key strengths and weaknesses
- Strategic focus
- Threat level: [CRITICAL/HIGH/MEDIUM/LOW]

### 3. Indirect Competitors (Substitute Solutions)
List alternatives that solve the same customer problem differently

### 4. Emerging Threats
Identify potential future competitors

### 5. Competitive Positioning Map
Describe where {company_name} sits relative to competitors

### 6. Competitive Advantages Assessment
Rate applicable advantages:
- Technology leadership
- Cost leadership
- Brand/reputation
- Distribution/partnerships
- Data/network effects

### 7. Strategic Recommendations
- Defensive moves needed
- Offensive opportunities
- Partnerships to consider

Provide your competitive intelligence analysis:"""


# ============================================================================
# Agent Prompts - Product
# ============================================================================

PRODUCT_ANALYSIS_PROMPT = """You are a product analyst reviewing search results about a company.

Company: {company_name}

Search Results:
{search_results}

Task: Extract ALL product, service, and technology information from these search results.

Focus on:
1. **Products/Services**: Complete list of main products or services offered
2. **Key Features**: Important features, capabilities, or differentiators
3. **Technology**: Technology stack, innovations, patents, R&D focus
4. **Recent Launches**: New products, updates, or announcements
5. **Strategy**: Product strategy, target markets, future direction

Requirements:
- List all products/services specifically
- Describe key features and capabilities
- Include technology details when available
- Note recent developments
- Format as bullet points

Output format:
- Main Products/Services: [complete list with descriptions]
- Key Features: [notable features or capabilities]
- Technology: [tech stack, innovations, R&D]
- Recent Launches: [new products or updates]
- Product Strategy: [target markets, direction]

Extract the product data now:"""


# ============================================================================
# Agent Prompts - Synthesis & Quality
# ============================================================================

SYNTHESIS_PROMPT = """You are a senior research analyst synthesizing insights from multiple specialized analysts.

Company: {company_name}

You have received analysis from three specialist teams:

## Financial Analysis
{financial_analysis}

## Market Analysis
{market_analysis}

## Product Analysis
{product_analysis}

Task: Create a comprehensive, well-structured research report by synthesizing these specialized analyses.

Generate the following sections:

## Company Overview
A 2-3 sentence summary combining insights from all analysts about what the company does and its significance.

## Key Metrics
Extract and list all financial metrics in bullet format

## Main Products/Services
List the company's products/services from the product analysis (bullet points)

## Competitors
List main competitors from market analysis

## Key Insights
List 3-4 most important insights combining perspectives from all three analyses

Requirements:
- Synthesize, don't just concatenate
- Resolve any contradictions intelligently
- Maintain factual accuracy
- Keep formatting clean and consistent
- If information is missing, note "Not available in research"

Generate the synthesized report now:"""


LOGIC_CRITIC_PROMPT = """You are a critical analyst reviewing research about {company_name}.

## Research Summary
{research_summary}

## Facts Analyzed: {fact_count}
## Contradictions Found: {contradiction_count}
## Gaps Identified: {gap_count}

## Quality Score: {quality_score}/100

## Task
Provide a critical assessment of this research including:

1. **Verification Status**: What facts are well-supported vs questionable?
2. **Contradiction Analysis**: For any contradictions, which version is likely correct and why?
3. **Gap Assessment**: What critical information is missing?
4. **Confidence Assessment**: How confident should we be in the overall research?
5. **Recommendations**: What specific actions would improve this research?

Be specific and actionable. Focus on the most important issues.

Provide your analysis:"""


# ============================================================================
# Agent Prompts - Deep Research
# ============================================================================

DEEP_RESEARCH_PROMPT = """You are an expert research analyst conducting deep research on {company_name}.

**RESEARCH DEPTH:** {depth}
**ITERATION:** {iteration}/{max_iterations}

**CURRENT SEARCH RESULTS:**
{search_results}

**FACTS ALREADY GATHERED:**
{existing_facts}

**IDENTIFIED GAPS:**
{gaps}

**TASK:**
Perform comprehensive research analysis. Extract ALL verifiable facts and identify gaps.

**STRUCTURE YOUR ANALYSIS:**

### 1. Key Facts Extracted
For each fact, provide:
- **Fact:** [The factual statement]
- **Category:** [financial/market/product/operational/strategic]
- **Confidence:** [HIGH/MEDIUM/LOW]
- **Source:** [Where this fact comes from]

### 2. Data Cross-Validation
Identify which facts are supported by multiple sources

### 3. Research Gaps
List information that is still missing or unclear

### 4. Follow-up Queries
Suggest specific queries to fill the gaps

### 5. Confidence Assessment
Rate overall data completeness by category

### 6. Key Findings Summary
Summarize the most important discoveries (3-5 bullet points)

Begin your deep research analysis:"""


DEEP_RESEARCH_QUERY_PROMPT = """Based on the research gaps identified for {company_name}:

**GAPS:**
{gaps}

**ALREADY SEARCHED:**
{previous_queries}

Generate 5-7 specific, targeted search queries to fill these gaps.

Format each query on its own line:
1. [query] | Priority: [1-10] | Category: [financial/market/product/competitive]

Focus on queries that will yield specific, verifiable data."""


# ============================================================================
# Agent Prompts - Reasoning
# ============================================================================

REASONING_PROMPT = """You are an expert strategic analyst applying structured reasoning to company research.

**COMPANY:** {company_name}
**REASONING TYPE:** {reasoning_type}

**AVAILABLE RESEARCH DATA:**
{research_data}

**TASK:**
Apply {reasoning_type} reasoning to analyze this company.

### 1. Key Observations
List the most important facts from the research

### 2. Pattern Analysis
Identify patterns, trends, relationships, and anomalies in the data

### 3. {reasoning_type} Analysis
Apply the specific reasoning framework to the data

### 4. Inferences
Based on the analysis, what can we infer? (with confidence levels)

### 5. Conclusions
Key takeaways from this reasoning exercise

### 6. Limitations
What are the limitations of this analysis?

Provide your {reasoning_type} analysis:"""


HYPOTHESIS_TESTING_PROMPT = """Test the following hypothesis against available evidence:

**HYPOTHESIS:** {hypothesis}

**EVIDENCE:**
{evidence}

### 1. Hypothesis Statement
Clearly restate the hypothesis being tested

### 2. Supporting Evidence
List evidence that supports this hypothesis

### 3. Contradicting Evidence
List evidence that contradicts this hypothesis

### 4. Evidence Quality Assessment
Rate the quality of supporting vs contradicting evidence

### 5. Verdict
- **Result:** [SUPPORTED/PARTIALLY SUPPORTED/NOT SUPPORTED/INCONCLUSIVE]
- **Confidence:** [HIGH/MEDIUM/LOW]
- **Explanation:** Why this verdict

### 6. Implications
If this hypothesis is true/false, what does it mean?

Provide your hypothesis test analysis:"""


STRATEGIC_INFERENCE_PROMPT = """Based on the research data for {company_name}, perform strategic inference:

**RESEARCH DATA:**
{research_data}

### 1. Strategic Position Assessment
Current market position, competitive standing, key strengths and weaknesses

### 2. Strategic Options
What strategic paths are available? (with pros/cons)

### 3. Threat Analysis
Immediate, medium-term, and long-term threats

### 4. Opportunity Analysis
Immediate, medium-term, and long-term opportunities

### 5. Strategic Recommendations
Prioritized recommendations with rationale

### 6. Key Success Factors
What must go right for the company to succeed?

Provide your strategic inference analysis:"""


# ============================================================================
# Agent Prompts - Specialized (Brand, Social, Sales)
# ============================================================================

BRAND_AUDIT_PROMPT = """You are an expert brand strategist conducting a comprehensive brand audit.

Company: {company_name}

**SEARCH RESULTS:**
{search_results}

**STRUCTURE YOUR ANALYSIS:**

### 1. Brand Identity
- Visual identity assessment
- Brand voice and personality
- Brand values (stated vs demonstrated)

### 2. Brand Perception
- Public sentiment (POSITIVE/NEUTRAL/NEGATIVE/MIXED)
- Customer perception indicators
- Industry perception and recognition

### 3. Brand Positioning
- Market position and differentiation
- Competitive positioning
- Unique value proposition clarity

### 4. Brand Equity Assessment
- Brand awareness level
- Brand associations
- Brand loyalty indicators

### 5. Brand Strength Score
Rate overall brand strength: [DOMINANT/STRONG/MODERATE/WEAK/EMERGING]
- Brand Score: [0-100]
- Trend: [IMPROVING/STABLE/DECLINING]

### 6. Recommendations
Top 3 brand improvement priorities

Provide your brand audit analysis:"""


SOCIAL_MEDIA_PROMPT = """You are an expert social media analyst evaluating a company's social presence.

Company: {company_name}

**SEARCH RESULTS:**
{search_results}

**STRUCTURE YOUR ANALYSIS:**

### 1. Platform Presence Overview
For each active platform (LinkedIn, Twitter/X, Instagram, YouTube, TikTok):
- Follower count (if available)
- Posting frequency
- Engagement level: [HIGH/MODERATE/LOW]
- Content focus

### 2. Content Strategy Analysis
- Content themes and variety
- Content quality assessment
- Strategy type: [THOUGHT_LEADERSHIP/PRODUCT_FOCUSED/COMMUNITY_BUILDING/SALES_DRIVEN/EDUCATIONAL]

### 3. Engagement Analysis
- Overall engagement rate estimate
- Sentiment analysis of comments
- Community interaction level

### 4. Competitive Social Comparison
- Relative following size vs competitors
- Relative engagement
- Content differentiation

### 5. Social Media Score
Overall social presence score: [0-100]

### 6. Recommendations
Top 3 social media improvement priorities

Provide your social media analysis:"""


SALES_INTELLIGENCE_PROMPT = """You are an expert sales intelligence analyst generating actionable B2B sales insights.

Company: {company_name}

**SEARCH RESULTS:**
{search_results}

**STRUCTURE YOUR ANALYSIS:**

### 1. Company Snapshot
- Industry/sector and company size
- Business focus and key offerings

### 2. Lead Qualification
- **Lead Score:** [HOT/WARM/COOL/COLD]
- Company fit, budget indicators, growth trajectory
- **Buying Stage:** [AWARENESS/CONSIDERATION/DECISION/EVALUATION/PURCHASE]

### 3. Decision Makers
- Key roles to target
- Organizational structure insights

### 4. Pain Points & Needs
- Identified pain points with evidence
- Potential explicit and implicit needs

### 5. Buying Triggers
- Recent events (leadership changes, funding, initiatives)
- Timing indicators

### 6. Engagement Strategy
- Best initial contact method
- Key value propositions to lead with
- Objections to anticipate

### 7. Account Intelligence Score
Overall account priority: [0-100]

Provide your sales intelligence analysis:"""
