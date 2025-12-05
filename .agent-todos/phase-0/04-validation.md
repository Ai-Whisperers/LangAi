# Task: Validation & Performance Testing

**Phase:** 0
**Estimated Time:** 2 hours
**Dependencies:** 01, 02, 03 (all previous tasks)
**Status:** [ ] Not Started

## Context

Before declaring Phase 0 complete, we must validate that our research script actually works well across different types of companies and meets our success criteria. This task involves systematic testing, metric collection, and decision-making about whether to proceed to Phase 1.

## Prerequisites

- [x] `hello_research.py` working
- [x] Can research at least one company successfully
- [x] Script completes without crashing

## Implementation Steps

### Step 1: Create Test Company List

**Goal:** Diverse set of companies to test

**Actions:**
- [ ] Create `test_companies.json`:

```json
{
  "test_companies": [
    {
      "name": "Tesla",
      "type": "Large Public",
      "industry": "Automotive",
      "expected_data": {
        "has_revenue": true,
        "has_stock": true,
        "has_ceo": true
      }
    },
    {
      "name": "OpenAI",
      "type": "Large Private",
      "industry": "AI",
      "expected_data": {
        "has_funding": true,
        "has_valuation": true
      }
    },
    {
      "name": "Stripe",
      "type": "Large Private",
      "industry": "Fintech",
      "expected_data": {
        "has_revenue": true,
        "has_funding": true
      }
    },
    {
      "name": "Anthropic",
      "type": "Medium Private",
      "industry": "AI",
      "expected_data": {
        "has_funding": true
      }
    },
    {
      "name": "Rivian",
      "type": "Public (Recent IPO)",
      "industry": "Automotive",
      "expected_data": {
        "has_stock": true
      }
    }
  ]
}
```

### Step 2: Create Validation Script

**Goal:** Automated testing framework

**Actions:**
- [ ] Create `validate_phase0.py`:

```python
#!/usr/bin/env python3
"""
Validate Phase 0 - Test research script with multiple companies
"""

import json
import subprocess
import time
from pathlib import Path
from datetime import datetime

TEST_COMPANIES = [
    "Tesla",
    "OpenAI",
    "Stripe",
    "Anthropic",
    "Rivian"
]

def main():
    print("=" * 70)
    print("  PHASE 0 VALIDATION - Company Research System")
    print("=" * 70)

    results = []

    for i, company in enumerate(TEST_COMPANIES, 1):
        print(f"\n\n[{i}/{len(TEST_COMPANIES)}] Testing: {company}")
        print("-" * 70)

        result = test_company(company)
        results.append(result)

        # Show summary
        status = "✅ PASS" if result['passed'] else "❌ FAIL"
        print(f"\n{status} - {company}")
        print(f"  Time: {result['time']:.1f}s")
        print(f"  Cost: ${result.get('cost', 0):.4f}")
        print(f"  Quality: {result.get('quality', 0)}/100")

        # Wait between tests
        if i < len(TEST_COMPANIES):
            print("\nWaiting 5 seconds...")
            time.sleep(5)

    # Generate summary report
    print("\n\n" + "=" * 70)
    print("  VALIDATION SUMMARY")
    print("=" * 70)

    generate_summary(results)

def test_company(company: str) -> dict:
    """Test research for one company"""

    start_time = time.time()

    # Run research script
    try:
        result = subprocess.run(
            ["python", "hello_research.py", company],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        elapsed = time.time() - start_time
        success = result.returncode == 0

        # Parse output for metrics
        output = result.stdout
        cost = extract_cost(output)

        # Check if report exists
        report_path = Path(f"outputs/{company.replace(' ', '_')}/report.md")
        report_exists = report_path.exists()

        # Evaluate report quality
        quality = 0
        if report_exists:
            quality = evaluate_report(report_path, company)

        passed = (
            success and
            report_exists and
            elapsed < 300 and  # < 5 minutes
            cost < 0.50 and    # < $0.50
            quality >= 60      # >= 60% quality
        )

        return {
            'company': company,
            'passed': passed,
            'success': success,
            'time': elapsed,
            'cost': cost,
            'report_exists': report_exists,
            'quality': quality,
            'output': output,
            'error': result.stderr if not success else None
        }

    except subprocess.TimeoutExpired:
        return {
            'company': company,
            'passed': False,
            'success': False,
            'time': 300,
            'cost': 0,
            'report_exists': False,
            'quality': 0,
            'error': "Timeout after 5 minutes"
        }

    except Exception as e:
        return {
            'company': company,
            'passed': False,
            'success': False,
            'time': 0,
            'cost': 0,
            'report_exists': False,
            'quality': 0,
            'error': str(e)
        }

def extract_cost(output: str) -> float:
    """Extract cost from script output"""
    import re
    match = re.search(r'Total: \$([0-9.]+)', output)
    if match:
        return float(match.group(1))
    return 0.0

def evaluate_report(report_path: Path, company: str) -> int:
    """Evaluate report quality (0-100)"""

    content = report_path.read_text()

    score = 0

    # Check for required sections (50 points)
    required_sections = [
        "Company Overview",
        "Financial Metrics",
        "Products",
        "Competitors",
        "Sources"
    ]

    for section in required_sections:
        if section in content:
            score += 10

    # Check for specific data (30 points)
    checks = [
        ("Industry" in content, 5),
        ("Founded" in content, 5),
        ("Revenue" in content or "Funding" in content, 10),
        ("http" in content, 5),  # Has URLs
        (company.lower() in content.lower(), 5)  # Mentions company
    ]

    for check, points in checks:
        if check:
            score += points

    # Check content length (20 points)
    word_count = len(content.split())
    if word_count > 500:
        score += 20
    elif word_count > 300:
        score += 10

    return min(score, 100)

def generate_summary(results: list[dict]):
    """Generate validation summary"""

    passed_count = sum(1 for r in results if r['passed'])
    total_count = len(results)

    avg_time = sum(r['time'] for r in results) / total_count
    avg_cost = sum(r.get('cost', 0) for r in results) / total_count
    avg_quality = sum(r.get('quality', 0) for r in results) / total_count

    print(f"\nResults: {passed_count}/{total_count} tests passed")
    print(f"\nAverage Metrics:")
    print(f"  Time: {avg_time:.1f} seconds")
    print(f"  Cost: ${avg_cost:.4f}")
    print(f"  Quality: {avg_quality:.0f}/100")

    print(f"\nDetailed Results:")
    for r in results:
        status = "✅" if r['passed'] else "❌"
        print(f"\n{status} {r['company']}")
        print(f"   Time: {r['time']:.1f}s | Cost: ${r.get('cost', 0):.4f} | Quality: {r.get('quality', 0)}/100")
        if not r['passed']:
            print(f"   Error: {r.get('error', 'Unknown')}")

    # Check if Phase 0 is complete
    print(f"\n" + "=" * 70)
    phase_complete = (
        passed_count >= 4 and  # At least 4/5 pass
        avg_time < 300 and     # < 5 minutes average
        avg_cost < 0.50 and    # < $0.50 average
        avg_quality >= 70      # >= 70% quality average
    )

    if phase_complete:
        print("✅ PHASE 0 COMPLETE - Ready for Phase 1")
        print("\nPhase 0 Success Criteria Met:")
        print(f"  ✅ Pass rate: {passed_count}/{total_count} (target: 4/5)")
        print(f"  ✅ Avg time: {avg_time:.1f}s (target: <300s)")
        print(f"  ✅ Avg cost: ${avg_cost:.4f} (target: <$0.50)")
        print(f"  ✅ Avg quality: {avg_quality:.0f}/100 (target: ≥70)")
    else:
        print("❌ PHASE 0 INCOMPLETE - Needs improvement")
        print("\nFailed Criteria:")
        if passed_count < 4:
            print(f"  ❌ Pass rate: {passed_count}/{total_count} (need: 4/5)")
        if avg_time >= 300:
            print(f"  ❌ Avg time: {avg_time:.1f}s (need: <300s)")
        if avg_cost >= 0.50:
            print(f"  ❌ Avg cost: ${avg_cost:.4f} (need: <$0.50)")
        if avg_quality < 70:
            print(f"  ❌ Avg quality: {avg_quality:.0f}/100 (need: ≥70)")

    # Save results
    results_file = Path("outputs/phase0_validation.json")
    results_file.parent.mkdir(exist_ok=True)
    results_file.write_text(json.dumps({
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'passed': phase_complete,
            'pass_rate': f"{passed_count}/{total_count}",
            'avg_time': avg_time,
            'avg_cost': avg_cost,
            'avg_quality': avg_quality
        },
        'results': results
    }, indent=2))

    print(f"\n📁 Results saved to: {results_file}")

if __name__ == "__main__":
    main()
```

- [ ] Run validation:

```bash
python validate_phase0.py
```

### Step 3: Manual Quality Review

**Goal:** Human assessment of report quality

**Actions:**
- [ ] Read each generated report
- [ ] For each report, assess:
  - [ ] Accuracy: Are the facts correct?
  - [ ] Completeness: Are all sections filled?
  - [ ] Sources: Are sources cited?
  - [ ] Usefulness: Would this be useful to a user?

- [ ] Create `quality_review.md`:

```markdown
# Phase 0 Quality Review

**Date:** 2025-12-05
**Reviewer:** [Your Name]

## Tesla Report

**Accuracy:** 9/10
- Revenue figures correct ✅
- CEO name correct ✅
- Founded year correct ✅
- One minor error: [describe]

**Completeness:** 8/10
- All required sections present ✅
- Some sections thin (e.g., competitors)

**Sources:** 10/10
- All facts have sources ✅
- URLs work ✅

**Usefulness:** 9/10
- Would be useful for quick research ✅
- Good starting point for deeper dive

**Overall:** 90/100

## [Repeat for each company]

---

## Summary

- **Average Accuracy:** X/10
- **Average Completeness:** X/10
- **Average Sources:** X/10
- **Average Usefulness:** X/10

**Overall Assessment:** Phase 0 [PASS/FAIL]
```

### Step 4: Performance Benchmarking

**Goal:** Measure actual system performance

**Actions:**
- [ ] Create benchmark spreadsheet or markdown table:

```markdown
# Phase 0 Performance Benchmarks

| Company | Type | Time (s) | Cost ($) | Quality | Pass |
|---------|------|----------|----------|---------|------|
| Tesla | Public | 145 | $0.32 | 90 | ✅ |
| OpenAI | Private | 167 | $0.28 | 85 | ✅ |
| Stripe | Private | 134 | $0.35 | 80 | ✅ |
| Anthropic | Private | 122 | $0.29 | 75 | ✅ |
| Rivian | Public | 156 | $0.31 | 82 | ✅ |

**Averages:**
- Time: 144.8s (target: <300s) ✅
- Cost: $0.31 (target: <$0.50) ✅
- Quality: 82.4 (target: ≥70) ✅
- Pass Rate: 5/5 (100%) ✅

**Phase 0 Status:** ✅ COMPLETE
```

### Step 5: Decision Point Analysis

**Goal:** Decide whether to proceed to Phase 1

**Actions:**
- [ ] Answer these questions:

```markdown
# Phase 0 Decision Point

## Technical Viability

**Q1: Does the core concept work?**
Answer: [Yes/No]
Evidence: [Reference test results]

**Q2: Is quality acceptable?**
Answer: [Yes/No]
Evidence: Average quality score: [X]/100

**Q3: Is performance acceptable?**
Answer: [Yes/No]
Evidence: Average time: [X]s, Average cost: $[X]

## Business Viability

**Q4: Would users pay for this?**
Answer: [Yes/No]
Reasoning: [Your assessment]

**Q5: What's the unit economics?**
- Cost per research: $[X]
- Potential price: $[X]
- Margin: [X]%

## Risk Assessment

**Q6: What are the biggest risks?**
1. [Risk 1]
2. [Risk 2]
3. [Risk 3]

**Q7: Can these risks be mitigated?**
Answer: [Yes/No]
Plan: [Mitigation strategy]

## Decision

**Proceed to Phase 1?** [Yes/No]

**Rationale:**
[Why you're making this decision]

**If NO:**
What needs to change: [List]

**If YES:**
Next steps: [List]
```

## Acceptance Criteria

- [ ] Tested with 5+ companies
- [ ] Validation script runs successfully
- [ ] All metrics documented
- [ ] Manual quality review complete
- [ ] Performance benchmarks recorded
- [ ] Decision documented
- [ ] README updated with results
- [ ] Phase 0 marked complete or action items defined

## Testing Instructions

Run complete validation:

```bash
# 1. Run automated validation
python validate_phase0.py

# 2. Check results
cat outputs/phase0_validation.json

# 3. Manually review reports
ls outputs/*/report.md

# 4. Open each report and assess quality
```

## Success Metrics

### Technical Thresholds
- **Pass Rate:** ≥ 4/5 companies (80%)
- **Average Time:** < 300 seconds (5 minutes)
- **Average Cost:** < $0.50
- **Average Quality:** ≥ 70/100

### Business Thresholds
- **User Value:** Reports are useful (subjective)
- **Unit Economics:** Positive margin possible
- **Scalability:** No obvious blockers

## Common Issues & Solutions

**Issue 1: Quality scores too low**
- **Solution:** Improve prompts, add iteration loop
- **Decision:** If < 60%, rework prompts before Phase 1

**Issue 2: Costs too high**
- **Solution:** Optimize token usage, use cheaper models
- **Decision:** If > $0.75, investigate cost reduction

**Issue 3: Time too long**
- **Solution:** Parallel execution, reduce searches
- **Decision:** If > 600s, optimize critical path

**Issue 4: Accuracy issues**
- **Solution:** Add fact verification, better sources
- **Decision:** If < 70% accurate, add quality checks

## Next Steps

### If Phase 0 PASSES:
1. Mark Phase 0 as [x] Complete
2. Update README with metrics
3. Document lessons learned
4. Create Phase 0 → Phase 1 transition plan
5. Start Phase 1: [Basic Research Loop](../phase-1/README.md)

### If Phase 0 FAILS:
1. Document failure reasons
2. Create action plan to address issues
3. Re-run validation after fixes
4. Re-evaluate viability

### Either Way:
1. Commit all results:

```bash
git add outputs/ quality_review.md validate_phase0.py
git commit -m "test(phase-0): complete validation and performance testing

Results:
- Pass rate: X/5
- Avg time: Xs
- Avg cost: $X
- Avg quality: X/100

Status: [PASS/FAIL]"
```

---

**Completed By:** TBD
**Validation Date:** TBD
**Results:** TBD
**Decision:** TBD
