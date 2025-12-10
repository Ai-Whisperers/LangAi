# Customer Intelligence Platform - Research Targets

## Overview

This folder contains research targets for our **Customer Intelligence Platform** business - companies and organizations that can benefit from our social media comment extraction and analysis services.

## Our Service Stack

```
┌─────────────────────────────────────────────────────────────────┐
│              CUSTOMER INTELLIGENCE PLATFORM                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  MODULE 1: SOCIAL MEDIA COMMENT EXTRACTOR                       │
│  ─────────────────────────────────────────                      │
│  • Extract comments from target company profiles                 │
│  • Extract competitor comments for benchmarking                  │
│  • Multi-platform support (Facebook, Instagram, Twitter, etc.)  │
│  • Historical data extraction                                    │
│                                                                  │
│  MODULE 2: COMMENT ANALYZER (36 Data Points)                    │
│  ───────────────────────────────────────────                    │
│  • NPS Categorization & Scoring                                 │
│  • Emotion Detection (7 dimensions)                             │
│  • Pain Point Extraction (3 levels with drivers)                │
│  • Churn Risk & Urgency Scoring                                 │
│  • Competitive Intelligence                                      │
│  • Quality Confidence Metrics                                    │
│                                                                  │
│  MODULE 3: REPORTS & DELIVERABLES                               │
│  ────────────────────────────────                               │
│  • Customer Feedback Analysis Reports                           │
│  • Competitive Intelligence Reports                              │
│  • Industry Benchmark Studies                                    │
│  • Custom Internal Data Analysis                                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
customer_intelligence_platform/
├── README.md                    # This file
├── _config.yaml                 # Master configuration
├── _service_offerings.yaml      # Detailed service packages
├── _prospect_criteria.yaml      # How we prioritize prospects
│
├── verticals/                   # Target companies by industry
│   ├── telecommunications/      # Telcos (high priority)
│   ├── financial_services/      # Banks, FinTech, Insurance
│   ├── retail/                  # Retail chains, E-commerce
│   ├── healthcare/              # Hospitals, Pharma, Clinics
│   ├── conglomerates/           # Multi-sector groups
│   ├── hospitality/             # Hotels, Restaurants, Tourism
│   ├── automotive/              # Dealers, Brands
│   ├── education/               # Universities, EdTech
│   └── utilities/               # Energy, Water, Services
│
├── regions/                     # Geographic organization
│   ├── paraguay/                # Primary market
│   ├── argentina/               # Expansion market
│   ├── brazil/                  # Large market opportunity
│   ├── chile/                   # Advanced market
│   └── central_america/         # Regional opportunity
│
├── campaigns/                   # Active sales campaigns
│   ├── _active_campaigns.yaml
│   └── {campaign_name}/
│
└── competitive_landscape/       # Our competitors
    └── _competitors.yaml
```

## Data Points We Extract (36 Columns)

| Category | Fields |
|----------|--------|
| **Basic** | ID, NPS Category, Score, Comment, Length, Word Count |
| **Emotions** | Satisfaction, Frustration, Anger, Trust, Disappointment, Confusion, Anticipation |
| **Scoring** | Sentiment Score, Churn Risk, Urgency |
| **Pain Points** | PP1-3 (Keyword, Category, Severity, Principal, Impact, Drivers) |
| **Actions** | Follow-up Required, Suggested Department, Customer Intent |
| **Analysis** | Root Cause, Main Themes, Products, Features, Competitors Mentioned |
| **Quality** | Sentiment Confidence, Ambiguity Score, Human Review Required, Uncertainty Reasons |
| **Meta** | Priority Level, Language, Analysis Date |

## Ideal Customer Profile (ICP)

### Tier 1 - High Value Targets
- **Telecommunications**: High comment volume, competitive market, churn-sensitive
- **Banks/FinTech**: Trust-dependent, regulatory pressure, customer experience focus
- **Large Retailers**: High transaction volume, multiple touchpoints, brand reputation

### Tier 2 - Strong Fit
- **Healthcare**: Patient experience critical, reputation sensitive
- **Conglomerates**: Multiple brands to monitor, competitive intelligence needs
- **Insurance**: Claims sentiment, customer retention focus

### Tier 3 - Growth Potential
- **Education**: Student/parent feedback, competitive landscape
- **Hospitality**: Review-dependent, reputation management
- **Utilities**: Service complaints, regulatory visibility

## Quick Start

1. Review `_config.yaml` for master settings
2. Check `_prospect_criteria.yaml` for prioritization logic
3. Browse `verticals/` for industry-specific targets
4. See `regions/paraguay/` for primary market focus
