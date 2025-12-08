"""
Comprehensive Researcher Module.

Main research orchestration class that coordinates:
- Query generation
- Web searches
- Analysis with Claude
- Report generation
"""

import os
import asyncio
import yaml
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

from anthropic import Anthropic
from tavily import TavilyClient
from dotenv import load_dotenv

from .config import (
    CompanyProfile,
    MarketConfig,
    ResearchResult,
    ResearchDepth,
)

load_dotenv()


class ComprehensiveResearcher:
    """
    Comprehensive company research orchestrator.

    Coordinates the full research pipeline:
    1. Query generation from profile
    2. Web search execution
    3. Analysis with Claude
    4. Report generation in multiple formats
    """

    def __init__(
        self,
        output_base: str = "outputs/research",
        formats: Optional[List[str]] = None,
        depth: str = "comprehensive",
        use_cache: bool = True,
        cache_ttl_days: int = 7,
        force_refresh: bool = False
    ):
        """
        Initialize researcher.

        Args:
            output_base: Base directory for outputs
            formats: Output formats (md, pdf, excel)
            depth: Research depth (quick, standard, comprehensive)
            use_cache: Whether to use search result caching
            cache_ttl_days: Cache TTL in days
            force_refresh: Force refresh of cached data
        """
        self.output_base = Path(output_base)
        self.formats = formats or ["md"]
        self.depth = depth
        self.use_cache = use_cache
        self.cache_ttl_days = cache_ttl_days
        self.force_refresh = force_refresh

        # Initialize clients
        self.anthropic_client = Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.tavily_client = TavilyClient(
            api_key=os.getenv("TAVILY_API_KEY")
        )

        # Initialize cache if enabled
        self.cache = None
        if use_cache:
            try:
                from src.company_researcher.cache import create_cache
                self.cache = create_cache(
                    cache_dir=self.output_base / ".cache",
                    ttl_days=cache_ttl_days,
                    enabled=True
                )
            except ImportError:
                print("[WARNING] Cache module not available, running without cache")

    async def research_company(
        self,
        company_name: str,
        profile: Optional[CompanyProfile] = None
    ) -> ResearchResult:
        """
        Research a single company.

        Args:
            company_name: Company name to research
            profile: Optional company profile with additional context

        Returns:
            ResearchResult with all findings
        """
        start_time = datetime.now()
        print(f"\n{'='*70}")
        print(f"[RESEARCH] Starting research for: {company_name}")
        print(f"{'='*70}")

        try:
            # Step 1: Generate queries
            queries = self._generate_queries(company_name, profile)
            print(f"\n[QUERIES] Generated {len(queries)} search queries")

            # Step 2: Execute searches
            print("\n[SEARCH] Executing web searches...")
            search_results = await self._execute_searches(queries)

            # Step 3: Analyze with Claude
            print("\n[ANALYSIS] Analyzing sources with Claude...")
            analysis = await self._analyze_company(
                company_name, profile, search_results
            )

            # Step 4: Generate reports
            print("\n[REPORTS] Generating reports...")
            report_paths = await self._generate_reports(
                company_name, profile, analysis, search_results
            )

            # Calculate metrics
            duration = (datetime.now() - start_time).total_seconds()
            cost = self._estimate_cost(analysis)

            result = ResearchResult(
                company_name=company_name,
                success=True,
                profile=profile,
                summary=analysis.get("summary", ""),
                analysis=analysis,
                sources=search_results.get("sources", []),
                report_paths=report_paths,
                metrics={
                    "duration_seconds": duration,
                    "cost_usd": cost,
                    "sources_count": len(search_results.get("sources", [])),
                    "queries_count": len(queries)
                },
                quality_score=analysis.get("quality_score", 70.0)
            )

            self._print_result_summary(result)
            return result

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            print(f"\n[ERROR] Research failed: {e}")
            return ResearchResult(
                company_name=company_name,
                success=False,
                profile=profile,
                error=str(e),
                metrics={"duration_seconds": duration}
            )

    async def research_market(
        self,
        market_folder: str,
        generate_comparison: bool = True
    ) -> List[ResearchResult]:
        """
        Research all companies in a market folder.

        Args:
            market_folder: Path to market folder with YAML files
            generate_comparison: Whether to generate comparison report

        Returns:
            List of research results
        """
        market_path = Path(market_folder)
        results = []

        # Load market config if exists
        market_config = None
        market_file = market_path / "_market.yaml"
        if market_file.exists():
            with open(market_file) as f:
                market_config = MarketConfig.from_yaml(yaml.safe_load(f))
            print(f"\n[MARKET] Loading market: {market_config.name}")
            print(f"  Country: {market_config.country}")
            print(f"  Industry: {market_config.industry}")

        # Find all company YAML files
        company_files = [
            f for f in market_path.glob("*.yaml")
            if not f.name.startswith("_")
        ]

        print(f"\n[BATCH] Found {len(company_files)} companies to research\n")

        # Research each company
        for i, yaml_file in enumerate(company_files, 1):
            print(f"\n[{i}/{len(company_files)}] Processing: {yaml_file.name}")

            with open(yaml_file) as f:
                data = yaml.safe_load(f)

            profile = CompanyProfile.from_yaml(data)
            result = await self.research_company(profile.name, profile)
            results.append(result)

        # Generate comparison report if requested
        if generate_comparison and len(results) > 1:
            await self._generate_comparison_report(results, market_config)

        # Print batch summary
        self._print_batch_summary(results)

        return results

    def _generate_queries(
        self,
        company_name: str,
        profile: Optional[CompanyProfile]
    ) -> List[str]:
        """Generate search queries for a company."""
        queries = []

        # Base queries
        queries.extend([
            f'"{company_name}" company overview',
            f'"{company_name}" revenue financials 2024',
            f'"{company_name}" market share industry position',
            f'"{company_name}" products services offerings',
            f'"{company_name}" news developments 2024',
            f'"{company_name}" competitors analysis'
        ])

        # Profile-based queries
        if profile:
            if profile.industry:
                queries.append(f'"{company_name}" {profile.industry} market')

            if profile.country:
                queries.append(f'"{company_name}" {profile.country} operations')

            if profile.parent_company:
                queries.append(f'"{profile.parent_company}" investor presentation 2024')
                queries.append(f'"{profile.parent_company}" {company_name} subsidiary')

            if profile.competitors:
                comp = profile.competitors[0] if profile.competitors else ""
                queries.append(f'"{company_name}" vs "{comp}" comparison market share')

        # Apply query limits based on depth
        depth_limits = {
            "quick": 6,
            "standard": 9,
            "comprehensive": 12
        }
        max_queries = depth_limits.get(self.depth, 12)
        return queries[:max_queries]

    async def _execute_searches(self, queries: List[str]) -> Dict[str, Any]:
        """Execute web searches for all queries."""
        all_sources = []
        all_content = []
        cache_hits = 0
        cache_misses = 0

        for query in queries:
            # Check cache first
            cached_results = None
            if self.cache and not self.force_refresh:
                cached_results = self.cache.get_search_results(query)

            if cached_results:
                print(f"  [CACHE HIT] {query[:60]}...")
                cache_hits += 1
                results = cached_results
            else:
                print(f"  [SEARCH] {query}")
                cache_misses += 1
                try:
                    results = await asyncio.to_thread(
                        self.tavily_client.search,
                        query=query,
                        max_results=3
                    )

                    if self.cache:
                        self.cache.store_search_results(query, results)

                except Exception as e:
                    print(f"  [ERROR] Search failed: {e}")
                    continue

            # Process results
            for item in results.get("results", []):
                all_sources.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "score": item.get("score", 0),
                    "query": query
                })
                all_content.append({
                    "title": item.get("title", ""),
                    "content": item.get("content", ""),
                })

        if self.cache:
            print(f"  [OK] Found {len(all_sources)} sources (cache: {cache_hits} hits, {cache_misses} API calls)\n")
        else:
            print(f"  [OK] Found {len(all_sources)} sources\n")

        return {
            "sources": all_sources,
            "content": all_content
        }

    async def _analyze_company(
        self,
        company_name: str,
        profile: Optional[CompanyProfile],
        search_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze company with Claude."""
        content = search_results.get("content", [])
        combined = "\n---\n".join([
            f"Source: {c['title']}\n{c['content']}"
            for c in content[:12]
        ])

        # Build context from profile
        context = ""
        if profile:
            context = f"""
Company Profile Context:
- Legal Name: {profile.legal_name or 'N/A'}
- Industry: {profile.industry or 'N/A'}
- Country: {profile.country or 'N/A'}
- Region: {profile.region or 'N/A'}
- Parent Company: {profile.parent_company or 'N/A'}
- Services: {', '.join(profile.services[:5]) if profile.services else 'N/A'}
- Key Competitors: {', '.join(profile.competitors[:3]) if profile.competitors else 'N/A'}
"""

        prompt = f"""Analyze the following research sources about {company_name} and create a comprehensive research report.

{context}

Research Sources:
{combined}

Create a detailed report with the following sections:
1. **Executive Summary** - Key findings in 3-4 sentences
2. **Company Overview** - History, mission, leadership
3. **Financial Performance** - Revenue, growth, profitability (with specific numbers if available)
4. **Market Position** - Market share, competitive advantages
5. **Products & Services** - Main offerings
6. **Competitive Landscape** - Key competitors, differentiation
7. **Recent Developments** - News, announcements, strategic moves
8. **SWOT Analysis** - Strengths, Weaknesses, Opportunities, Threats
9. **Key Metrics Summary** - Table format

Requirements:
- Use specific numbers and dates when available
- Cite sources for key claims
- Be objective and balanced
- Note any data gaps or limitations
- Format using Markdown"""

        response = self.anthropic_client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=4000,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}]
        )

        summary = response.content[0].text

        return {
            "summary": summary,
            "tokens": {
                "input": response.usage.input_tokens,
                "output": response.usage.output_tokens
            },
            "quality_score": self._calculate_quality_score(summary, search_results)
        }

    def _calculate_quality_score(
        self,
        summary: str,
        search_results: Dict[str, Any]
    ) -> float:
        """Calculate research quality score."""
        score = 50.0

        # Source quantity bonus
        sources = search_results.get("sources", [])
        if len(sources) >= 10:
            score += 15
        elif len(sources) >= 5:
            score += 10

        # Content length bonus
        if len(summary) > 3000:
            score += 10
        elif len(summary) > 1500:
            score += 5

        # Financial data presence
        if re.search(r'\$[\d,.]+\s*(?:billion|million|B|M)?', summary):
            score += 10

        # Specific metrics presence
        if re.search(r'[\d,.]+\s*(?:percent|%)', summary):
            score += 5

        # SWOT presence
        if "SWOT" in summary or "Strength" in summary:
            score += 5

        return min(100.0, score)

    async def _generate_reports(
        self,
        company_name: str,
        profile: Optional[CompanyProfile],
        analysis: Dict[str, Any],
        search_results: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate reports in requested formats."""
        # Create output directory
        safe_name = company_name.lower().replace(" ", "_").replace(".", "")
        timestamp = datetime.now().strftime("%Y%m%d")
        company_dir = self.output_base / safe_name
        company_dir.mkdir(parents=True, exist_ok=True)

        report_paths = {}

        # Generate Markdown
        if "md" in self.formats:
            md_path = company_dir / f"{safe_name}_report_{timestamp}.md"
            self._write_markdown_report(md_path, company_name, profile, analysis, search_results)
            report_paths["markdown"] = str(md_path)

        # Generate PDF if requested
        if "pdf" in self.formats:
            try:
                pdf_path = company_dir / f"{safe_name}_report_{timestamp}.pdf"
                self._write_pdf_report(pdf_path, company_name, profile, analysis)
                report_paths["pdf"] = str(pdf_path)
            except Exception as e:
                print(f"  [WARNING] PDF generation failed: {e}")

        # Generate Excel if requested
        if "excel" in self.formats:
            try:
                excel_path = company_dir / f"{safe_name}_report_{timestamp}.xlsx"
                self._write_excel_report(excel_path, company_name, profile, analysis)
                report_paths["excel"] = str(excel_path)
            except Exception as e:
                print(f"  [WARNING] Excel generation failed: {e}")

        return report_paths

    def _write_markdown_report(
        self,
        path: Path,
        company_name: str,
        profile: Optional[CompanyProfile],
        analysis: Dict[str, Any],
        search_results: Dict[str, Any]
    ):
        """Write Markdown report."""
        content = f"""# {company_name} Research Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}

---

{analysis.get('summary', '')}

---

## Sources

"""
        for source in search_results.get("sources", [])[:10]:
            content += f"- [{source.get('title', 'Source')}]({source.get('url', '')})\n"

        path.write_text(content, encoding="utf-8")

    def _write_pdf_report(
        self,
        path: Path,
        company_name: str,
        profile: Optional[CompanyProfile],
        analysis: Dict[str, Any]
    ):
        """Write PDF report (requires reportlab or similar)."""
        # Simple text-based PDF fallback
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas

            c = canvas.Canvas(str(path), pagesize=letter)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, 750, f"{company_name} Research Report")
            c.setFont("Helvetica", 10)
            c.drawString(50, 730, f"Generated: {datetime.now().strftime('%Y-%m-%d')}")

            # Write summary (simplified)
            y = 700
            summary = analysis.get("summary", "")[:2000]
            for line in summary.split('\n')[:50]:
                if y < 50:
                    c.showPage()
                    y = 750
                c.drawString(50, y, line[:100])
                y -= 12

            c.save()
        except ImportError:
            # Fallback: write as text file with .pdf extension
            path.write_text(
                f"{company_name} Research Report\n\n{analysis.get('summary', '')}",
                encoding="utf-8"
            )

    def _write_excel_report(
        self,
        path: Path,
        company_name: str,
        profile: Optional[CompanyProfile],
        analysis: Dict[str, Any]
    ):
        """Write Excel report (requires openpyxl)."""
        try:
            from openpyxl import Workbook

            wb = Workbook()
            ws = wb.active
            ws.title = "Summary"

            # Header
            ws['A1'] = "Company Research Report"
            ws['A2'] = company_name
            ws['A3'] = f"Generated: {datetime.now().strftime('%Y-%m-%d')}"

            # Profile info
            if profile:
                ws['A5'] = "Company Profile"
                ws['A6'] = "Industry"
                ws['B6'] = profile.industry
                ws['A7'] = "Country"
                ws['B7'] = profile.country

            # Report sheet
            ws2 = wb.create_sheet("Full Report")
            summary = analysis.get("summary", "")
            for i, line in enumerate(summary.split('\n')[:100], 1):
                ws2[f'A{i}'] = line

            wb.save(path)
        except ImportError:
            print("  [WARNING] openpyxl not installed, skipping Excel")

    def _estimate_cost(self, analysis: Dict[str, Any]) -> float:
        """Estimate cost based on token usage."""
        tokens = analysis.get("tokens", {})
        input_tokens = tokens.get("input", 0)
        output_tokens = tokens.get("output", 0)

        # Haiku pricing
        input_cost = (input_tokens / 1_000_000) * 0.80
        output_cost = (output_tokens / 1_000_000) * 4.00

        # Add estimated search costs
        search_cost = 0.01  # Approximate Tavily cost

        return input_cost + output_cost + search_cost

    def _print_result_summary(self, result: ResearchResult):
        """Print research result summary."""
        print(f"\n{'='*70}")
        print(f"[COMPLETE] Research completed for: {result.company_name}")
        print(f"{'='*70}")
        print(f"Duration:      {result.metrics.get('duration_seconds', 0):.1f} seconds")
        print(f"Cost:          ${result.metrics.get('cost_usd', 0):.4f}")
        print(f"Sources:       {result.metrics.get('sources_count', 0)}")
        print(f"Quality Score: {result.quality_score:.1f}/100")
        print(f"\nReports generated:")
        for fmt, path in result.report_paths.items():
            print(f"  - {fmt}: {path}")
        print(f"{'='*70}\n")

    def _print_batch_summary(self, results: List[ResearchResult]):
        """Print batch research summary."""
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]

        print(f"\n{'='*70}")
        print("[BATCH COMPLETE] Market Research Summary")
        print(f"{'='*70}")
        print(f"Total companies: {len(results)}")
        print(f"Successful:      {len(successful)}")
        print(f"Failed:          {len(failed)}")

        if successful:
            total_cost = sum(r.metrics.get('cost_usd', 0) for r in successful)
            total_duration = sum(r.metrics.get('duration_seconds', 0) for r in successful)
            avg_quality = sum(r.quality_score for r in successful) / len(successful)
            print(f"Total cost:      ${total_cost:.4f}")
            print(f"Total duration:  {total_duration:.1f} seconds")
            print(f"Avg quality:     {avg_quality:.1f}/100")

        if failed:
            print(f"\nFailed companies:")
            for r in failed:
                print(f"  - {r.company_name}: {r.error}")

        print(f"{'='*70}\n")

    async def _generate_comparison_report(
        self,
        results: List[ResearchResult],
        market_config: Optional[MarketConfig]
    ):
        """Generate market comparison report."""
        print("\n[COMPARISON] Generating comparison report...")

        market_name = market_config.name if market_config else "Market Comparison"
        safe_name = market_name.lower().replace(" ", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        successful_results = [r for r in results if r.success]

        if len(successful_results) < 2:
            print("[WARNING] Not enough successful results for comparison")
            return

        # Create comparison directory
        comparison_dir = self.output_base / "comparisons"
        comparison_dir.mkdir(parents=True, exist_ok=True)

        # Generate comparison content
        content = f"# {market_name} Comparison Report\n\n"
        content += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        content += f"**Companies Analyzed:** {len(successful_results)}\n\n"

        content += "## Company Overview\n\n"
        content += "| Company | Industry | Country | Quality Score |\n"
        content += "|---------|----------|---------|---------------|\n"

        for r in successful_results:
            industry = r.profile.industry if r.profile else "N/A"
            country = r.profile.country if r.profile else "N/A"
            content += f"| {r.company_name} | {industry} | {country} | {r.quality_score:.1f} |\n"

        # Write comparison report
        comparison_path = comparison_dir / f"{safe_name}_comparison_{timestamp}.md"
        comparison_path.write_text(content, encoding="utf-8")
        print(f"[COMPARISON] Report saved: {comparison_path}")
