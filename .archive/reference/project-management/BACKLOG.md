# Product Backlog

**Last Updated:** 2025-12-05

This backlog contains future features, enhancements, and technical debt items not yet scheduled for implementation.

---

## Prioritization Framework

Items are prioritized using **RICE Score**:
- **R**each: How many users will benefit?
- **I**mpact: How much will it improve the product?
- **C**onfidence: How sure are we about estimates?
- **E**ffort: How much work is required?

**RICE Score = (Reach × Impact × Confidence) / Effort**

---

## High Priority (RICE > 7.0)

### Feature: Memory System for Past Research Caching

**Description:**
Implement long-term memory to cache past company research and avoid re-researching.

**Benefits:**
- 70-90% cost savings on repeat queries
- 100x faster for cached companies
- Cross-company insights

**RICE:**
- Reach: 80% of users (repeat research common)
- Impact: High (3/3) - massive cost savings
- Confidence: 90% (well-understood feature)
- Effort: 3 weeks
- **Score: 7.2**

**Status:** 🟡 Planned for Phase 2 (Week 8-9)

---

### Feature: Real-time Streaming Responses

**Description:**
Stream research findings to users in real-time via WebSocket instead of waiting 5 minutes.

**Benefits:**
- Better user experience
- Perceived 5x speed improvement
- Users see progress

**RICE:**
- Reach: 100% of users
- Impact: Medium (2/3) - UX improvement
- Confidence: 80% (standard feature)
- Effort: 1 week
- **Score: 8.0**

**Status:** 🟡 Planned for Phase 1 (Week 5)

---

### Feature: Multi-Company Comparison Reports

**Description:**
Allow users to compare 2-5 companies side-by-side in a single report.

**Benefits:**
- Common user need (competitor analysis)
- Higher value per report
- Differentiator feature

**RICE:**
- Reach: 60% of users
- Impact: High (3/3) - key feature
- Confidence: 70% (more complex)
- Effort: 2 weeks
- **Score: 6.3 → 7.5** (high value)

**Status:** 🟢 Prioritized for Phase 2

---

## Medium Priority (RICE 4.0-7.0)

### Enhancement: PDF Export with Branding

**Description:**
Generate professional PDF reports with custom branding, charts, and formatting.

**Benefits:**
- Professional deliverable
- Enterprise customers expect PDFs
- Branding opportunities

**RICE:**
- Reach: 40% of users
- Impact: Medium (2/3)
- Confidence: 80%
- Effort: 1 week
- **Score: 6.4**

**Status:** 🟡 Backlog

---

### Feature: API Rate Limiting & Usage Quotas

**Description:**
Implement per-user rate limits and usage quotas to control costs.

**Benefits:**
- Cost control
- Prevent abuse
- Fair usage

**RICE:**
- Reach: 100% (system-wide)
- Impact: Medium (2/3) - operational
- Confidence: 90%
- Effort: 1 week
- **Score: 6.0**

**Status:** 🟡 Planned for Phase 1 (Week 6)

---

### Feature: Custom Agent Configurations

**Description:**
Allow users to enable/disable specific agents based on their research needs.

**Benefits:**
- Cost savings for simple queries
- Faster for targeted research
- User control

**RICE:**
- Reach: 30% of users (power users)
- Impact: Medium (2/3)
- Confidence: 60%
- Effort: 2 weeks
- **Score: 2.7**

**Status:** 🔴 Low priority

---

### Enhancement: Agent Performance Dashboard

**Description:**
Internal dashboard showing per-agent performance (speed, cost, quality).

**Benefits:**
- Identify slow agents
- Optimize costs
- Quality monitoring

**RICE:**
- Reach: Internal team (5 people)
- Impact: High (3/3) - operational insight
- Confidence: 80%
- Effort: 1 week
- **Score: 1.2** (but high internal value)

**Status:** 🟡 Planned for Phase 2

---

## Low Priority (RICE < 4.0)

### Feature: Voice Input (Research via Speech)

**Description:**
Allow users to request research via voice input.

**Benefits:**
- Convenience
- Accessibility

**RICE:**
- Reach: 5% of users
- Impact: Low (1/3)
- Confidence: 50%
- Effort: 2 weeks
- **Score: 0.1**

**Status:** 🔴 Not planned

---

### Enhancement: Dark Mode UI

**Description:**
Add dark mode theme to web dashboard.

**Benefits:**
- User preference
- Modern UI expectation

**RICE:**
- Reach: 20% of users
- Impact: Low (1/3)
- Confidence: 90%
- Effort: 0.5 weeks
- **Score: 1.2**

**Status:** 🔴 Nice to have

---

## Technical Debt

### TD-001: Add Type Hints Throughout Codebase

**Priority:** Medium
**Effort:** 1 week
**Impact:** Better IDE support, fewer bugs

---

### TD-002: Refactor State Management

**Priority:** Low
**Effort:** 2 weeks
**Impact:** Cleaner code, easier to extend

**Note:** Wait until patterns stabilize

---

### TD-003: Add Integration Test Suite

**Priority:** High
**Effort:** 1 week
**Impact:** Catch regressions, confidence in deployments

**Status:** 🟢 Scheduled for Week 4

---

## Research & Exploration

### R&D: Multi-Language Support

**Description:**
Research companies in non-English markets (China, Japan, LATAM).

**Unknowns:**
- Source availability
- LLM quality for non-English
- Translation costs

**Next Steps:**
- Prototype with 5 non-English companies
- Evaluate quality degradation
- Document findings

---

### R&D: Image/Chart Analysis

**Description:**
Extract data from charts, infographics, and screenshots.

**Unknowns:**
- Vision model costs
- Accuracy vs manual extraction
- Integration complexity

**Next Steps:**
- Test GPT-4 Vision on sample charts
- Compare cost/quality trade-offs

---

## Ideas Inbox (Unscored)

Add ideas here before scoring and prioritizing:

- [ ] Mobile app (iOS/Android)
- [ ] Slack/Teams integration
- [ ] Automated daily company monitoring
- [ ] Industry trend reports (not just companies)
- [ ] Data visualization (interactive charts)
- [ ] Export to Google Sheets
- [ ] Email digest of research
- [ ] Collaborative research (team features)
- [ ] API webhooks for automation
- [ ] Chrome extension for quick research

---

## Archived / Rejected

### Custom Web Scraping (Rejected)

**Reason:** Too brittle, Tavily API is better (see EXP-099)
**Date:** 2025-11-28

---

### Blockchain Integration (Rejected)

**Reason:** No clear use case
**Date:** 2025-10-15

---

## Review Schedule

- **Weekly:** Review top 5 items, re-score based on new learnings
- **Monthly:** Major backlog grooming, archive stale items
- **Quarterly:** Strategic reprioritization based on user feedback
