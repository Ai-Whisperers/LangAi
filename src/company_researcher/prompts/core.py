"""
Core workflow prompts for basic research operations.

This module contains prompts used in the main research workflow:
- Query generation
- Results analysis
- Data extraction
- Quality checking
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

Task: Analyze these search results and extract all relevant information about the company.

Focus on:
1. Company Overview
   - What the company does (products/services)
   - Industry and sector
   - Founded date and history
   - Headquarters location
   - Company size (employees, offices)

2. Financial Information
   - Revenue, profit, growth rates
   - Market cap, valuation
   - Key financial metrics
   - Stock ticker and performance

3. Business Model
   - How they make money
   - Key customer segments
   - Distribution channels
   - Competitive advantages

4. Market Position
   - Market share
   - Key competitors
   - Industry rankings
   - Geographic presence

5. Leadership & Governance
   - CEO and key executives
   - Board members
   - Ownership structure

6. Recent Developments
   - Latest news and announcements
   - Strategic initiatives
   - Partnerships or acquisitions
   - Challenges or controversies

Important Guidelines:
- Focus on FACTS and DATA, not speculation
- Include specific numbers and dates when available
- Note the source/URL for key claims
- If information contradicts between sources, note both versions
- Use bullet points for clarity
- Be comprehensive but concise

Output Format:
Provide your analysis in well-structured markdown with clear sections.
"""


# ============================================================================
# Data Extraction
# ============================================================================

EXTRACT_DATA_PROMPT = """You are an expert data extraction specialist analyzing research notes about a company.

Company: {company_name}

Research Notes:
{notes}

Available Sources:
{sources}

Task: Extract and structure ALL available data about this company into a comprehensive markdown report.

IMPORTANT: Extract EVERY piece of information from the notes. Do not summarize or omit details.

Your report should include ALL of the following sections (if data is available):

# Company Overview

## Basic Information
- **Company Name:**
- **Legal Name:** (if different)
- **Stock Ticker:**
- **Founded:**
- **Headquarters:**
- **Industry/Sector:**
- **Website:**

## Company Description
[Comprehensive description of what the company does, its mission, and core business]

## Key Facts
- Number of Employees:
- Number of Offices/Locations:
- Geographic Presence:
- Public/Private Status:

# Financial Performance

## Revenue & Profitability
- **Annual Revenue (Latest):**
- **Revenue Growth Rate:**
- **Net Income:**
- **Profit Margin:**
- **EBITDA:**

## Market Valuation
- **Market Cap:**
- **Stock Price (Latest):**
- **52-Week High/Low:**
- **P/E Ratio:**

## Other Financial Metrics
[Any other financial data: cash flow, debt, assets, etc.]

# Products & Services

## Main Products/Services
[Detailed list with descriptions]

## Product Lines/Business Segments
[If applicable, revenue breakdown by segment]

## Key Features/Differentiation
[What makes their products unique]

# Market Position

## Market Share
[Industry position and market share data]

## Competitors
[List of main competitors with brief comparison]

## Competitive Advantages
[Key differentiators and moats]

## Industry Trends
[Relevant market trends affecting the company]

# Leadership & Governance

## Key Executives
- **CEO:**
- **CFO:**
- **Other C-Level:**

## Board of Directors
[If available]

## Ownership Structure
[Major shareholders, ownership percentage]

# Recent Developments

## Latest News (Past 12 Months)
[Recent announcements, achievements, challenges]

## Strategic Initiatives
[M&A, partnerships, expansions, etc.]

## Challenges & Risks
[Known issues, controversies, risks]

# Additional Information

## Corporate Culture
[If available: values, work environment, DEI initiatives]

## ESG/Sustainability
[Environmental, Social, Governance initiatives]

## Other Notable Facts
[Any other relevant information]

---

GUIDELINES:
1. Extract ALL available data - be comprehensive
2. Use exact numbers and dates from the sources
3. If a section has no data, write "No data available"
4. Use markdown formatting for clarity
5. Include source references [Source: URL] for key claims
6. If data conflicts between sources, note both versions
7. Use tables for comparing data points
8. Be precise with numbers (include units: $M, $B, %, etc.)

Generate the complete structured report now:"""


# ============================================================================
# Quality Checking
# ============================================================================

QUALITY_CHECK_PROMPT = """You are a quality assurance specialist reviewing company research.

Company: {company_name}

Extracted Data:
{extracted_data}

Sources Used:
{sources}

Task: Evaluate the completeness and quality of this research.

Evaluation Criteria:

1. **Completeness** (40 points)
   - Company Overview: Name, industry, description, founding [10 pts]
   - Financial Data: Revenue, profit, metrics [10 pts]
   - Products/Services: What they sell [5 pts]
   - Market Position: Competitors, market share [5 pts]
   - Leadership: CEO, key executives [5 pts]
   - Recent News: Latest developments [5 pts]

2. **Data Quality** (30 points)
   - Specific numbers with dates [10 pts]
   - Multiple reliable sources [10 pts]
   - Recent information (< 1 year old) [10 pts]

3. **Detail Level** (20 points)
   - Depth of analysis [10 pts]
   - Specificity of claims [10 pts]

4. **Source Reliability** (10 points)
   - Quality of sources used [10 pts]

Score each criterion and provide:

1. **Overall Score**: X/100
2. **Missing Information**: List what's missing or weak
3. **Data Gaps**: Key questions that remain unanswered
4. **Recommendations**: What additional research would improve quality

Output Format:
```json
{
  "quality_score": <0-100>,
  "completeness_score": <0-40>,
  "data_quality_score": <0-30>,
  "detail_score": <0-20>,
  "source_score": <0-10>,
  "missing_information": ["item1", "item2", ...],
  "data_gaps": ["gap1", "gap2", ...],
  "recommendations": ["recommendation1", "recommendation2", ...]
}
```

Provide your evaluation:"""


# Report Generation Template
GENERATE_REPORT_TEMPLATE = """# {company_name} - Research Report

*Generated on {date}*

---

{content}

---

## Sources

{sources}

---

*This report was automatically generated by the Company Researcher System*
"""
