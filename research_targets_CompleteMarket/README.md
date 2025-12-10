# Research Targets Repository v2.0

## Comprehensive Company Research Database

This repository contains organized research targets for company analysis, organized by **Region > Country > Sector > Company**.

---

## Quick Navigation

| Region | Countries | Sectors | Companies |
|--------|-----------|---------|-----------|
| [LATAM](#latin-america) | 20 | 15+ | 250+ |
| [North America](#north-america) | 3 | 12+ | 100+ |
| [Europe](#europe) | 15 | 12+ | 80+ |
| [Asia-Pacific](#asia-pacific) | 12 | 10+ | 70+ |
| [Middle East & Africa](#middle-east--africa) | 10 | 8+ | 40+ |

---

## Directory Structure

```
research_targets_v2/
|
+-- _global/                      # Cross-regional configurations
|   +-- _market_config.yaml       # Global market definitions
|   +-- _sectors.yaml             # Sector taxonomy
|   +-- _research_templates/      # YAML templates
|   +-- _priorities.yaml          # Research priority matrix
|
+-- latam/                        # Latin America
|   +-- _region_config.yaml
|   +-- south_america/
|   |   +-- argentina/
|   |   +-- brazil/
|   |   +-- chile/
|   |   +-- colombia/
|   |   +-- ecuador/
|   |   +-- paraguay/
|   |   +-- peru/
|   |   +-- uruguay/
|   |   +-- venezuela/
|   |   +-- bolivia/
|   +-- central_america/
|   |   +-- costa_rica/
|   |   +-- el_salvador/
|   |   +-- guatemala/
|   |   +-- honduras/
|   |   +-- nicaragua/
|   |   +-- panama/
|   |   +-- belize/
|   +-- caribbean/
|   |   +-- dominican_republic/
|   |   +-- puerto_rico/
|   |   +-- jamaica/
|   |   +-- cuba/
|   +-- mexico/
|
+-- north_america/
|   +-- usa/
|   +-- canada/
|
+-- europe/
|   +-- western_europe/
|   +-- southern_europe/
|   +-- northern_europe/
|   +-- eastern_europe/
|
+-- asia_pacific/
|   +-- east_asia/
|   +-- southeast_asia/
|   +-- south_asia/
|   +-- oceania/
|
+-- middle_east_africa/
|   +-- gulf_states/
|   +-- north_africa/
|   +-- sub_saharan_africa/
|
+-- _cross_sector/               # Sector-focused research
|   +-- telecommunications/
|   +-- aviation/
|   +-- fintech/
|   +-- ai_ml/
|   +-- renewable_energy/
```

---

## Sector Taxonomy

### Primary Sectors

| Code | Sector | Subsectors |
|------|--------|------------|
| `FIN` | Financial Services | Banking, Insurance, Asset Management, FinTech |
| `TEL` | Telecommunications | Mobile, Fixed, Internet, Media |
| `ENE` | Energy | Oil & Gas, Renewables, Utilities |
| `IND` | Industrials | Manufacturing, Construction, Engineering |
| `CON` | Consumer | Retail, Food & Beverage, Luxury |
| `TEC` | Technology | Software, Hardware, AI/ML, Cloud |
| `HEA` | Healthcare | Pharma, Medical Devices, Services |
| `MAT` | Materials | Mining, Chemicals, Steel, Forestry |
| `TRA` | Transportation | Airlines, Logistics, Ground Transport |
| `REA` | Real Estate | Commercial, Residential, REITs |
| `AGR` | Agriculture | Agribusiness, Food Processing |
| `MED` | Media & Entertainment | Broadcasting, Streaming, Publishing |
| `DIV` | Diversified | Conglomerates, Holdings |

---

## Research Priority Levels

| Level | Code | Description | Depth |
|-------|------|-------------|-------|
| P1 | `critical` | Strategic priority, full deep-dive | 50+ data points |
| P2 | `high` | Important targets, comprehensive | 30-50 data points |
| P3 | `medium` | Standard research | 20-30 data points |
| P4 | `low` | Basic overview | 10-20 data points |
| P5 | `monitor` | Watch list only | 5-10 data points |

---

## Company Profile YAML Schema

```yaml
company:
  # Identity
  name: "Company Name"
  legal_name: "Full Legal Entity Name"
  ticker: "TICK"
  exchange: "NYSE/NASDAQ/B3/BMV"
  isin: "ISIN Code"

  # Classification
  sector: "Primary Sector"
  subsector: "Subsector"
  industry_codes:
    sic: "XXXX"
    naics: "XXXXXX"
    gics: "XXXXXXXX"

  # Geography
  country: "Country"
  region: "Region"
  headquarters: "City, Country"

  # Corporate
  founded: YYYY
  website: "https://..."
  ownership_type: "public|private|state|family"
  controlling_entity: "Family/Entity Name"

  # Scale
  market_cap_usd: 0
  revenue_usd: 0
  employees: 0

  # Operations
  operating_countries: []
  business_segments: []
  key_subsidiaries: []

research:
  priority: "P1|P2|P3|P4|P5"
  depth: "deep|comprehensive|standard|quick"
  focus_areas: []
  priority_queries: []
  priority_sources: []
  kpis_to_find: []
  data_gaps: []

competitive:
  direct_competitors: []
  indirect_competitors: []
  market_position: ""
  market_share: 0

notes: |
  Additional context and research notes.
```

---

## How to Use

### 1. Find Companies by Region
Navigate to the region folder (e.g., `latam/south_america/brazil/`)

### 2. Find Companies by Sector
Use the `_cross_sector/` directory for sector-focused views

### 3. Research Priority
Check `_global/_priorities.yaml` for prioritized target lists

### 4. Add New Companies
Use templates in `_global/_research_templates/`

---

## Statistics

- **Total Research Targets**: 500+ companies
- **Regions Covered**: 5
- **Countries Covered**: 60+
- **Sectors Covered**: 13 primary, 50+ subsectors
- **Last Updated**: 2024-12

---

## Related Documentation

- [Research Methodology](../docs/03-agents/AGENT_DEVELOPMENT_GUIDE.md)
- [Data Sources](../docs/05-integrations/README.md)
- [Output Format](../outputs/research/README.md)
