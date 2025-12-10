"""
Deep research and reasoning prompts.

This module contains prompts used for:
- Deep iterative research
- Strategic reasoning
- Hypothesis testing
"""

# ============================================================================
# Deep Research Prompts
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
# Reasoning Prompts
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
