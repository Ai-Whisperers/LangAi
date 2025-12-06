# Report Generation - 13 Report Features

**Category:** Report Generation
**Total Ideas:** 13
**Priority:** ⭐⭐⭐⭐⭐ HIGH (#86, #90), ⭐⭐⭐⭐ MEDIUM-HIGH (remaining)
**Phase:** 4
**Total Effort:** 85-110 hours

---

## 📋 Overview

Professional report generation features including templating, multi-format export, charts, and structured schemas.

**Sources:** Company-researcher + langchain-reference/open_deep_research

---

## 🎯 Report Feature Catalog

### Templating & Structure (Ideas #86, #90-91)
1. [Jinja2 Template System](#86-jinja2-template-system-) - Professional templates
2. [Structured Schema V2](#90-structured-schema-v2-) - 20+ file organization
3. [Executive Summary Generator](#91-executive-summary-generator-) - Key findings extraction

### Export Formats (Ideas #87-88, #93-94)
4. [PDF Export (WeasyPrint)](#87-pdf-export-weasyprint-) - HTML → PDF
5. [Excel Export](#88-excel-export-) - Multi-sheet workbooks
6. [Markdown Beautifier](#93-markdown-beautifier-) - Consistent formatting
7. [Multi-Format Export](#94-multi-format-export-) - MD, PDF, Excel, JSON

### Visual & Interactive (Ideas #89, #97)
8. [Chart Generation](#89-chart-generation-) - Revenue trends, market share
9. [Interactive Reports](#97-interactive-reports-) - HTML with filtering

### Management & Branding (Ideas #92, #95-96, #98)
10. [Source Log Generator](#92-source-log-generator-) - Auto-bibliography
11. [Report Versioning](#95-report-versioning-) - Change tracking
12. [Custom Branding](#96-custom-branding-) - Logos, colors
13. [Report Scheduling](#98-report-scheduling-) - Automated generation

---

## 📝 Detailed Specifications

### 86. Jinja2 Template System ⭐⭐⭐⭐⭐

**Priority:** HIGH
**Phase:** 4
**Effort:** Medium (8-10 hours)
**Source:** Company-researcher + open_deep_research

#### What It Does

Professional report templates using Jinja2 for consistent, reusable, and customizable report generation.

#### Template Structure

```python
templates/
├── reports/
│   ├── executive_summary.md.j2
│   ├── financial_analysis.md.j2
│   ├── competitive_landscape.md.j2
│   ├── market_intelligence.md.j2
│   └── investment_memo.md.j2
├── sections/
│   ├── revenue_table.md.j2
│   ├── metrics_chart.md.j2
│   ├── swot_analysis.md.j2
│   └── source_log.md.j2
└── exports/
    ├── pdf_layout.html.j2
    └── excel_template.xlsx.j2
```

#### Template Example

```jinja2
{# templates/reports/financial_analysis.md.j2 #}
# Financial Analysis: {{ company.name }}

**Analysis Date:** {{ analysis_date }}
**Analyst:** {{ analyst_name }}

## Executive Summary

{{ company.name }} demonstrates {{ financial_health }} financial health with:
- Revenue: ${{ revenue.current }}B ({{ revenue.growth }}% YoY)
- Profitability: {{ margins.net }}% net margin
- Cash Position: ${{ cash.current }}B

{% if highlights %}
### Key Highlights
{% for highlight in highlights %}
- {{ highlight }}
{% endfor %}
{% endif %}

## Revenue Performance

{% include 'sections/revenue_table.md.j2' %}

### Revenue Analysis

{{ revenue_analysis }}

## Profitability Metrics

| Metric | Value | Industry Avg | Assessment |
|--------|-------|--------------|------------|
| Gross Margin | {{ margins.gross }}% | {{ industry.gross_margin }}% | {{ assessment.gross }} |
| Operating Margin | {{ margins.operating }}% | {{ industry.operating_margin }}% | {{ assessment.operating }} |
| Net Margin | {{ margins.net }}% | {{ industry.net_margin }}% | {{ assessment.net }} |

{% if insights %}
## Strategic Insights

{% for insight in insights %}
### {{ insight.title }}

{{ insight.content }}

**Impact:** {{ insight.impact }}
**Confidence:** {{ insight.confidence }}
{% endfor %}
{% endif %}

---

## Sources

{% include 'sections/source_log.md.j2' %}
```

#### Implementation

```python
from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime

class ReportGenerator:
    """Generate reports from templates"""

    def __init__(self, template_dir: str = "templates"):
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Custom filters
        self.env.filters['currency'] = self.format_currency
        self.env.filters['percentage'] = self.format_percentage
        self.env.filters['date'] = self.format_date

    def generate(
        self,
        template_name: str,
        data: dict,
    ) -> str:
        """Generate report from template"""

        template = self.env.get_template(template_name)

        # Add metadata
        data['generated_at'] = datetime.now()
        data['generator'] = "LangAI Research System"

        # Render
        report = template.render(**data)

        return report

    @staticmethod
    def format_currency(value: float) -> str:
        """Format as currency"""
        return f"${value:,.2f}"

    @staticmethod
    def format_percentage(value: float) -> str:
        """Format as percentage"""
        return f"{value:.1f}%"

    @staticmethod
    def format_date(value: datetime) -> str:
        """Format date"""
        return value.strftime("%B %d, %Y")

# Usage
generator = ReportGenerator()

report = generator.generate(
    "reports/financial_analysis.md.j2",
    data={
        "company": {"name": "Tesla"},
        "revenue": {
            "current": 96.7,
            "growth": 18.8,
        },
        "margins": {
            "gross": 18.2,
            "operating": 9.2,
            "net": 15.5,
        },
        # ...
    },
)
```

#### Benefits

- **Consistency:** All reports follow same format
- **Reusability:** Templates used across agents
- **Maintainability:** Easy to update all reports
- **Professionalism:** Clean, structured output

---

### 87-98. Additional Report Features

### 87. PDF Export (WeasyPrint) ⭐⭐⭐⭐
**Phase:** 4 | **Effort:** 6-8h

```python
from weasyprint import HTML, CSS

def generate_pdf(markdown_content: str, output_path: str):
    # Convert MD to HTML
    html = markdown.markdown(markdown_content, extensions=['tables', 'fenced_code'])

    # Apply CSS styling
    css = CSS(string="""
        @page { margin: 2cm; }
        body { font-family: Arial, sans-serif; }
        h1 { color: #2c3e50; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; }
    """)

    # Generate PDF
    HTML(string=html).write_pdf(output_path, stylesheets=[css])
```

### 88. Excel Export ⭐⭐⭐⭐
**Phase:** 4 | **Effort:** 8-10h

Multi-sheet workbooks with formatted tables and charts

### 89. Chart Generation ⭐⭐⭐⭐
**Phase:** 4 | **Effort:** 8-10h

Revenue trends, market share, competitive positioning using matplotlib/plotly

### 90. Structured Schema V2 ⭐⭐⭐⭐⭐
**Phase:** 4 | **Effort:** 10-15h

```
company_report/
├── 00_executive_summary.md
├── 01_company_overview.md
├── 02_financial_analysis.md
├── 03_market_position.md
├── 04_competitive_landscape.md
├── 05_product_portfolio.md
├── 06_technology_stack.md
├── 07_customer_analysis.md
├── 08_partnerships.md
├── 09_risks_opportunities.md
├── 10_investment_thesis.md
└── sources/
    ├── bibliography.md
    └── source_quality_report.md
```

### 91. Executive Summary Generator ⭐⭐⭐⭐
**Phase:** 4 | **Effort:** 8-10h

Key findings extraction, concise summaries, action items

### 92. Source Log Generator ⭐⭐⭐⭐
**Phase:** 4 | **Effort:** 4-6h

Automatic bibliography, source tracking, citation formatting

### 93. Markdown Beautifier ⭐⭐⭐
**Phase:** 4 | **Effort:** 4-6h

Consistent formatting, table alignment, heading hierarchy

### 94. Multi-Format Export ⭐⭐⭐
**Phase:** 4 | **Effort:** 6-8h

Export to Markdown, PDF, Excel, JSON with format conversion

### 95. Report Versioning ⭐⭐⭐
**Phase:** 4 | **Effort:** 4-6h

Version tracking, change history, diff generation

### 96. Custom Branding ⭐⭐⭐
**Phase:** 4 | **Effort:** 4-6h

Logo integration, color schemes, custom headers/footers

### 97. Interactive Reports ⭐⭐⭐
**Phase:** 4 | **Effort:** 10-12h

HTML export with interactive charts and filterable tables

### 98. Report Scheduling ⭐⭐⭐
**Phase:** 4 | **Effort:** 6-8h

Automated generation, periodic updates, email delivery

---

## 📊 Summary Statistics

### Total Ideas: 13
### Total Effort: 85-110 hours

### Implementation Order:
**Phase 4 - Weeks 7-8:**
1. Jinja2 Templates (#86)
2. Structured Schema V2 (#90)
3. PDF Export (#87)
4. Excel Export (#88)
5. Chart Generation (#89)
6. Executive Summary (#91)
7. Remaining features (#92-98)

---

## 🔗 Related Documents

- [02-agent-specialization.md](02-agent-specialization.md#20-report-writer-) - Report Writer agent
- [05-quality-assurance.md](05-quality-assurance.md#68-citation-management-) - Citation management
- [README.md](README.md) - Navigation hub

---

**Status:** ✅ Complete
**Total Features:** 13
**Ready for:** Phase 4 implementation
