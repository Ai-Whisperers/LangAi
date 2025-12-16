"""
Output Formatters Module (Phase 16).

Advanced output format generation:
- PDF reports with professional styling
- Excel workbooks with multiple sheets
- PowerPoint presentations
- Comparison reports (multi-company)
- Markdown export

Usage:
    from src.company_researcher.output import (
        generate_pdf_report,
        export_to_excel,
        generate_presentation,
        compare_companies
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

    # Compare companies
    report = await compare_companies(
        {"Apple": apple_data, "Microsoft": msft_data},
        output_format="markdown"
    )
"""

# Comparison Reports
from .comparison_report import (
    CompanyData,
    ComparisonCategory,
    ComparisonMetric,
    ComparisonReport,
    ComparisonReportGenerator,
    MetricComparison,
    compare_companies,
    create_comparison_generator,
)

# Excel Export
from .excel_exporter import (
    OPENPYXL_AVAILABLE,
    XLSXWRITER_AVAILABLE,
    ExcelConfig,
    ExcelExporter,
    SheetType,
    export_to_excel,
)

# PDF Generation
from .pdf_generator import (
    REPORTLAB_AVAILABLE,
    PDFReportGenerator,
    ReportConfig,
    ReportSection,
    ReportStyle,
    generate_pdf_report,
)

# Report Pipeline (unified generation)
from .pipeline import GeneratedReport, ReportPipeline, get_report_pipeline, reset_report_pipeline

# Presentation Generation
from .presentation_generator import (
    PPTX_AVAILABLE,
    PresentationConfig,
    PresentationGenerator,
    PresentationStyle,
    SlideContent,
    SlideType,
    generate_presentation,
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
    # Comparison Reports
    "ComparisonReportGenerator",
    "ComparisonReport",
    "CompanyData",
    "MetricComparison",
    "ComparisonMetric",
    "ComparisonCategory",
    "compare_companies",
    "create_comparison_generator",
    # Report Pipeline
    "ReportPipeline",
    "GeneratedReport",
    "get_report_pipeline",
    "reset_report_pipeline",
]
