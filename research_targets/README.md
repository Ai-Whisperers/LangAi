# Research Targets

This folder contains company profiles for batch research. Each YAML file defines a company to research, and related companies can be grouped together for comparative analysis.

## Folder Structure

```
research_targets/
  README.md                         # This file
  latam_telecoms/                   # Latin America Telecommunications
    _market.yaml                    # Market-level configuration
    _gap_analysis.md                # Research gaps analysis
    # Holding Companies
    america_movil.yaml              # Claro parent (NYSE: AMX)
    millicom.yaml                   # Tigo parent (NASDAQ: TIGO)
    telecom_argentina.yaml          # Personal parent (NYSE: TEO)
    # Paraguay Operators
    tigo_paraguay.yaml              # Market leader (~42%)
    personal_paraguay.yaml          # Second player (~30%)
    claro_paraguay.yaml             # Third player (~10-11%)
    copaco.yaml                     # State telecom
    vox_paraguay.yaml               # MVNO
  latam_aeronautics/                # Latin America Aeronautics & Aviation
    _market.yaml                    # Market-level configuration
    # Airlines
    latam_airlines.yaml             # Largest LATAM airline (NYSE: LTM)
    avianca.yaml                    # Colombian flag carrier (NYSE: AVH)
    aeromexico.yaml                 # Mexican flag carrier
    gol.yaml                        # Brazilian low-cost (NYSE: GOL)
    azul.yaml                       # Brazilian airline (NYSE: AZUL)
    copa.yaml                       # Panama hub carrier (NYSE: CPA)
    volaris.yaml                    # Mexican ULCC (NYSE: VLRS)
    # Aircraft Manufacturing
    embraer.yaml                    # Brazilian manufacturer (NYSE: ERJ)
    # Ground Services & Check-in
    sita.yaml                       # Aviation IT / Check-in systems
    swissport.yaml                  # Ground handling
    amadeus.yaml                    # Travel tech / DCS systems
    menzies_aviation.yaml           # Ground handling
    dnata.yaml                      # Ground handling / catering
```

## Usage

### Research a single company:
```bash
python run_research.py --profile research_targets/latam_telecoms/tigo_paraguay.yaml
```

### Research all companies in a market:
```bash
python run_research.py --market research_targets/latam_telecoms/
```

### Research with comparison report:
```bash
python run_research.py --market research_targets/latam_telecoms/ --compare
```

### Research with multiple output formats:
```bash
python run_research.py --market research_targets/latam_telecoms/ --formats md,json,pdf,excel
```

## Profile Format

Each company profile is a YAML file with the following structure:

```yaml
company:
  name: "Company Name"
  legal_name: "Legal Entity Name"
  website: "https://company.com"
  industry: "Telecommunications"
  country: "Country"
  parent_company: "Parent Corp"
  parent_ticker: "TICK"
  market_position:
    rank: 1
    market_share: "42%"
  services:
    - "Mobile voice and data"
    - "Fixed broadband"

competitors:
  direct:
    - "Competitor 1"
    - "Competitor 2"

research:
  focus_areas:
    - market
    - financial
    - competitor
  priority_queries:
    - "Company market share 2024"
    - "Company revenue"

notes: |
  Any special research notes or context.
```

## Output Structure

Research outputs are organized in:

```
outputs/
  reports/
    markdown/     # Detailed .md reports
    pdf/          # PDF reports (requires reportlab)
    excel/        # Excel workbooks (requires openpyxl)
    pptx/         # PowerPoint (requires python-pptx)
  comparisons/    # Market comparison reports
  data/
    raw/          # Raw search results
    processed/    # JSON data exports
  logs/           # Execution logs
```
