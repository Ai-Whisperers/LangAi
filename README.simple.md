# Company Researcher

AI-powered company research in under 5 minutes for less than $0.50.

## Quick Start

```bash
# 1. Clone and setup
git clone <repository-url>
cd "Lang ai"
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure API keys
cp .env.example .env
# Edit .env and add your Anthropic & Tavily API keys

# 4. Run your first research
python hello_research.py "Tesla"
```

## What This Does

Automatically researches any company and generates a markdown report with:
- **Company Overview** - Industry, founding, headquarters
- **Financial Metrics** - Revenue, funding, valuation
- **Products & Services** - What they sell
- **Competitors** - Who they compete with
- **Sources** - Citations for all facts

**Output:** `outputs/{Company}/report.md`

## Project Status

🚧 **Phase 0: Proof of Concept**

| Task | Status |
|------|--------|
| Environment Setup | ✅ Complete |
| API Integration | [ ] In Progress |
| Hello Research Script | [ ] Not Started |
| Validation | [ ] Not Started |

**Next:** Build basic research workflow → See [.agent-todos/phase-0/](. agent-todos/phase-0/)

## Development

```bash
# Run tests
python tests/api_tests/test_claude.py
python tests/api_tests/test_tavily.py

# Validate Phase 0
python validate_phase0.py

# Check outputs
ls outputs/*/report.md
```

## Cost & Performance

**Current Targets:**
- **Time:** < 5 minutes per research
- **Cost:** < $0.50 per research (Claude + Tavily)
- **Quality:** 80%+ usable information

**Actual:** TBD after Phase 0 validation

## Architecture

**Phase 0 (Current):** Simple Python script
```
Input → Claude (queries) → Tavily (search) → Claude (extract) → Report
```

**Phase 1 (Next):** LangGraph workflow with iteration
**Phase 2 (Future):** Multi-agent system
**Phase 3 (Future):** Production API

## Documentation

- **Getting Started:** [.agent-todos/phase-0/README.md](.agent-todos/phase-0/README.md)
- **Task Breakdown:** [.agent-todos/](.agent-todos/)
- **MVP Roadmap:** See `.archive/planning/MVP_ROADMAP.md`
- **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md)

## API Keys Required

1. **Anthropic** (Claude 3.5 Sonnet): https://console.anthropic.com/
   - Free: $5 credit
   - Cost: ~$0.25-$0.35 per research

2. **Tavily** (Web Search): https://tavily.com/
   - Free: 1,000 searches/month
   - Cost: ~$0.01-$0.02 per research

## Roadmap

- [x] Phase 0: Hello World script (Week 1)
- [ ] Phase 1: LangGraph workflow (Weeks 2-3)
- [ ] Phase 2: Multi-agent system (Weeks 4-6)
- [ ] Phase 3: Production API (Weeks 7-8)

## License

[TBD]

---

**Built with:** LangChain, Claude 3.5 Sonnet, Tavily
**Status:** Active Development
**Last Updated:** 2025-12-05
