# Quick Start Guide

Get your first company research report in 5 minutes.

## Prerequisites

- Completed [Installation](INSTALLATION.md)
- Valid `ANTHROPIC_API_KEY` in `.env`
- (Recommended) Valid `TAVILY_API_KEY` for better search

## Option 1: Simple CLI (Fastest)

```bash
# Research any company
python run_research.py "Microsoft"
```

**Output**:
```
Researching: Microsoft
[1/5] Generating search queries...
[2/5] Executing searches...
[3/5] Running specialist agents...
[4/5] Synthesizing report...
[5/5] Saving report...

Research complete!
Quality Score: 88/100
Cost: $0.0386
Time: 2m 34s
Report: outputs/research/microsoft/00_full_report.md
```

## Option 2: Research Script (More Control)

```bash
# Standard research
python scripts/research/cli.py research "Tesla"

# With options
python scripts/research/cli.py research "Tesla" --depth comprehensive --format pdf
```

## Option 3: Python API

```python
from company_researcher import execute_research, ResearchDepth

# Run research
result = execute_research(
    company_name="Apple",
    depth=ResearchDepth.STANDARD
)

# Access results
print(f"Quality: {result.quality_score}/100")
print(f"Cost: ${result.total_cost:.4f}")
print(f"Report: {result.report_path}")
```

## Option 4: LangGraph Studio (Visual)

```bash
# Start LangGraph Studio
langgraph studio

# Open browser to http://localhost:8000
# Input company name in the UI
# Watch agents execute in real-time
```

## Understanding the Output

After research completes, find your report at:

```
outputs/research/<company_name>/
├── 00_full_report.md       # Complete report
├── 01_executive_summary.md # Key findings
├── 02_company_overview.md  # Background
├── 03_financials.md        # Financial analysis
├── 04_market_position.md   # Market position
├── 05_competitive_analysis.md # Competitors
├── 06_strategy.md          # Strategic outlook
├── 07_sources.md           # All sources
└── metrics.json            # Quality & cost metrics
```

## Research Depth Levels

| Depth | Time | Cost | Sources | Use Case |
|-------|------|------|---------|----------|
| `quick` | 1-2 min | ~$0.03 | 10-15 | Fast overview |
| `standard` | 2-3 min | ~$0.08 | 20-30 | Default, balanced |
| `comprehensive` | 4-6 min | ~$0.15 | 40-50 | Deep analysis |

## Batch Research

Research multiple companies from a YAML file:

```bash
# Create target file
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

## Quality Scores

The system targets 85%+ quality. Scores measure:

| Component | Weight | Description |
|-----------|--------|-------------|
| Completeness | 30% | All sections present |
| Financial Data | 25% | Revenue, profitability, metrics |
| Market Analysis | 20% | Position, trends, share |
| Source Quality | 15% | Diverse, recent sources |
| Coherence | 10% | No contradictions |

## Cost Management

Monitor and control costs:

```python
from company_researcher import config

# Set cost limit
config.max_cost_per_research = 0.10  # $0.10 max

# Use cheaper model for drafts
config.llm_model = "claude-3-haiku-20240307"
```

## Troubleshooting

### Low Quality Score

```
Quality Score: 65/100 (below threshold)
```

**Solution**: System will automatically iterate. If still low:
- Use `comprehensive` depth
- Add more API keys for financial data
- Check if company has limited online presence

### Slow Research

**Solution**:
- Use `quick` depth for faster results
- Check network connectivity
- Verify API rate limits not exceeded

### Missing Financial Data

**Solution**:
- Add `ALPHA_VANTAGE_API_KEY` or `FMP_API_KEY`
- For private companies, financial data may be limited
- Check if company has SEC filings

## Next Steps

1. **Customize Research**: See [Configuration Guide](../06-configuration/README.md)
2. **Add Integrations**: See [Integrations](../05-integrations/README.md)
3. **Understand Flow**: See [Workflows](../04-workflows/README.md)
4. **Develop Agents**: See [Agent Development](../03-agents/README.md)

---

**Last Updated**: December 2024
