# Quality Assurance & Verification System

**Source:** Inspired by Open Deep Research quality patterns + LangMem verification

---

## Overview

Quality assurance ensures research is:
- ✅ Accurate (facts are correct)
- ✅ Complete (no major gaps)
- ✅ Verifiable (sources cited)
- ✅ Consistent (no contradictions)
- ✅ Recent (data is current)

---

## Architecture

### Logic Critic Agent

```
┌──────────────────────────────────────────────────────┐
│              Research Results                         │
│  (From all specialist agents)                        │
└───────────────────┬──────────────────────────────────┘
                    │
        ┌───────────▼───────────┐
        │   Logic Critic Agent  │
        │  (Quality Assurance)  │
        └───────────┬───────────┘
                    │
    ┌───────────────┼───────────────┐
    │               │               │
┌───▼────┐  ┌──────▼─────┐  ┌─────▼──────┐
│ Verify │  │Contradition│  │   Source   │
│ Facts  │  │  Detection │  │   Quality  │
└───┬────┘  └──────┬─────┘  └─────┬──────┘
    │               │               │
    └───────────────┴───────────────┘
                    │
        ┌───────────▼───────────┐
        │   Quality Report      │
        │   - Score: 0-100      │
        │   - Issues found      │
        │   - Recommendations   │
        └───────────────────────┘
```

---

## Core Components

### 1. Fact Verification

**Cross-Reference Checker**
```python
class FactVerifier:
    """Verify facts across multiple sources"""

    async def verify_fact(
        self,
        fact: str,
        sources: list[dict],
        llm
    ) -> dict:
        """Verify a single fact"""

        # Extract fact from multiple sources
        prompt = f"""Verify this fact across these sources:

Fact: {fact}

Sources:
{sources}

Check:
1. Is the fact stated in multiple sources?
2. Do the sources agree on the details?
3. Are there any contradictions?
4. How recent is the information?

Return JSON:
{{
  "verified": true/false,
  "confidence": 0.0-1.0,
  "supporting_sources": [url1, url2],
  "contradictions": ["any contradictions found"],
  "recency_days": number of days since data was published
}}"""

        response = llm.invoke(prompt)
        return eval(response.content)

    async def verify_all_facts(
        self,
        research_data: dict,
        sources: list[dict],
        llm
    ) -> dict:
        """Verify all extracted facts"""

        # Extract key facts from research data
        facts = self._extract_facts(research_data)

        # Verify each fact
        verification_results = []
        for fact in facts:
            result = await self.verify_fact(fact, sources, llm)
            verification_results.append({
                "fact": fact,
                "verification": result
            })

        # Calculate overall verification score
        verified_count = sum(1 for r in verification_results if r["verification"]["verified"])
        total_count = len(verification_results)
        verification_score = verified_count / total_count if total_count > 0 else 0

        return {
            "verification_score": verification_score,
            "results": verification_results,
            "verified_facts": verified_count,
            "total_facts": total_count
        }

    def _extract_facts(self, research_data: dict) -> list[str]:
        """Extract verifiable facts from research data"""

        # Use LLM to extract facts
        prompt = f"""Extract all verifiable facts from this research:

{research_data}

Return as JSON array: ["fact1", "fact2", ...]

Focus on:
- Numerical data (revenue, employees, funding)
- Dates (founded, acquisition dates)
- Locations (headquarters)
- Key events (product launches, funding rounds)
- Relationships (partnerships, investors)"""

        response = llm.invoke(prompt)
        return eval(response.content)
```

### 2. Contradiction Detection

```python
class ContradictionDetector:
    """Find contradictions in research data"""

    def detect_contradictions(
        self,
        research_data: dict,
        llm
    ) -> list[dict]:
        """Find contradictory information"""

        prompt = f"""Analyze this research for contradictions:

{research_data}

Look for:
1. Conflicting numbers (e.g., "Revenue: $10M" vs "Revenue: $15M")
2. Contradictory statements
3. Timeline inconsistencies
4. Logical impossibilities

Return JSON array of contradictions:
[
  {{
    "type": "conflicting_data",
    "description": "Revenue stated as both $10M and $15M",
    "locations": ["section1.revenue", "section2.financials"],
    "severity": "high"
  }}
]

Return empty array [] if no contradictions."""

        response = llm.invoke(prompt)
        contradictions = eval(response.content)

        return contradictions

    def resolve_contradictions(
        self,
        contradictions: list[dict],
        sources: list[dict],
        llm
    ) -> list[dict]:
        """Attempt to resolve contradictions using sources"""

        resolutions = []

        for contradiction in contradictions:
            # Find relevant sources for this contradiction
            relevant_sources = self._find_relevant_sources(
                contradiction,
                sources
            )

            # Use LLM to determine which is correct
            prompt = f"""Resolve this contradiction:

Contradiction: {contradiction['description']}

Relevant sources:
{relevant_sources}

Which version is correct? Why?

Return JSON:
{{
  "resolution": "explanation",
  "correct_value": "the correct value",
  "confidence": 0.0-1.0,
  "reasoning": "why this is correct"
}}"""

            response = llm.invoke(prompt)
            resolution = eval(response.content)

            resolutions.append({
                "contradiction": contradiction,
                "resolution": resolution
            })

        return resolutions
```

### 3. Source Quality Scoring

```python
class SourceQualityScorer:
    """Score source reliability and quality"""

    AUTHORITATIVE_DOMAINS = {
        "company_official": 1.0,  # tesla.com
        "sec_gov": 1.0,           # sec.gov (SEC filings)
        "major_news": 0.9,        # wsj.com, bloomberg.com, reuters.com
        "industry_publication": 0.85,  # techcrunch.com, fortune.com
        "verified_database": 0.9,      # crunchbase.com, pitchbook.com
        "academic": 0.85,               # .edu domains
        "wikipedia": 0.6,               # Good for overview, not authoritative
        "blog": 0.4,                    # Individual blogs
        "social_media": 0.3,            # Twitter, Reddit (unless verified)
        "unknown": 0.5                  # Default
    }

    def score_source(self, source: dict) -> float:
        """Score a single source"""

        url = source["url"]
        domain = self._extract_domain(url)

        # Categorize domain
        category = self._categorize_domain(domain)

        # Base score
        base_score = self.AUTHORITATIVE_DOMAINS.get(category, 0.5)

        # Adjust for recency
        recency_penalty = self._calculate_recency_penalty(source.get("date"))

        # Adjust for HTTPS
        https_bonus = 0.05 if url.startswith("https://") else 0.0

        # Final score
        final_score = min(1.0, base_score - recency_penalty + https_bonus)

        return final_score

    def _categorize_domain(self, domain: str) -> str:
        """Categorize domain into quality tier"""

        # Company's own domain
        if self._is_company_domain(domain):
            return "company_official"

        # Government/official
        if domain.endswith(".gov"):
            return "sec_gov"

        # Major news outlets
        major_news = ["wsj.com", "bloomberg.com", "reuters.com", "ft.com"]
        if domain in major_news:
            return "major_news"

        # Industry publications
        industry = ["techcrunch.com", "fortune.com", "forbes.com"]
        if domain in industry:
            return "industry_publication"

        # Verified databases
        databases = ["crunchbase.com", "pitchbook.com", "cbinsights.com"]
        if domain in databases:
            return "verified_database"

        # Academic
        if domain.endswith(".edu"):
            return "academic"

        # Wikipedia
        if "wikipedia.org" in domain:
            return "wikipedia"

        # Social media
        social = ["twitter.com", "x.com", "reddit.com", "facebook.com"]
        if any(s in domain for s in social):
            return "social_media"

        return "unknown"

    def _calculate_recency_penalty(self, date_str: str | None) -> float:
        """Penalty for old data"""

        if not date_str:
            return 0.1  # Unknown date, small penalty

        try:
            date = datetime.fromisoformat(date_str)
            age_days = (datetime.now() - date).days

            # Penalty scale
            if age_days < 30:
                return 0.0      # Recent, no penalty
            elif age_days < 90:
                return 0.05     # Slightly old
            elif age_days < 180:
                return 0.1      # 6 months old
            elif age_days < 365:
                return 0.2      # 1 year old
            else:
                return 0.3      # Very old

        except:
            return 0.1

    def score_all_sources(self, sources: list[dict]) -> dict:
        """Score all sources"""

        scored_sources = []
        for source in sources:
            score = self.score_source(source)
            scored_sources.append({
                **source,
                "quality_score": score
            })

        # Calculate average
        avg_score = sum(s["quality_score"] for s in scored_sources) / len(scored_sources)

        # Count by quality tier
        high_quality = sum(1 for s in scored_sources if s["quality_score"] >= 0.8)
        medium_quality = sum(1 for s in scored_sources if 0.5 <= s["quality_score"] < 0.8)
        low_quality = sum(1 for s in scored_sources if s["quality_score"] < 0.5)

        return {
            "sources": scored_sources,
            "average_quality": avg_score,
            "distribution": {
                "high_quality": high_quality,
                "medium_quality": medium_quality,
                "low_quality": low_quality
            }
        }
```

### 4. Completeness Checker

```python
class CompletenessChecker:
    """Check if research covers all required areas"""

    REQUIRED_SECTIONS = {
        "company_overview": {
            "required_fields": ["name", "industry", "founded", "headquarters"],
            "weight": 0.2
        },
        "financial_metrics": {
            "required_fields": ["revenue", "funding_or_market_cap", "employees"],
            "weight": 0.25
        },
        "products_services": {
            "required_fields": ["main_products", "target_customers"],
            "weight": 0.15
        },
        "market_position": {
            "required_fields": ["market_share", "competitors", "differentiation"],
            "weight": 0.2
        },
        "key_people": {
            "required_fields": ["ceo", "founders"],
            "weight": 0.1
        },
        "recent_news": {
            "required_fields": ["latest_developments"],
            "weight": 0.1
        }
    }

    def check_completeness(self, research_data: dict) -> dict:
        """Check if research is complete"""

        section_scores = {}
        missing_fields = []

        for section, requirements in self.REQUIRED_SECTIONS.items():
            section_data = research_data.get(section, {})

            # Count present fields
            present = sum(
                1 for field in requirements["required_fields"]
                if field in section_data and section_data[field]
            )

            # Calculate section score
            total = len(requirements["required_fields"])
            section_score = present / total if total > 0 else 0

            section_scores[section] = {
                "score": section_score,
                "present": present,
                "required": total
            }

            # Track missing fields
            for field in requirements["required_fields"]:
                if field not in section_data or not section_data[field]:
                    missing_fields.append(f"{section}.{field}")

        # Calculate weighted overall score
        overall_score = sum(
            score["score"] * self.REQUIRED_SECTIONS[section]["weight"]
            for section, score in section_scores.items()
        )

        return {
            "completeness_score": overall_score,
            "section_scores": section_scores,
            "missing_fields": missing_fields,
            "is_complete": overall_score >= 0.9
        }
```

---

## Logic Critic Agent

### Complete Implementation

```python
class LogicCriticAgent:
    """Quality assurance agent that verifies research"""

    def __init__(self, llm):
        self.llm = llm
        self.fact_verifier = FactVerifier()
        self.contradiction_detector = ContradictionDetector()
        self.source_scorer = SourceQualityScorer()
        self.completeness_checker = CompletenessChecker()

    async def critique(
        self,
        research_data: dict,
        sources: list[dict]
    ) -> dict:
        """Comprehensive quality assurance"""

        # 1. Verify facts
        fact_verification = await self.fact_verifier.verify_all_facts(
            research_data,
            sources,
            self.llm
        )

        # 2. Detect contradictions
        contradictions = self.contradiction_detector.detect_contradictions(
            research_data,
            self.llm
        )

        # 3. Score sources
        source_quality = self.source_scorer.score_all_sources(sources)

        # 4. Check completeness
        completeness = self.completeness_checker.check_completeness(research_data)

        # 5. Calculate overall quality score
        quality_score = self._calculate_quality_score(
            fact_verification["verification_score"],
            len(contradictions),
            source_quality["average_quality"],
            completeness["completeness_score"]
        )

        # 6. Generate recommendations
        recommendations = self._generate_recommendations(
            fact_verification,
            contradictions,
            source_quality,
            completeness
        )

        return {
            "quality_score": quality_score,
            "approved": quality_score >= 0.85 and len(contradictions) == 0,
            "fact_verification": fact_verification,
            "contradictions": contradictions,
            "source_quality": source_quality,
            "completeness": completeness,
            "recommendations": recommendations
        }

    def _calculate_quality_score(
        self,
        fact_score: float,
        contradiction_count: int,
        source_score: float,
        completeness_score: float
    ) -> float:
        """Calculate weighted quality score"""

        # Penalties
        contradiction_penalty = min(0.3, contradiction_count * 0.1)

        # Weighted average
        score = (
            fact_score * 0.3 +           # 30% weight
            source_score * 0.3 +         # 30% weight
            completeness_score * 0.4     # 40% weight
            - contradiction_penalty      # Penalty
        )

        return max(0.0, min(1.0, score))

    def _generate_recommendations(
        self,
        fact_verification: dict,
        contradictions: list[dict],
        source_quality: dict,
        completeness: dict
    ) -> list[str]:
        """Generate actionable recommendations"""

        recommendations = []

        # Fact verification recommendations
        if fact_verification["verification_score"] < 0.8:
            recommendations.append(
                f"⚠️ Only {fact_verification['verified_facts']}/{fact_verification['total_facts']} "
                f"facts verified. Re-search for better sources."
            )

        # Contradiction recommendations
        if contradictions:
            recommendations.append(
                f"⚠️ Found {len(contradictions)} contradictions. Resolve before publishing."
            )

        # Source quality recommendations
        if source_quality["average_quality"] < 0.7:
            recommendations.append(
                f"⚠️ Average source quality is {source_quality['average_quality']:.0%}. "
                f"Use more authoritative sources."
            )

        if source_quality["distribution"]["low_quality"] > 3:
            recommendations.append(
                f"⚠️ {source_quality['distribution']['low_quality']} low-quality sources. "
                f"Replace with official or major news sources."
            )

        # Completeness recommendations
        if completeness["completeness_score"] < 0.9:
            missing = ", ".join(completeness["missing_fields"][:5])
            recommendations.append(
                f"⚠️ Missing fields: {missing}. Research these areas."
            )

        # Positive feedback
        if not recommendations:
            recommendations.append("✅ Research quality is excellent! Ready to publish.")

        return recommendations
```

---

## Integration with Research Workflow

### Quality Gate Pattern

```python
async def research_with_quality_gate(company_name: str):
    """Research with quality assurance"""

    max_iterations = 3
    current_iteration = 0

    while current_iteration < max_iterations:
        # 1. Conduct research
        research_data, sources = await conduct_research(company_name)

        # 2. Quality check
        critic = LogicCriticAgent(llm)
        quality_report = await critic.critique(research_data, sources)

        # 3. Check if approved
        if quality_report["approved"]:
            # Quality is good!
            return {
                "research_data": research_data,
                "quality_report": quality_report,
                "status": "approved"
            }

        # 4. Not approved - identify gaps
        gaps = quality_report["recommendations"]

        # 5. Follow-up research
        follow_up_results = await conduct_follow_up_research(
            company_name,
            gaps
        )

        # 6. Merge results
        research_data = merge_research_results(research_data, follow_up_results)

        current_iteration += 1

    # Max iterations reached
    return {
        "research_data": research_data,
        "quality_report": quality_report,
        "status": "max_iterations_reached"
    }
```

---

## Quality Metrics

### Target Benchmarks

```yaml
Quality Scores:
  Overall Quality: ≥ 85%
  Fact Verification: ≥ 90%
  Source Quality: ≥ 75%
  Completeness: ≥ 95%
  Contradictions: 0

Source Distribution:
  High Quality (≥0.8): ≥ 60%
  Medium Quality (0.5-0.8): ≥ 30%
  Low Quality (<0.5): ≤ 10%
```

---

## Implementation Roadmap

### Week 9: Basic QA
- Implement source quality scoring
- Add completeness checker
- Simple quality score calculation

### Week 10: Advanced QA
- Add fact verification
- Implement contradiction detection
- Full Logic Critic agent

### Week 11: Quality Gates
- Integrate into research workflow
- Auto-retry on low quality
- Quality dashboard

---

## References

- Open Deep Research verification patterns
- LangMem memory quality tracking
- Academic research verification standards
