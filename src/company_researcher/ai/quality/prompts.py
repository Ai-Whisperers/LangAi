"""Prompts for AI quality assessment."""

CONTENT_QUALITY_PROMPT = """You are an expert research quality assessor. Evaluate the quality of this research content about {company_name}.

## CONTENT TO ASSESS
Section: {section_name}
Content:
{content}

## CONTEXT
Company: {company_name}
Industry: {industry}
Company Type: {company_type}

## ASSESSMENT CRITERIA

### 1. FACTUAL DENSITY (0.0-1.0)
Measure concrete facts per 100 words:
- HIGH (0.8-1.0): Multiple specific facts (numbers, dates, names, events)
- MEDIUM (0.5-0.7): Mix of facts and general statements
- LOW (0.0-0.4): Mostly vague or filler content

Examples:
- "Revenue of $10.5B in 2024" = HIGH factual density
- "The company has significant revenue" = LOW factual density
- "Founded in 1985 by John Smith in Austin, Texas" = HIGH
- "The company was founded many years ago" = LOW

### 2. SPECIFICITY (0.0-1.0)
How specific and precise is the information:
- HIGH: Exact figures, named entities, specific dates
- MEDIUM: Approximate figures, general references
- LOW: Vague statements, no specifics

### 3. COMPLETENESS (0.0-1.0)
Coverage of expected topics for this section:

For "company_overview":
- History and founding
- Headquarters/locations
- Business description
- Size indicators

For "key_metrics" / "financial":
- Revenue figures
- Growth metrics
- Market cap (if public)
- Employee count

For "products_services":
- Main product lines
- Key features
- Target markets
- Technology/innovation

For "competitors":
- Named competitors
- Competitive position
- Market share
- Advantages/disadvantages

### 4. QUALITY ISSUES TO FLAG
- "Data not available" or placeholder text
- Information older than 2 years (for fast-moving industries)
- Unsubstantiated claims without sources
- Contradictory statements
- Missing critical information
- Promotional/marketing language without facts

### 5. QUALITY STRENGTHS TO NOTE
- Specific numbers with sources
- Recent data (within 6 months)
- Multiple corroborating data points
- Primary source references
- Clear, factual language

## OUTPUT FORMAT

Respond in this exact JSON format:
{{
    "section_name": "{section_name}",
    "quality_level": "excellent|good|acceptable|poor|insufficient",
    "score": 0-100,
    "factual_density": 0.0-1.0,
    "specificity": 0.0-1.0,
    "completeness": 0.0-1.0,
    "accuracy_indicators": 0.0-1.0,
    "recency": 0.0-1.0,
    "issues": ["issue1", "issue2"],
    "strengths": ["strength1", "strength2"],
    "improvement_suggestions": ["suggestion1", "suggestion2"],
    "missing_topics": ["topic1", "topic2"]
}}
"""

SOURCE_QUALITY_PROMPT = """Assess the quality and reliability of this source for company research.

## SOURCE INFORMATION
URL: {url}
Title: {title}
Domain: {domain}
Snippet: {snippet}

## TARGET COMPANY
{company_name}

## ASSESSMENT CRITERIA

### 1. AUTHORITY (0.0-1.0)
- 1.0: Official company source, regulatory filing (SEC, CVM)
- 0.9: Major financial news (Bloomberg, Reuters, WSJ)
- 0.8: Reputable industry publications
- 0.7: Regional news, trade publications
- 0.5: General news sites
- 0.3: Blogs, opinion pieces
- 0.1: Forums, social media, unknown sources

### 2. RECENCY (0.0-1.0)
- 1.0: Within last month
- 0.8: Within 6 months
- 0.6: Within 1 year
- 0.4: 1-2 years old
- 0.2: 2-5 years old
- 0.0: Over 5 years or undated

### 3. RELEVANCE (0.0-1.0)
- 1.0: Article is primarily about {company_name}
- 0.8: {company_name} is main subject with analysis
- 0.6: Significant mention with useful information
- 0.4: Brief mention with some context
- 0.2: Passing mention only
- 0.0: Not actually about {company_name}

### 4. SOURCE TYPE
Classify as: official, regulatory, news_major, news_trade, news_local, academic, analyst, blog, social, unknown

### 5. PRIMARY SOURCE
Is this a primary source (directly from company or regulators) or secondary (reporting on information)?

## OUTPUT FORMAT

{{
    "url": "{url}",
    "domain": "{domain}",
    "title": "{title}",
    "quality_level": "excellent|good|acceptable|poor|insufficient",
    "source_type": "official|regulatory|news_major|news_trade|news_local|academic|analyst|blog|social|unknown",
    "authority_score": 0.0-1.0,
    "recency_score": 0.0-1.0,
    "relevance_score": 0.0-1.0,
    "depth_score": 0.0-1.0,
    "is_primary_source": true|false,
    "is_paywalled": true|false,
    "reasoning": "Brief explanation of the assessment"
}}
"""

OVERALL_QUALITY_PROMPT = """Provide an overall quality assessment for this company research report.

## COMPANY CONTEXT
Company: {company_name}
Industry: {industry}
Company Type: {company_type}
Quality Threshold: {threshold}%

## SECTION ASSESSMENTS
{section_scores}

## SOURCE SUMMARY
Total Sources: {total_sources}
Primary Sources: {primary_sources}
Average Source Quality: {avg_source_quality}

## REQUIREMENTS BY COMPANY TYPE

For PUBLIC companies:
- MUST have: financial data, products/services, competitors
- SHOULD have: recent news, market position, leadership
- Minimum source quality: 0.7

For PRIVATE companies:
- MUST have: company overview, products/services
- SHOULD have: leadership, news, market
- Can have: financials (if available)

For STARTUPS:
- MUST have: product/technology, funding, leadership
- SHOULD have: market opportunity, competitors
- Can have: detailed financials

For CONGLOMERATES:
- MUST have: group structure, major subsidiaries, overall financials
- SHOULD have: per-subsidiary details, market positions

## DECISION CRITERIA

Ready for Delivery if:
1. All MUST-have sections score >= 60
2. Overall score >= threshold
3. No critical issues
4. Sufficient source coverage

Iteration Needed if:
1. Any MUST-have section scores < 60
2. Critical information gaps identified
3. Contradictions unresolved
4. Overall score < threshold

## OUTPUT FORMAT

{{
    "overall_score": 0-100,
    "overall_level": "excellent|good|acceptable|poor|insufficient",
    "key_gaps": ["gap1", "gap2"],
    "critical_issues": ["issue1", "issue2"],
    "recommendations": ["rec1", "rec2"],
    "ready_for_delivery": true|false,
    "iteration_needed": true|false,
    "focus_areas_for_iteration": ["area1", "area2"]
}}
"""

CONFIDENCE_ASSESSMENT_PROMPT = """Assess the confidence level for this claim about {company_name}.

## CLAIM
{claim}

## SUPPORTING EVIDENCE
{evidence}

## ASSESSMENT

1. How many independent sources support this claim?
2. What is the quality of those sources?
3. Are there any contradicting sources?
4. Does the language indicate certainty or uncertainty?

Uncertainty indicators: "reportedly", "estimated", "approximately", "may", "might", "could", "around", "about"
Certainty indicators: "confirmed", "announced", "official", "according to SEC filing"

## OUTPUT FORMAT

{{
    "claim": "{claim}",
    "confidence_level": "excellent|good|acceptable|poor|insufficient",
    "confidence_score": 0.0-1.0,
    "supporting_sources": number,
    "contradicting_sources": number,
    "source_quality_avg": 0.0-1.0,
    "uncertainty_indicators": ["word1", "word2"],
    "verification_status": "verified|unverified|conflicting|uncertain",
    "reasoning": "Explanation"
}}
"""

BATCH_SOURCE_QUALITY_PROMPT = """Assess the quality of multiple sources for company research about {company_name}.

## SOURCES TO ASSESS
{sources_list}

## ASSESSMENT CRITERIA
For each source, evaluate:
1. Authority (0.0-1.0): Source trustworthiness
2. Recency (0.0-1.0): How recent the information is
3. Relevance (0.0-1.0): How relevant to {company_name}
4. Source Type: official, regulatory, news_major, news_trade, news_local, academic, analyst, blog, social, unknown

## OUTPUT FORMAT
Return a JSON array with one object per source:
[
    {{
        "url": "source_url",
        "authority_score": 0.0-1.0,
        "recency_score": 0.0-1.0,
        "relevance_score": 0.0-1.0,
        "source_type": "type",
        "is_primary_source": true|false
    }},
    ...
]
"""

SECTION_COMPLETENESS_PROMPT = """Evaluate what information is missing from this research section.

## SECTION: {section_name}
## COMPANY: {company_name}
## INDUSTRY: {industry}

## CURRENT CONTENT
{content}

## EXPECTED TOPICS FOR {section_name}
{expected_topics}

## TASK
Identify which expected topics are:
1. COVERED: Present with sufficient detail
2. PARTIALLY_COVERED: Mentioned but lacking depth
3. MISSING: Not present at all

## OUTPUT FORMAT
{{
    "covered_topics": ["topic1", "topic2"],
    "partially_covered": [
        {{"topic": "topic3", "missing_aspects": ["aspect1", "aspect2"]}}
    ],
    "missing_topics": ["topic4", "topic5"],
    "completeness_score": 0.0-1.0,
    "priority_gaps": ["Most critical missing information"]
}}
"""

QUALITY_IMPROVEMENT_PROMPT = """Suggest specific improvements for this research section.

## SECTION: {section_name}
## COMPANY: {company_name}

## CURRENT CONTENT
{content}

## IDENTIFIED ISSUES
{issues}

## TASK
For each issue, provide:
1. Specific search queries to find better information
2. Types of sources to prioritize
3. Specific data points to look for

## OUTPUT FORMAT
{{
    "improvements": [
        {{
            "issue": "issue description",
            "search_queries": ["query1", "query2"],
            "target_sources": ["source type 1", "source type 2"],
            "data_points_needed": ["specific data to find"]
        }}
    ],
    "priority_order": ["issue1", "issue2"]
}}
"""
