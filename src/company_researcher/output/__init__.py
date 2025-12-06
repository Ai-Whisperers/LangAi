"""
Output Formatters Module (Phase 16).

Advanced output format generation:
- PDF reports with professional styling
- Excel workbooks with multiple sheets
- PowerPoint presentations
- Markdown export

Usage:
    from src.company_researcher.output import (
        generate_pdf_report,
        export_to_excel,
        generate_presentation
    )

    # Generate PDF report
    pdf_path = generate_pdf_report(
        research_data=data,
        company_name="Tesla",
        style="investor"
    )

    # Export to Excel
    excel_path = export_to_excel(
        research_data=data,
        company_name="Tesla"
    )

    # Generate presentation
    pptx_path = generate_presentation(
        research_data=data,
        company_name="Tesla",
        style="executive"
    )
"""

# PDF Generation
from .pdf_generator import (
    PDFReportGenerator,
    ReportConfig,
    ReportStyle,
    ReportSection,
    generate_pdf_report,
    REPORTLAB_AVAILABLE,
)

# Excel Export
from .excel_exporter import (
    ExcelExporter,
    ExcelConfig,
    SheetType,
    export_to_excel,
    OPENPYXL_AVAILABLE,
    XLSXWRITER_AVAILABLE,
)

# Presentation Generation
from .presentation_generator import (
    PresentationGenerator,
    PresentationConfig,
    PresentationStyle,
    SlideContent,
    SlideType,
    generate_presentation,
    PPTX_AVAILABLE,
)

__all__ = [
    # PDF
    "PDFReportGenerator",
    "ReportConfig",
    "ReportStyle",
    "ReportSection",
    "generate_pdf_report",
    "REPORTLAB_AVAILABLE",
    # Excel
    "ExcelExporter",
    "ExcelConfig",
    "SheetType",
    "export_to_excel",
    "OPENPYXL_AVAILABLE",
    "XLSXWRITER_AVAILABLE",
    # Presentation
    "PresentationGenerator",
    "PresentationConfig",
    "PresentationStyle",
    "SlideContent",
    "SlideType",
    "generate_presentation",
    "PPTX_AVAILABLE",
]
