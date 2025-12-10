# Prompt Engineering Guide

Documentation of prompt design decisions, patterns, and optimization strategies.

---

## Prompt Architecture

### Prompt Types

| Type | Purpose | Example |
|------|---------|---------|
| **Task** | Define what to do | "Extract financial data..." |
| **Context** | Provide background | "Company: {company_name}" |
| **Format** | Specify output structure | "Return as JSON..." |
| **Constraints** | Set boundaries | "Be factual and objective" |

### Prompt Template Structure

```
ROLE DEFINITION
↓
CONTEXT/INPUT
↓
TASK DESCRIPTION
↓
SPECIFIC INSTRUCTIONS
↓
OUTPUT FORMAT
↓
REQUIREMENTS/CONSTRAINTS
```

---

## Core Prompts Analysis

### GENERATE_QUERIES_PROMPT

**Location**: `prompts.py:13-50`

**Purpose**: Generate targeted search queries

**Design Decisions**:

1. **Multilingual Support**
   ```
   IMPORTANT INSTRUCTIONS:
   1. If this appears to be a LATAM company (Brazilian, Mexican, etc.),
      include queries in BOTH English AND the local language
   2. For Brazilian companies: include Portuguese queries ("receita", "lucro")
   ```
   *Rationale*: Many LATAM companies have better coverage in local language sources.

2. **Structured Coverage**
   ```
   Your queries should cover:
   1. Company overview and background
   2. Financial performance and metrics
   3. Products and services
   4. Market position and competitors
   5. Recent news and developments
   6. Leadership team and executives
   ```
   *Rationale*: Ensures comprehensive research coverage from first iteration.

3. **Example Outputs**
   ```
   Example output for a Brazilian company:
   ["Gerdau empresa overview", "Gerdau receita 2024", ...]
   ```
   *Rationale*: Examples demonstrate expected format and quality.

4. **JSON Output Format**
   ```
   Output format:
   Return ONLY a JSON array of query strings, nothing else.
   ```
   *Rationale*: Structured output enables programmatic parsing.

---

### ANALYZE_RESULTS_PROMPT

**Location**: `prompts.py:57-135`

**Purpose**: Extract and analyze search results

**Design Decisions**:

1. **Language Flexibility**
   ```
   CRITICAL INSTRUCTIONS:
   1. Process content in ANY language (English, Spanish, Portuguese, etc.)
   2. Translate key findings to English while preserving original terms
   ```
   *Rationale*: Sources may be in any language; LLM handles translation.

2. **Source Attribution**
   ```
   3. Extract ALL numerical data: revenue, employees, funding, market share, etc.
   4. Note the SOURCE and YEAR for each data point when available
   ```
   *Rationale*: Enables fact verification and freshness assessment.

3. **LATAM-Specific Terms**
   ```
   5. For LATAM companies, pay special attention to:
      - "receita" / "ingresos" / "faturamento" = revenue
      - "lucro" / "beneficio" = profit
   ```
   *Rationale*: Maps local terminology to standard fields.

4. **Comprehensive Sections**
   ```
   ## 1. Company Identity
   ## 2. Financial Data (EXTRACT ALL NUMBERS FOUND)
   ## 3. Operational Data
   ## 4. Products & Services
   ## 5. Market Position
   ## 6. Recent Developments
   ## 7. Data Confidence Assessment
   ```
   *Rationale*: Structured sections map to downstream processing.

---

### EXTRACT_DATA_PROMPT

**Location**: `prompts.py:142-222`

**Purpose**: Convert analysis notes to structured data

**Design Decisions**:

1. **Currency Conversion Guidance**
   ```
   2. Convert currencies to USD where possible (1 BRL ≈ 0.20 USD, 1 MXN ≈ 0.06 USD)
   3. Include BOTH local currency AND USD equivalent when available
   ```
   *Rationale*: Standardizes financial data for comparison.

2. **Exhaustive Extraction**
   ```
   Requirements:
   - Extract EVERY data point found, even partial information
   - NEVER say "Not available" if ANY related information exists
   ```
   *Rationale*: Prevents LLM from being overly conservative.

3. **Quality Assessment**
   ```
   ## Data Quality Notes
   - Confidence level: [HIGH/MEDIUM/LOW]
   - Data gaps identified: [list any missing critical information]
   - Data freshness: [most recent data year found]
   ```
   *Rationale*: Self-assessment enables downstream quality checks.

---

### QUALITY_CHECK_PROMPT

**Location**: `prompts.py:279-326`

**Purpose**: Evaluate research quality and identify gaps

**Design Decisions**:

1. **Numerical Scoring**
   ```
   1. **Completeness** (0-40 points):
   2. **Accuracy** (0-30 points):
   3. **Depth** (0-30 points):
   ```
   *Rationale*: Quantitative scoring enables threshold-based decisions.

2. **JSON Output**
   ```
   Provide your assessment in this exact JSON format:
   {
     "quality_score": <number 0-100>,
     "missing_information": [...],
     ...
   }
   ```
   *Rationale*: Structured output enables programmatic quality decisions.

3. **Strict Scoring Guidance**
   ```
   Be strict: Only score 85+ if the research is truly comprehensive and well-sourced.
   ```
   *Rationale*: Prevents score inflation, ensures quality threshold is meaningful.

---

## Specialist Agent Prompts

### FINANCIAL_ANALYSIS_PROMPT

**Pattern**: Focused extraction with specific fields

```python
FINANCIAL_ANALYSIS_PROMPT = """
...
Focus on:
1. **Revenue**: Annual revenue, quarterly revenue, revenue growth
2. **Funding**: Total funding raised, valuation, recent rounds
3. **Profitability**: Operating income, net income, profit margins
4. **Market Value**: Market cap (if public), valuation (if private)
5. **Financial Metrics**: R&D spending, cash flow, any other metrics
...
"""
```

**Design Principles**:
- Numbered focus areas guide extraction priority
- Both public (market cap) and private (valuation) scenarios covered
- Open-ended "any other metrics" catches unexpected data

---

### ENHANCED_FINANCIAL_PROMPT

**Pattern**: Multi-section comprehensive analysis

```python
ENHANCED_FINANCIAL_PROMPT = """
...
**STRUCTURE YOUR ANALYSIS:**

### 1. Revenue Analysis
### 2. Profitability Analysis
### 3. Financial Health Indicators
### 4. Valuation Assessment
### 5. Risk Assessment
### 6. Financial Summary
...
"""
```

**Design Principles**:
- Section headers with `###` create scannable output
- Progressive depth (data → analysis → assessment)
- Summary section provides quick takeaways

---

### INVESTMENT_ANALYSIS_PROMPT

**Pattern**: Structured recommendation framework

```python
INVESTMENT_ANALYSIS_PROMPT = """
...
### 1. Investment Thesis
### 2. Business Quality Assessment
    **Competitive Moat Analysis:**
    Rate moat strength: [WIDE/NARROW/NONE]
### 3. Growth Assessment
    **Growth Stage:** [EARLY/GROWTH/MATURE/DECLINING]
### 4. Risk Analysis
    **Risk Level:** [LOW/MODERATE/HIGH/CRITICAL]
### 5. Valuation Assessment
    **Valuation Verdict:** [UNDERVALUED/FAIRLY VALUED/OVERVALUED]
### 6. Investment Recommendation
    **Rating:** [STRONG BUY/BUY/HOLD/SELL/STRONG SELL]
...
"""
```

**Design Principles**:
- Categorical ratings (WIDE/NARROW/NONE) enable aggregation
- Standard investment framework (thesis → moat → growth → risk → valuation)
- Actionable recommendation at end

---

## Prompt Patterns

### Pattern 1: Role + Task + Format

```python
PROMPT = """You are a {ROLE} {CONTEXT}.

{INPUT_DATA}

Task: {TASK_DESCRIPTION}

{OUTPUT_FORMAT}
"""
```

**Example**:
```python
"""You are a financial analyst reviewing search results about a company.

Company: {company_name}
Search Results: {search_results}

Task: Extract ALL financial data and metrics from these search results.

Output format:
- Revenue: [specific figures with years]
- Funding: [total raised, rounds, investors if mentioned]
...
"""
```

---

### Pattern 2: Structured Analysis

```python
PROMPT = """You are an expert {ROLE}.

{CONTEXT}

**STRUCTURE YOUR ANALYSIS:**

### 1. {Section 1}
{Sub-items}

### 2. {Section 2}
{Sub-items}

...

**REQUIREMENTS:**
- {Requirement 1}
- {Requirement 2}

Provide your analysis:
"""
```

---

### Pattern 3: Evaluation with Criteria

```python
PROMPT = """You are a {ROLE} evaluating {SUBJECT}.

{INPUT_DATA}

Please assess:

1. **{Criterion 1}** ({Weight} points):
   - {Sub-criterion}

2. **{Criterion 2}** ({Weight} points):
   - {Sub-criterion}

Provide your assessment in this exact JSON format:
{
  "{field}": <value>,
  ...
}
"""
```

---

## Output Format Strategies

### JSON Output

**When to Use**: Structured data needed for downstream processing

```python
"""
Provide your assessment in this exact JSON format:
{
  "quality_score": <number 0-100>,
  "missing_information": [
    "Specific information that's missing",
    ...
  ]
}
"""
```

**Benefits**:
- Machine-parseable
- Type-enforced (number vs string)
- Consistent structure

---

### Markdown Output

**When to Use**: Human-readable reports, flexible structure

```python
"""
Generate the following sections:

## Company Overview
A 2-3 sentence summary...

## Key Metrics
Extract and list all financial metrics in bullet format

## Main Products/Services
List the company's products/services (bullet points)
"""
```

**Benefits**:
- Human-readable
- Natural structure
- Flexible content length

---

### Categorical Output

**When to Use**: Classification tasks, ratings

```python
"""
Rate moat strength: [WIDE/NARROW/NONE]

**Growth Stage:** [EARLY/GROWTH/MATURE/DECLINING]

**Risk Level:** [LOW/MODERATE/HIGH/CRITICAL]
"""
```

**Benefits**:
- Easy aggregation
- Consistent vocabulary
- Enables filtering/sorting

---

## Temperature Guidelines

| Task Type | Temperature | Rationale |
|-----------|-------------|-----------|
| Fact extraction | 0.0 | Deterministic, consistent |
| Query generation | 0.7 | Creative, diverse |
| Analysis | 0.1 | Slight variation allowed |
| Synthesis | 0.1 | Consistent format needed |
| Recommendations | 0.2 | Balance insight/consistency |

---

## Prompt Optimization Tips

### 1. Be Specific About What to Extract

**Bad**:
```
Extract important information about the company.
```

**Good**:
```
Extract ALL numerical data: revenue, employees, funding, market share, etc.
Note the SOURCE and YEAR for each data point when available.
```

---

### 2. Provide Examples

**Bad**:
```
Generate search queries for the company.
```

**Good**:
```
Example output for a Brazilian company:
["Gerdau empresa overview", "Gerdau receita 2024", "Gerdau GGBR4 stock price"]

Now generate queries for {company_name}:
```

---

### 3. Set Explicit Constraints

**Bad**:
```
Analyze the search results.
```

**Good**:
```
Requirements:
- Be exhaustive - extract EVERY data point
- Cite the source for significant facts
- Note the language of original source
- Flag any conflicting information
- Be factual and objective
```

---

### 4. Define Output Structure

**Bad**:
```
Provide your analysis.
```

**Good**:
```
Provide your assessment in this exact JSON format:
{
  "quality_score": <number 0-100>,
  "missing_information": [...]
}
```

---

### 5. Handle Edge Cases

**Bad**:
```
Extract the company's revenue.
```

**Good**:
```
- Revenue: [amount in local currency AND USD, specify year]
  If not found, note "Revenue data not available in sources"
```

---

## Prompt Testing Checklist

- [ ] Does prompt specify role clearly?
- [ ] Is context/input data clearly labeled?
- [ ] Is task description unambiguous?
- [ ] Is output format explicitly defined?
- [ ] Are examples provided for complex outputs?
- [ ] Are edge cases handled?
- [ ] Is temperature appropriate for task?
- [ ] Does prompt avoid ambiguous terms?

---

**Related Documentation**:
- [Agent Contracts](../03-agents/AGENT_CONTRACTS.md)
- [Configuration](README.md)
- [Quality System](../08-quality-system/README.md)

---

**Last Updated**: December 2024
