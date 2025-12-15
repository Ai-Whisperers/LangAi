---
id: templar.rca.v1
kind: templar
version: 1.0.0
description: Template structure for rca.md files - Root Cause Analysis for defects and issues
globs: ""
governs: ""
implements: rca.structure
requires: []
model_hints: { temp: 0.2, top_p: 0.9 }
provenance: { owner: team-ticket, last_review: 2025-11-04 }
---

# Root Cause Analysis

## Problem Statement

{{problem_description}}

## Impact Assessment

**Severity**: {{severity_level}}  
**Scope**: {{impact_scope}}  
**Users Affected**: {{users_affected}}  
**Duration**: {{problem_duration}}

## Timeline of Events

{{#timeline_events}}
- **{{event_time}}**: {{event_description}}
{{/timeline_events}}

## Investigation Process

{{investigation_description}}

## Root Cause

{{root_cause_description}}

**Category**: {{root_cause_category}}  
(Human Error | Process Gaps | System Limitations | Communication Issues | Resource Constraints | Environmental Factors)

## Contributing Factors

{{#contributing_factors}}
- {{factor_description}}
{{/contributing_factors}}

## Resolution

{{#resolution_steps}}
{{step_number}}. {{resolution_action}}
{{/resolution_steps}}

## Prevention Measures

{{#prevention_measures}}
- **{{measure_type}}**: {{measure_description}}
{{/prevention_measures}}

## Process Improvements

{{#process_improvements}}
- {{improvement_description}}
{{/process_improvements}}

## Lessons Learned

{{#lessons}}
- {{lesson}}
{{/lessons}}

