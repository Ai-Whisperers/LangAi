---
name: find-workflow-candidates
description: "Find prompts or scripts that should be chained into guided workflows with explicit pre/post links"
agent: cursor-agent
model: GPT-4
category: housekeeping
tags: housekeeping, chaining, prompts, workflows, maintenance
argument-hint: "Root path to scan (e.g., .cursor/prompts)"
rules:
  - .cursor/rules/prompts/prompt-creation-rule.mdc
  - .cursor/rules/prompts/prompt-registry-integration-rule.mdc
---

# Find Workflow Candidates

Identify prompts/scripts that should participate in workflow chains (pre/post handoffs) so follow-up actions are recommended automatically and workflows are discoverable.

## Purpose
- Surface artifacts that benefit from explicit pre/post chaining (similar to find-condense-candidates / find-extraction-candidates / find-script-extraction-candidates).
- Detect natural workflow groupings (scan → triage → execute/ticket) and propose workflow names.
- Capture where follow-up prompts should be suggested after completion.
- Produce a ranked list with roles and workflow membership.

## Required Context
- Target root to scan (default: `.cursor/prompts`).
- Chain and workflow signals to look for (examples, shared domain, “next step” language).
- Access to housekeeping scan scripts (if any) or read access to the target tree.

## Inputs
- **Targets**: One or more roots to scan.  
- **Signals**:
  - Prompts that end with “next”, “follow-up”, or reference another prompt.
  - Prompts that generate data consumed elsewhere (JSON/CSV paths, ticket payloads).
  - Shared domains (same category/tag) that form natural sequences (scan → triage → execute).
  - Existing but undocumented dependencies (e.g., “run the scan first”).
  - Clusters sharing tags/category/model/agent that imply a workflow.
- **Thresholds**: Optional minimum lines or match counts to focus results.

## Process
1. **Scan**
   - Traverse target root for `.prompt.md` (and companion scripts under `.cursor/scripts/housekeeping` if present).
   - **Include uncommitted changes**: Check `git status` for uncommitted prompt files that might form new workflows.
   - Note filename, category, tags, and any references to other prompts/scripts.
2. **Detect Chain Signals**  
   - Look for “next”, “follow-up”, “post step”, “handoff”, “invoke [prompt]”, data paths, or ticket handoffs.  
   - Group by domain (condense, extraction, scripting, validation) to spot natural sequences.
3. **Detect Workflow Clusters**  
   - Cluster by shared tags/category and cross-references; propose workflow names (e.g., “Condense Flow”, “Extraction Flow”, “Script Standards Flow”).  
   - Identify typical phases: Producer (scan), Processor (triage/chain), Launcher (ticket/start), Terminal (final validation/recap).
3. **Rank & Classify**  
   - Rank by strength of chain/workflow signals and reuse potential.  
   - Classify each as **Producer** (emits data), **Processor** (consumes/transforms), **Launcher** (starts tickets), or **Terminal** (final step).  
4. **Recommend Chain**  
   - Propose pre/post links (e.g., Scan → Chain → Start-Ticket).  
   - Note required artifacts to pass (JSON path, ticket ID, root path).  
   - Suggest follow-up prompt names for each candidate.  
   - Assign candidate workflows for grouped items.
5. **Output**  
   - Emit table and actions per Output Format.  
   - Include paths to any referenced scripts.

## Output Format
```markdown
## Chain Candidates (Root: [ROOT])

| Rank | Artifact | Role | Workflow | Signals | Proposed Pre → Post | Required Artifacts | Notes |
|------|----------|------|----------|---------|---------------------|--------------------|-------|
| 1 | [path] | Producer | [Condense Flow] | [data path, “next” refs] | [pre] → [post] | [JSON path, ticket id] | [why] |

### Actions
- [path] → Add pre/post references: [pre] → [post]; pass [artifacts]
- ...
```

## Validation Checklist
- [ ] Targets and thresholds recorded.  
- [ ] Chain signals captured with rationale.  
- [ ] Role assigned (Producer/Processor/Launcher/Terminal).  
- [ ] Workflow grouping proposed (name + members).  
- [ ] Pre/post links proposed with required artifacts.  
- [ ] Report saved/linked for follow-up work.

## Related Prompts
- `housekeeping/find-condense-candidates.prompt.md`
- `housekeeping/find-extraction-candidates.prompt.md`
- `housekeeping/find-script-extraction-candidates.prompt.md`
- `housekeeping/workflow-link-prompt.prompt.md`

