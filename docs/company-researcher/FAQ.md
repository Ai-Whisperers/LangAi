# Frequently Asked Questions

Common questions about the Company Researcher system.

**Version**: 0.4.0
**Last Updated**: December 5, 2025

---

## General Questions

### What is Company Researcher?

Company Researcher is an AI-powered system that automatically researches companies using specialized agents and generates comprehensive reports. It uses Claude 3.5 Haiku for analysis and Tavily for web search.

### What does "Phase 4" mean?

The system has evolved through multiple phases:
- **Phase 0-1**: Basic research workflow
- **Phase 2**: Quality iteration
- **Phase 3**: Sequential multi-agent
- **Phase 4**: **Parallel multi-agent** (current)

See [PHASE_EVOLUTION.md](PHASE_EVOLUTION.md) for complete history.

### Is this ready for production?

**Not yet**. Phase 4 is a functional prototype with:
- ✅ 67% success rate (quality ≥85%)
- ✅ Parallel agent execution
- ⚠️ No monitoring/observability
- ⚠️ No caching or optimization

See [Master Plan](../planning/MASTER_20_PHASE_PLAN.md) for roadmap to production (Phase 20).

---

## Usage Questions

### How do I run a research?

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Research a company
python hello_research.py "Company Name"

# View report
cat outputs/Company Name/report_*.md
```

See [QUICK_START.md](../../QUICK_START.md) for detailed walkthrough.

### Can I research multiple companies?

Yes, run the script multiple times:

```bash
python hello_research.py "Tesla"
python hello_research.py "Microsoft"
python hello_research.py "Stripe"
```

**Future**: Batch processing (Phase 20)

### How long does research take?

**Normal**: 2-5 minutes per company

**Factors**:
- Internet speed (search API calls)
- Company complexity
- Number of iterations (1 or 2)

### How much does it cost?

**Average**: $0.08 per research

**Range**: $0.02 - $0.15 depending on:
- Company complexity
- Iterations (2x cost if iterates)
- Search result volume

**Breakdown**:
| Component | Cost |
|-----------|------|
| Initial Research | ~25% |
| Quality Checks | ~25% |
| Specialist Agents | ~40% |
| Synthesis | ~10% |

### Can I reduce costs?

**Current optimizations** (already active):
- Using Claude 3.5 Haiku (cheapest model)
- Max 2 iterations
- Limited search results (15 max)

**Future optimizations** (Phases 11-12):
- Caching search results
- Reusing company research
- **Expected savings**: 40-60% on repeats

---

## Quality Questions

### Why is quality below 85%?

**Normal behavior!** Current system has 67% success rate.

**Reasons**:
- **Limited public info**: Private/stealth companies
- **Recent companies**: Startups with minimal history
- **Complex structures**: Conglomerates
- **Search limitations**: Niche sources not found

**Quality score breakdown**:
- 90-100: Excellent ✅
- 85-89: Good ✅ (meets threshold)
- 70-84: Acceptable ⚠️ (still useful!)
- <70: Poor ⚠️

### Should I use reports with quality <85%?

**Yes!** Quality 70-84% is still valuable.

**What it means**:
- Core information present
- Some gaps (noted in missing_info)
- Good enough for initial research
- May need manual followup

**Review the report** - judge for yourself if it meets your needs.

### How can I improve quality?

**Current system** (Phase 4):
- Quality improves automatically via iteration
- System tries up to 2 iterations
- Specialist agents add depth

**Future improvements** (Phases 7-19):
- More specialist agents
- Better source verification
- Enhanced search capabilities
- **Expected**: 85%+ success rate

### What does "missing_info" mean?

Information the quality checker identified as missing or incomplete.

**Example**:
```
missing_info: [
  "specific revenue figures for 2024",
  "detailed product pricing",
  "competitive market share data"
]
```

**Use this to**:
- Understand gaps
- Do manual research for critical items
- Decide if report is sufficient

---

## Technical Questions

### What models does it use?

**LLM**: Claude 3.5 Haiku (`claude-3-5-haiku-20241022`)
- Input: $0.80 per 1M tokens
- Output: $4.00 per 1M tokens
- Fast and cost-effective

**Search**: Tavily API
- $0.001 per search
- Optimized for LLMs

### Can I use a different LLM?

Currently hardcoded to Claude. Future:
- Configurable model selection
- Support for other providers
- Cost/quality tradeoffs

### How does parallel execution work?

**Phase 4 innovation**: Financial, Market, and Product agents run simultaneously.

**Pattern**: Fan-out/fan-in
```
Researcher
   ├─→ Financial ─┐
   ├─→ Market ────┼─→ Synthesizer
   └─→ Product ───┘
```

**Benefits**:
- 3-4x faster specialist phase
- Better resource utilization
- No race conditions (custom reducers)

See [ARCHITECTURE.md](ARCHITECTURE.md) for details.

### What's a "reducer"?

A function that safely merges concurrent state updates.

**Example**: `merge_dicts` reducer
```python
# Financial agent updates:
{"financial": {...}}

# Market agent updates (concurrent):
{"market": {...}}

# merge_dicts combines:
{"financial": {...}, "market": {...}}
```

See [IMPLEMENTATION.md](IMPLEMENTATION.md) for code details.

### Can I create custom agents?

Yes! See [AGENT_DEVELOPMENT.md](AGENT_DEVELOPMENT.md).

**Basic steps**:
1. Define agent purpose
2. Create agent file (`agents/my_agent.py`)
3. Write agent prompt
4. Implement agent node function
5. Add to workflow

**Example agents to build**:
- News Agent (recent developments)
- Tech Stack Agent (technologies used)
- Team Agent (leadership, hiring)

---

## Data Questions

### Where does the data come from?

**Search**: Tavily API
- Web search optimized for LLMs
- ~15 sources per company
- Recent, high-quality results

**Sources tracked**:
- URL
- Title
- Relevance score

All sources cited in reports.

### Is the data accurate?

**Best effort** with limitations:
- ✅ Uses reputable sources
- ✅ Cites all sources
- ✅ Multiple sources per fact
- ⚠️ No human verification
- ⚠️ Search API limitations
- ⚠️ LLM hallucination possible

**Always verify** critical information from source URLs.

### How recent is the data?

**Current**: Depends on what Tavily returns
- Usually last 6-12 months
- Some historical data included
- Focuses on recent when available

**Future** (Phase 13): Deep research agent with time filtering

### Can I export data as JSON?

**Current**: Markdown reports only

**Workaround**: Parse markdown or access state:
```python
from company_researcher.workflows.parallel_agent_research import create_parallel_agent_workflow

workflow = create_parallel_agent_workflow()
result = workflow.invoke({"company_name": "Tesla"})

# Access structured data:
print(result["company_overview"])
print(result["agent_outputs"]["financial"]["analysis"])
```

**Future** (Phase 20): Multiple export formats (JSON, CSV, API)

---

## Comparison Questions

### How is this different from ChatGPT/Claude?

**Company Researcher**:
- ✅ Automated end-to-end research
- ✅ Specialized agents for depth
- ✅ Quality iteration
- ✅ Structured reports
- ✅ Source tracking
- ⚠️ Limited to company research

**ChatGPT/Claude**:
- ✅ General purpose
- ✅ Conversational
- ⚠️ Manual prompting required
- ⚠️ No structured output
- ⚠️ No iteration/improvement
- ⚠️ Limited web search

### How does it compare to Perplexity?

**Similarities**:
- Web search integration
- AI-powered analysis
- Source citations

**Differences**:

| Feature | Company Researcher | Perplexity |
|---------|-------------------|------------|
| **Specialized** | Company research only | General queries |
| **Agents** | 5 specialist agents | Single model |
| **Iteration** | Quality-driven loops | One-shot |
| **Cost** | ~$0.08/research | Subscription |
| **Custom** | Extendable agents | Fixed system |

### Is this better than manual research?

**Advantages**:
- ⚡ Faster (5 min vs hours)
- 🔄 Consistent structure
- 📊 Multiple dimensions (financial, market, product)
- 💰 Cost-effective ($0.08 vs analyst time)

**Limitations**:
- 🎯 67% success rate (vs human 100%)
- 🔍 Limited to public info (vs interviews)
- ❌ No critical thinking (vs expert analysis)
- ⚠️ Potential errors (vs verified facts)

**Best use**: Initial research, not final analysis.

---

## Future Questions

### What's coming in future phases?

See [Master 20-Phase Plan](../planning/MASTER_20_PHASE_PLAN.md):

**Short term** (Phases 5-6):
- Observability (AgentOps, LangSmith)
- Quality improvements

**Medium term** (Phases 7-12):
- 4 critical specialist agents
- Memory system and caching
- Context optimization

**Long term** (Phases 13-20):
- 7 additional specialist agents
- Advanced quality systems
- Production deployment

### When will feature X be available?

| Feature | Phase | ETA* |
|---------|-------|------|
| Observability | 4-5 | 2-3 weeks |
| Memory/Caching | 11-12 | 2-3 months |
| Additional Agents | 7-15 | 1-4 months |
| Production Ready | 20 | 4-6 months |

*ETA based on 20-30 hours/week development

### Can I contribute?

**Current**: Solo development project

**Future** (Phase 20):
- Open contribution guidelines
- Code standards
- Pull request process
- Community features

See [CONTRIBUTING.md](../../CONTRIBUTING.md) (coming soon).

### Will this stay free/open source?

**Current**: Personal/learning project

**Future plans** (TBD):
- Core system: Likely open source
- Advanced features: Possibly premium
- API access: May have costs
- Self-hosted: Always free

---

## Troubleshooting

### My question isn't answered here

Check these resources:

1. **[Troubleshooting Guide](TROUBLESHOOTING.md)** - Common errors
2. **[User Guide](USER_GUIDE.md)** - How to use
3. **[Architecture](ARCHITECTURE.md)** - How it works
4. **[Implementation](IMPLEMENTATION.md)** - Code details

### I found a bug

**Report it**:
1. Check [Troubleshooting](TROUBLESHOOTING.md) first
2. Create GitHub issue (coming soon)
3. Include:
   - Error message
   - Steps to reproduce
   - Expected vs actual behavior
   - System info (OS, Python version)

### I have a feature request

**Submit it**:
1. Check [Master Plan](../planning/MASTER_20_PHASE_PLAN.md) - might already be planned!
2. Check [External Ideas](../planning/external-ideas/README.md) - 159 features cataloged
3. Create GitHub issue (coming soon)
4. Describe:
   - Use case
   - Expected behavior
   - Why it's valuable

---

## Quick Reference

### Essential Commands

```bash
# Setup
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp env.example .env  # Then edit with API keys

# Run research
python hello_research.py "Company Name"

# View report
cat outputs/"Company Name"/report_*.md
```

### Key Files

- `hello_research.py` - Entry point
- `.env` - API keys (you create this)
- `env.example` - Environment template
- `outputs/reports/` - Generated reports
- `src/company_researcher/` - Core code

### Important Links

- [Quick Start](../../QUICK_START.md)
- [Installation](../../INSTALLATION.md)
- [Troubleshooting](TROUBLESHOOTING.md)
- [Master Plan](../planning/MASTER_20_PHASE_PLAN.md)

---

**Last Updated**: December 5, 2025
**Version**: 0.4.0 (Phase 4 Complete)
