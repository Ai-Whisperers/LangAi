# Python Rich Terminal UI Pattern Exemplar

## Overview

Rich library provides beautiful terminal output with tables, progress bars, and panels for professional-grade scripts.

## When to Use

- **Use for**: Advanced quality level scripts, user-facing tools, reports
- **Skip for**: Headless scripts, simple logging

## Good Pattern ✅

```python
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.panel import Panel

console = Console()

def display_coverage_table(results: List[Dict], threshold: int):
    """Display coverage results in formatted table."""
    table = Table(title="📊 Coverage Analysis Results", show_header=True)
    
    table.add_column("Package", style="cyan")
    table.add_column("Line %", justify="right", style="green")
    table.add_column("Status", justify="center")
    
    for result in results:
        line_cov = result['line_coverage']
        status = "✅" if line_cov >= threshold else "❌"
        style = "green" if line_cov >= threshold else "red"
        
        table.add_row(result['package'], f"{line_cov:.2f}%", status, style=style)
    
    console.print(table)

def show_progress(packages: List[Package]) -> List[Dict]:
    """Analyze packages with progress bar."""
    results = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    ) as progress:
        task = progress.add_task("Analyzing packages...", total=len(packages))
        
        for package in packages:
            progress.update(task, description=f"Analyzing {package.name}")
            result = analyze_package(package)
            results.append(result)
            progress.advance(task)
    
    return results
```

**Why this is good:**
- Beautiful, colorized output
- Progress bars with spinners
- Tables with automatic formatting
- Panels for grouping

---
Produced-by: rule.scripts.exemplars.v1 | ts=2025-12-07T00:00:00Z

