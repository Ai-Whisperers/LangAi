"""Prompts for AI sentiment analysis."""

SENTIMENT_ANALYSIS_PROMPT = """You are an expert financial news analyst specializing in sentiment analysis. Analyze this news article about {company_name}.

<article>
{article_text}
</article>

<target_company>{company_name}</target_company>

Perform a comprehensive sentiment analysis:

## 1. OVERALL SENTIMENT
Determine the overall sentiment of the article. Consider:
- The main message and tone
- Factual vs. opinion content
- Headlines vs. body sentiment

## 2. ENTITY-SPECIFIC SENTIMENT
For EACH company, person, or product mentioned, determine the sentiment ABOUT THAT SPECIFIC ENTITY.

CRITICAL DISTINCTIONS:
- "Apple's competitor Samsung failed" -> Negative about Samsung, potentially POSITIVE for Apple
- "Tesla beat expectations" -> Positive about Tesla
- "Despite BYD's growth, Tesla maintained leadership" -> Positive about both, slight edge to Tesla
- "The CEO resigned amid scandal" -> Negative about CEO, potentially negative for company

## 3. CONTEXT ANALYSIS
Identify:
- Negations: "not a failure", "didn't decline" = positive despite negative words
- Qualifiers: "might", "could", "reportedly" = uncertainty
- Sarcasm/Irony: detect if tone contradicts literal meaning
- Comparisons: how is {company_name} positioned vs competitors?

## 4. KEY FACTORS
List the specific information driving the sentiment:
- Financial results (beat/miss expectations)
- Product announcements
- Leadership changes
- Legal/regulatory issues
- Market position changes

## 5. CATEGORIZATION
Classify the news: financial, product, legal, partnership, executive, market, regulatory, esg, technology, general

Respond in this exact JSON format:
{{
    "overall_sentiment": "very_positive|positive|neutral|negative|very_negative",
    "overall_score": -1.0 to 1.0,
    "overall_confidence": 0.0 to 1.0,
    "entity_sentiments": [
        {{
            "entity_name": "Company/Person/Product name",
            "entity_type": "company|person|product|brand",
            "sentiment": "very_positive|positive|neutral|negative|very_negative",
            "confidence": 0.0 to 1.0,
            "reasoning": "Brief explanation",
            "context_snippet": "Relevant quote from article",
            "is_target_company": true if this is {company_name}
        }}
    ],
    "target_company_sentiment": "sentiment for {company_name} specifically, or null if not mentioned",
    "target_company_confidence": 0.0 to 1.0,
    "key_factors": ["factor1", "factor2", "factor3"],
    "detected_language": "en|es|pt|de|fr|etc",
    "has_negations": true|false,
    "has_uncertainty": true|false,
    "has_sarcasm": false,
    "news_category": "financial|product|legal|partnership|executive|market|regulatory|esg|technology|general",
    "secondary_categories": ["category1", "category2"],
    "summary": "One sentence summarizing the news and its implications for {company_name}"
}}

IMPORTANT:
- Be precise about WHO the sentiment is about
- Distinguish between sentiment about {company_name} vs. competitors
- Consider the business implications, not just the tone
- If uncertain, reflect that in confidence scores
"""

NEWS_CATEGORIZATION_PROMPT = """Categorize this news article and assess its relevance to {company_name}.

<article>
{article_text}
</article>

<target_company>{company_name}</target_company>

Determine:

1. **Primary Category**: What is this article primarily about?
   - financial: Earnings, revenue, funding, stock, valuation
   - product: Product launches, features, technology
   - legal: Lawsuits, investigations, settlements
   - partnership: Deals, collaborations, M&A
   - executive: Leadership changes, management news
   - market: Market share, industry trends, competition
   - regulatory: Government actions, compliance
   - esg: Environmental, social, governance
   - technology: Tech innovations, R&D
   - general: Other news

2. **Relevance**: How relevant is this to {company_name}?
   - 1.0: Article is primarily about {company_name}
   - 0.7-0.9: {company_name} is a major subject
   - 0.4-0.6: {company_name} is mentioned significantly
   - 0.1-0.3: {company_name} is briefly mentioned
   - 0.0: {company_name} is not mentioned

3. **Companies Mentioned**: List all companies referenced

Respond in JSON:
{{
    "primary_category": "category",
    "secondary_categories": ["cat1", "cat2"],
    "relevance_to_company": 0.0 to 1.0,
    "is_about_target_company": true|false,
    "mentioned_companies": ["company1", "company2"],
    "topic_keywords": ["keyword1", "keyword2", "keyword3"]
}}
"""

SENTIMENT_AGGREGATION_PROMPT = """Aggregate the sentiment analysis results for {company_name} across multiple articles.

<individual_results>
{results_summary}
</individual_results>

Provide an aggregated sentiment assessment:

1. What is the overall sentiment trend across all articles?
2. What are the most common positive and negative factors?
3. Are there any contradictions between articles?
4. What is the dominant news category?

Respond in JSON:
{{
    "overall_sentiment": "very_positive|positive|neutral|negative|very_negative",
    "overall_score": -1.0 to 1.0,
    "confidence": 0.0 to 1.0,
    "top_positive_factors": ["factor1", "factor2"],
    "top_negative_factors": ["factor1", "factor2"],
    "top_categories": ["category1", "category2"],
    "trend_summary": "Brief description of the overall sentiment trend"
}}
"""

# System prompts for different analysis modes
SENTIMENT_SYSTEM_PROMPT = """You are an expert financial news sentiment analyst.
You specialize in:
- Understanding context and nuance in business news
- Distinguishing entity-specific sentiment (who the news is good/bad for)
- Detecting negations, sarcasm, and uncertainty
- Identifying the business implications of news

Always respond with valid JSON matching the requested format.
Be precise about confidence levels - don't overclaim certainty.
"""

CATEGORIZATION_SYSTEM_PROMPT = """You are a news categorization expert.
You specialize in:
- Classifying business news into appropriate categories
- Assessing relevance to specific companies
- Identifying key themes and topics

Always respond with valid JSON matching the requested format.
"""
