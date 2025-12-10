# Scripts & CLI Tools

Documentation for research scripts and command-line tools.

## Overview

```
scripts/
├── research/              # Main research orchestration
│   ├── cli.py             # Command-line interface
│   ├── researcher.py      # ComprehensiveResearcher class
│   ├── search_provider.py # Multi-provider search
│   ├── financial_provider.py # Financial data
│   ├── config_loader.py   # YAML configuration
│   └── research_config.yaml # Configuration file
├── run_research.py        # Quick research script
└── hello_research.py      # Getting started script
```

## Quick Research Scripts

### run_research.py

Simple entry point for single company research:

```bash
# Basic usage
python run_research.py "Microsoft"

# With options
python run_research.py "Tesla" --depth comprehensive
```

### hello_research.py

Getting started demonstration:

```bash
python hello_research.py "Apple"
```

## CLI Tool (cli.py)

Full-featured command-line interface.

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Verify installation
python scripts/research/cli.py --help
```

### Commands

#### research

Research a single company:

```bash
python scripts/research/cli.py research "Microsoft"

# With options
python scripts/research/cli.py research "Tesla" \
    --depth comprehensive \
    --format pdf \
    --iterations 3 \
    --quality-threshold 90 \
    --output-dir ./reports
```

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--depth` | standard | quick, standard, comprehensive |
| `--format` | md | md, pdf, excel |
| `--iterations` | 2 | Maximum iterations |
| `--quality-threshold` | 85 | Minimum quality score |
| `--output-dir` | outputs/research | Output directory |
| `--config` | research_config.yaml | Config file |
| `--no-cache` | False | Disable caching |
| `--verbose` | False | Verbose logging |

#### market

Batch research from YAML file:

```bash
# Create market file
cat > targets.yaml << EOF
market: Tech Giants
companies:
  - name: Microsoft
  - name: Apple
  - name: Google
EOF

# Run batch research
python scripts/research/cli.py market targets.yaml
```

**Market File Format:**

```yaml
market: Tech Giants
description: Major technology companies
companies:
  - name: Microsoft
    ticker: MSFT
  - name: Apple
    ticker: AAPL
  - name: Google
    ticker: GOOGL
    aliases:
      - Alphabet
```

#### compare

Compare multiple companies:

```bash
python scripts/research/cli.py compare \
    --companies "Microsoft,Apple,Google" \
    --output comparison_report.md
```

### Output

CLI produces:

```
outputs/research/<company>/
├── 00_full_report.md       # Complete report
├── 01_executive_summary.md # Executive summary
├── 02_company_overview.md  # Company background
├── 03_financials.md        # Financial analysis
├── 04_market_position.md   # Market position
├── 05_competitive_analysis.md # Competitors
├── 06_strategy.md          # Strategic outlook
├── 07_sources.md           # Source citations
├── metrics.json            # Quality metrics
└── financial_data.json     # Raw financial data
```

## ComprehensiveResearcher Class

**Location**: `scripts/research/researcher.py`

Main research orchestration class with 1500+ lines.

### Class Structure

```python
class ComprehensiveResearcher:
    def __init__(self, config: ResearchConfig):
        self.config = config
        self.search_provider = SearchProvider(config)
        self.financial_provider = FinancialProvider(config)
        self.llm_client = get_anthropic_client(config)

    async def research_company(self, company: str) -> ResearchResult:
        """Research a single company."""
        pass

    async def research_market(self, market_file: str) -> List[ResearchResult]:
        """Batch research from market file."""
        pass
```

### Key Methods

#### research_company

```python
async def research_company(self, company: str) -> ResearchResult:
    """
    Research a company with iterative gap-filling.

    Flow:
    1. Generate search queries
    2. Execute searches (free first, then Tavily)
    3. Analyze with Claude
    4. Detect gaps and quality score
    5. Iterate if quality < threshold
    6. Generate reports
    """
```

#### _generate_queries

```python
def _generate_queries(self, company: str, iteration: int) -> List[str]:
    """
    Generate search queries based on iteration.

    Iteration 0: General queries
    Iteration 1+: Targeted gap-filling queries
    """
```

#### _execute_searches

```python
async def _execute_searches(
    self,
    queries: List[str]
) -> List[SearchResult]:
    """
    Execute searches with fallback.

    1. Try DuckDuckGo (free)
    2. Add Tavily refinement if enabled
    3. Deduplicate results
    """
```

#### _analyze_company

```python
async def _analyze_company(
    self,
    company: str,
    results: List[SearchResult]
) -> Analysis:
    """
    Analyze company using Claude.

    Returns structured analysis with:
    - Company overview
    - Financial metrics
    - Market position
    - Products/services
    - Competitors
    """
```

#### _detect_gaps

```python
def _detect_gaps(self, analysis: Analysis) -> List[str]:
    """
    Detect missing information.

    Pattern-based detection:
    - Missing sections
    - Empty metrics
    - Low confidence areas
    """
```

### Usage Example

```python
from scripts.research.researcher import ComprehensiveResearcher
from company_researcher.config import ResearchConfig

# Initialize
config = ResearchConfig.from_env()
researcher = ComprehensiveResearcher(config)

# Research company
result = await researcher.research_company("Microsoft")

# Access results
print(f"Quality: {result.quality_score}")
print(f"Cost: ${result.total_cost:.4f}")
print(f"Report: {result.report_path}")
```

## Search Provider

**Location**: `scripts/research/search_provider.py`

Multi-provider search with fallback.

### Features

- Multiple search providers
- Automatic fallback
- Rate limiting
- Result deduplication
- Caching

### Implementation

```python
class SearchProvider:
    def __init__(self, config: ResearchConfig):
        self.config = config
        self.tavily = TavilyClient(config) if config.tavily_api_key else None
        self.duckduckgo = DuckDuckGoClient()

    async def search(
        self,
        query: str,
        strategy: str = "free_first"
    ) -> List[SearchResult]:
        """
        Execute search with strategy.

        Strategies:
        - free_first: DuckDuckGo, then Tavily
        - tavily_only: Tavily only
        - auto: Choose based on results
        """
```

## Financial Provider

**Location**: `scripts/research/financial_provider.py`

Financial data collection.

### Implementation

```python
class FinancialProvider:
    def __init__(self, config: ResearchConfig):
        self.yfinance = YFinanceClient()
        self.alpha_vantage = AlphaVantageClient(config)
        self.fmp = FMPClient(config)

    async def get_financials(self, company: str) -> FinancialData:
        """
        Get financial data from multiple sources.

        Priority:
        1. yfinance (always available)
        2. Alpha Vantage (if key provided)
        3. FMP (if key provided)
        """
```

## Configuration Loader

**Location**: `scripts/research/config_loader.py`

YAML configuration loading.

### Usage

```python
from scripts.research.config_loader import load_config

# Load from file
config = load_config("research_config.yaml")

# Merge with CLI args
config = config.merge_cli(args)
```

## Persistence

**Location**: `scripts/research/persistence.py`

Checkpoint persistence for resume capability.

### Features

- Save state at checkpoints
- Resume from interruption
- State versioning
- Cleanup old checkpoints

### Usage

```python
from scripts.research.persistence import CheckpointManager

checkpoint = CheckpointManager("microsoft_research")

# Save state
checkpoint.save(state)

# Resume
state = checkpoint.load()
```

---

**Related Documentation**:
- [Quick Start](../01-overview/QUICKSTART.md)
- [Configuration](../06-configuration/)
- [Workflows](../04-workflows/)

---

**Last Updated**: December 2024
