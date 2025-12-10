"""
Market analysis prompts for competitive and market positioning evaluation.

This module contains prompts used for:
- Market position analysis
- Competitive intelligence
- Market sizing and trends
- Product analysis
"""

# ============================================================================
# Market Analysis Prompts
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
# Product Analysis Prompts
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
