"""
Specialty analysis prompts for brand, social media, and sales intelligence.

This module contains prompts used for:
- Brand auditing and positioning
- Social media presence analysis
- B2B sales intelligence
"""

# ============================================================================
# Specialty Analysis Prompts
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
