---
name: create-epic
description: "Create a well-structured Agile Epic with strategic alignment and feature breakdown"
category: agile
tags: agile, epic, strategic-planning, documentation
argument-hint: "Epic title or strategic initiative name"
---

# Create Epic for [Strategic Initiative]

**Pattern**: Strategic Initiative Documentation ⭐⭐⭐⭐⭐ | **Effectiveness**: Very High | **Use When**: Translating business strategy into actionable development roadmap

Create a well-structured Agile Epic documentation file.

## Purpose

Generate comprehensive Epic documentation that links high-level business strategy to implementable features, providing executive-level overview while breaking down strategic initiatives into manageable Business and Technical Features with clear success metrics.

**Required Context**:

- `[EPIC_TITLE]`: The name of the strategic initiative.
- `[BUSINESS_GOAL]`: The primary business outcome desired.
- `[STAKEHOLDERS]`: Key stakeholders involved.
- `[TIMELINE]`: Target timeline (e.g., Q1 2026).

## User Process

1. **Gather Strategic Context**: Identify business goal, stakeholders, and target timeline
2. **Invoke Prompt**: Provide Epic title, business goal, stakeholders, and timeline
3. **Review Generated Epic**: Validate strategic alignment and scope boundaries
4. **Refine Feature Breakdown**: Adjust feature list and success metrics as needed
5. **Stakeholder Review**: Present to stakeholders for approval and prioritization
6. **Commit Documentation**: Save to `docs/agile/epics/` with appropriate naming

## Reasoning Process (for AI Agent)

1. **Identify Strategic Alignment**: Connect the Epic to high-level business goals, OKRs, or company strategy
2. **Define Scope**: Clearly state what is IN scope and OUT of scope to manage expectations and prevent scope creep
3. **Break Down into Features**: Identify the key Business Features (user-facing) and Technical Features (enablers) required
4. **Determine Metrics**: Define how success will be measured with specific KPIs and success criteria
5. **Assess Risks**: Identify potential blockers, dependencies, and mitigation strategies
6. **Validate Completeness**: Ensure executive summary, problem statement, SMART goals, and success metrics are all present

## Process

1. **Epic Identifier**:
   - Format: `EPIC-[Name]`
   - Example: `EPIC-CLOUD-MIGRATION`

2. **Executive Summary**:
   - High-level overview for leadership.
   - Business value proposition.

3. **Problem Statement**:
   - What problem are we solving?
   - Who is affected?

4. **Goals & Objectives (SMART)**:
   - Specific, Measurable, Achievable, Relevant, Time-bound.

5. **Scope Boundaries**:
   - **In Scope**: specific deliverables.
   - **Out of Scope**: specific exclusions.

6. **Key Features**:
   - List of Business Features (functional).
   - List of Technical Features (enablers).

7. **Success Metrics**:
   - KPIs and success criteria.

8. **Dependencies & Risks**:
   - Internal/External dependencies.
   - Risk assessment matrix.

## Examples (Few-Shot)

### Example 1: Modernize Reporting Infrastructure

**Input**:
```
Epic Title: Modernize Reporting Infrastructure
Business Goal: Replace legacy Crystal Reports with PowerBI for real-time business intelligence
Stakeholders: Finance (CFO), Sales (VP Sales), IT (CTO)
Timeline: Q1-Q2 2026 (6 months)
```

**AI Reasoning**:
- Strategic alignment: Supports company OKR "Data-Driven Decision Making"
- Problem: Legacy Crystal Reports are slow, manual, and difficult to maintain
- Scope: Reporting infrastructure only (NOT operational dashboards, NOT data collection systems)
- Key features: Data warehouse (enabler), Sales Dashboard (user-facing), Finance Dashboard (user-facing)
- Success metrics: Reduce report generation time, increase data freshness, improve user satisfaction
- Risks: Data migration complexity, user adoption, training requirements

**Output**:
```markdown
# Epic: EPIC-MODERN-REPORTING

## Epic Identifier
EPIC-MODERN-REPORTING: Modernize Reporting Infrastructure

## Executive Summary
Replace legacy Crystal Reports with modern PowerBI infrastructure to enable real-time business intelligence and data-driven decision making across Finance and Sales departments. This strategic initiative will reduce report generation time from days to minutes, eliminate manual data aggregation, and provide executive leadership with up-to-date business metrics.

**Business Value**: $200K annual savings in IT maintenance, 80% reduction in report generation time, real-time data access for 50+ managers

## Problem Statement

### What Problem Are We Solving?
Current Crystal Reports infrastructure is 15+ years old, requires manual data extraction, and produces reports with 24-48 hour data lag. Business leaders cannot make timely decisions based on stale data.

### Who Is Affected?
- **Primary**: Finance team (monthly/quarterly reporting), Sales managers (daily performance tracking)
- **Secondary**: C-level executives (strategic decision making), Regional directors (operational oversight)

### Business Impact
- Report generation takes 2-4 days per month (finance team)
- Sales managers lack real-time visibility into performance
- Manual errors in report aggregation (~5% error rate)
- High IT maintenance costs ($50K/year for Crystal Reports)

## Goals & Objectives (SMART)

1. **Specific**: Migrate all finance and sales reports from Crystal Reports to PowerBI
2. **Measurable**: Reduce report generation time from days to <3 seconds, achieve 99.5% uptime
3. **Achievable**: Leverage existing data warehouse (or build if needed), utilize Microsoft ecosystem
4. **Relevant**: Aligns with company OKR "Data-Driven Decision Making", supports strategic growth
5. **Time-bound**: Complete by Q2 2026 (6-month timeline)

## Scope Boundaries

### In Scope
- Migration of all Finance reports (monthly P&L, quarterly board reports, budget tracking)
- Migration of all Sales reports (daily sales, regional performance, pipeline tracking)
- Data warehouse setup (if not exists) for centralized data
- PowerBI licensing and infrastructure setup
- User training for Finance and Sales teams (10 sessions)
- Documentation and best practices

### Out of Scope
- Operational dashboards (manufacturing, inventory) - deferred to Phase 2
- Real-time alerting system - separate initiative
- Historical data migration beyond 5 years
- Mobile app development (PowerBI mobile is sufficient)
- Custom report development beyond standard templates

## Key Features

### Business Features (User-Facing)
- **FEAT-RPT-SALES-DASH**: Interactive sales dashboard with filtering, drill-down, and export capabilities
- **FEAT-RPT-FINANCE-DASH**: Executive finance dashboard (P&L, budget vs actual, variance analysis)
- **FEAT-RPT-BOARD-REPORTS**: Automated quarterly board reporting with PDF export
- **FEAT-RPT-PIPELINE**: Sales pipeline visibility with forecast accuracy tracking

### Technical Features (Enablers)
- **TECH-DATA-WAREHOUSE**: Establish Snowflake data warehouse with 5-year historical data
- **TECH-ETL-PIPELINE**: Build ETL pipelines from source systems to data warehouse
- **TECH-POWERBI-INFRA**: Setup PowerBI Premium workspace, security, and licensing
- **TECH-RPT-MONITORING**: Monitoring and alerting for data pipeline failures

## Success Metrics (KPIs)

### Quantitative Metrics
- **Report Generation Time**: Reduce from 48 hours to <3 seconds (98% improvement)
- **Data Freshness**: Improve from 24-hour lag to 5-minute intervals (real-time)
- **User Adoption**: 80%+ of finance and sales staff using PowerBI daily within 30 days
- **Cost Savings**: Eliminate $50K/year Crystal Reports maintenance costs
- **Uptime**: Achieve 99.5% availability during business hours

### Qualitative Metrics
- **User Satisfaction**: 90%+ satisfaction score in post-rollout survey
- **Decision Quality**: Executives report improved decision-making speed and confidence
- **Error Reduction**: Eliminate manual aggregation errors (currently ~5%)

## Dependencies & Risks

### Internal Dependencies
- Data warehouse infrastructure approval (CTO sign-off)
- Budget allocation for PowerBI Premium licensing ($20K/year)
- IT team availability for ETL development (2 developers, 3 months)
- User availability for training sessions (10 sessions, 2 hours each)

### External Dependencies
- Microsoft PowerBI licensing agreement renewal
- Snowflake data warehouse contract (if not exists)
- Network bandwidth upgrade for data sync (if needed)

### Risk Assessment Matrix

| Risk | Likelihood | Impact | Mitigation Strategy |
|------|-----------|--------|-------------------|
| Data migration complexity | High | High | Phased migration, extensive testing, data validation framework |
| User adoption resistance | Medium | High | Change management, hands-on training, executive sponsorship |
| Budget overrun | Low | Medium | Fixed-price contracts, phased approach with stop gates |
| Legacy data quality issues | High | Medium | Data cleansing phase, validation rules, manual review |
| PowerBI performance issues | Low | High | Performance testing, data model optimization, Premium capacity |

## Timeline & Milestones

- **Q1 2026 Month 1**: Requirements gathering, data warehouse setup
- **Q1 2026 Month 2**: ETL pipeline development, data migration phase 1
- **Q1 2026 Month 3**: PowerBI dashboard development, user testing
- **Q2 2026 Month 1**: Training rollout, pilot with Finance team
- **Q2 2026 Month 2**: Full rollout to Sales, documentation complete
- **Q2 2026 Month 3**: Retrospective, optimization, Crystal Reports decommission

## Stakeholders

- **Executive Sponsor**: CFO (budget approval, strategic alignment)
- **Product Owner**: Director of Finance (requirements, acceptance)
- **Technical Lead**: CTO (architecture, infrastructure decisions)
- **Key Users**: VP Sales, Finance Manager, Regional Directors
- **Delivery Team**: 2 backend developers, 1 PowerBI specialist, 1 QA engineer

## Success Criteria (Epic Completion)

- [ ] All Finance and Sales reports migrated to PowerBI
- [ ] Data warehouse operational with 5-year historical data
- [ ] ETL pipelines running reliably (99% success rate)
- [ ] 80%+ user adoption achieved
- [ ] Crystal Reports decommissioned
- [ ] User satisfaction >90% in survey
- [ ] Performance SLAs met (<3 second load time, 99.5% uptime)
- [ ] ROI validated ($200K annual savings achieved)
```

### Example 2: Quick Epic (Brief Input)

**Input**:
```
Title: Cloud Migration. Goal: Move on-premise infrastructure to AWS. Timeline: 9 months.
```

**AI Reasoning**:
- Strategic initiative: Infrastructure modernization
- Problem: On-premise maintenance costs, scalability limitations
- Features: Lift-and-shift (Tech), Network setup (Tech), Application refactoring (Tech), Cost monitoring (Biz)
- Success: Reduce operational costs, improve scalability

**Output**:
```markdown
# Epic: EPIC-CLOUD-MIGRATION

## Executive Summary
Migrate on-premise infrastructure to AWS to reduce operational costs by 40%, improve scalability, and enable faster feature deployment.

## Problem Statement
Current on-premise infrastructure requires $500K/year maintenance, limits scalability during peak seasons, and slows feature deployment cycles.

## Goals & Objectives (SMART)
- Migrate 100% of production workloads to AWS within 9 months
- Reduce infrastructure costs by 40% ($200K annual savings)
- Improve deployment frequency from monthly to weekly
- Achieve 99.9% uptime SLA

## Key Features
- **TECH-CLOUD-NETWORK**: Setup VPC, subnets, security groups
- **TECH-CLOUD-MIGRATION**: Lift-and-shift existing applications
- **TECH-CLOUD-REFACTOR**: Refactor applications for cloud-native architecture
- **FEAT-CLOUD-MONITORING**: Cost monitoring and optimization dashboard

## Success Metrics
- 40% reduction in infrastructure costs
- 99.9% uptime achieved
- Deployment frequency increased to weekly
- Zero data loss during migration
```

## Expected Output

**Deliverables**:

1. Complete Epic markdown file.
2. Feature breakdown list.
3. Risk assessment.

**Format**: Markdown file following `docs/agile/epics/` structure.

## Quality Criteria

- [ ] Clear business value statement with quantified impact
- [ ] Explicit scope boundaries (IN scope and OUT of scope)
- [ ] SMART goals (Specific, Measurable, Achievable, Relevant, Time-bound)
- [ ] Measurable success metrics (quantitative and qualitative)
- [ ] Breakdown into manageable Business and Technical Features
- [ ] Risk assessment with mitigation strategies
- [ ] Dependencies identified (internal and external)
- [ ] Timeline with key milestones
- [ ] Stakeholder list with roles
- [ ] Success criteria for Epic completion
- [ ] Document saved to `docs/agile/epics/` folder

---

**Related Prompts**:
- `create-business-feature.prompt.md` - Create Business Features from this Epic
- `create-technical-feature.prompt.md` - Create Technical Features (enablers) from this Epic
- `create-user-story.prompt.md` - Create User Stories from Features

**Related Rules**:
- `.cursor/rules/agile/epic-documentation-rule.mdc`
- `.cursor/rules/agile/business-feature-documentation-rule.mdc`
- `.cursor/rules/agile/technical-feature-documentation-rule.mdc`

---

**Provenance**: Created 2025-12-08 | Updated 2025-12-08 (PROMPTS-OPTIMIZE) | Pattern: Strategic Initiative Documentation

