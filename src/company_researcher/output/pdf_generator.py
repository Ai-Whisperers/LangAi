"""
PDF Report Generator (Phase 16.1).

Professional PDF report generation:
- Executive summary
- Detailed analysis sections
- Charts and visualizations
- Tables and metrics
- Professional styling

Supports multiple PDF libraries with fallback.
"""
from __future__ import annotations

from typing import Dict, Any, List, Optional, TYPE_CHECKING
from ..utils import utc_now

if TYPE_CHECKING:
    from reportlab.platypus import Table
from dataclasses import dataclass, field
from enum import Enum
import os

# Try to import PDF libraries
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak
    )
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


# ============================================================================
# Data Models
# ============================================================================

class ReportStyle(str, Enum):
    """Report style options."""
    EXECUTIVE = "executive"      # Concise, high-level
    DETAILED = "detailed"        # Comprehensive
    TECHNICAL = "technical"      # Technical focus
    INVESTOR = "investor"        # Investment focused


@dataclass
class ReportSection:
    """A section in the report."""
    title: str
    content: str
    subsections: List["ReportSection"] = field(default_factory=list)
    tables: List[Dict[str, Any]] = field(default_factory=list)
    bullet_points: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReportConfig:
    """Configuration for report generation."""
    title: str
    company_name: str
    style: ReportStyle = ReportStyle.DETAILED
    page_size: str = "letter"  # letter or A4
    include_toc: bool = True
    include_executive_summary: bool = True
    include_appendix: bool = False
    logo_path: Optional[str] = None
    author: str = "Company Researcher"
    date: str = field(default_factory=lambda: utc_now().strftime("%Y-%m-%d"))


# ============================================================================
# PDF Generator
# ============================================================================

class PDFReportGenerator:
    """
    Generate professional PDF reports from research data.

    Usage:
        generator = PDFReportGenerator()
        pdf_path = generator.generate(
            research_data=data,
            config=ReportConfig(
                title="Tesla Research Report",
                company_name="Tesla",
                style=ReportStyle.INVESTOR
            )
        )
    """

    def __init__(self):
        """Initialize generator."""
        if not REPORTLAB_AVAILABLE:
            print("[PDF] Warning: reportlab not installed. PDF generation limited.")

        self._styles = None
        if REPORTLAB_AVAILABLE:
            self._styles = self._create_styles()

    def _create_styles(self):
        """Create custom paragraph styles."""
        styles = getSampleStyleSheet()

        # Title style
        styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1a365d')
        ))

        # Section header
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading2'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=10,
            textColor=colors.HexColor('#2c5282')
        ))

        # Subsection header
        styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=styles['Heading3'],
            fontSize=13,
            spaceBefore=15,
            spaceAfter=8,
            textColor=colors.HexColor('#2d3748')
        ))

        # Body text
        styles.add(ParagraphStyle(
            name='BodyText',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            alignment=TA_JUSTIFY,
            spaceAfter=10
        ))

        # Metric style
        styles.add(ParagraphStyle(
            name='MetricValue',
            parent=styles['Normal'],
            fontSize=18,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2b6cb0'),
            spaceAfter=5
        ))

        return styles

    def generate(
        self,
        research_data: Dict[str, Any],
        config: ReportConfig,
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate PDF report.

        Args:
            research_data: Research data from agents
            config: Report configuration
            output_path: Output file path (auto-generated if not provided)

        Returns:
            Path to generated PDF
        """
        if not REPORTLAB_AVAILABLE:
            return self._generate_fallback(research_data, config, output_path)

        # Generate output path
        if not output_path:
            safe_name = config.company_name.lower().replace(" ", "_")
            output_path = f"./reports/{safe_name}_report_{config.date}.pdf"

        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

        # Create document
        page_size = letter if config.page_size == "letter" else A4
        doc = SimpleDocTemplate(
            output_path,
            pagesize=page_size,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )

        # Build story (content)
        story = []

        # Title page
        story.extend(self._create_title_page(config))

        # Executive summary
        if config.include_executive_summary:
            story.extend(self._create_executive_summary(research_data, config))

        # Table of contents placeholder
        if config.include_toc:
            story.extend(self._create_toc_placeholder())

        # Main sections
        story.extend(self._create_main_sections(research_data, config))

        # Appendix
        if config.include_appendix:
            story.extend(self._create_appendix(research_data))

        # Build PDF
        doc.build(story)

        return output_path

    def _create_title_page(self, config: ReportConfig) -> List:
        """Create title page elements."""
        elements = []

        # Spacer at top
        elements.append(Spacer(1, 2*inch))

        # Title
        elements.append(Paragraph(config.title, self._styles['ReportTitle']))
        elements.append(Spacer(1, 0.5*inch))

        # Company name
        elements.append(Paragraph(
            f"<b>{config.company_name}</b>",
            self._styles['SectionHeader']
        ))
        elements.append(Spacer(1, inch))

        # Metadata
        meta_style = ParagraphStyle(
            name='Meta',
            parent=self._styles['Normal'],
            alignment=TA_CENTER,
            textColor=colors.gray
        )
        elements.append(Paragraph(f"Report Date: {config.date}", meta_style))
        elements.append(Paragraph(f"Generated by: {config.author}", meta_style))
        elements.append(Paragraph(f"Report Style: {config.style.value.title()}", meta_style))

        elements.append(PageBreak())

        return elements

    def _create_executive_summary(
        self,
        data: Dict[str, Any],
        config: ReportConfig
    ) -> List:
        """Create executive summary section."""
        elements = []

        elements.append(Paragraph("Executive Summary", self._styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))

        # Extract key findings
        summary_points = self._extract_summary_points(data)

        if summary_points:
            for point in summary_points[:5]:
                elements.append(Paragraph(
                    f"• {point}",
                    self._styles['BodyText']
                ))
        else:
            elements.append(Paragraph(
                "This report provides comprehensive research and analysis of "
                f"{config.company_name}, covering financial performance, market position, "
                "competitive landscape, and strategic outlook.",
                self._styles['BodyText']
            ))

        # Key metrics table
        metrics = self._extract_key_metrics(data)
        if metrics:
            elements.append(Spacer(1, 0.3*inch))
            elements.append(Paragraph("Key Metrics", self._styles['SubsectionHeader']))
            elements.append(self._create_metrics_table(metrics))

        elements.append(PageBreak())

        return elements

    def _create_toc_placeholder(self) -> List:
        """Create table of contents placeholder."""
        elements = []

        elements.append(Paragraph("Table of Contents", self._styles['SectionHeader']))
        elements.append(Spacer(1, 0.3*inch))

        toc_items = [
            "1. Executive Summary",
            "2. Company Overview",
            "3. Financial Analysis",
            "4. Market Analysis",
            "5. Competitive Landscape",
            "6. Strategic Assessment",
            "7. Recommendations"
        ]

        for item in toc_items:
            elements.append(Paragraph(item, self._styles['BodyText']))

        elements.append(PageBreak())

        return elements

    def _create_main_sections(
        self,
        data: Dict[str, Any],
        config: ReportConfig
    ) -> List:
        """Create main report sections."""
        elements = []

        # Section mapping from agent outputs
        section_map = {
            "overview": ("Company Overview", self._format_overview_section),
            "financial": ("Financial Analysis", self._format_financial_section),
            "market": ("Market Analysis", self._format_market_section),
            "competitor": ("Competitive Landscape", self._format_competitor_section),
            "product": ("Product & Technology", self._format_product_section),
            "brand": ("Brand Analysis", self._format_brand_section),
            "investment": ("Investment Analysis", self._format_investment_section),
        }

        agent_outputs = data.get("agent_outputs", data)

        for key, (title, formatter) in section_map.items():
            if key in agent_outputs:
                elements.append(Paragraph(title, self._styles['SectionHeader']))
                elements.append(Spacer(1, 0.2*inch))

                section_content = formatter(agent_outputs[key])
                elements.extend(section_content)

                elements.append(PageBreak())

        return elements

    def _format_overview_section(self, data: Dict[str, Any]) -> List:
        """Format company overview section."""
        elements = []
        analysis = data.get("analysis", str(data))

        # Split into paragraphs
        paragraphs = analysis.split("\n\n")
        for para in paragraphs[:5]:
            if para.strip():
                elements.append(Paragraph(para.strip(), self._styles['BodyText']))

        return elements

    def _format_financial_section(self, data: Dict[str, Any]) -> List:
        """Format financial analysis section."""
        elements = []

        analysis = data.get("analysis", "")
        if analysis:
            # Extract key financial data
            elements.append(Paragraph(
                analysis[:1500] + "..." if len(analysis) > 1500 else analysis,
                self._styles['BodyText']
            ))

        # Add financial metrics table if available
        if "metrics" in data:
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph("Financial Metrics", self._styles['SubsectionHeader']))
            elements.append(self._create_metrics_table(data["metrics"]))

        return elements

    def _format_market_section(self, data: Dict[str, Any]) -> List:
        """Format market analysis section."""
        elements = []

        analysis = data.get("analysis", str(data))
        elements.append(Paragraph(
            analysis[:1500] + "..." if len(analysis) > 1500 else analysis,
            self._styles['BodyText']
        ))

        return elements

    def _format_competitor_section(self, data: Dict[str, Any]) -> List:
        """Format competitive landscape section."""
        elements = []

        analysis = data.get("analysis", str(data))
        elements.append(Paragraph(
            analysis[:1500] + "..." if len(analysis) > 1500 else analysis,
            self._styles['BodyText']
        ))

        return elements

    def _format_product_section(self, data: Dict[str, Any]) -> List:
        """Format product section."""
        elements = []

        analysis = data.get("analysis", str(data))
        elements.append(Paragraph(
            analysis[:1500] + "..." if len(analysis) > 1500 else analysis,
            self._styles['BodyText']
        ))

        return elements

    def _format_brand_section(self, data: Dict[str, Any]) -> List:
        """Format brand section."""
        elements = []

        if "brand_score" in data:
            elements.append(Paragraph(
                f"Brand Score: {data['brand_score']}",
                self._styles['MetricValue']
            ))

        analysis = data.get("analysis", "")
        if analysis:
            elements.append(Paragraph(
                analysis[:1000] + "..." if len(analysis) > 1000 else analysis,
                self._styles['BodyText']
            ))

        return elements

    def _format_investment_section(self, data: Dict[str, Any]) -> List:
        """Format investment section."""
        elements = []

        if "investment_rating" in data:
            elements.append(Paragraph(
                f"Rating: {data['investment_rating'].upper()}",
                self._styles['MetricValue']
            ))

        if "investment_thesis" in data:
            elements.append(Paragraph(
                data["investment_thesis"],
                self._styles['BodyText']
            ))

        return elements

    def _create_appendix(self, data: Dict[str, Any]) -> List:
        """Create appendix section."""
        elements = []

        elements.append(Paragraph("Appendix", self._styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))

        elements.append(Paragraph(
            "This appendix contains additional data and methodology notes.",
            self._styles['BodyText']
        ))

        return elements

    def _extract_summary_points(self, data: Dict[str, Any]) -> List[str]:
        """Extract key summary points from data."""
        points = []

        agent_outputs = data.get("agent_outputs", data)

        # Look for key findings in each agent output
        for key, value in agent_outputs.items():
            if isinstance(value, dict):
                if "key_findings" in value:
                    points.extend(value["key_findings"][:2])
                elif "conclusions" in value:
                    points.extend(value["conclusions"][:2])
                elif "recommendations" in value:
                    points.extend(value["recommendations"][:1])

        return points[:5]

    def _extract_key_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key metrics for display."""
        metrics = {}

        agent_outputs = data.get("agent_outputs", data)

        if "financial" in agent_outputs:
            fin = agent_outputs["financial"]
            if "revenue" in fin:
                metrics["Revenue"] = fin["revenue"]
            if "growth_rate" in fin:
                metrics["Growth Rate"] = fin["growth_rate"]

        if "market" in agent_outputs:
            mkt = agent_outputs["market"]
            if "market_size" in mkt:
                metrics["Market Size"] = mkt["market_size"]

        if "brand" in agent_outputs:
            brand = agent_outputs["brand"]
            if "brand_score" in brand:
                metrics["Brand Score"] = brand["brand_score"]

        return metrics

    def _create_metrics_table(self, metrics: Dict[str, Any]) -> Table:
        """Create a metrics table."""
        data = [["Metric", "Value"]]

        for key, value in metrics.items():
            data.append([str(key), str(value)])

        table = Table(data, colWidths=[2.5*inch, 2.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#edf2f7')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2d3748')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e0')),
            ('ROWHEIGHT', (0, 0), (-1, -1), 25),
        ]))

        return table

    def _generate_fallback(
        self,
        data: Dict[str, Any],
        config: ReportConfig,
        output_path: Optional[str]
    ) -> str:
        """Generate a text-based report as fallback."""
        if not output_path:
            safe_name = config.company_name.lower().replace(" ", "_")
            output_path = f"./reports/{safe_name}_report_{config.date}.txt"

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

        with open(output_path, "w") as f:
            f.write(f"{'='*60}\n")
            f.write(f"{config.title}\n")
            f.write(f"Company: {config.company_name}\n")
            f.write(f"Date: {config.date}\n")
            f.write(f"{'='*60}\n\n")

            agent_outputs = data.get("agent_outputs", data)

            for key, value in agent_outputs.items():
                f.write(f"\n{'-'*40}\n")
                f.write(f"{key.upper()}\n")
                f.write(f"{'-'*40}\n")

                if isinstance(value, dict) and "analysis" in value:
                    f.write(value["analysis"][:2000])
                else:
                    f.write(str(value)[:1000])

                f.write("\n")

        return output_path


# ============================================================================
# Factory Function
# ============================================================================

def generate_pdf_report(
    research_data: Dict[str, Any],
    company_name: str,
    title: Optional[str] = None,
    style: str = "detailed",
    output_path: Optional[str] = None
) -> str:
    """
    Generate a PDF report from research data.

    Args:
        research_data: Research data from agents
        company_name: Company name
        title: Report title
        style: Report style (executive, detailed, technical, investor)
        output_path: Output file path

    Returns:
        Path to generated report
    """
    config = ReportConfig(
        title=title or f"{company_name} Research Report",
        company_name=company_name,
        style=ReportStyle(style)
    )

    generator = PDFReportGenerator()
    return generator.generate(research_data, config, output_path)
