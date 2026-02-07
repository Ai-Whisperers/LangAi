"""
Topic report persistence.

Saves the synthesized topic report to disk in a stable folder structure.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, Optional

from ...config import get_config
from ...utils import get_logger

logger = get_logger(__name__)


def _slugify(value: str, max_len: int = 80, fallback: str = "topic") -> str:
    value = (value or "").strip().lower()
    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"[\s_-]+", "-", value).strip("-")
    return value[:max_len] or fallback


def make_save_topic_report_node(output_dir: Optional[str] = None):
    """
    Factory that returns a node function capturing an optional output_dir override.
    """

    def save_topic_report_node(state: Dict[str, Any]) -> Dict[str, Any]:
        topic = (
            state.get("topic") or state.get("subject") or state.get("company_name") or ""
        ).strip()
        report = (state.get("topic_report") or "").strip()
        if not report:
            raise ValueError(
                "❌ ERROR: Topic report is empty\n\n"
                "Explanation: Topic synthesis did not produce any markdown.\n\n"
                "Solution: Inspect previous nodes (topic_synthesize/topic_refine) and LLM config.\n\n"
                "Location: workflows/nodes/topic_output_nodes.py:save_topic_report_node\n"
            )

        config = get_config()
        base = Path(output_dir or getattr(config, "reports_dir", config.output_dir))
        topic_dir = base / "topics" / _slugify(topic)
        topic_dir.mkdir(parents=True, exist_ok=True)

        report_path = topic_dir / "00_full_report.md"
        report_path.write_text(report, encoding="utf-8")

        logger.info("[TOPIC] Report saved: %s", str(report_path))
        return {"report_path": str(report_path)}

    return save_topic_report_node
