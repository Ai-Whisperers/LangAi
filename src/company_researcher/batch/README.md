# Batch Research Module

Research multiple companies in parallel with intelligent caching, progress tracking, and comparative analysis.

## Features

- **Parallel Processing**: Research 5-100+ companies simultaneously
- **Intelligent Caching**: Automatic cache hit detection for cost optimization
- **Progress Tracking**: Real-time progress updates with cache status
- **Comparative Analysis**: Side-by-side company comparison reports
- **Cost Tracking**: Detailed cost breakdown per company and provider
- **Flexible Output**: Individual reports + comparative summary + JSON metrics

## Quick Start

### CLI Usage

```bash
# Research companies from command line
python scripts/batch_research.py Tesla Apple Microsoft Amazon

# Research from file (one company per line)
python scripts/batch_research.py --file companies.txt

# Custom configuration
python scripts/batch_research.py \
    --workers 10 \
    --output results/ \
    --enhanced \
    Tesla Apple Microsoft
```

### Python API Usage

```python
from company_researcher.batch import BatchResearcher

# Initialize researcher
researcher = BatchResearcher(
    max_workers=5,           # Parallel workers
    timeout_per_company=300, # 5 min timeout per company
    enable_cache=True        # Use caching
)

# Research batch
result = researcher.research_batch(
    companies=["Tesla", "Apple", "Microsoft"],
    use_enhanced_workflow=False,
    show_progress=True
)

# Print summary
summary = result.get_summary()
print(f"Successful: {summary['successful']}/{summary['total_companies']}")
print(f"Total Cost: ${summary['total_cost']}")
print(f"Cache Hit Rate: {summary['cache_hit_rate']:.1%}")

# Save results
output_dir = researcher.save_batch_results(result, output_dir="outputs/batch")
print(f"Results saved to: {output_dir}")
```

## CLI Options

```
usage: batch_research.py [-h] [-f FILE] [-w WORKERS] [-o OUTPUT]
                         [--timeout TIMEOUT] [--no-save] [--enhanced]
                         [--quiet]
                         [companies ...]

Options:
  -f, --file FILE       Load company names from file (one per line)
  -w, --workers WORKERS Maximum parallel workers (default: 5)
  -o, --output OUTPUT   Output directory (default: outputs/batch)
  --timeout TIMEOUT     Timeout per company in seconds (default: 300)
  --no-save             Do not save results to disk
  --enhanced            Use enhanced research workflow (if available)
  --quiet               Suppress progress output
```

## Output Structure

When you run batch research, the results are saved to a timestamped directory:

```
outputs/batch/batch_20251209_143000/
├── 00_comparison.md           # Comparative analysis report
├── tesla.md                   # Individual company reports
├── apple.md
├── microsoft.md
└── summary.json               # JSON metrics and metadata
```

### Comparison Report

The comparison report includes:

- **Summary Table**: Key metrics for all companies side-by-side
- **Detailed Sections**: In-depth analysis for each company
- **Batch Statistics**: Total cost, cache hit rate, duration, success rate

### Summary JSON

```json
{
  "timestamp": "2025-12-09T14:30:00",
  "summary": {
    "total_companies": 3,
    "successful": 3,
    "failed": 0,
    "total_cost": 0.0123,
    "cache_hit_rate": 0.67,
    "avg_cost_per_company": 0.0041
  },
  "companies": ["Tesla", "Apple", "Microsoft"],
  "results": [
    {
      "company": "Tesla",
      "success": true,
      "cost": 0.0045,
      "cached": false,
      "duration": 45.2
    }
  ]
}
```

## API Reference

### BatchResearcher

Main class for batch research operations.

```python
class BatchResearcher:
    def __init__(
        self,
        max_workers: int = 5,
        timeout_per_company: int = 300,
        enable_cache: bool = True
    )
```

#### Methods

##### `research_batch()`

Research multiple companies in parallel.

```python
def research_batch(
    self,
    companies: List[str],
    use_enhanced_workflow: bool = False,
    show_progress: bool = True
) -> BatchResearchResult
```

**Parameters:**
- `companies`: List of company names to research
- `use_enhanced_workflow`: Use enhanced research workflow (experimental)
- `show_progress`: Print real-time progress updates

**Returns:** `BatchResearchResult` with all research results and statistics

##### `generate_comparison()`

Generate comparative markdown report from batch results.

```python
def generate_comparison(
    self,
    batch_result: BatchResearchResult,
    comparison_fields: Optional[List[str]] = None
) -> str
```

**Parameters:**
- `batch_result`: Batch research result
- `comparison_fields`: Fields to compare (defaults to industry, founded, headquarters, revenue, employees)

**Returns:** Markdown comparison report

##### `save_batch_results()`

Save batch results to disk.

```python
def save_batch_results(
    self,
    batch_result: BatchResearchResult,
    output_dir: str = "outputs/batch"
) -> str
```

**Parameters:**
- `batch_result`: Batch result to save
- `output_dir`: Output directory

**Returns:** Path to saved files

### Data Classes

#### CompanyResearchResult

Result from researching a single company.

```python
@dataclass
class CompanyResearchResult:
    company_name: str
    success: bool
    report: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    cost: float = 0.0
    tokens: int = 0
    cached: bool = False
    duration_seconds: float = 0.0
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
```

#### BatchResearchResult

Result from batch research operation.

```python
@dataclass
class BatchResearchResult:
    companies: List[str]
    results: List[CompanyResearchResult] = field(default_factory=list)
    total_cost: float = 0.0
    total_tokens: int = 0
    total_duration: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    success_count: int = 0
    failure_count: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def get_summary(self) -> Dict[str, Any]
```

## Convenience Functions

### `research_companies()`

Quick function to research multiple companies.

```python
from company_researcher.batch import research_companies

result = research_companies(
    companies=["Tesla", "Apple", "Microsoft"],
    max_workers=5,
    save_results=True
)
```

### `compare_companies()`

Quick function to research and compare companies.

```python
from company_researcher.batch import compare_companies

comparison_report = compare_companies(["Tesla", "Apple", "Microsoft"])
print(comparison_report)
```

## Performance & Cost Optimization

### Caching Benefits

The batch researcher leverages the result cache system:

- **Search results**: 24-hour cache (avoids repeat Tavily API calls @ $0.001/query)
- **Web scraping**: 7-day cache (avoids redundant HTTP requests)
- **News data**: 6-hour cache (reduces news API calls)
- **Wikipedia**: 30-day cache (persistent company info)
- **SEC filings**: 30-day cache (filings rarely change)

**Cache Detection**: Results with duration < 2 seconds are marked as cached.

### Cost Estimates

**Without caching (first run):**
- Basic research: ~$0.05-0.15 per company
- Enhanced research: ~$0.20-0.40 per company

**With caching (subsequent runs):**
- Cached company: ~$0.00-0.02 (70-90% cost reduction)
- Batch of 10 companies: ~$0.50-1.50 (first run) → ~$0.05-0.30 (cached)
- Batch of 100 companies: ~$5-15 (first run) → ~$0.50-3.00 (cached)

### Performance Tuning

**Worker Count:**
- Default: 5 workers (balanced for most cases)
- Light load: 3-5 workers (local testing, limited API keys)
- Heavy load: 10-20 workers (production, multiple API keys)
- Maximum: Limited by API rate limits (typically 100-200 req/min)

**Timeout:**
- Default: 300 seconds (5 minutes) per company
- Simple companies: 120-180 seconds
- Complex companies: 300-600 seconds
- Research-heavy mode: 600+ seconds

## Examples

### Example 1: Tech Giants Comparison

```bash
python scripts/batch_research.py \
    --workers 10 \
    --output outputs/tech_giants \
    Apple Microsoft Google Amazon Meta
```

### Example 2: Industry Analysis from File

Create `ev_companies.txt`:
```
Tesla
Rivian
Lucid Motors
NIO
BYD
```

Run:
```bash
python scripts/batch_research.py --file ev_companies.txt
```

### Example 3: Cached Follow-up Research

```python
from company_researcher.batch import BatchResearcher

researcher = BatchResearcher()

# First run (expensive, ~$1.50)
result1 = researcher.research_batch([
    "Tesla", "Apple", "Microsoft",
    "Amazon", "Google", "Meta",
    "NVIDIA", "Netflix", "Adobe", "Salesforce"
])

# Second run same day (cheap, ~$0.15, 90% cached)
result2 = researcher.research_batch([
    "Tesla", "Apple", "Microsoft",
    "Amazon", "Google", "Meta",
    "NVIDIA", "Netflix", "Adobe", "Salesforce"
])

print(f"Cache hit rate: {result2.cache_hits}/{len(result2.companies)}")
# Output: Cache hit rate: 9/10 (90%)
```

### Example 4: Progressive Research Pipeline

```python
from company_researcher.batch import BatchResearcher

researcher = BatchResearcher(max_workers=10)

# Stage 1: Quick research (standard workflow)
batch_1 = ["Tesla", "Apple", "Microsoft"]
result_1 = researcher.research_batch(batch_1, use_enhanced_workflow=False)

# Stage 2: Deep dive on successful companies (enhanced workflow)
successful = [r.company_name for r in result_1.results if r.success]
result_2 = researcher.research_batch(successful, use_enhanced_workflow=True)

# Generate comparison
comparison = researcher.generate_comparison(result_2)
print(comparison)
```

## Error Handling

The batch researcher is resilient to individual failures:

```python
result = researcher.research_batch([
    "Tesla",           # Success
    "Invalid Corp",    # Fails - no results found
    "Apple",           # Success
    "XYZ123",          # Fails - invalid company
    "Microsoft"        # Success
])

print(f"Success rate: {result.success_count}/{len(result.companies)}")
# Output: Success rate: 3/5

# Failed companies are included in results with error info
for r in result.results:
    if not r.success:
        print(f"{r.company_name}: {r.error}")
```

## Integration with Enhanced Workflow

The batch researcher supports both standard and enhanced research workflows:

**Standard Workflow:**
- Fast, cost-effective
- Good for bulk research
- ~$0.05-0.15 per company

**Enhanced Workflow:**
- Deep research with specialist agents
- Competitive analysis, risk assessment, investment thesis
- ~$0.20-0.40 per company

```python
# Use enhanced workflow
result = researcher.research_batch(
    companies=["Tesla", "Apple"],
    use_enhanced_workflow=True  # Enable enhanced workflow
)
```

## Best Practices

1. **Start with small batches** (3-5 companies) to test configuration
2. **Use caching** to reduce costs on iterative research
3. **Adjust workers** based on API rate limits and system resources
4. **Monitor progress** with `show_progress=True` for visibility
5. **Save results** with timestamped directories for historical tracking
6. **Use comparison reports** to identify patterns across companies
7. **Handle failures gracefully** - check `success` field for each result

## Troubleshooting

### High failure rate
- Check API keys in `.env` file
- Verify network connectivity
- Increase `timeout_per_company` for complex research
- Review error messages in individual results

### Slow performance
- Reduce `max_workers` if hitting rate limits
- Check if enhanced workflow is needed (slower but more comprehensive)
- Verify caching is enabled (`enable_cache=True`)

### High costs
- Ensure caching is working (check cache hit rate in summary)
- Use standard workflow for bulk research
- Consider using free search tier for initial exploration

## License

Part of the Company Researcher system.
