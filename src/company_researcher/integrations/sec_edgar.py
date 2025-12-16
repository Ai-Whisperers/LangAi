"""
SEC EDGAR Integration - FREE US Public Company Filings.

Access official SEC filings for all US public companies - completely free.
No API key required, unlimited access to official government data.

Features:
- Company search by name or ticker
- 10-K (annual reports), 10-Q (quarterly), 8-K (current events)
- Financial statement extraction
- Insider trading data (Forms 3, 4, 5)
- Institutional holdings (13F)
- NO API KEY REQUIRED
- UNLIMITED QUERIES (be respectful with rate limiting)

Cost: $0 (completely free, official government data)
Replaces: Parts of FMP, Finnhub, Alpha Vantage for US public companies

Usage:
    from company_researcher.integrations.sec_edgar import get_sec_edgar

    edgar = get_sec_edgar()

    # Search for company
    company = edgar.search_company("Apple Inc")

    # Get recent filings
    filings = edgar.get_filings("AAPL", form_type="10-K")

    # Get specific filing content
    content = edgar.get_filing_content(filing_url)
"""

import json
import time
from dataclasses import dataclass, field
from threading import Lock
from typing import Any, Dict, List, Optional

import requests
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import HTTPError, RequestException
from requests.exceptions import Timeout as RequestsTimeout

from ..utils import get_logger, utc_now

logger = get_logger(__name__)

# Error message constants (avoid duplication)
ERR_REQUEST_TIMEOUT = "Request timeout"
ERR_INVALID_JSON = "Invalid JSON response"


# SEC requires a User-Agent header with contact info
DEFAULT_USER_AGENT = "CompanyResearcher/1.0 (research@example.com)"


@dataclass
class SECCompany:
    """SEC registered company information."""

    cik: str
    name: str
    ticker: Optional[str] = None
    sic: Optional[str] = None  # Standard Industrial Classification
    sic_description: Optional[str] = None
    state: Optional[str] = None
    fiscal_year_end: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cik": self.cik,
            "name": self.name,
            "ticker": self.ticker,
            "sic": self.sic,
            "sic_description": self.sic_description,
            "state": self.state,
            "fiscal_year_end": self.fiscal_year_end,
        }


@dataclass
class SECFiling:
    """SEC filing information."""

    accession_number: str
    form_type: str
    filing_date: str
    report_date: Optional[str] = None
    primary_document: Optional[str] = None
    file_url: Optional[str] = None
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accession_number": self.accession_number,
            "form_type": self.form_type,
            "filing_date": self.filing_date,
            "report_date": self.report_date,
            "primary_document": self.primary_document,
            "file_url": self.file_url,
            "description": self.description,
        }


@dataclass
class SECSearchResult:
    """Result from SEC search operations."""

    query: str
    companies: List[SECCompany] = field(default_factory=list)
    filings: List[SECFiling] = field(default_factory=list)
    success: bool = True
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "companies": [c.to_dict() for c in self.companies],
            "filings": [f.to_dict() for f in self.filings],
            "success": self.success,
            "error": self.error,
        }


class SECEdgarClient:
    """
    Free SEC EDGAR client for US public company data.

    100% free, no API key required, official government data.
    """

    # SEC EDGAR API endpoints
    BASE_URL = "https://data.sec.gov"
    WWW_URL = "https://www.sec.gov"  # Some files are served from www.sec.gov
    SEARCH_URL = "https://efts.sec.gov/LATEST/search-index"
    FULL_TEXT_URL = "https://efts.sec.gov/LATEST/full-text-search"

    # Common form types
    FORM_TYPES = {
        "10-K": "Annual report",
        "10-Q": "Quarterly report",
        "8-K": "Current report (material events)",
        "10-K/A": "Annual report amendment",
        "10-Q/A": "Quarterly report amendment",
        "8-K/A": "Current report amendment",
        "DEF 14A": "Proxy statement",
        "S-1": "Registration statement (IPO)",
        "4": "Insider trading",
        "13F-HR": "Institutional holdings",
        "13D": "Beneficial ownership (activist)",
        "13G": "Beneficial ownership (passive)",
        "SC 13D": "Schedule 13D filing",
        "SC 13G": "Schedule 13G filing",
    }

    def __init__(
        self,
        user_agent: str = DEFAULT_USER_AGENT,
        timeout: int = 30,
        rate_limit_delay: float = 0.1,  # SEC requests max 10/sec
    ):
        """
        Initialize SEC EDGAR client.

        Args:
            user_agent: Required by SEC - include contact email
            timeout: Request timeout in seconds
            rate_limit_delay: Delay between requests (SEC limit: 10/sec)
        """
        self.user_agent = user_agent
        self.timeout = timeout
        self.rate_limit_delay = rate_limit_delay

        self._session = requests.Session()
        self._session.headers.update({"User-Agent": user_agent, "Accept": "application/json"})

        self._last_request_time = 0.0
        self._total_queries = 0
        self._lock = Lock()

        # Cache for CIK lookups
        self._cik_cache: Dict[str, str] = {}

    def _rate_limit(self) -> None:
        """Enforce rate limiting for SEC API."""
        current_time = time.time()
        elapsed = current_time - self._last_request_time

        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)

        self._last_request_time = time.time()

    def _format_cik(self, cik: str) -> str:
        """Format CIK to 10-digit zero-padded string."""
        return cik.zfill(10)

    def get_company_by_cik(self, cik: str) -> Optional[SECCompany]:
        """
        Get company information by CIK number.

        Args:
            cik: Central Index Key (SEC identifier)

        Returns:
            SECCompany or None if not found
        """
        try:
            self._rate_limit()

            formatted_cik = self._format_cik(cik)
            url = f"{self.BASE_URL}/submissions/CIK{formatted_cik}.json"

            response = self._session.get(url, timeout=self.timeout)

            if response.status_code == 404:
                logger.debug(f"SEC EDGAR: CIK {cik} not found (404)")
                return None

            response.raise_for_status()
            data = response.json()

            with self._lock:
                self._total_queries += 1

            # Extract ticker from exchanges
            ticker = None
            if data.get("tickers"):
                ticker = data["tickers"][0]

            return SECCompany(
                cik=cik,
                name=data.get("name", ""),
                ticker=ticker,
                sic=data.get("sic"),
                sic_description=data.get("sicDescription"),
                state=data.get("stateOfIncorporation"),
                fiscal_year_end=data.get("fiscalYearEnd"),
            )

        except RequestsTimeout:
            logger.warning(f"SEC EDGAR timeout for CIK {cik} (timeout={self.timeout}s)")
            return None
        except RequestsConnectionError as e:
            logger.warning(f"SEC EDGAR connection error for CIK {cik}: {e}")
            return None
        except HTTPError as e:
            logger.error(
                f"SEC EDGAR HTTP error for CIK {cik}: {e.response.status_code if e.response else 'unknown'}"
            )
            return None
        except json.JSONDecodeError as e:
            logger.error(f"SEC EDGAR invalid JSON response for CIK {cik}: {e}")
            return None
        except RequestException as e:
            logger.error(f"SEC EDGAR request error for CIK {cik}: {e}")
            return None
        except Exception as e:
            logger.error(f"SEC EDGAR unexpected error for CIK {cik}: {type(e).__name__}: {e}")
            return None

    def search_company(self, query: str, max_results: int = 10) -> SECSearchResult:
        """
        Search for companies by name or ticker (with caching).

        Args:
            query: Company name or ticker symbol
            max_results: Maximum results to return

        Returns:
            SECSearchResult with matching companies
        """
        # Check cache first (30-day TTL)
        cache_key = f"search:{query}:{max_results}"
        try:
            from ..cache.result_cache import cache_sec_filing, get_cached_sec_filing

            cached = get_cached_sec_filing(query, cache_key)
            if cached:
                logger.debug(f"[CACHE HIT] SEC company search: '{query}'")
                # Reconstruct SECSearchResult from cached dict
                result_dict = cached.copy()
                result_dict["companies"] = [
                    SECCompany(**c) for c in result_dict.get("companies", [])
                ]
                result_dict["filings"] = [SECFiling(**f) for f in result_dict.get("filings", [])]
                return SECSearchResult(**result_dict)
        except ImportError:
            pass

        try:
            self._rate_limit()

            # Try to find by ticker first using company tickers JSON
            # Note: company_tickers.json is served from www.sec.gov, not data.sec.gov
            url = f"{self.WWW_URL}/files/company_tickers.json"
            response = self._session.get(url, timeout=self.timeout)
            response.raise_for_status()

            tickers_data = response.json()

            companies = []
            query_lower = query.lower().strip()

            for _, company_data in tickers_data.items():
                ticker = company_data.get("ticker", "").lower()
                name = company_data.get("title", "").lower()

                # Match by ticker (exact) or name (partial)
                if ticker == query_lower or query_lower in name:
                    cik = str(company_data.get("cik_str", ""))

                    companies.append(
                        SECCompany(
                            cik=cik,
                            name=company_data.get("title", ""),
                            ticker=company_data.get("ticker"),
                        )
                    )

                    if len(companies) >= max_results:
                        break

            with self._lock:
                self._total_queries += 1

            result = SECSearchResult(query=query, companies=companies, success=True)

            # Cache results (30 days)
            try:
                from ..cache.result_cache import cache_sec_filing

                cache_sec_filing(query, cache_key, result.to_dict())
                logger.debug(f"[CACHED] SEC company search: '{query}'")
            except ImportError:
                pass

            return result

        except RequestsTimeout:
            logger.warning(f"SEC company search timeout for '{query}' (timeout={self.timeout}s)")
            return SECSearchResult(query=query, success=False, error=ERR_REQUEST_TIMEOUT)
        except RequestsConnectionError as e:
            logger.warning(f"SEC company search connection error for '{query}': {e}")
            return SECSearchResult(query=query, success=False, error=f"Connection error: {e}")
        except HTTPError as e:
            status_code = e.response.status_code if e.response else "unknown"
            logger.error(f"SEC company search HTTP error for '{query}': {status_code}")
            return SECSearchResult(query=query, success=False, error=f"HTTP error: {status_code}")
        except json.JSONDecodeError as e:
            logger.error(f"SEC company search invalid JSON for '{query}': {e}")
            return SECSearchResult(query=query, success=False, error=ERR_INVALID_JSON)
        except RequestException as e:
            logger.error(f"SEC company search request error for '{query}': {e}")
            return SECSearchResult(query=query, success=False, error=f"Request error: {e}")
        except Exception as e:
            logger.error(
                f"SEC company search unexpected error for '{query}': {type(e).__name__}: {e}"
            )
            return SECSearchResult(query=query, success=False, error=str(e))

    def get_cik(self, ticker: str) -> Optional[str]:
        """
        Get CIK number for a ticker symbol.

        Args:
            ticker: Stock ticker symbol

        Returns:
            CIK number or None
        """
        # Check cache first
        ticker_upper = ticker.upper()
        if ticker_upper in self._cik_cache:
            return self._cik_cache[ticker_upper]

        result = self.search_company(ticker, max_results=1)

        if result.success and result.companies:
            cik = result.companies[0].cik
            self._cik_cache[ticker_upper] = cik
            return cik

        return None

    def get_filings(
        self,
        ticker_or_cik: str,
        form_type: Optional[str] = None,
        max_results: int = 20,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> SECSearchResult:
        """
        Get SEC filings for a company (with caching).

        Args:
            ticker_or_cik: Stock ticker or CIK number
            form_type: Filter by form type (10-K, 10-Q, 8-K, etc.)
            max_results: Maximum filings to return
            start_date: Filter filings after this date (YYYY-MM-DD)
            end_date: Filter filings before this date (YYYY-MM-DD)

        Returns:
            SECSearchResult with filings
        """
        # Check cache first (30-day TTL)
        cache_key = f"{ticker_or_cik}:{form_type or 'all'}:{max_results}:{start_date or 'none'}:{end_date or 'none'}"
        try:
            from ..cache.result_cache import cache_sec_filing, get_cached_sec_filing

            cached = get_cached_sec_filing(ticker_or_cik, cache_key)
            if cached:
                logger.debug(f"[CACHE HIT] SEC filings: '{ticker_or_cik}' form={form_type}")
                # Reconstruct SECSearchResult from cached dict
                result_dict = cached.copy()
                result_dict["filings"] = [SECFiling(**f) for f in result_dict.get("filings", [])]
                result_dict["companies"] = [
                    SECCompany(**c) for c in result_dict.get("companies", [])
                ]
                return SECSearchResult(**result_dict)
        except ImportError:
            pass

        try:
            # Resolve to CIK if ticker provided
            if not ticker_or_cik.isdigit():
                cik = self.get_cik(ticker_or_cik)
                if not cik:
                    return SECSearchResult(
                        query=ticker_or_cik,
                        success=False,
                        error=f"Could not find CIK for ticker: {ticker_or_cik}",
                    )
            else:
                cik = ticker_or_cik

            self._rate_limit()

            formatted_cik = self._format_cik(cik)
            url = f"{self.BASE_URL}/submissions/CIK{formatted_cik}.json"

            response = self._session.get(url, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            # Get recent filings
            recent = data.get("filings", {}).get("recent", {})

            filings = []
            accession_numbers = recent.get("accessionNumber", [])
            form_types = recent.get("form", [])
            filing_dates = recent.get("filingDate", [])
            report_dates = recent.get("reportDate", [])
            primary_docs = recent.get("primaryDocument", [])
            descriptions = recent.get("primaryDocDescription", [])

            for i in range(len(accession_numbers)):
                # Apply form type filter
                if form_type and form_types[i] != form_type:
                    continue

                # Apply date filters
                filing_date = filing_dates[i] if i < len(filing_dates) else ""

                if start_date and filing_date < start_date:
                    continue
                if end_date and filing_date > end_date:
                    continue

                # Build file URL
                accession = accession_numbers[i].replace("-", "")
                primary_doc = primary_docs[i] if i < len(primary_docs) else ""
                file_url = (
                    f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{primary_doc}"
                )

                filings.append(
                    SECFiling(
                        accession_number=accession_numbers[i],
                        form_type=form_types[i],
                        filing_date=filing_date,
                        report_date=report_dates[i] if i < len(report_dates) else None,
                        primary_document=primary_doc,
                        file_url=file_url,
                        description=descriptions[i] if i < len(descriptions) else None,
                    )
                )

                if len(filings) >= max_results:
                    break

            with self._lock:
                self._total_queries += 1

            result = SECSearchResult(query=ticker_or_cik, filings=filings, success=True)

            # Cache results (30 days)
            try:
                from ..cache.result_cache import cache_sec_filing

                cache_sec_filing(ticker_or_cik, cache_key, result.to_dict())
                logger.debug(f"[CACHED] SEC filings: '{ticker_or_cik}' form={form_type}")
            except ImportError:
                pass

            return result

        except RequestsTimeout:
            logger.warning(f"SEC filings timeout for '{ticker_or_cik}' (timeout={self.timeout}s)")
            return SECSearchResult(query=ticker_or_cik, success=False, error=ERR_REQUEST_TIMEOUT)
        except RequestsConnectionError as e:
            logger.warning(f"SEC filings connection error for '{ticker_or_cik}': {e}")
            return SECSearchResult(
                query=ticker_or_cik, success=False, error=f"Connection error: {e}"
            )
        except HTTPError as e:
            status_code = e.response.status_code if e.response else "unknown"
            logger.error(f"SEC filings HTTP error for '{ticker_or_cik}': {status_code}")
            return SECSearchResult(
                query=ticker_or_cik, success=False, error=f"HTTP error: {status_code}"
            )
        except json.JSONDecodeError as e:
            logger.error(f"SEC filings invalid JSON for '{ticker_or_cik}': {e}")
            return SECSearchResult(query=ticker_or_cik, success=False, error=ERR_INVALID_JSON)
        except RequestException as e:
            logger.error(f"SEC filings request error for '{ticker_or_cik}': {e}")
            return SECSearchResult(query=ticker_or_cik, success=False, error=f"Request error: {e}")
        except Exception as e:
            logger.error(
                f"SEC filings unexpected error for '{ticker_or_cik}': {type(e).__name__}: {e}"
            )
            return SECSearchResult(query=ticker_or_cik, success=False, error=str(e))

    def get_10k_filings(self, ticker_or_cik: str, years: int = 5) -> SECSearchResult:
        """
        Get annual 10-K filings.

        Args:
            ticker_or_cik: Stock ticker or CIK number
            years: Number of years of filings to retrieve

        Returns:
            SECSearchResult with 10-K filings
        """
        return self.get_filings(ticker_or_cik, form_type="10-K", max_results=years)

    def get_10q_filings(self, ticker_or_cik: str, quarters: int = 8) -> SECSearchResult:
        """
        Get quarterly 10-Q filings.

        Args:
            ticker_or_cik: Stock ticker or CIK number
            quarters: Number of quarters of filings to retrieve

        Returns:
            SECSearchResult with 10-Q filings
        """
        return self.get_filings(ticker_or_cik, form_type="10-Q", max_results=quarters)

    def get_8k_filings(self, ticker_or_cik: str, max_results: int = 20) -> SECSearchResult:
        """
        Get 8-K current event filings.

        Args:
            ticker_or_cik: Stock ticker or CIK number
            max_results: Maximum filings to return

        Returns:
            SECSearchResult with 8-K filings
        """
        return self.get_filings(ticker_or_cik, form_type="8-K", max_results=max_results)

    def get_insider_filings(self, ticker_or_cik: str, max_results: int = 50) -> SECSearchResult:
        """
        Get insider trading filings (Form 4).

        Args:
            ticker_or_cik: Stock ticker or CIK number
            max_results: Maximum filings to return

        Returns:
            SECSearchResult with Form 4 filings
        """
        return self.get_filings(ticker_or_cik, form_type="4", max_results=max_results)

    def get_filing_content(self, filing_url: str, as_text: bool = True) -> Optional[str]:
        """
        Download filing content.

        Args:
            filing_url: URL to the filing document
            as_text: Return as text (otherwise bytes)

        Returns:
            Filing content or None on error
        """
        try:
            self._rate_limit()

            response = self._session.get(filing_url, timeout=self.timeout)
            response.raise_for_status()

            with self._lock:
                self._total_queries += 1

            if as_text:
                return response.text
            return response.content

        except RequestsTimeout:
            logger.warning(
                f"SEC filing download timeout for {filing_url} (timeout={self.timeout}s)"
            )
            return None
        except RequestsConnectionError as e:
            logger.warning(f"SEC filing download connection error for {filing_url}: {e}")
            return None
        except HTTPError as e:
            status = e.response.status_code if e.response is not None else "unknown"
            logger.error(f"SEC filing download HTTP error for {filing_url}: {status}")
            return None
        except RequestException as e:
            logger.error(f"SEC filing download request error for {filing_url}: {e}")
            return None
        except Exception as e:
            logger.error(
                f"SEC filing download unexpected error for {filing_url}: {type(e).__name__}: {e}"
            )
            return None

    def full_text_search(
        self,
        query: str,
        form_types: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        max_results: int = 20,
    ) -> SECSearchResult:
        """
        Full-text search across all SEC filings.

        Args:
            query: Search query
            form_types: List of form types to search
            start_date: Filter after date (YYYY-MM-DD)
            end_date: Filter before date (YYYY-MM-DD)
            max_results: Maximum results

        Returns:
            SECSearchResult with matching filings
        """
        try:
            self._rate_limit()

            # Build search query
            params = {
                "q": query,
                "dateRange": "custom",
                "startdt": start_date or "2000-01-01",
                "enddt": end_date or utc_now().strftime("%Y-%m-%d"),
            }

            if form_types:
                params["forms"] = ",".join(form_types)

            url = "https://efts.sec.gov/LATEST/search-index"
            response = self._session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            filings = []
            hits = data.get("hits", {}).get("hits", [])

            for hit in hits[:max_results]:
                source = hit.get("_source", {})

                filings.append(
                    SECFiling(
                        accession_number=source.get("adsh", ""),
                        form_type=source.get("form", ""),
                        filing_date=source.get("file_date", ""),
                        description=(
                            source.get("display_names", [""])[0]
                            if source.get("display_names")
                            else ""
                        ),
                    )
                )

            with self._lock:
                self._total_queries += 1

            return SECSearchResult(query=query, filings=filings, success=True)

        except RequestsTimeout:
            logger.warning(f"SEC full-text search timeout for '{query}' (timeout={self.timeout}s)")
            return SECSearchResult(query=query, success=False, error=ERR_REQUEST_TIMEOUT)
        except RequestsConnectionError as e:
            logger.warning(f"SEC full-text search connection error for '{query}': {e}")
            return SECSearchResult(query=query, success=False, error=f"Connection error: {e}")
        except HTTPError as e:
            status = e.response.status_code if e.response is not None else "unknown"
            logger.error(f"SEC full-text search HTTP error for '{query}': {status}")
            return SECSearchResult(query=query, success=False, error=f"HTTP {status}")
        except json.JSONDecodeError as e:
            logger.error(f"SEC full-text search invalid JSON response for '{query}': {e}")
            return SECSearchResult(query=query, success=False, error=ERR_INVALID_JSON)
        except RequestException as e:
            logger.error(f"SEC full-text search request error for '{query}': {e}")
            return SECSearchResult(query=query, success=False, error=str(e))
        except Exception as e:
            logger.error(
                f"SEC full-text search unexpected error for '{query}': {type(e).__name__}: {e}"
            )
            return SECSearchResult(query=query, success=False, error=str(e))

    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        with self._lock:
            return {
                "total_queries": self._total_queries,
                "cached_tickers": len(self._cik_cache),
                "cost": 0.0,  # FREE!
            }

    def reset_stats(self) -> None:
        """Reset statistics."""
        with self._lock:
            self._total_queries = 0


# Singleton instance
_sec_edgar: Optional[SECEdgarClient] = None
_edgar_lock = Lock()


def get_sec_edgar(user_agent: str = DEFAULT_USER_AGENT) -> SECEdgarClient:
    """Get singleton SEC EDGAR instance."""
    global _sec_edgar
    if _sec_edgar is None:
        with _edgar_lock:
            if _sec_edgar is None:
                _sec_edgar = SECEdgarClient(user_agent=user_agent)
    return _sec_edgar


def reset_sec_edgar() -> None:
    """Reset SEC EDGAR instance."""
    global _sec_edgar
    _sec_edgar = None


# Convenience functions
def get_company_filings(
    ticker: str, form_type: str = "10-K", max_results: int = 5
) -> List[Dict[str, Any]]:
    """Quick function to get company filings."""
    edgar = get_sec_edgar()
    result = edgar.get_filings(ticker, form_type=form_type, max_results=max_results)
    return [f.to_dict() for f in result.filings] if result.success else []


def search_sec_filings(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Quick function to search SEC filings."""
    edgar = get_sec_edgar()
    result = edgar.full_text_search(query, max_results=max_results)
    return [f.to_dict() for f in result.filings] if result.success else []
