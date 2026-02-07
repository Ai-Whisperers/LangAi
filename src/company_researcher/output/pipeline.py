"""
Report Generation Pipeline.

Orchestrates report generation from research results, connecting
the research workflow output to various report formats.

Features:
- Multiple output formats (Markdown, Excel, PDF)
- Template-based generation
- Database integration
- Batch report generation

Usage:
    from company_researcher.output import get_report_pipeline

    pipeline = get_report_pipeline()

    # Generate from workflow state
    files = pipeline.generate_from_state(
        state=research_result,
        formats=["markdown", "excel"]
    )

    # Generate from database
    files = pipeline.generate_from_research_run(
        run_id="20241201_123456_abc123",
        formats=["markdown"]
    )
"""

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional

from ..utils import get_logger, utc_now

logger = get_logger(__name__)


@dataclass
class GeneratedReport:
    """Information about a generated report."""

    format: str
    filepath: Path
    size_bytes: int
    generated_at: datetime
    company_name: str
    run_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "format": self.format,
            "filepath": str(self.filepath),
            "size_bytes": self.size_bytes,
            "generated_at": self.generated_at.isoformat(),
            "company_name": self.company_name,
            "run_id": self.run_id,
        }


class ReportPipeline:
    """
    Orchestrates report generation from research results.

    Connects research workflow output to report generators,
    with optional database integration.
    """

    def __init__(self, output_dir: str = "./reports", use_database: bool = True):
        """
        Initialize the report pipeline.

        Args:
            output_dir: Directory for generated reports
            use_database: Whether to use database integration
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.use_database = use_database

        # Initialize generators lazily
        self._markdown_generator = None
        self._excel_generator = None

    @property
    def markdown_generator(self):
        """Lazy load markdown generator."""
        if self._markdown_generator is None:
            from .report_generator import MarkdownReportGenerator

            self._markdown_generator = MarkdownReportGenerator()
        return self._markdown_generator

    @property
    def excel_generator(self):
        """Lazy load Excel generator."""
        if self._excel_generator is None:
            try:
                from .excel_generator import ExcelReportGenerator

                self._excel_generator = ExcelReportGenerator()
            except ImportError:
                self._excel_generator = None
        return self._excel_generator

    def generate_from_state(
        self, state: Dict[str, Any], formats: List[str] = None, output_dir: Optional[str] = None
    ) -> Dict[str, GeneratedReport]:
        """
        Generate reports directly from workflow state.

        Args:
            state: Workflow state dictionary
            formats: Output formats (markdown, excel, json)
            output_dir: Optional custom output directory

        Returns:
            Dictionary mapping format to GeneratedReport
        """
        if formats is None:
            formats = ["markdown"]

        output_path = Path(output_dir) if output_dir else self.output_dir
        output_path.mkdir(parents=True, exist_ok=True)

        company_name = state.get("company_name", "Unknown")
        timestamp = utc_now().strftime("%Y%m%d_%H%M%S")
        safe_name = self._sanitize_filename(company_name)
        base_name = f"{safe_name}_{timestamp}"

        # Prepare report data
        report_data = self._prepare_report_data(state)

        generated = {}

        for fmt in formats:
            try:
                if fmt == "markdown":
                    report = self._generate_markdown(report_data, output_path, base_name)
                elif fmt == "excel":
                    report = self._generate_excel(report_data, output_path, base_name)
                elif fmt == "json":
                    report = self._generate_json(report_data, output_path, base_name)
                else:
                    continue

                if report:
                    generated[fmt] = report

            except Exception as e:
                print(f"[Pipeline] Error generating {fmt}: {e}")

        return generated

    def generate_from_research_run(
        self, run_id: str, formats: List[str] = None, output_dir: Optional[str] = None
    ) -> Dict[str, GeneratedReport]:
        """
        Generate reports from a database research run.

        Args:
            run_id: Research run ID
            formats: Output formats
            output_dir: Optional custom output directory

        Returns:
            Dictionary mapping format to GeneratedReport
        """
        if not self.use_database:
            raise ValueError("Database integration is disabled")

        from ..database import get_repository

        repo = get_repository()
        run = repo.get_research_run(run_id)

        if not run:
            raise ValueError(f"Research run {run_id} not found")

        # Get agent outputs
        outputs = repo.get_agent_outputs(run.id)

        # Build state from database
        state = {
            "company_name": run.company.name if hasattr(run, "company") else "Unknown",
            "run_id": run_id,
            "company_overview": "",
            "agent_outputs": {},
            "total_cost": run.total_cost,
            "completed_at": run.completed_at.isoformat() if run.completed_at else None,
        }

        for output in outputs:
            state["agent_outputs"][output.agent_name] = {
                "analysis": output.analysis,
                "cost": output.cost,
                "tokens": {"input": output.input_tokens, "output": output.output_tokens},
            }
            # Get synthesized overview
            if output.agent_name == "synthesizer":
                state["company_overview"] = output.analysis

        return self.generate_from_state(state, formats, output_dir)

    def generate_batch(
        self,
        states: List[Dict[str, Any]],
        formats: List[str] = None,
        output_dir: Optional[str] = None,
    ) -> List[Dict[str, GeneratedReport]]:
        """
        Generate reports for multiple research results.

        Args:
            states: List of workflow states
            formats: Output formats
            output_dir: Optional custom output directory

        Returns:
            List of generated report dictionaries
        """
        results = []
        for state in states:
            try:
                reports = self.generate_from_state(state, formats, output_dir)
                results.append(reports)
            except Exception as e:
                print(f"[Pipeline] Error generating batch report: {e}")
                results.append({})
        return results

    # =========================================================================
    # Internal Generation Methods
    # =========================================================================

    def _prepare_report_data(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare standardized report data from state."""
        company_name = state.get("company_name", "Unknown")
        agent_outputs = state.get("agent_outputs", {})

        # Extract analyses
        financial_analysis = agent_outputs.get("financial", {}).get("analysis", "")
        market_analysis = agent_outputs.get("market", {}).get("analysis", "")
        product_analysis = agent_outputs.get("product", {}).get("analysis", "")
        synthesized = state.get("company_overview", "")

        # Get synthesizer output if not in company_overview
        if not synthesized and "synthesizer" in agent_outputs:
            synthesized = agent_outputs["synthesizer"].get("synthesis", "")

        # Calculate total cost
        total_cost = state.get("total_cost", 0)
        if total_cost == 0:
            for output in agent_outputs.values():
                total_cost += output.get("cost", 0)

        # Get sources
        sources = state.get("sources", [])

        return {
            "company_name": company_name,
            "generated_at": utc_now(),
            "run_id": state.get("run_id"),
            # Analyses
            "executive_summary": synthesized,
            "financial_analysis": financial_analysis,
            "market_analysis": market_analysis,
            "product_analysis": product_analysis,
            # Metadata
            "total_cost": total_cost,
            "source_count": len(sources),
            "sources": sources,
            "agent_outputs": agent_outputs,
            # Optional data
            "key_metrics": state.get("key_metrics", {}),
            "competitors": state.get("competitors", []),
            "quality_score": state.get("quality_score"),
        }

    def _generate_markdown(
        self, data: Dict[str, Any], output_dir: Path, base_name: str
    ) -> GeneratedReport:
        """Generate Markdown report."""
        filepath = output_dir / f"{base_name}.md"

        content = self._build_markdown_content(data)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return GeneratedReport(
            format="markdown",
            filepath=filepath,
            size_bytes=filepath.stat().st_size,
            generated_at=utc_now(),
            company_name=data["company_name"],
            run_id=data.get("run_id"),
        )

    def _build_markdown_content(self, data: Dict[str, Any]) -> str:
        """Build Markdown content from report data."""
        lines = []

        # Header
        lines.append(f"# Company Research Report: {data['company_name']}")
        lines.append("")
        lines.append(f"*Generated: {data['generated_at'].strftime('%Y-%m-%d %H:%M:%S')}*")
        if data.get("run_id"):
            lines.append(f"*Run ID: {data['run_id']}*")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Executive Summary
        if data.get("executive_summary"):
            lines.append("## Executive Summary")
            lines.append("")
            lines.append(data["executive_summary"])
            lines.append("")

        # Financial Analysis
        if data.get("financial_analysis"):
            lines.append("## Financial Analysis")
            lines.append("")
            lines.append(data["financial_analysis"])
            lines.append("")

        # Market Analysis
        if data.get("market_analysis"):
            lines.append("## Market Analysis")
            lines.append("")
            lines.append(data["market_analysis"])
            lines.append("")

        # Product Analysis
        if data.get("product_analysis"):
            lines.append("## Product Analysis")
            lines.append("")
            lines.append(data["product_analysis"])
            lines.append("")

        # Sources
        if data.get("sources"):
            lines.append("## Sources")
            lines.append("")
            for i, source in enumerate(data["sources"][:20], 1):
                title = source.get("title", "Untitled")
                url = source.get("url", "")
                lines.append(f"{i}. [{title}]({url})")
            lines.append("")

        # Metadata
        lines.append("---")
        lines.append("")
        lines.append("## Report Metadata")
        lines.append("")
        lines.append(f"- **Total Cost**: ${data.get('total_cost', 0):.4f}")
        lines.append(f"- **Sources Used**: {data.get('source_count', 0)}")
        if data.get("quality_score"):
            lines.append(f"- **Quality Score**: {data['quality_score']:.2f}")
        lines.append("")

        return "\n".join(lines)

    def _generate_excel(
        self, data: Dict[str, Any], output_dir: Path, base_name: str
    ) -> Optional[GeneratedReport]:
        """Generate Excel report."""
        if self.excel_generator is None:
            print("[Pipeline] Excel generator not available (missing openpyxl)")
            return None

        filepath = output_dir / f"{base_name}.xlsx"

        # Use Excel generator
        self.excel_generator.generate(data, str(filepath))

        return GeneratedReport(
            format="excel",
            filepath=filepath,
            size_bytes=filepath.stat().st_size,
            generated_at=utc_now(),
            company_name=data["company_name"],
            run_id=data.get("run_id"),
        )

    def _generate_json(
        self, data: Dict[str, Any], output_dir: Path, base_name: str
    ) -> GeneratedReport:
        """Generate JSON export."""
        filepath = output_dir / f"{base_name}.json"

        # Convert datetime to string for JSON
        json_data = {k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in data.items()}

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, default=str)

        return GeneratedReport(
            format="json",
            filepath=filepath,
            size_bytes=filepath.stat().st_size,
            generated_at=utc_now(),
            company_name=data["company_name"],
            run_id=data.get("run_id"),
        )

    def _sanitize_filename(self, name: str) -> str:
        """
        Sanitize company name for safe filename usage.

        Prevents path traversal attacks and ensures safe filenames
        across different operating systems.

        Args:
            name: Raw company name

        Returns:
            Safe filename string
        """
        if not name:
            return "unknown"

        # Remove null bytes (security)
        sanitized = name.replace("\x00", "")

        # Remove path traversal sequences
        sanitized = sanitized.replace("..", "")
        sanitized = sanitized.replace("./", "")
        sanitized = sanitized.replace(".\\", "")

        # Remove invalid filename characters (Windows + Unix)
        sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", sanitized)

        # Replace whitespace with underscores
        sanitized = re.sub(r"\s+", "_", sanitized)

        # Remove leading/trailing dots and spaces (Windows issue)
        sanitized = sanitized.strip(". ")

        # Remove any remaining path-like patterns
        sanitized = re.sub(r"[/\\]", "", sanitized)

        # Ensure not empty after sanitization
        if not sanitized:
            sanitized = "unknown"

        # Limit length
        return sanitized[:50]

    def _validate_output_path(self, filepath: Path, base_dir: Path) -> Path:
        """
        Validate that the output path is within the allowed directory.

        Prevents path traversal attacks by ensuring resolved path
        stays within the base directory.

        Args:
            filepath: Proposed file path
            base_dir: Allowed base directory

        Returns:
            Validated path

        Raises:
            ValueError: If path would escape base directory
        """
        # Resolve both paths to absolute
        resolved_filepath = filepath.resolve()
        resolved_base = base_dir.resolve()

        # Check if filepath is within base_dir
        try:
            resolved_filepath.relative_to(resolved_base)
        except ValueError:
            logger.error(f"Path traversal attempt blocked: {filepath} is outside {base_dir}")
            raise ValueError(f"Output path '{filepath}' would escape the allowed directory")

        return resolved_filepath


# Singleton instance
_report_pipeline: Optional[ReportPipeline] = None
_pipeline_lock = Lock()


def get_report_pipeline(
    output_dir: Optional[str] = None, use_database: bool = True
) -> ReportPipeline:
    """
    Get singleton report pipeline instance.

    Args:
        output_dir: Optional custom output directory
        use_database: Whether to enable database integration

    Returns:
        ReportPipeline instance
    """
    global _report_pipeline

    if _report_pipeline is None:
        with _pipeline_lock:
            if _report_pipeline is None:
                _report_pipeline = ReportPipeline(
                    output_dir=output_dir or "./reports", use_database=use_database
                )

    return _report_pipeline


def reset_report_pipeline() -> None:
    """Reset pipeline instance (for testing)."""
    global _report_pipeline
    _report_pipeline = None
