"""
Human-in-the-Loop Package - Phase 15

This package provides human intervention capabilities for LangGraph workflows:
- Interrupt before critical decisions
- Allow human review and approval
- Modify workflow direction based on human input
- Resume after human intervention

Usage:
    from company_researcher.graphs.human_in_loop import (
        create_human_reviewed_workflow,
        research_with_review,
        approve_and_continue,
        reject_and_revise,
    )

    # Research with human review at quality check
    result = await research_with_review("Tesla")

    # In another context, approve the pending review
    result = await approve_and_continue(thread_id)
"""

from .review_workflow import (
    create_human_reviewed_workflow,
    research_with_review,
    approve_and_continue,
    reject_and_revise,
    modify_and_continue,
    get_pending_reviews,
    HumanReviewConfig,
    ReviewDecision,
    PendingReview,
)

__all__ = [
    # Workflow creation
    "create_human_reviewed_workflow",
    # Research functions
    "research_with_review",
    "approve_and_continue",
    "reject_and_revise",
    "modify_and_continue",
    "get_pending_reviews",
    # Types
    "HumanReviewConfig",
    "ReviewDecision",
    "PendingReview",
]
