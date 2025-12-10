"""Prompts for AI query generation."""

QUERY_GENERATION_PROMPT = """You are an expert research analyst. Generate optimal search queries to research {company_name}.

## COMPANY CONTEXT
Company Name: {company_name}
Known Industry: {industry}
Known Region: {region}
Known Country: {country}
Is Public Company: {is_public}
Stock Ticker: {ticker}
Stock Exchange: {exchange}
Known Products: {products}
Known Competitors: {competitors}
Known Executives: {executives}
Research Focus: {focus}
Research Depth: {depth}
Languages to Search: {languages}

## PREVIOUS RESEARCH
Previous Queries: {previous_queries}
Identified Gaps: {gaps}

## INSTRUCTIONS

Generate {num_queries} search queries that will:

1. **Find Comprehensive Information**
   - Official company sources (website, investor relations)
   - News articles from reputable sources
   - Industry reports and analyses
   - Regulatory filings (SEC, local equivalents)

2. **Cover Key Categories**
   - Overview: Company history, headquarters, size
   - Financial: Revenue, profit, funding, valuation
   - Products: Main offerings, technology, features
   - Market: Market share, positioning, trends
   - Competition: Competitors, advantages, threats
   - Leadership: Key executives, founders
   - News: Recent developments, announcements

3. **Adapt to Company Type**
   - PUBLIC: Include SEC filings, earnings reports, stock analysis
   - STARTUP: Include funding rounds, investors, growth metrics
   - PRIVATE: Focus on news, industry reports, leadership
   - CONGLOMERATE: Include subsidiary information, group structure

4. **Use Appropriate Languages**
   - For LATAM companies: Include Spanish and Portuguese queries
   - For specific countries: Include local language queries
   - Always include English for international coverage

5. **Optimize Query Formulation**
   - Use industry-specific terminology
   - Include company name variations (full name, ticker, abbreviations)
   - Target high-quality source types
   - Avoid overly generic queries

## OUTPUT FORMAT

For each query, provide:
- The exact search query text
- The purpose (overview, financial, products, competitors, news, leadership, market, esg, technology, strategy, funding, regulatory, history)
- Expected source types
- Language of the query
- Priority (1=highest, 5=lowest)
- Brief reasoning

Respond in this exact JSON format:
{{
    "queries": [
        {{
            "query": "exact search query text",
            "purpose": "financial|products|competitors|etc",
            "expected_sources": ["news", "official", "sec", "industry_report"],
            "language": "en|es|pt|etc",
            "priority": 1-5,
            "reasoning": "Why this query will find valuable information"
        }}
    ],
    "company_context_inferred": {{
        "likely_industry": "inferred industry if unknown",
        "likely_type": "public|private|startup|conglomerate",
        "likely_region": "inferred region",
        "likely_size": "startup|smb|enterprise|large"
    }},
    "suggested_follow_ups": [
        "backup query if main queries fail",
        "alternative approach query"
    ],
    "estimated_coverage": {{
        "overview": 0.0-1.0,
        "financial": 0.0-1.0,
        "products": 0.0-1.0,
        "market": 0.0-1.0,
        "competitors": 0.0-1.0,
        "news": 0.0-1.0
    }}
}}

## EXAMPLES

For "Tesla" (public, automotive):
- "Tesla Inc investor relations annual report 2024"
- "TSLA SEC 10-K filing latest"
- "Tesla revenue earnings Q4 2024"
- "Tesla vs BYD market share comparison"
- "Tesla Cybertruck production updates"

For "Grupo Bimbo" (public, LATAM, food):
- "Grupo Bimbo annual report financial results"
- "Grupo Bimbo BMV filing informe anual"
- "Bimbo ingresos ventas 2024" (Spanish)
- "Grupo Bimbo competitors Latin America bakery"

For "Rappi" (startup, LATAM):
- "Rappi funding round valuation 2024"
- "Rappi investors Series funding"
- "Rappi competidores delivery LATAM" (Spanish)
- "Rappi expansion strategy growth"
"""

QUERY_REFINEMENT_PROMPT = """Based on the search results quality, generate refined queries to fill gaps.

## ORIGINAL QUERIES AND RESULTS
{original_queries_with_results}

## COVERAGE ASSESSMENT
{coverage_assessment}

## IDENTIFIED GAPS
{gaps}

## INSTRUCTIONS

Generate {num_queries} refined queries to address the gaps:

1. **For Low-Coverage Categories**
   - Try alternative phrasings
   - Use more specific terms
   - Target different source types

2. **For Failed Queries**
   - Simplify overly complex queries
   - Remove terms that may be filtering out results
   - Try variations of company name

3. **For Missing Information**
   - Create targeted queries for specific facts
   - Use question-based queries ("What is X revenue")
   - Include time-specific queries ("2024", "latest")

Respond in JSON format:
{{
    "refined_queries": [
        {{
            "query": "refined query text",
            "purpose": "category this addresses",
            "expected_sources": ["source types"],
            "language": "language",
            "priority": 1,
            "reasoning": "How this addresses the gap",
            "is_fallback": false
        }}
    ],
    "gaps_addressed": ["gap1", "gap2"],
    "dropped_purposes": ["purposes with enough coverage"],
    "confidence_in_refinement": 0.0-1.0
}}
"""

MULTILINGUAL_QUERY_PROMPT = """Generate search queries in multiple languages for {company_name}.

## CONTEXT
Company: {company_name}
Region: {region}
Country: {country}
Languages Needed: {languages}
Query Purpose: {purpose}

## INSTRUCTIONS

Generate equivalent queries in each requested language:
1. Translate the query concept, not word-for-word
2. Use local business terminology
3. Include local regulatory body names if applicable
4. Adapt to local search patterns

For example, for financial queries:
- English: "Tesla revenue annual report"
- Spanish: "Tesla ingresos informe anual"
- Portuguese: "Tesla receita relatorio anual"

Respond in JSON:
{{
    "queries_by_language": {{
        "en": ["query1", "query2"],
        "es": ["query1_spanish", "query2_spanish"],
        "pt": ["query1_portuguese", "query2_portuguese"]
    }}
}}
"""
