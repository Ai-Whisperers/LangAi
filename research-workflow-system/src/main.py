"""Main orchestrator for the Research Workflow System."""

import uuid
from typing import Dict, Any, List
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ResearchWorkflowSystem:
    """
    Main system orchestrator integrating:
    - Research agents (multi-topic)
    - Memory system (LangMem)
    - File management
    - Source quality tracking
    - Cross-topic enhancement
    """

    def __init__(self):
        """Initialize all system components."""
        # Will be implemented in phases
        self.store = None  # Memory store (Phase 3)
        self.file_manager = None  # File manager (Phase 4)
        self.quality_tracker = None  # Quality tracker (Phase 3)
        self.cross_topic_enhancer = None  # Cross-topic system (Phase 5)
        self.research_graph = None  # Research graph (Phase 2)

        print("🚀 Research Workflow System initialized")
        print(f"   Version: {self._get_version()}")
        print(f"   Output path: {os.getenv('OUTPUT_BASE_PATH', 'research_outputs')}")

    def research_topic(
        self,
        topic: str,
        topic_type: str,
        max_queries: int = None,
        enable_cross_topic: bool = True
    ) -> Dict[str, Any]:
        """
        Main research workflow.

        Args:
            topic: Topic to research (e.g., "OpenAI", "AI Market")
            topic_type: Type of research ("company", "market", "region", "competitor")
            max_queries: Max search queries (default from env)
            enable_cross_topic: Enable cross-topic enhancement

        Returns:
            Dictionary with research_id, file paths, and metadata
        """
        print(f"\n{'='*60}")
        print(f"🔬 Starting research: {topic}")
        print(f"   Type: {topic_type}")
        print(f"   Cross-topic learning: {'enabled' if enable_cross_topic else 'disabled'}")
        print(f"{'='*60}\n")

        # 1. Initialize research state
        state = self._initialize_state(topic, topic_type, max_queries)

        # 2. Find related past research (Phase 5)
        if enable_cross_topic and self.cross_topic_enhancer:
            related = self.cross_topic_enhancer.find_related_topics(topic)
            state["related_topics"] = [r["topic"] for r in related]
            print(f"📚 Found {len(related)} related topics")

        # 3. Execute research graph (Phase 2)
        if self.research_graph:
            print("🔍 Executing research workflow...")
            result = self.research_graph.invoke(state)
        else:
            print("⚠️  Research graph not yet implemented")
            result = state

        # 4. Enhance with cross-topic insights (Phase 5)
        if enable_cross_topic and self.cross_topic_enhancer:
            print("🔗 Applying cross-topic enhancements...")
            enhanced = self.cross_topic_enhancer.enhance_research(
                result,
                related
            )
        else:
            enhanced = result

        # 5. Save all files (Phase 4)
        if self.file_manager:
            print("💾 Saving research files...")
            files = self.file_manager.save_research(enhanced)
        else:
            print("⚠️  File manager not yet implemented")
            files = {}

        # 6. Update source quality database (Phase 3)
        if self.quality_tracker:
            print("⭐ Updating source quality ratings...")
            for source in enhanced.get("websites_visited", []):
                self.quality_tracker.rate_source(
                    url=source["url"],
                    usefulness=source.get("quality_score", 0.5),
                    reason=source.get("notes", ""),
                    research_id=enhanced["research_id"]
                )

        # 7. Update past research files (Phase 5)
        if enable_cross_topic and self.cross_topic_enhancer:
            print("📝 Updating past research with new insights...")
            self.cross_topic_enhancer.update_past_research(enhanced)

        print(f"\n✅ Research complete!")
        print(f"   Research ID: {enhanced['research_id']}")
        print(f"   Files saved: {len(files)}")
        print(f"   Sources visited: {len(enhanced.get('websites_visited', []))}")
        print(f"   Cross-references: {len(enhanced.get('related_topics', []))}")

        return {
            "research_id": enhanced["research_id"],
            "topic": topic,
            "topic_type": topic_type,
            "files": files,
            "related_topics": enhanced.get("related_topics", []),
            "enhancements_applied": len(enhanced.get("enhancements", [])),
            "sources_count": len(enhanced.get("websites_visited", [])),
            "timestamp": datetime.now().isoformat()
        }

    def _initialize_state(
        self,
        topic: str,
        topic_type: str,
        max_queries: int = None
    ) -> Dict[str, Any]:
        """Initialize research state."""
        return {
            "topic": topic,
            "topic_type": topic_type,
            "research_id": str(uuid.uuid4()),
            "max_queries": max_queries or int(os.getenv("MAX_SEARCH_QUERIES", 5)),
            "websites_visited": [],
            "extracted_data": {},
            "related_topics": [],
            "search_queries": [],
            "sources_tracker": {},
            "quality_scores": {},
            "cross_references": [],
            "report_content": "",
            "timestamp": datetime.now().isoformat()
        }

    @staticmethod
    def _get_version() -> str:
        """Get system version."""
        from . import __version__
        return __version__


# Example usage
if __name__ == "__main__":
    # Initialize system
    system = ResearchWorkflowSystem()

    # Example research
    result = system.research_topic(
        topic="OpenAI",
        topic_type="company"
    )

    print(f"\n{'='*60}")
    print("Result:")
    print(result)
