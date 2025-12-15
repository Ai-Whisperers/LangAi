---
id: templar.rca.v1
kind: templar
version: 1.0.0
description: Structure template for rca.md files
implements: rca.create
globs: ""
governs: ""
requires: []
provenance: { owner: team-ticket, last_review: 2025-12-06 }
---

# {{ticket_id}} Root Cause Analysis

## Incident Summary
{{what_happened}}

## Root Cause (5 Whys)
1. Why? {{answer_1}}
2. Why? {{answer_2}}
3. Why? {{answer_3}}
4. Why? {{answer_4}}
5. Why? {{answer_5}}

## Root Cause Category
{{category}} (e.g., Code, Process, Configuration, External)

## Solution
{{how_it_was_fixed}}

## Prevention
- [ ] {{prevention_action_1}}
- [ ] {{prevention_action_2}}

