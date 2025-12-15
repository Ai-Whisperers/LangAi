---
name: workflow-link-prompt
description: "Recommend and trigger the next prompt in a workflow chain (pre/post/flow aware) once the current step is done"
agent: cursor-agent
model: GPT-4
category: housekeeping
tags: housekeeping, chaining, follow-up, prompts, workflows
argument-hint: "Previous prompt, current prompt, status/result, workflow name, and any produced artifacts"
rules:
  - .cursor/rules/prompts/prompt-creation-rule.mdc
  - .cursor/rules/prompts/prompt-registry-integration-rule.mdc
---

# Workflow Link Prompt

Given a completed prompt (with output artifacts), recommend and emit the next prompt call(s) in the workflow chain, carrying forward required inputs and the flow context.

## Prompt Chain

- **Pre-Prompt**: Any upstream producer (e.g., scan/find prompts)
- **This Prompt**: `housekeeping/workflow-link-prompt`
- **Post-Prompt**: Downstream consumer(s) (e.g., `housekeeping/chain-condense-ticket`, `ticket/start-ticket`, or other domain steps)

## Purpose

- Make chaining explicit: when a step finishes, propose the correct next prompt(s).
- Pass along artifacts (paths, IDs) so the next step is copy-paste ready.
- Preserve provenance: where we came from (`previousPrompt`), who is handing off (`currentPrompt`), and which workflow we’re in (`workflow`).

## Required Context

```xml
<handoff>
  <previousPrompt>[NAME]</previousPrompt>        <!-- e.g., find-condense-candidates -->
  <currentPrompt>[NAME]</currentPrompt>          <!-- e.g., chain-condense-ticket -->
  <workflow>[OPTIONAL_WORKFLOW_NAME]</workflow>  <!-- e.g., Condense Flow -->
  <status>[done|pending|error]</status>          <!-- must be done to proceed -->
  <artifacts>
    <path>[ARTIFACT_PATH]</path>                 <!-- e.g., tickets/…/data/scan.json -->
    <ticketId>[TICKET_ID]</ticketId>             <!-- optional -->
    <root>[ROOT]</root>                          <!-- optional -->
  </artifacts>
  <recommendedNext>[OPTIONAL_HINT]</recommendedNext> <!-- e.g., chain-condense-ticket -->
</handoff>
```

## Process

1. **Validate Completion**
   - Ensure `status=done`. If not, stop and request completion.
2. **Match Chain**
   - Map `currentPrompt` to known workflows (scan → chain → start-ticket, extraction → templar/exemplar, script standards → validate).
   - If `recommendedNext` provided, respect it; otherwise pick the default chain.
   - Capture `previousPrompt` for provenance so downstream knows its upstream source.
   - Carry forward `workflow` if provided, so the next step can label the flow.
3. **Assemble Handoff Payload**
   - Include required artifacts (JSON path, ticket ID, root, data folder).
   - Provide exact next prompt invocation snippet.
   - Include `previousPrompt` (where we came from), `currentPrompt` (who is handing off), and `workflow` (flow label) so the next step can log pre/post/flow.
4. **Emit Next Steps**
   - List the next prompt(s) with their order (pre/post).
   - If multiple branches exist, present choices with rationale.
5. **Confirm Post-Prompt Awareness**
   - Remind that downstream prompt should note its pre- and post-prompts and workflow.

## Expected Output

- Clear next prompt(s) with order (e.g., `Next: housekeeping/chain-condense-ticket -> ticket/start-ticket`).
- Ready-to-run snippet including required arguments/artifacts.
- Brief rationale tying the chain together.
- Explicit pre/post/flow context: where we came from (`previousPrompt`), who is handing off (`currentPrompt`), and which workflow we’re in (`workflow`), so downstream can record its pre-prompt and flow.

## Validation

- status is `done`.
- Artifacts carried forward.
- Next prompt(s) identified with explicit ordering.
- Handoff snippet present and accurate.
- Chain references included, with `previousPrompt`, `currentPrompt`, and `workflow` (if available) populated.

## Related Prompts
- `housekeeping/find-workflow-candidates.prompt.md`
- `housekeeping/chain-condense-ticket.prompt.md`
- `ticket/start-ticket.prompt.md`

