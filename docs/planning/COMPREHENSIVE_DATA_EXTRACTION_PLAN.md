# Comprehensive Data Extraction Plan

## Objective
Extract ALL publicly available company data regardless of industry type.

---

## Phase 1: Universal Search Queries

### 1.1 Add Dedicated Search Query Templates

```python
UNIVERSAL_QUERIES = {
    # Leadership
    "leadership": '"{company}" CEO CFO executive team management 2024',
    "board": '"{company}" board of directors chairman',

    # Financial Deep Dive
    "financials_detailed": '"{company}" annual report revenue EBITDA net income 2024',
    "investor_presentation": '"{company}" investor presentation earnings call Q4 2024',
    "sec_filings": '"{parent_company}" 10-K 20-F SEC filing {year}',

    # Operational
    "company_history": '"{company}" founded history headquarters employees',
    "capex_debt": '"{company}" capital expenditure CapEx debt leverage ratio',
}

TELECOM_QUERIES = {
    "arpu_churn": '"{company}" ARPU churn rate subscriber metrics',
    "spectrum": '"{company}" spectrum license MHz frequency allocation',
    "network_coverage": '"{company}" 4G 5G coverage network rollout',
    "prepaid_postpaid": '"{company}" prepaid postpaid subscriber mix',
}

SAAS_QUERIES = {
    "saas_metrics": '"{company}" ARR MRR net revenue retention',
    "customer_metrics": '"{company}" CAC LTV customer acquisition cost',
    "growth_metrics": '"{company}" NDR logo retention expansion revenue',
}

RETAIL_QUERIES = {
    "retail_metrics": '"{company}" same-store sales comparable sales',
    "store_count": '"{company}" store count locations expansion',
}

MANUFACTURING_QUERIES = {
    "production": '"{company}" production capacity utilization',
    "supply_chain": '"{company}" supply chain inventory days',
}
```

### 1.2 Industry Detection
```python
INDUSTRY_QUERY_MAP = {
    "Telecommunications": TELECOM_QUERIES,
    "Software": SAAS_QUERIES,
    "SaaS": SAAS_QUERIES,
    "Retail": RETAIL_QUERIES,
    "Manufacturing": MANUFACTURING_QUERIES,
    "Consumer Goods": RETAIL_QUERIES,
}
```

---

## Phase 2: Enhanced Metrics Extraction

### 2.1 Universal Financial Patterns

```python
# ===== UNIVERSAL FINANCIAL =====

# Net Income / Profit
net_income_patterns = [
    r'net\s+income[:\s]+\$?([\d,.]+)\s*(billion|million|B|M)',
    r'net\s+profit[:\s]+\$?([\d,.]+)\s*(billion|million)',
    r'profit[:\s]+\$?([\d,.]+)\s*(billion|million)',
    r'earned\s+\$?([\d,.]+)\s*(billion|million)',
]

# CapEx
capex_patterns = [
    r'(?:capital\s+expenditure|capex)[:\s]+\$?([\d,.]+)\s*(billion|million)',
    r'\$?([\d,.]+)\s*(billion|million)\s*(?:in\s+)?(?:capital\s+expenditure|capex)',
    r'invested\s+\$?([\d,.]+)\s*(billion|million)\s*in\s+(?:infrastructure|network)',
]

# Debt / Leverage
debt_patterns = [
    r'(?:total\s+)?debt[:\s]+\$?([\d,.]+)\s*(billion|million)',
    r'net\s+debt[:\s]+\$?([\d,.]+)\s*(billion|million)',
    r'leverage\s+ratio[:\s]+([\d.]+)x',
    r'debt[/-]to[/-](?:equity|ebitda)[:\s]+([\d.]+)',
]

# Operating Income
operating_income_patterns = [
    r'operating\s+income[:\s]+\$?([\d,.]+)\s*(billion|million)',
    r'EBIT[:\s]+\$?([\d,.]+)\s*(billion|million)',
]

# Free Cash Flow
fcf_patterns = [
    r'free\s+cash\s+flow[:\s]+\$?([\d,.]+)\s*(billion|million)',
    r'FCF[:\s]+\$?([\d,.]+)\s*(billion|million)',
    r'operating\s+cash\s+flow[:\s]+\$?([\d,.]+)\s*(billion|million)',
]
```

### 2.2 Telecom-Specific Patterns

```python
# ===== TELECOM SPECIFIC =====

# ARPU
arpu_patterns = [
    r'ARPU[:\s]+\$?([\d.]+)',
    r'average\s+revenue\s+per\s+user[:\s]+\$?([\d.]+)',
    r'\$?([\d.]+)\s*(?:per\s+)?(?:user|subscriber|month)\s*ARPU',
    r'blended\s+ARPU[:\s]+\$?([\d.]+)',
    r'mobile\s+ARPU[:\s]+\$?([\d.]+)',
]

# Churn Rate
churn_patterns = [
    r'churn[:\s]+(?:rate[:\s]+)?([\d.]+)%',
    r'([\d.]+)%\s*(?:monthly\s+)?churn',
    r'subscriber\s+churn[:\s]+([\d.]+)%',
    r'customer\s+churn[:\s]+([\d.]+)%',
]

# Prepaid/Postpaid Mix
subscriber_mix_patterns = [
    r'prepaid[:\s]+([\d.]+)%',
    r'postpaid[:\s]+([\d.]+)%',
    r'([\d.]+)%\s*prepaid',
    r'([\d.]+)%\s*postpaid',
    r'prepaid\s+subscribers?[:\s]+([\d,.]+)\s*(million|M)?',
    r'postpaid\s+subscribers?[:\s]+([\d,.]+)\s*(million|M)?',
]

# Spectrum Holdings
spectrum_patterns = [
    r'([\d]+)\s*MHz\s*(?:of\s+)?spectrum',
    r'spectrum[:\s]+([\d]+)\s*MHz',
    r'(\d+)\s*MHz\s+(?:in\s+the\s+)?(\d+)\s*(?:GHz|MHz)\s+band',
    r'licensed\s+spectrum[:\s]+([\d]+)\s*MHz',
]

# 5G Coverage
coverage_5g_patterns = [
    r'5G\s+coverage[:\s]+([\d.]+)%',
    r'([\d.]+)%\s*(?:of\s+)?(?:population|territory)\s*(?:with\s+)?5G',
    r'5G\s+(?:available\s+)?(?:in|to)\s+([\d]+)\s*cities',
]

# Data Traffic
data_traffic_patterns = [
    r'data\s+(?:traffic|usage)[:\s]+([\d.]+)\s*(PB|TB|GB)',
    r'([\d.]+)\s*(PB|TB)\s*(?:of\s+)?(?:monthly\s+)?data\s+traffic',
]
```

### 2.3 SaaS-Specific Patterns

```python
# ===== SAAS SPECIFIC =====

# ARR/MRR
arr_patterns = [
    r'ARR[:\s]+\$?([\d,.]+)\s*(billion|million|B|M)',
    r'annual\s+recurring\s+revenue[:\s]+\$?([\d,.]+)\s*(billion|million)',
    r'MRR[:\s]+\$?([\d,.]+)\s*(million|thousand|K)',
]

# Net Revenue Retention
nrr_patterns = [
    r'(?:net\s+)?(?:revenue\s+)?retention[:\s]+([\d]+)%',
    r'NRR[:\s]+([\d]+)%',
    r'NDR[:\s]+([\d]+)%',  # Net Dollar Retention
    r'([\d]+)%\s*(?:net\s+)?(?:dollar\s+)?retention',
]

# CAC / LTV
cac_ltv_patterns = [
    r'CAC[:\s]+\$?([\d,.]+)',
    r'customer\s+acquisition\s+cost[:\s]+\$?([\d,.]+)',
    r'LTV[:\s]+\$?([\d,.]+)',
    r'lifetime\s+value[:\s]+\$?([\d,.]+)',
    r'LTV[:/]CAC[:\s]+([\d.]+)',
]

# Logo Retention
logo_retention_patterns = [
    r'(?:gross\s+)?(?:logo\s+)?retention[:\s]+([\d]+)%',
    r'customer\s+retention[:\s]+([\d]+)%',
]
```

### 2.4 Leadership Extraction

```python
# ===== LEADERSHIP =====

# CEO
ceo_patterns = [
    r'(?:CEO|Chief\s+Executive\s+Officer)[:\s,]+([A-Z][a-z]+\s+[A-Z][a-z]+)',
    r'([A-Z][a-z]+\s+[A-Z][a-z]+)[,\s]+(?:the\s+)?CEO',
    r'led\s+by\s+(?:CEO\s+)?([A-Z][a-z]+\s+[A-Z][a-z]+)',
    r'CEO\s+([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
]

# CFO
cfo_patterns = [
    r'(?:CFO|Chief\s+Financial\s+Officer)[:\s,]+([A-Z][a-z]+\s+[A-Z][a-z]+)',
    r'([A-Z][a-z]+\s+[A-Z][a-z]+)[,\s]+(?:the\s+)?CFO',
]

# CTO
cto_patterns = [
    r'(?:CTO|Chief\s+Technology\s+Officer)[:\s,]+([A-Z][a-z]+\s+[A-Z][a-z]+)',
]

# Founded Year
founded_patterns = [
    r'founded\s+(?:in\s+)?(\d{4})',
    r'established\s+(?:in\s+)?(\d{4})',
    r'since\s+(\d{4})',
    r'(?:founded|established)[:\s]+(\d{4})',
]

# Headquarters
hq_patterns = [
    r'headquartered\s+in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?(?:,\s+[A-Z]{2})?)',
    r'headquarters[:\s]+([A-Z][a-z]+(?:,\s+[A-Z][a-z]+)?)',
    r'based\s+in\s+([A-Z][a-z]+(?:,\s+[A-Z][a-z]+)?)',
]
```

---

## Phase 3: Structured Output Schema

### 3.1 Enhanced metrics.json Structure

```json
{
  "financial": {
    "revenue_usd_millions": null,
    "revenue_usd_billions": null,
    "ebitda_usd_millions": null,
    "net_income_usd_millions": null,
    "operating_income_usd_millions": null,
    "free_cash_flow_usd_millions": null,
    "capex_usd_millions": null,
    "total_debt_usd_millions": null,
    "net_debt_usd_millions": null,
    "leverage_ratio": null,
    "growth_rate_percent": null,
    "gross_margin_percent": null,
    "operating_margin_percent": null,
    "net_margin_percent": null,
    "revenue_warning": null
  },
  "operational": {
    "customers": null,
    "employees": null,
    "coverage_percent": null,
    "stores_locations": null
  },
  "market": {
    "market_share_percent": null,
    "market_ranking": null
  },
  "telecom": {
    "arpu_usd": null,
    "churn_rate_percent": null,
    "prepaid_percent": null,
    "postpaid_percent": null,
    "prepaid_subscribers": null,
    "postpaid_subscribers": null,
    "spectrum_mhz": null,
    "coverage_4g_percent": null,
    "coverage_5g_percent": null,
    "data_traffic_pb": null
  },
  "saas": {
    "arr_usd_millions": null,
    "mrr_usd_thousands": null,
    "nrr_percent": null,
    "gross_retention_percent": null,
    "cac_usd": null,
    "ltv_usd": null,
    "ltv_cac_ratio": null
  },
  "leadership": {
    "ceo": null,
    "cfo": null,
    "cto": null,
    "chairman": null
  },
  "company_info": {
    "founded_year": null,
    "headquarters": null,
    "legal_name": null,
    "stock_ticker": null,
    "stock_exchange": null
  },
  "data_freshness": {
    "years_mentioned": [],
    "most_recent_year": null,
    "quarters_mentioned": [],
    "warning": null
  }
}
```

---

## Phase 4: Implementation Tasks

### Task 1: Add Industry-Specific Query Generation
**File:** `run_research.py` - `_build_search_queries()`
**Changes:**
- Detect industry from profile
- Add universal queries (leadership, financials, history)
- Add industry-specific queries based on detection
- Increase query count for comprehensive coverage

### Task 2: Enhance Metrics Extraction
**File:** `run_research.py` - `_extract_metrics_from_report()`
**Changes:**
- Add all new regex patterns from Phase 2
- Add industry-specific extraction based on profile.industry
- Add leadership extraction
- Add company info extraction

### Task 3: Update Output Schema
**File:** `run_research.py` - `_extract_metrics_from_report()`
**Changes:**
- Return enhanced metrics structure
- Include industry-specific sections only when relevant
- Add null handling for missing data

### Task 4: Update Comparison Report
**File:** `run_research.py` - `_generate_comparison_report()`
**Changes:**
- Add new comparison tables for:
  - Leadership comparison
  - Industry-specific metrics (ARPU, ARR, etc.)
  - Debt/leverage comparison

### Task 5: Add Data Quality Scoring
**New logic to score data completeness:**
- Universal fields (revenue, employees, CEO): +10 each
- Industry-specific fields: +5 each
- Data freshness (2024+): +10
- Multiple sources confirming same value: +5

---

## Phase 5: Validation & Testing

### Test Cases
1. **Telecom company** - Should extract ARPU, churn, spectrum
2. **SaaS company** - Should extract ARR, NRR, CAC/LTV
3. **Retail company** - Should extract store count, same-store sales
4. **Conglomerate** - Should handle multiple business segments

### Quality Metrics
- **Data Coverage**: % of fields populated
- **Data Freshness**: % of data from current year
- **Source Diversity**: Number of unique sources per metric

---

## Estimated Implementation Time

| Phase | Tasks | Complexity |
|-------|-------|------------|
| Phase 1 | Query templates | Low |
| Phase 2 | Regex patterns | Medium |
| Phase 3 | Schema updates | Low |
| Phase 4 | Code implementation | High |
| Phase 5 | Testing | Medium |

---

## Priority Order

1. **Universal financials** (Net Income, CapEx, Debt) - Applies to ALL companies
2. **Leadership extraction** (CEO, CFO) - High value, easy to find
3. **Founded year / HQ** - Basic info often missing
4. **Telecom metrics** (ARPU, Churn) - Current use case
5. **SaaS metrics** (ARR, NRR) - Future use case
6. **Retail/Manufacturing** - Lower priority

---

## Next Steps

1. [ ] Implement Phase 1: Add query templates
2. [ ] Implement Phase 2: Add extraction patterns
3. [ ] Implement Phase 3: Update output schema
4. [ ] Test with Tigo Paraguay (telecom)
5. [ ] Test with a SaaS company
6. [ ] Refine based on results
