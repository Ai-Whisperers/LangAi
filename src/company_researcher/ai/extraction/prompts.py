"""Prompts for AI data extraction."""

COMPANY_CLASSIFICATION_PROMPT = """Classify this company based on available information.

## COMPANY NAME
{company_name}

## AVAILABLE INFORMATION
{context}

## CLASSIFICATION TASK

Determine:

### 1. COMPANY TYPE
- **public**: Listed on stock exchange, has ticker symbol
- **private**: Not publicly traded
- **startup**: Early-stage, venture-backed
- **conglomerate**: Large holding company with diverse subsidiaries
- **subsidiary**: Part of larger group
- **nonprofit**: Non-profit organization
- **government**: Government entity

### 2. INDUSTRY
Identify primary industry and sub-industry.

### 3. GEOGRAPHY
Determine region and country using clues:
- Domain extensions (.com.br = Brazil, .mx = Mexico)
- Currency mentions (R$ = Brazil, MXN = Mexico)
- Language of content
- Regulatory bodies mentioned (SEC = US, CVM = Brazil)
- Company suffixes (S.A. = Latin America, Inc. = US, GmbH = Germany)

### 4. PUBLIC COMPANY INFO
If public, identify:
- Stock ticker symbol
- Stock exchange (NYSE, NASDAQ, B3, BMV, etc.)

### 5. CORPORATE STRUCTURE
- Is this company part of a larger group?
- Is it a conglomerate with subsidiaries?
- What is the parent company if any?

## OUTPUT FORMAT

{{
    "company_name": "{company_name}",
    "normalized_name": "Clean name without suffixes",
    "company_type": "public|private|startup|conglomerate|subsidiary|nonprofit|government|unknown",
    "industry": "Primary industry",
    "sub_industry": "Sub-industry or null",
    "sector": "Market sector or null",
    "region": "North America|Latin America|Europe|Asia Pacific|Middle East|Africa",
    "country": "Full country name",
    "country_code": "ISO 2-letter code (US, BR, MX, etc.)",
    "headquarters_city": "City or null",
    "stock_ticker": "Ticker or null",
    "stock_exchange": "Exchange name or null",
    "is_listed": true|false,
    "parent_company": "Parent company name or null",
    "is_conglomerate": true|false,
    "is_subsidiary": true|false,
    "known_subsidiaries": ["sub1", "sub2"],
    "confidence": 0.0-1.0,
    "reasoning": "Brief explanation"
}}
"""

FACT_EXTRACTION_PROMPT = """Extract structured facts from this text about {company_name}.

## TEXT TO ANALYZE
{text}

## EXTRACTION RULES

### 1. FINANCIAL FACTS
Extract ALL financial data with precision:
- Revenue: Annual, quarterly, with time period
- Profit/Net Income: With time period
- Market Cap: Current value
- Funding: Rounds, amounts, investors
- Growth rates: Percentage changes

Number formats to handle:
- "$10.5B" = 10,500,000,000 USD
- "10.5 billion" = 10,500,000,000
- "R$ 50 milhoes" = 50,000,000 BRL
- "EUR2.3M" = 2,300,000 EUR
- "~$500M" = ~500,000,000 (mark as estimate)
- "500K" = 500,000

### 2. COMPANY INFO
- Founding date/year
- Headquarters location
- Employee count
- Business description

### 3. MARKET DATA
- Market share percentages
- Market position (leader, challenger, etc.)
- Geographic presence

### 4. LEADERSHIP
- CEO, CFO, executives
- Founders
- Board members

### 5. PRODUCTS/SERVICES
- Product names
- Key features
- Target markets

## CONFIDENCE SCORING
- 1.0: Explicitly stated with source
- 0.8: Clearly stated
- 0.6: Implied or calculated
- 0.4: Approximate/estimated
- 0.2: Uncertain/ambiguous

## OUTPUT FORMAT

{{
    "facts": [
        {{
            "category": "financial|company_info|product|market|leadership|technology|esg|legal|news",
            "fact_type": "revenue|profit|market_cap|funding_total|employee_count|founding_date|etc",
            "value": "extracted value",
            "value_normalized": numeric_value_or_null,
            "unit": "USD|employees|percent|etc",
            "currency": "USD|BRL|EUR|etc",
            "time_period": "2024|Q3 2024|FY2023|etc",
            "as_of_date": "date or null",
            "is_estimate": true|false,
            "source_text": "Exact quote from text",
            "confidence": 0.0-1.0
        }}
    ]
}}
"""

CONTRADICTION_RESOLUTION_PROMPT = """Analyze potential contradictions in extracted data about {company_name}.

## FACT TYPE
{fact_type}

## VALUES FOUND
{values}

## ANALYSIS TASK

Determine if these values actually contradict each other:

### NOT A CONTRADICTION IF:
1. Different time periods (2023 vs 2024 revenue)
2. Different metrics (gross revenue vs net revenue)
3. Different currencies (converted incorrectly)
4. Different scopes (subsidiary vs parent company)
5. Rounding differences (<5%)
6. Estimate vs actual

### TRUE CONTRADICTION IF:
1. Same time period, same metric, significant difference
2. Cannot be explained by scope or methodology
3. >20% difference with no explanation

### SEVERITY ASSESSMENT:
- CRITICAL: >50% difference, core financial data
- HIGH: 30-50% difference
- MEDIUM: 20-30% difference
- LOW: <20% difference

### RESOLUTION:
If contradiction exists, determine most likely correct value:
- Prefer official sources (SEC, company IR)
- Prefer more recent sources
- Prefer more specific values over rounded
- Note if unresolvable

## OUTPUT FORMAT

{{
    "fact_type": "{fact_type}",
    "values_found": [...],
    "is_contradiction": true|false,
    "severity": "critical|high|medium|low|none",
    "difference_percentage": number or null,
    "can_be_resolved": true|false,
    "resolution_explanation": "Explanation or null",
    "most_likely_value": value or null,
    "most_likely_source": "source or null",
    "reasoning": "Detailed explanation"
}}
"""

COUNTRY_DETECTION_PROMPT = """Determine the country for this company based on available clues.

## COMPANY
{company_name}

## CLUES
{clues}

## DETECTION RULES

Use these indicators:
1. Domain extension: .br (Brazil), .mx (Mexico), .ar (Argentina), etc.
2. Currency: R$ (Brazil), MXN (Mexico), ARS (Argentina), CLP (Chile)
3. Stock exchange: B3/BOVESPA (Brazil), BMV (Mexico), BCS (Chile)
4. Regulatory body: CVM (Brazil), CNBV (Mexico), CMF (Chile)
5. Company suffix: S.A. (LATAM), Inc./Corp (US), Ltd/PLC (UK)
6. Language: Portuguese (Brazil), Spanish (most LATAM)
7. City mentions: Sao Paulo, Mexico City, Buenos Aires
8. Local companies mentioned as competitors

## OUTPUT FORMAT

{{
    "country": "Full country name",
    "country_code": "ISO 2-letter code",
    "region": "Latin America|North America|Europe|etc",
    "confidence": 0.0-1.0,
    "indicators_found": ["indicator1", "indicator2"],
    "reasoning": "Explanation"
}}
"""

MULTI_FACT_EXTRACTION_PROMPT = """Extract multiple categories of facts from these sources about {company_name}.

## SOURCES
{sources}

## EXTRACT THESE FACT CATEGORIES

1. **FINANCIALS**: Revenue, profit, margins, growth rates, funding
2. **COMPANY INFO**: Founded, HQ, employees, description
3. **MARKET**: Share, position, competitors
4. **LEADERSHIP**: CEO, founders, executives
5. **PRODUCTS**: Names, features, launches

## IMPORTANT RULES

- Extract ALL facts, even if partially available
- Preserve original quotes as source_text
- Normalize numbers to base units (not millions/billions)
- Mark estimates with is_estimate=true
- Include confidence scores

## OUTPUT FORMAT

{{
    "facts": [
        {{
            "category": "...",
            "fact_type": "...",
            "value": "...",
            "value_normalized": null or number,
            "currency": "USD|BRL|etc" or null,
            "time_period": "2024|Q1 2024|etc" or null,
            "is_estimate": false,
            "source_text": "exact quote",
            "source_url": "url if available",
            "confidence": 0.0-1.0
        }}
    ],
    "languages_detected": ["en", "pt", "es"]
}}
"""

FINANCIAL_EXTRACTION_PROMPT = """Extract detailed financial data from this text about {company_name}.

## TEXT
{text}

## EXTRACT

### Revenue & Sales
- Annual revenue (with year)
- Quarterly revenue (with quarter)
- Revenue by segment/region
- Revenue growth (YoY, QoQ)

### Profitability
- Net income/profit
- EBITDA
- Gross margin %
- Operating margin %
- Net margin %

### Valuation
- Market capitalization
- Enterprise value
- P/E ratio
- EV/EBITDA

### Funding (if startup/private)
- Total funding raised
- Latest round details
- Valuation (if disclosed)
- Key investors

### Other Metrics
- Employee count
- Customer count
- ARR/MRR (if SaaS)
- GMV (if marketplace)

## NUMBER PARSING

Handle these formats:
- "$X.XB" or "$X.X billion" -> X,X00,000,000
- "$XXM" or "$XX million" -> XX,000,000
- "$XXK" or "$XX thousand" -> XX,000
- "R$ XX milhoes" -> XX,000,000 BRL
- "EUR XX.X million" -> XX,X00,000 EUR
- Approximate (~, about, around) -> is_estimate=true

## OUTPUT FORMAT

{{
    "revenue": {{
        "value": number or null,
        "currency": "USD",
        "period": "FY2023",
        "growth_yoy": percent or null,
        "source_text": "quote"
    }},
    "profit": {{
        "net_income": number or null,
        "ebitda": number or null,
        "gross_margin": percent or null,
        "operating_margin": percent or null,
        "period": "FY2023",
        "source_text": "quote"
    }},
    "valuation": {{
        "market_cap": number or null,
        "enterprise_value": number or null,
        "source_text": "quote"
    }},
    "funding": {{
        "total_raised": number or null,
        "last_round": "Series X",
        "last_round_amount": number or null,
        "valuation": number or null,
        "source_text": "quote"
    }},
    "size": {{
        "employees": number or null,
        "customers": number or null,
        "source_text": "quote"
    }},
    "extraction_confidence": 0.0-1.0
}}
"""

ENTITY_RECOGNITION_PROMPT = """Extract named entities from this text related to {company_name}.

## TEXT
{text}

## ENTITY TYPES TO EXTRACT

1. **PEOPLE**: CEOs, founders, executives, board members
2. **ORGANIZATIONS**: Parent companies, subsidiaries, competitors, partners
3. **LOCATIONS**: Headquarters, offices, markets
4. **PRODUCTS**: Product names, services, brands
5. **DATES**: Founding dates, events, milestones
6. **MONEY**: Revenue figures, funding amounts, valuations

## OUTPUT FORMAT

{{
    "entities": [
        {{
            "text": "Elon Musk",
            "type": "PERSON",
            "role": "CEO",
            "context": "CEO of Tesla",
            "confidence": 0.95
        }},
        {{
            "text": "Model 3",
            "type": "PRODUCT",
            "role": "product",
            "context": "bestselling electric vehicle",
            "confidence": 0.9
        }}
    ]
}}
"""
