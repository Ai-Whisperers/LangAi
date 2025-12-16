# Ticket Folder Structure - Example

**Related Rule**: `ticket-workflow-rule.mdc`

## Quick Reference

```
tickets/TICKET-123/
|---- [Core Documentation - Always in Root]
|   |---- plan.md               # Objectives and strategy
|   |---- context.md            # Current state and focus
|   |---- progress.md           # Chronological log
|   |---- timeline.md           # Session timestamps
|   |---- references.md         # File/conversation links
|   |---- recap.md              # Final summary (at completion)
|   |---- rca.md                # Root cause analysis (if needed)
|   |---- story.md / feature.md / epic.md
|   `---- design.md             # Design docs (if needed)
|
|---- [Important Final Records - Root]
|   |---- IMPLEMENTATION-COMPLETE.md
|   |---- VALIDATION-SUMMARY.md
|   `---- IMPLEMENTATION-STATUS.md  # (if referenced)
|
|---- [External Data - Not Committed]
|   |---- data/                 # JIRA ticket data
|   `---- logs/                 # JIRA history/comments
|
`---- [Working Documents - Not Committed]
    `---- work/
        |---- checklists/
        |   |---- IMPLEMENTATION-CHECKLIST.md
        |   |---- PRE-TESTING-VALIDATION-CHECKLIST.md
        |   `---- R910-RELEASE-REVIEW-CHECKLIST.md
        |---- analysis/
        |   |---- SPEC-VS-IMPLEMENTATION-ANALYSIS.md
        |   |---- STORY-SCOPE-REALITY-CHECK.md
        |   |---- DOCUMENTATION-RECOMMENDATIONS.md
        |   `---- COMPLETE-VERIFICATION-REPORT.md
        |---- reviews/
        |   `---- ARCHITECTURE-REVIEW.md
        `---- sessions/
            |---- SESSION-SUMMARY.md
            `---- CONVERSATION-1-SUMMARY.md
```

## Decision Guide

### Put in **Root** when:
- [X] Part of core documentation (plan, context, progress, etc.)
- [X] Final record that tells the ticket story
- [X] Referenced by other files or communications
- [X] Needed 6+ months later
- [X] Goes into git repository

### Put in **work/** when:
- [X] Working checklist (used then discarded)
- [X] Analysis document (served its purpose)
- [X] Session summary (already captured in progress.md)
- [X] Detailed verification report (summary in root is enough)
- [X] Not committed to git

## Examples from EPP-196

### Would Stay in Root:
- `epic.md`, `plan.md`, `context.md`, `progress.md`, `references.md`
- `IMPLEMENTATION-COMPLETE.md` <- Final record
- `VALIDATION-SUMMARY.md` <- Final validation
- `IMPLEMENTATION-STATUS.md` <- Referenced document

### Would Move to work/:
- `work/checklists/PRE-TESTING-VALIDATION-CHECKLIST.md`
- `work/checklists/R910-RELEASE-REVIEW-CHECKLIST.md`
- `work/checklists/IMPLEMENTATION-CHECKLIST.md`
- `work/analysis/SPEC-VS-IMPLEMENTATION-ANALYSIS.md`
- `work/analysis/STORY-SCOPE-REALITY-CHECK.md`
- `work/analysis/DOCUMENTATION-RECOMMENDATIONS.md`
- `work/analysis/ITERATION-ANALYSIS.md`
- `work/analysis/COMPLETE-VERIFICATION-REPORT.md`
- `work/sessions/SESSION-SUMMARY.md`
- `work/sessions/CONVERSATION-1-SUMMARY.md`
- `work/READY-TO-START.md`
- `work/READY-FOR-TESTING-SUMMARY.md`
- `work/SETUP-COMPLETE.md`

## .gitignore Entries

Add to your `.gitignore`:
```gitignore
# Ticket working documents
tickets/**/work/
tickets/**/data/
tickets/**/logs/
```

## Benefits

1. **Clean Root** - Only essential docs in main folder
2. **Clear Purpose** - Easy to know where to put new documents
3. **Easy Cleanup** - Delete entire `work/` folder after ticket closure
4. **No Git Bloat** - Working docs don't clutter repository
5. **Organized** - Subdirectories keep work/ tidy
6. **Flexible** - Can use flat structure or subdirectories as needed

## Migration Strategy

For existing tickets (like EPP-196):
1. Create `work/` folder
2. Move working documents to appropriate subfolders
3. Keep important final records in root
4. Add `work/` to .gitignore
5. Can keep current structure or migrate gradually
