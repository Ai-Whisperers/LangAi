# Quick Start Guide

Get up and running with your first company research in 5 minutes.

---

## Prerequisites

Before starting, make sure you've completed:

- ✅ Python 3.11+ installed
- ✅ Dependencies installed (`pip install -r requirements.txt`)
- ✅ API keys configured in `.env` file

If not, see [INSTALLATION.md](INSTALLATION.md) first.

---

## Your First Research (5 minutes)

### Step 1: Activate Virtual Environment

**Windows**:
```bash
cd "Lang ai"
venv\Scripts\activate
```

**Mac/Linux**:
```bash
cd "Lang ai"
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### Step 2: Run Your First Research

```bash
python hello_research.py "Microsoft"
```

### Step 3: Watch the Progress

You'll see the research workflow in action:

```
🔬 Researching: Microsoft
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Starting research workflow...

📋 Iteration 1/2
  ✓ Researcher Agent: Gathering initial information...
    └─ Found 10 sources about Microsoft
    └─ Extracted company overview

  🎯 Quality Check: 82.0/100
    ⚠️  Below threshold (85.0)
    ⟳  Triggering specialist agents...

📋 Iteration 2/2
  ⚡ Running specialist agents in parallel...

    ↻ Financial Agent: Analyzing financial data...
      └─ Revenue: $211.9B (2023)
      └─ Profit Margin: 36.7%
      └─ Market Cap: $2.8T

    ↻ Market Agent: Analyzing market position...
      └─ Market: Cloud computing, Software, AI
      └─ Competitors: Amazon, Google, Apple
      └─ Market Share: #2 cloud (Azure 23%)

    ↻ Product Agent: Analyzing products...
      └─ Products: Windows, Office 365, Azure, Xbox
      └─ Recent: Copilot AI integration

  ✓ Synthesizer: Creating comprehensive report...

  🎯 Quality Check: 88.0/100
    ✅ Meets threshold!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Research complete!

📊 Quality Score: 88.0/100
💰 Total Cost: $0.0386
⏱️  Duration: 47 seconds
📝 Report saved to: outputs/reports/microsoft_report.md
```

### Step 4: View Your Report

```bash
# View the report
cat outputs/reports/microsoft_report.md

# Or on Windows:
type outputs\reports\microsoft_report.md

# Or open in your editor
code outputs/reports/microsoft_report.md
```

---

## Understanding the Output

### Research Report Structure

The generated report contains:

1. **Executive Summary**
   - Company name, industry, headquarters
   - Key metrics snapshot

2. **Company Overview**
   - Business description
   - Products and services
   - Market position

3. **Financial Analysis**
   - Revenue trends
   - Profitability metrics
   - Financial health indicators

4. **Market Analysis**
   - Market size and opportunity
   - Industry trends
   - Competitive landscape

5. **Product & Technology**
   - Product portfolio
   - Technology stack
   - Innovation areas

6. **Quality Assessment**
   - Quality score breakdown
   - Confidence level
   - Source quality distribution

7. **Sources**
   - All citations with URLs
   - Source quality ratings

### Quality Scores Explained

The system rates research quality on a 0-100 scale:

| Score | Meaning | What Happens |
|-------|---------|--------------|
| **90-100** | Excellent | High-quality, comprehensive research |
| **85-89** | Good | Meets quality threshold ✅ |
| **70-84** | Acceptable | Below threshold, triggers iteration ⟳ |
| **<70** | Poor | Significant gaps, needs improvement |

**Target**: 85+ quality score

**What the system does**:
- If score < 85: Run specialist agents (Financial, Market, Product)
- If still < 85: Try one more iteration (max 2 total)
- If max iterations reached: Return best result

### Cost Breakdown

Average research costs ~$0.08:

| Component | Cost | % of Total |
|-----------|------|-----------|
| Initial Research | $0.01-0.02 | 12-25% |
| Specialist Agents | $0.04-0.06 | 50-75% |
| Synthesis | $0.01-0.02 | 12-25% |

**Variables affecting cost**:
- Company complexity (more data = higher cost)
- Number of iterations (2 iterations ≈ 2x cost)
- Search results volume

---

## Try More Examples

### Research Different Companies

```bash
# Tech companies
python hello_research.py "Tesla"
python hello_research.py "Stripe"
python hello_research.py "OpenAI"

# Traditional companies
python hello_research.py "Walmart"
python hello_research.py "Toyota"

# Startups
python hello_research.py "Anthropic"
python hello_research.py "Mistral AI"
```

### View All Reports

```bash
# List all generated reports
ls outputs/reports/

# View multiple reports
cat outputs/reports/*.md
```

---

## Common Scenarios

### Scenario 1: High-Quality Result (No Iteration)

```
Researching: Stripe
  ✓ Researcher Agent: Complete
  🎯 Quality: 86.0/100 ✅
✅ Research complete (1 iteration)
💰 Cost: $0.0234
```

**What happened**: Initial research met quality threshold, no specialists needed.

### Scenario 2: Iteration Required

```
Researching: Tesla
  ✓ Researcher Agent: Complete
  🎯 Quality: 78.0/100 ⚠️
  ⟳ Iteration 2: Running specialists...
    ↻ Financial, Market, Product agents
  ✓ Synthesizer: Complete
  🎯 Quality: 82.0/100 ⚠️
⚠️  Max iterations reached
💰 Cost: $0.0710
```

**What happened**: Initial research was low quality (78%), specialists helped improve to 82%, but still below 85% threshold. System stopped at max iterations.

### Scenario 3: Successful Iteration

```
Researching: Microsoft
  ✓ Researcher Agent: Complete
  🎯 Quality: 82.0/100 ⚠️
  ⟳ Iteration 2: Running specialists...
  ✓ Synthesizer: Complete
  🎯 Quality: 88.0/100 ✅
✅ Research complete!
💰 Cost: $0.0386
```

**What happened**: Iteration improved quality from 82% to 88%, meeting threshold.

---

## What to Do Next

### 1. Explore the Reports

Look at the generated reports in `outputs/reports/`:
- Notice how specialist agents add depth
- Check source citations
- Review quality assessments

### 2. Understand the System

Read the documentation:
- [Architecture](docs/company-researcher/ARCHITECTURE.md) - How it works
- [Implementation](docs/company-researcher/IMPLEMENTATION.md) - Code structure
- [User Guide](docs/company-researcher/USER_GUIDE.md) - Detailed usage

### 3. Experiment

Try different scenarios:
- Research companies in different industries
- Notice quality variation
- Observe iteration patterns
- Track costs

### 4. Customize (Advanced)

Modify the system:
- Adjust quality threshold (`.env`: `QUALITY_THRESHOLD=85.0`)
- Change max iterations (`.env`: `MAX_ITERATIONS=2`)
- Add custom agents (see [Agent Development](docs/company-researcher/AGENT_DEVELOPMENT.md))

---

## Troubleshooting

### "API key not found"

```bash
# Check .env file exists and has correct keys
cat .env

# Should contain:
ANTHROPIC_API_KEY=sk-ant-...
TAVILY_API_KEY=tvly-...
```

### "Quality always below threshold"

This is normal! Current success rate is 67% (2 out of 3 companies).

**Why**: Some companies have limited public information or complex structures.

**What to do**: Check the report anyway - quality 78-84% is still useful.

### "Cost higher than expected"

Average cost: $0.08 per research
- Some companies cost more (complex = more data)
- Iterations double the cost
- This is expected behavior

**Future phases** (11-12) will add caching to reduce costs.

### "No report generated"

```bash
# Check outputs directory exists
ls -la outputs/reports/

# If missing, create it:
mkdir -p outputs/reports
mkdir -p outputs/logs

# Run again
python hello_research.py "Microsoft"
```

### "UnicodeEncodeError" (Windows)

If you see emoji encoding errors on Windows:

```bash
# Quick fix: Use Windows Terminal or PowerShell instead of cmd.exe
# Or set UTF-8 encoding:
chcp 65001

# Then run again
python hello_research.py "Microsoft"
```

**Note**: This doesn't affect functionality - reports are still generated correctly. See [INSTALLATION.md](INSTALLATION.md) for more details.

---

## Understanding Current Limitations

**Phase 4 System** (current):
- ✅ Parallel multi-agent execution
- ✅ Quality iteration
- ✅ Comprehensive reports
- ⚠️ 67% success rate (quality ≥85%)
- ⚠️ No caching (repeat research costs same)
- ⚠️ No monitoring/debugging tools

**Future Phases** will add:
- Phases 5-6: Monitoring, quality improvements
- Phases 7-10: More specialist agents
- Phases 11-12: Memory/caching system
- Phase 20: Production deployment

See [Master Plan](docs/planning/MASTER_20_PHASE_PLAN.md) for details.

---

## Next Steps

1. ✅ **Complete**: You've run your first research!
2. **Learn**: Read [User Guide](docs/company-researcher/USER_GUIDE.md)
3. **Explore**: Try more companies
4. **Understand**: Review [Architecture](docs/company-researcher/ARCHITECTURE.md)
5. **Contribute**: See roadmap in [Master Plan](docs/planning/MASTER_20_PHASE_PLAN.md)

---

## Getting Help

- **Troubleshooting**: [docs/company-researcher/TROUBLESHOOTING.md](docs/company-researcher/TROUBLESHOOTING.md)
- **FAQ**: [docs/company-researcher/FAQ.md](docs/company-researcher/FAQ.md)
- **Technical Docs**: [docs/company-researcher/](docs/company-researcher/)

---

**Congratulations!** You've successfully run your first company research. Ready to dive deeper? Check out the [User Guide](docs/company-researcher/USER_GUIDE.md).
