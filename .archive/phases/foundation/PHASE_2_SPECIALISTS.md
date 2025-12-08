# Phase 2: Specialist Agents - Multi-Agent System

**Duration:** 2 weeks (Weeks 3-4)
**Effort:** 80-100 hours
**Team:** 2-3 developers
**Priority:** ⭐⭐⭐⭐⭐ Critical
**Status:** Pending Phase 1 completion

---

## 🎯 Objectives

Transform from single-agent to professional multi-agent research system:
1. **Specialization:** 14 domain-expert agents
2. **Quality:** Automated fact verification
3. **Orchestration:** Parallel execution pipeline
4. **Intelligence:** Strategic synthesis

---

## 📋 Specialist Agents to Implement

### Core Research Agents (3)

#### 1. Deep Research Agent ⭐⭐⭐⭐⭐
**Role:** Recursive web exploration and comprehensive data gathering
**Effort:** 8-10 hours

**Capabilities:**
- Navigate complex websites
- Handle anti-bot detection
- Extract and clean content
- Recursive link following
- Comprehensive background research

**Tools:**
- Search manager (multi-provider)
- Browser automation (Playwright)
- Content extractor
- Link analyzer

**Implementation:**
```python
# src/agents/core/deep_research.py
class DeepResearchAgent(BaseAgent):
    """Conducts deep recursive web exploration"""

    name = "deep_research"
    description = "Explores web comprehensively with recursive navigation"

    async def research(self, context: ResearchContext) -> AgentResult:
        # Initial search
        initial_results = await self.search_manager.search(
            query=f"{context.company} {context.industry} overview",
            max_results=20
        )

        # Visit top results
        visited = set()
        insights = []

        for result in initial_results[:5]:
            if result.url in visited:
                continue

            try:
                content = await self.browser.extract_content(result.url)
                insights.append(self._analyze_content(content))
                visited.add(result.url)

                # Find related links
                links = self._extract_relevant_links(content)
                for link in links[:3]:
                    if link not in visited:
                        sub_content = await self.browser.extract_content(link)
                        insights.append(self._analyze_content(sub_content))
                        visited.add(link)

            except Exception as e:
                logger.warning(f"Failed to visit {result.url}: {e}")
                continue

        return AgentResult(
            agent_name=self.name,
            insights=insights,
            sources=list(visited),
            confidence="High" if len(insights) > 10 else "Medium"
        )
```

**Output Example:**
```markdown
## Deep Research Findings

**Company Website:** https://tesla.com
- Mission: Accelerate sustainable energy
- Founded: 2003
- Products: Electric vehicles, solar, energy storage

**Recent News (10 sources):**
- Production milestone: 5M vehicles
- Cybertruck deliveries begin
- FSD version 12 released

**Related Information:**
- Supply chain partnerships
- Manufacturing facilities
- Technology developments
```

---

#### 2. Reasoning Agent ⭐⭐⭐⭐
**Role:** Advanced logical reasoning and inference
**Effort:** 8-10 hours

**Capabilities:**
- Connect disparate information
- Identify patterns
- Logical inference
- Validate consistency
- Critical thinking

**Tools:**
- LLM (GPT-4 or Claude)
- Chain-of-thought prompting
- Logical frameworks

**Implementation:**
```python
# src/agents/core/reasoning.py
class ReasoningAgent(BaseAgent):
    """Provides logical reasoning and inference"""

    async def reason(
        self,
        facts: List[ResearchFact],
        question: str
    ) -> AgentResult:

        # Build reasoning chain
        prompt = f"""
Given these facts about the company:
{self._format_facts(facts)}

Question: {question}

Think step by step:
1. What facts are relevant?
2. What can we infer?
3. What are the implications?
4. What is the confidence level?

Provide reasoned answer:
"""

        response = await self.llm.ainvoke(prompt)

        return AgentResult(
            agent_name=self.name,
            insights=[response.content],
            reasoning_chain=response.reasoning,
            confidence=self._assess_confidence(response)
        )
```

---

#### 3. Generic Research Agent ⭐⭐⭐
**Role:** Flexible general-purpose research
**Effort:** 6-8 hours

**Capabilities:**
- Handle general queries
- Adapt to various needs
- Fill gaps in research
- Quick lookups

---

### Specialist Analysts (6)

#### 4. Financial Agent ⭐⭐⭐⭐⭐
**Role:** Financial analysis and metrics
**Effort:** 12-15 hours

**Capabilities:**
- Revenue analysis
- Profit trends
- Growth metrics
- SEC filings
- Funding rounds
- Financial health

**Data Sources:**
- Alpha Vantage API
- SEC EDGAR
- Yahoo Finance
- Crunchbase

**Implementation:**
```python
# src/agents/specialists/financial.py
class FinancialAgent(BaseAgent):
    """Analyzes financial performance and metrics"""

    async def research(self, context: ResearchContext) -> AgentResult:
        insights = []

        # 1. Get stock data (if public)
        try:
            stock_data = await self.alpha_vantage.get_stock_data(
                symbol=context.ticker
            )
            insights.append(self._analyze_stock_performance(stock_data))
        except:
            logger.info("Company not publicly traded")

        # 2. SEC filings (if available)
        try:
            filings = await self.sec.get_filings(
                company_name=context.company
            )
            insights.append(self._analyze_sec_filings(filings))
        except:
            logger.info("No SEC filings found")

        # 3. Funding data (if startup)
        try:
            funding = await self.crunchbase.get_funding(
                company_name=context.company
            )
            insights.append(self._analyze_funding(funding))
        except:
            logger.info("No funding data found")

        # 4. Financial metrics synthesis
        metrics = self._calculate_key_metrics(insights)

        return AgentResult(
            agent_name=self.name,
            insights=insights,
            metrics=metrics,
            confidence=self._calculate_confidence(insights)
        )
```

**Output Example:**
```markdown
## Financial Analysis

### Revenue Performance
- FY 2023: $96.7B (+18.8% YoY)
- FY 2022: $81.5B (+51.4% YoY)
- FY 2021: $53.8B (+70.7% YoY)

### Profitability
- Gross Margin: 18.2% (improving from 16.1%)
- Operating Margin: 9.2%
- Net Margin: 15.5%

### Growth Metrics
- Revenue CAGR (3-year): 44.2%
- Automotive revenue: 85% of total
- Energy/Services: 15% of total

### Financial Health
- Cash: $26.1B
- Debt: $2.8B
- Debt/Equity: 0.05 (very low)
- Free Cash Flow: $2.3B positive

**Source:** SEC 10-K 2023, Yahoo Finance
**Confidence:** High (official sources)
```

---

#### 5. Market Analyst ⭐⭐⭐⭐⭐
**Role:** Market size, trends, dynamics
**Effort:** 10-12 hours

**Capabilities:**
- Market sizing (TAM/SAM/SOM)
- Industry trends
- Regulatory landscape
- Customer behavior
- Market penetration

**Implementation:**
```python
# src/agents/specialists/market.py
class MarketAnalyst(BaseAgent):
    """Analyzes market dynamics and trends"""

    async def research(self, context: ResearchContext) -> AgentResult:
        # 1. Market size research
        market_size = await self._research_market_size(
            industry=context.industry
        )

        # 2. Growth trends
        trends = await self._research_trends(
            industry=context.industry
        )

        # 3. Regulatory environment
        regulations = await self._research_regulations(
            industry=context.industry,
            geography=context.geography
        )

        return AgentResult(
            agent_name=self.name,
            insights=[market_size, trends, regulations],
            confidence="High"
        )
```

**Output Example:**
```markdown
## Market Intelligence

### Market Size
- Global EV Market: $388.1B (2023)
- CAGR: 17.8% (2024-2030)
- Projected 2030: $1.1T
- Current penetration: 14% of new cars

### Key Trends
📈 **Growing:**
- Battery prices declining (enabled mass adoption)
- Government incentives (IRA, EU subsidies)
- Charging infrastructure (10x growth since 2020)

📉 **Declining:**
- Range anxiety (400+ mile range common)
- Price premium (EVs approaching ICE parity)

### Regulatory Landscape
- US: IRA tax credits ($7,500)
- EU: Zero-emission mandate by 2035
- China: NEV quotas and subsidies
```

---

#### 6. Competitor Scout ⭐⭐⭐⭐⭐
**Role:** Competitive intelligence
**Effort:** 10-12 hours

**Capabilities:**
- Identify competitors
- Market positioning
- Tech stack analysis
- GitHub activity
- Patent filings
- Funding intelligence

---

#### 7. Brand Auditor ⭐⭐⭐⭐
**Role:** Brand and reputation analysis
**Effort:** 8-10 hours

**Capabilities:**
- Social media presence
- Customer sentiment
- Review analysis
- Marketing campaigns
- Brand perception

---

#### 8. Sales Agent ⭐⭐⭐⭐
**Role:** Sales intelligence
**Effort:** 8-10 hours

**Capabilities:**
- Decision-maker identification
- Pain point detection
- Sales strategy
- Pricing analysis
- GTM insights

---

#### 9. Investment Agent ⭐⭐⭐⭐
**Role:** Investment thesis
**Effort:** 10-12 hours

**Capabilities:**
- Growth catalysts
- Risk assessment
- SWOT analysis
- Valuation
- Recommendations

---

### Quality & Synthesis (3)

#### 10. Logic Critic ⭐⭐⭐⭐⭐
**Role:** Quality assurance and verification
**Effort:** 12-15 hours

**Capabilities:**
- Fact verification
- Cross-source checking
- Contradiction detection
- Quality scoring
- Confidence assessment

**Implementation:**
```python
# src/agents/quality/logic_critic.py
class LogicCritic(BaseAgent):
    """Verifies quality and consistency of research"""

    async def verify(
        self,
        results: List[AgentResult]
    ) -> QualityReport:

        verified_facts = []
        contradictions = []

        # 1. Cross-verify facts
        all_facts = self._extract_all_facts(results)

        for fact in all_facts:
            verification = await self._verify_fact(fact, all_facts)
            if verification.verified:
                verified_facts.append(fact)
            elif verification.contradiction:
                contradictions.append(verification)

        # 2. Quality scoring
        quality_scores = {}
        for result in results:
            score = self._calculate_quality_score(result)
            quality_scores[result.agent_name] = score

        # 3. Generate report
        return QualityReport(
            verified_facts=verified_facts,
            contradictions=contradictions,
            quality_scores=quality_scores,
            overall_quality=self._calculate_overall(quality_scores),
            recommendations=self._generate_recommendations(contradictions)
        )

    async def _verify_fact(
        self,
        fact: ResearchFact,
        all_facts: List[ResearchFact]
    ) -> Verification:
        # Check if fact appears in multiple sources
        supporting = [f for f in all_facts if self._supports(f, fact)]
        contradicting = [f for f in all_facts if self._contradicts(f, fact)]

        return Verification(
            fact=fact,
            verified=len(supporting) >= 2,
            confidence=self._calculate_confidence(
                supporting,
                contradicting
            ),
            sources=len(supporting),
            contradiction=len(contradicting) > 0
        )
```

**Output Example:**
```markdown
## Quality Assurance Report

### Verification Summary
- Total facts: 127
- Verified (2+ sources): 98 (77%)
- Unverified (1 source): 24 (19%)
- Contradictions: 5 (4%)

### High Confidence Facts (90-100%)
✓ Revenue $96.7B (2023) - 4 sources
✓ Founded 2003 - 3 sources
✓ CEO: Elon Musk - 5 sources

### Medium Confidence (70-89%)
⚠ Market share 19.9% - 2 sources
⚠ Employee count 127,855 - 1 source

### Contradictions Detected
❌ Production capacity:
  - Source A: 2M vehicles/year
  - Source B: 1.8M vehicles/year
  **Recommendation:** Verify with official sources

### Quality Scores by Agent
- Financial Agent: 95/100
- Market Analyst: 88/100
- Deep Research: 82/100
```

---

#### 11. Insight Generator ⭐⭐⭐⭐⭐
**Role:** Strategic synthesis
**Effort:** 10-12 hours

**Capabilities:**
- Synthesize all agent outputs
- Generate strategic insights
- SWOT/PESTLE frameworks
- Identify opportunities
- Create recommendations

---

#### 12. Report Writer ⭐⭐⭐⭐
**Role:** Professional report generation
**Effort:** 8-10 hours

**Capabilities:**
- Structure content
- Format for readability
- Executive summaries
- Citations
- Professional presentation

---

## 🏗️ Pipeline Orchestrator

**Effort:** 15-20 hours
**Priority:** ⭐⭐⭐⭐⭐

**What:** Coordinate all agents in optimal sequence

**Implementation:**
```python
# src/pipeline/orchestrator.py
class ResearchOrchestrator:
    """Orchestrates multi-agent research workflow"""

    def __init__(self):
        # Core agents
        self.deep_research = DeepResearchAgent()
        self.reasoning = ReasoningAgent()
        self.generic = GenericAgent()

        # Specialists
        self.financial = FinancialAgent()
        self.market = MarketAnalyst()
        self.competitor = CompetitorScout()
        self.brand = BrandAuditor()
        self.sales = SalesAgent()
        self.investment = InvestmentAgent()

        # Quality
        self.critic = LogicCritic()
        self.insight_gen = InsightGenerator()
        self.writer = ReportWriter()

    async def execute(
        self,
        company: str,
        industry: str
    ) -> ResearchReport:

        # Stage 1: Initialization
        context = await self._initialize(company, industry)

        # Stage 2: Core Research (parallel)
        core_results = await asyncio.gather(
            self.deep_research.research(context),
            self.reasoning.research(context),
            self.generic.research(context)
        )

        # Stage 3: Specialist Analysis (parallel)
        specialist_results = await asyncio.gather(
            self.financial.research(context),
            self.market.research(context),
            self.competitor.research(context),
            self.brand.research(context),
            self.sales.research(context),
            self.investment.research(context)
        )

        # Stage 4: Quality Assurance
        all_results = core_results + specialist_results
        quality_report = await self.critic.verify(all_results)

        # Stage 5: Synthesis
        insights = await self.insight_gen.synthesize(
            results=all_results,
            quality_report=quality_report
        )

        # Stage 6: Report Generation
        report = await self.writer.generate_reports(
            context=context,
            results=all_results,
            insights=insights,
            quality_report=quality_report
        )

        return report
```

---

## 📅 Weekly Breakdown

### Week 3: Core Agents & Specialists

**Monday-Tuesday:**
- Base agent framework
- Deep Research Agent
- Reasoning Agent

**Wednesday-Thursday:**
- Financial Agent
- Market Analyst
- Logic Critic

**Friday:**
- Testing
- Code review
- Demo

---

### Week 4: More Specialists & Pipeline

**Monday-Tuesday:**
- Competitor Scout
- Brand Auditor
- Sales Agent

**Wednesday:**
- Investment Agent
- Insight Generator
- Report Writer

**Thursday:**
- Pipeline Orchestrator
- Integration testing

**Friday:**
- Phase 2 review
- Demo
- Phase 3 planning

---

## 🎯 Success Criteria

- ✅ 10+ specialist agents operational
- ✅ Logic Critic verifying outputs
- ✅ Pipeline executing end-to-end
- ✅ Parallel execution working
- ✅ Quality scores on all outputs
- ✅ 3x more comprehensive reports
- ✅ Research time still < 5 minutes

---

## 🧪 Testing Strategy

```python
# tests/integration/test_multi_agent.py
@pytest.mark.asyncio
async def test_full_pipeline():
    orchestrator = ResearchOrchestrator()
    report = await orchestrator.execute("Tesla", "Automotive")

    # Verify all agents ran
    assert len(report.agent_results) >= 10

    # Verify quality check
    assert report.quality_report is not None
    assert report.quality_report.overall_quality >= 80

    # Verify insights generated
    assert len(report.insights) > 0

    # Verify report structure
    assert report.executive_summary is not None
    assert report.financial_analysis is not None
    assert report.market_intelligence is not None
```

---

## 📊 Metrics

- Agent execution time: < 30s each
- Total research time: < 5 minutes
- Quality score: 80+ overall
- Fact verification rate: 70%+
- Parallel efficiency: 80%+

---

**Next:** [Phase 3: Data Enrichment](PHASE_3_DATA_ENRICHMENT.md)
