# Quality Integration Quick Start Guide

**Ready to use in 30 seconds!**

## 🚀 Quick Start

The quality system is **enabled by default** - just run batch research as usual and you'll automatically get quality scores!

### 1. Basic Usage (Quality Enabled)

```bash
# Research companies with automatic quality assessment
python scripts/batch_research.py Tesla Apple Microsoft

# Output includes quality scores:
#   ✓ [1/3] Tesla [Q:87]
#   ✓ [2/3] Apple [Q:82]
#   ✓ [3/3] Microsoft [Q:68⚠]
#
# 📊 Avg Quality Score: 79.0/100
# ⚠️  Low Quality Reports: 1/3 (Microsoft below 70)
```

### 2. Understanding Quality Scores

**[Q:87]** - High quality (≥80)
- Comprehensive coverage
- Few or no gaps
- Strong source diversity

**[Q:72]** - Good quality (70-79)
- Adequate coverage
- Minor gaps
- Acceptable source diversity

**[Q:68⚠]** - Needs improvement (<70)
- Significant gaps
- Missing key information
- Requires follow-up research

## 📋 Output Files

After running batch research with quality checking, you'll get:

```
outputs/batch/batch_20251210_143000/
├── 00_comparison.md          # Includes quality metrics section
├── tesla.md                  # Individual reports
├── apple.md
├── microsoft.md
├── summary.json              # Includes quality data per company
└── quality_issues.md         # 🆕 Auto-generated for low-quality results
```

## 🔍 Quality Issues Report Example

When you have low-quality results, `quality_issues.md` is automatically generated:

```markdown
# Quality Issues Report

**Generated**: 2025-12-10 14:30:00
**Low Quality Threshold**: 70/100
**Total Low Quality Reports**: 1

---

## Microsoft

**Quality Score**: 68.0/100 ⚠️

### Missing Information
- Revenue breakdown by division
- Market share in cloud computing
- Recent partnership details

### Recommended Follow-up Queries
- `Microsoft Azure market share 2024`
- `Microsoft revenue by segment Q3 2024`
- `Microsoft strategic partnerships 2024`

### Research Strengths
- Comprehensive company overview
- Strong financial data coverage
- Good competitor analysis
```

## 🎯 Common Use Cases

### Use Case 1: Quick Batch Research with Quality

```bash
# Default: Quality enabled, threshold 70
python scripts/batch_research.py Tesla Rivian Lucid "Nio" BYD

# Check quality_issues.md for any low-quality reports
# Follow recommended queries to improve quality
```

### Use Case 2: Strict Quality Standards

```bash
# Flag anything below 80/100 as low quality
python scripts/batch_research.py --quality-threshold 80 \
    Apple Microsoft Google Amazon Meta

# More reports will be flagged for review
# Ensures only high-quality reports pass
```

### Use Case 3: Speed Over Quality

```bash
# Disable quality checking for faster research
python scripts/batch_research.py --no-quality-check \
    Company1 Company2 Company3 Company4 Company5

# Saves ~1 second for 10 companies
# Use when you need speed and will review manually
```

### Use Case 4: Quality-Driven Iterative Research

```bash
# Step 1: Initial research
python scripts/batch_research.py Tesla Apple Microsoft Amazon

# Step 2: Review quality_issues.md
# Step 3: Re-research low-quality companies with enhanced workflow
python scripts/batch_research.py --enhanced Microsoft

# Step 4: Verify improved quality scores
```

## 💻 Python API

### Example 1: Basic Quality Integration

```python
from company_researcher.batch import BatchResearcher

# Initialize with quality checking enabled (default)
researcher = BatchResearcher(
    max_workers=5,
    enable_quality_check=True,    # Default: True
    quality_threshold=70.0         # Default: 70.0
)

# Research batch
result = researcher.research_batch([
    "Tesla", "Apple", "Microsoft"
])

# Access quality metrics
print(f"Average quality: {result.avg_quality_score:.1f}/100")
print(f"Low quality count: {result.low_quality_count}/{result.success_count}")

# Review individual results
for r in result.results:
    if r.quality_score:
        print(f"{r.company_name}: {r.quality_score:.1f}/100")
        if r.quality_score < 70:
            print(f"  Issues: {len(r.quality_issues)}")
            print(f"  Recommendations: {len(r.recommended_queries)}")
```

### Example 2: Filter Low-Quality Results

```python
from company_researcher.batch import BatchResearcher

researcher = BatchResearcher(quality_threshold=75.0)

result = researcher.research_batch([
    "Tesla", "Apple", "Microsoft", "Amazon",
    "Google", "Meta", "Netflix", "Adobe"
])

# Filter low-quality results
low_quality = [
    r for r in result.results
    if r.quality_score and r.quality_score < 75
]

print(f"\nLow Quality Reports: {len(low_quality)}/{result.success_count}")
for r in low_quality:
    print(f"\n{r.company_name}: {r.quality_score:.1f}/100")
    print(f"Missing: {', '.join(r.quality_issues[:3])}")
    if r.recommended_queries:
        print(f"Recommended: {r.recommended_queries[0]}")
```

### Example 3: Automatic Re-Research Loop

```python
from company_researcher.batch import BatchResearcher

researcher = BatchResearcher(quality_threshold=70.0)

# Initial research
print("Phase 1: Initial research...")
result = researcher.research_batch([
    "Tesla", "Apple", "Microsoft", "Amazon"
])

# Identify low-quality results
low_quality_companies = [
    r.company_name for r in result.results
    if r.quality_score and r.quality_score < 70
]

# Re-research with enhanced workflow
if low_quality_companies:
    print(f"\nPhase 2: Re-researching {len(low_quality_companies)} low-quality reports...")
    result2 = researcher.research_batch(
        low_quality_companies,
        use_enhanced_workflow=True  # More comprehensive
    )

    # Compare improvements
    for r in result2.results:
        if r.quality_score:
            original = next((x for x in result.results if x.company_name == r.company_name), None)
            if original and original.quality_score:
                improvement = r.quality_score - original.quality_score
                print(f"{r.company_name}: {original.quality_score:.1f} → {r.quality_score:.1f} (+{improvement:.1f})")
```

## 📊 Understanding JSON Output

The `summary.json` file includes quality data for analysis:

```json
{
  "timestamp": "2025-12-10T14:30:00",
  "summary": {
    "total_companies": 3,
    "successful": 3,
    "avg_quality_score": 79.0,
    "low_quality_count": 1
  },
  "results": [
    {
      "company": "Tesla",
      "quality_score": 87.0,
      "quality_issues": [],
      "quality_strengths": [
        "Comprehensive financial data",
        "Strong competitor analysis",
        "Good source diversity"
      ],
      "recommended_queries": []
    },
    {
      "company": "Microsoft",
      "quality_score": 68.0,
      "quality_issues": [
        "Revenue breakdown by division",
        "Market share in cloud computing"
      ],
      "quality_strengths": [
        "Comprehensive company overview",
        "Strong financial data coverage"
      ],
      "recommended_queries": [
        "Microsoft Azure market share 2024",
        "Microsoft revenue by segment Q3 2024"
      ]
    }
  ]
}
```

## ⚙️ Configuration Options

### CLI Options

```bash
# Disable quality checking
--no-quality-check

# Custom quality threshold (default: 70)
--quality-threshold 80

# Examples
python scripts/batch_research.py --no-quality-check Tesla Apple
python scripts/batch_research.py --quality-threshold 85 Tesla Apple
```

### Python API Options

```python
BatchResearcher(
    max_workers=5,              # Parallel workers (default: 5)
    timeout_per_company=300,    # Timeout in seconds (default: 300)
    enable_cache=True,          # Use caching (default: True)
    enable_quality_check=True,  # Enable quality checks (default: True)
    quality_threshold=70.0      # Quality threshold (default: 70.0)
)
```

## 💰 Cost Impact

Quality checking adds minimal cost:

**Per Company:**
- Quality check cost: ~$0.001 (using DeepSeek V3)
- Research cost: ~$0.05-0.15 (first run)
- Total overhead: <2%

**Batch of 10 Companies:**
- Quality check cost: ~$0.01
- Research cost: ~$0.50-1.50
- Total overhead: <2%

**Conclusion:** Quality insights for <2% additional cost!

## 🎯 Best Practices

1. **Use default settings** for most cases
   - Quality checking enabled
   - Threshold at 70/100
   - Balance between quality and performance

2. **Review quality_issues.md** after each batch
   - Check for patterns in missing information
   - Use recommended queries for follow-up
   - Track quality trends over time

3. **Adjust threshold** based on your needs
   - 60: Permissive (flag only very poor quality)
   - 70: Balanced (default)
   - 80: Strict (ensure high quality)
   - 90: Very strict (excellence required)

4. **Use --no-quality-check** only when:
   - Testing/debugging
   - Speed is critical
   - Manual quality review planned
   - Cost is a major concern

5. **Iterative improvement** for best results
   - Initial research with quality checks
   - Review low-quality reports
   - Re-research with enhanced workflow
   - Verify improved quality scores

## 🐛 Troubleshooting

### Quality checks not running

```bash
# Check that quality checking is enabled
python scripts/batch_research.py Tesla
# Should show: Quality checking: Yes

# If disabled, make sure not using --no-quality-check
```

### No quality_issues.md generated

This is normal if all reports meet the quality threshold:
- No low-quality reports = No quality_issues.md
- Only generated when quality_score < threshold

### Quality scores seem low

Quality scores reflect:
- **Completeness** of information
- **Data quality** (accuracy, recency)
- **Source diversity**

Low scores usually indicate:
- Missing key information (financials, market share)
- Limited source coverage
- Insufficient detail in key areas

**Solution:** Use recommended queries for follow-up research

## 📚 Additional Resources

- [QUALITY_INTEGRATION.md](QUALITY_INTEGRATION.md) - Complete integration guide
- [BATCH_RESEARCH_IMPLEMENTATION.md](BATCH_RESEARCH_IMPLEMENTATION.md) - Batch research details
- [SESSION_SUMMARY.md](SESSION_SUMMARY.md) - Session overview
- [src/company_researcher/batch/README.md](src/company_researcher/batch/README.md) - API reference

## ✅ Ready to Start!

The quality integration is ready to use with **zero configuration**. Just run your batch research as usual and you'll automatically get:

- ✅ Quality scores for each company
- ✅ Batch-level quality metrics
- ✅ Quality issues report (for low-quality results)
- ✅ Actionable recommendations

**Happy researching!** 🚀
