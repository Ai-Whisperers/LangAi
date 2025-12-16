"""
Crawling module for domain exploration, web scraping, and content extraction.

This module provides tools to:
- Explore websites and extract links (DomainExplorer)
- Scrape web pages with LLM-ready output (WebScraper with Firecrawl/ScrapeGraph)
- Smart AI-powered data extraction
- Crawl entire websites
"""

from .domain_explorer import (
    DomainExplorationResult,
    DomainExplorer,
    LinkInfo,
    PageContent,
    explore_domain,
    format_exploration_for_research,
)
from .web_scraper import (
    ScrapingBackend,
    UnifiedCrawlResult,
    UnifiedScrapeResult,
    WebScraper,
    create_web_scraper,
    quick_extract,
    quick_scrape,
)

__all__ = [
    # Domain Explorer
    "DomainExplorer",
    "PageContent",
    "LinkInfo",
    "DomainExplorationResult",
    "explore_domain",
    "format_exploration_for_research",
    # Unified Web Scraper
    "WebScraper",
    "ScrapingBackend",
    "UnifiedScrapeResult",
    "UnifiedCrawlResult",
    "create_web_scraper",
    "quick_scrape",
    "quick_extract",
]
