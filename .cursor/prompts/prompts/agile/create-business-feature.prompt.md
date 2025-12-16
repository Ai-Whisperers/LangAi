---
name: create-business-feature
description: "Create a well-structured Agile Business Feature with user value and requirements"
category: agile
tags: agile, business-feature, user-value, functional-requirements
argument-hint: "Feature title and parent Epic"
---

# Create Business Feature for [Epic]

**Pattern**: Agile Documentation Generation ⭐⭐⭐⭐ | **Effectiveness**: High | **Use When**: Translating Epic-level initiatives into user-focused functional features

Create a well-structured Agile Business Feature documentation file.

## Purpose

Generate comprehensive Business Feature documentation that captures functional requirements from the user's perspective, linking Epic-level strategic goals to implementable User Stories. Business Features focus on WHAT users can do (functional capabilities) rather than HOW the system works (technical implementation).

**Required Context**:

- `[PARENT_EPIC]`: The Epic this feature belongs to.
- `[FEATURE_TITLE]`: Name of the feature.
- `[USER_VALUE]`: What the user gets out of this.
- `[TARGET_AUDIENCE]`: Who this is for.

## User Process

1. **Gather Context**: Identify parent Epic, user value proposition, and target audience
2. **Invoke Prompt**: Provide Epic context, feature title, and user value
3. **Review Generated Feature**: Validate alignment with Epic and business goals
4. **Refine Requirements**: Adjust functional requirements and user journeys as needed
5. **Create Child Stories**: Use generated feature as basis for breaking down into User Stories
6. **Commit Documentation**: Save to `docs/agile/features/` with appropriate naming

## Reasoning Process (for AI Agent)

1. **Link to Epic**: Ensure alignment with the parent Epic's goals and strategic objectives
2. **Define User Value**: Focus on the benefit to the end-user (functional requirements, not technical details)
3. **Outline User Flows**: Describe the primary user journeys and interaction points
4. **Draft Acceptance Criteria**: Define high-level criteria for feature acceptance (Definition of Done)
5. **Break Down into Stories**: Identify potential User Stories that implement this feature
6. **Validate Completeness**: Ensure all required sections are present and business value is clear

## Process

1. **Feature Identifier**:
   - Format: `FEAT-[Domain]-[Name]`
   - Example: `FEAT-AUTH-SSO`

2. **Overview**:
   - Description of functionality.
   - Link to Parent Epic.

3. **User Value Proposition**:
   - Why does the user need this?
   - "As a [role], I can [capability]..."

4. **User Journeys**:
   - Step-by-step flows.
   - Key interaction points.

5. **Functional Requirements**:
   - specific capabilities.
   - Business rules.

6. **Non-Functional Requirements**:
   - Performance, Security, Usability specific to this feature.

7. **Acceptance Criteria (Feature Level)**:
   - Definition of Done for the feature.

8. **Child Stories**:
   - List of User Stories (US-*) that make up this feature.

## Examples (Few-Shot)

### Example 1: Sales Dashboard Feature

**Input**:
```
Epic: EPIC-MODERN-REPORTING (Modernize Reporting Infrastructure)
Feature Title: Sales Dashboard
User Value: Sales managers need real-time visibility into daily sales performance
Target Audience: Sales managers, regional directors
```

**AI Reasoning**:
- Parent Epic focuses on replacing legacy Crystal Reports with modern PowerBI
- This feature delivers direct user value: real-time sales visibility
- Primary user journey: Login → Select region → View metrics → Export report
- Functional requirements: filtering, real-time data, export capabilities
- Can be broken into 3-4 user stories (setup data source, build dashboard, add filters, export)

**Output**:
```markdown
# Business Feature: FEAT-RPT-SALES-DASH

## Parent Epic
EPIC-MODERN-REPORTING: Modernize Reporting Infrastructure

## Overview
Interactive sales dashboard providing real-time visibility into daily sales performance across all regions. Replaces legacy monthly reports with live PowerBI dashboard.

## User Value Proposition
**As a** Sales Manager
**I can** view real-time sales metrics filtered by region, product, and time period
**So that** I can make data-driven decisions and respond quickly to performance trends

## Target Audience
- Primary: Sales Managers (regional and district)
- Secondary: Regional Directors, C-level executives

## User Journeys

### Journey 1: Daily Performance Review
1. Sales manager logs into PowerBI portal
2. Opens Sales Dashboard
3. Selects region filter (e.g., "Northeast")
4. Reviews key metrics: daily sales, top products, conversion rates
5. Identifies trends or issues requiring action

### Journey 2: Export for Presentation
1. Sales manager prepares for leadership meeting
2. Configures dashboard filters for relevant data
3. Clicks "Export to PDF"
4. Downloads formatted report
5. Shares with leadership team

## Functional Requirements

### Data Display
- Display daily sales totals by region
- Show top 10 products by revenue
- Display conversion rates and sales trends
- Provide year-over-year comparison
- Real-time data refresh (5-minute intervals)

### Filtering & Interaction
- Filter by region (multi-select)
- Filter by date range (preset and custom)
- Filter by product category
- Drill-down capability for detailed views

### Export & Sharing
- Export to PDF (formatted for presentation)
- Export to Excel (raw data)
- Schedule automated email delivery
- Share dashboard links with permissions

## Non-Functional Requirements
- **Performance**: Dashboard load time < 3 seconds
- **Security**: Role-based access control, row-level security for regional data
- **Usability**: Mobile-responsive design, accessible via tablet
- **Availability**: 99.5% uptime during business hours

## Acceptance Criteria (Feature Level)
- [ ] Dashboard displays accurate real-time sales data
- [ ] All filtering options work correctly
- [ ] Export to PDF generates formatted report
- [ ] Performance meets <3 second load time requirement
- [ ] Mobile view works on tablets
- [ ] Security restrictions prevent cross-region data access

## Child Stories (Proposed)
- **US-RPT-001**: As a Sales Manager, I want to view daily sales totals by region, so that I can track regional performance
- **US-RPT-002**: As a Sales Manager, I want to filter dashboard by date range and product category, so that I can analyze specific segments
- **US-RPT-003**: As a Sales Manager, I want to export dashboard to PDF, so that I can share insights in presentations
- **US-RPT-004**: As a Sales Manager, I want mobile-responsive dashboard, so that I can review performance on my tablet

## Dependencies
- Data Warehouse setup (TECH-DATA-WAREHOUSE) must be complete
- PowerBI licensing and infrastructure in place
- Sales data ETL pipeline operational

## Risks & Mitigations
- **Risk**: Legacy Crystal Reports data format incompatibility
  **Mitigation**: Data transformation layer in ETL pipeline
- **Risk**: User adoption resistance to new tool
  **Mitigation**: Training sessions and gradual rollout

## Success Metrics
- 80%+ sales manager adoption within 30 days
- Average dashboard load time < 3 seconds
- 90%+ user satisfaction in feedback survey
```

### Example 2: Quick Feature (Brief Input)

**Input**:
```
Epic: User Authentication. Feature: Password Reset. Value: Users regain account access.
```

**AI Reasoning**:
- Clear user value: Account recovery
- Single user journey: Forgot password → Email link → Reset
- Functional requirement: Email delivery, secure token, password validation
- 2-3 user stories (request reset, validate token, set new password)

**Output**:
```markdown
# Business Feature: FEAT-AUTH-PASSWORD-RESET

## Parent Epic
EPIC-USER-AUTH: User Authentication System

## Overview
Self-service password reset capability allowing users to regain account access without IT support intervention.

## User Value Proposition
**As a** System User
**I can** reset my password via email verification
**So that** I can regain account access immediately when I forget my password

## Functional Requirements
- Initiate reset from login page
- Receive secure reset link via email
- Link expiry (24 hours)
- Password complexity validation
- Confirmation email after successful reset

## Acceptance Criteria
- [ ] User receives reset email within 1 minute
- [ ] Reset link expires after 24 hours
- [ ] Weak passwords are rejected with clear guidance
- [ ] User can successfully login with new password

## Child Stories (Proposed)
- **US-AUTH-001**: Request password reset via email
- **US-AUTH-002**: Validate reset token and set new password
```

## Expected Output

**Deliverables**:

1. Complete Business Feature markdown file.
2. Initial User Story list.

**Format**: Markdown file following `docs/agile/features/` structure.

## Quality Criteria

- [ ] Clear user value proposition with "As a... I want... So that..." format
- [ ] Linked to parent Epic with ID reference
- [ ] Defined functional requirements (specific capabilities)
- [ ] User journeys describe step-by-step workflows
- [ ] Non-functional requirements (performance, security, usability) included
- [ ] Feature-level acceptance criteria (Definition of Done) specified
- [ ] List of proposed child User Stories with IDs
- [ ] Dependencies and risks identified
- [ ] Success metrics defined
- [ ] Document saved to `docs/agile/features/` folder

---

**Related Prompts**:
- `create-epic.prompt.md` - Create parent Epic documentation
- `create-user-story.prompt.md` - Create child User Stories from this feature
- `create-technical-feature.prompt.md` - Create supporting technical enablers

**Related Rules**:
- `.cursor/rules/agile/business-feature-documentation-rule.mdc`
- `.cursor/rules/agile/epic-documentation-rule.mdc`
- `.cursor/rules/agile/user-story-documentation-rule.mdc`

---

**Provenance**: Created 2025-12-08 | Updated 2025-12-08 (PROMPTS-OPTIMIZE) | Pattern: Agile Documentation Generation
