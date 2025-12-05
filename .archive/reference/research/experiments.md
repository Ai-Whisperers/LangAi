# Research Experiments Log

This document tracks experiments, A/B tests, and prototypes for the Company Researcher System.

---

## Experiment Template

```markdown
## [EXP-XXX] Experiment Title

**Date:** YYYY-MM-DD
**Owner:** [Name]
**Status:** 🔬 In Progress | ✅ Complete | ❌ Abandoned

**Hypothesis:**
[What are we testing? What do we expect to happen?]

**Method:**
[How are we testing it? What's the experimental setup?]

**Results:**
[What did we observe? Include metrics, data, screenshots]

**Conclusions:**
[What did we learn? Was hypothesis confirmed?]

**Next Steps:**
[What should we do based on these results?]
```

---

## Active Experiments

### [EXP-001] Prompt Engineering for Financial Analysis

**Date:** 2025-12-05
**Owner:** TBD
**Status:** 🔬 Planned

**Hypothesis:**
Providing structured examples (few-shot prompting) will improve financial data extraction accuracy from 75% to 90%+.

**Method:**
1. Create test set of 20 companies with verified financial data
2. Test 3 prompt variations:
   - **Baseline:** Simple instruction
   - **Few-shot:** 3 examples provided
   - **Chain-of-thought:** Step-by-step reasoning
3. Measure accuracy, completeness, hallucination rate

**Results:**
[TBD]

**Conclusions:**
[TBD]

**Next Steps:**
[TBD]

---

### [EXP-002] Model Comparison: Claude vs GPT-4 for Research

**Date:** 2025-12-05
**Owner:** TBD
**Status:** 🔬 Planned

**Hypothesis:**
Claude 3.5 Sonnet will produce higher quality research summaries than GPT-4 Turbo for company research tasks.

**Method:**
1. Select 10 diverse companies (tech, retail, manufacturing, etc.)
2. Run identical research workflow with both models
3. Blind evaluation by 3 human raters on:
   - Accuracy
   - Completeness
   - Writing quality
   - Insight depth
4. Compare cost and speed

**Results:**
[TBD]

**Conclusions:**
[TBD]

**Next Steps:**
[TBD]

---

### [EXP-003] Parallel vs Sequential Agent Execution

**Date:** 2025-12-05
**Owner:** TBD
**Status:** 🔬 Planned

**Hypothesis:**
Running agents in parallel will reduce research time from ~5 minutes to ~2 minutes with minimal quality impact.

**Method:**
1. Test on 10 companies
2. Compare:
   - **Sequential:** Agents run one after another
   - **Parallel (Conservative):** 3 agents at a time
   - **Parallel (Aggressive):** All agents simultaneously
3. Measure:
   - Total execution time
   - Cost per research
   - Quality score (human evaluation)
   - Rate limit issues

**Results:**
[TBD]

**Conclusions:**
[TBD]

**Next Steps:**
[TBD]

---

## Completed Experiments

### [EXP-000] Proof of Concept - Single Agent Research

**Date:** 2025-12-01
**Owner:** Team
**Status:** ✅ Complete

**Hypothesis:**
A single LLM with web search can produce a basic company report in under 5 minutes.

**Method:**
1. Simple Python script
2. Claude 3.5 Sonnet + Tavily search
3. Test on Tesla
4. Generate markdown report

**Results:**
- ✅ Execution time: 2.5 minutes
- ✅ Cost: $0.18
- ✅ Generated coherent report
- ⚠️ Missing depth in financial analysis
- ⚠️ No competitor comparison

**Conclusions:**
- Proof of concept successful
- Need specialized agents for depth
- Speed and cost targets achievable

**Next Steps:**
- Build multi-agent system
- Create specialized financial agent
- Add competitor analysis agent

---

## Abandoned Experiments

### [EXP-099] Custom Web Scraper vs Tavily

**Date:** 2025-11-28
**Owner:** Team
**Status:** ❌ Abandoned

**Hypothesis:**
Building a custom web scraper will be cheaper than using Tavily API.

**Method:**
1. Build scraper with BeautifulSoup + Selenium
2. Compare cost, reliability, quality

**Results:**
- Custom scraper broke frequently (websites change)
- Rate limiting issues
- Poor content extraction
- High maintenance burden

**Conclusions:**
- Tavily is worth the cost ($0.001/search)
- Custom scraping not viable for production

**Next Steps:**
- Use Tavily as primary search tool
- Document in ADR-006

---

## Experiment Ideas (Backlog)

1. **Memory System Effectiveness**
   - Does caching past research reduce costs by 70%+?
   - Test cache hit rate over 100 requests

2. **Agent Coordination Patterns**
   - Supervisor vs Swarm for 14 agents
   - Measure quality, cost, speed

3. **Embedding Model Comparison**
   - OpenAI text-embedding-3-small vs Cohere
   - Impact on semantic search quality

4. **Source Quality Learning**
   - Can we learn to prioritize high-quality sources?
   - Track source reliability over time

5. **Streaming vs Batch Responses**
   - User experience with WebSocket streaming
   - Does streaming improve perceived speed?

6. **Cost Optimization Strategies**
   - Smaller model for simple tasks
   - Caching aggressive vs conservative

7. **Multi-Language Support**
   - Can system research non-English companies?
   - Quality degradation for non-English sources

---

## Metrics Dashboard

| Experiment | Status | Impact | Cost | Time Invested |
|------------|--------|--------|------|---------------|
| EXP-000 | ✅ Complete | High | $5 | 4 hours |
| EXP-001 | 🔬 Planned | Medium | TBD | TBD |
| EXP-002 | 🔬 Planned | High | TBD | TBD |
| EXP-003 | 🔬 Planned | High | TBD | TBD |
| EXP-099 | ❌ Abandoned | Low | $20 | 8 hours |

---

## Best Practices

1. **Always Define Success Metrics** - How will you know if the experiment worked?
2. **Use Small Test Sets** - 10-20 samples usually sufficient
3. **Document Negative Results** - Failures are valuable learning
4. **Version Control** - Tag code used in experiments
5. **Share Learnings** - Update team on findings
