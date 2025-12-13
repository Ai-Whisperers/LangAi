"""
SEC EDGAR Parser for Financial Filings (Phase 7).

Fetches and parses official financial filings from SEC EDGAR database.

SEC EDGAR: https://www.sec.gov/edgar/searchedgar/companysearch.html
API: https://www.sec.gov/edgar/sec-api-documentation

Note: SEC requires User-Agent header with contact info
"""

from typing import Dict, List, Optional, Any
from datetime import timedelta
from ..utils import utc_now


class SECEdgarParser:
    """
    Parser for SEC EDGAR financial filings.

    Fetches and parses:
    - 10-K (Annual reports)
    - 10-Q (Quarterly reports)
    - 8-K (Current reports)
    - Company information
    """

    def __init__(self, user_agent: str = "Company Researcher (contact@example.com)"):
        """
        Initialize SEC EDGAR parser.

        Args:
            user_agent: User-Agent string (SEC requires contact info)
        """
        self.base_url = "https://www.sec.gov"
        self.api_base = f"{self.base_url}/cgi-bin/browse-edgar"
        self.user_agent = user_agent
        self._cache = {}
        self._cache_ttl = timedelta(days=1)  # Cache for 1 day

    def is_available(self) -> bool:
        """
        Check if SEC EDGAR is available.

        SEC EDGAR is always available (no API key needed),
        but has rate limits (10 requests per second).
        """
        return True

    def _make_request(self, **params) -> Dict[str, Any]:
        """
        Make request to SEC EDGAR API.

        Args:
            **params: Query parameters

        Returns:
            Parsed response data
        """
        # Check cache
        cache_key = str(params)
        if cache_key in self._cache:
            cached_data, cached_time = self._cache[cache_key]
            if utc_now() - cached_time < self._cache_ttl:
                return cached_data

        # In production, would make actual HTTP request with requests library
        # headers = {"User-Agent": self.user_agent}
        # response = requests.get(self.api_base, params=params, headers=headers)

        # For now, return mock data
        mock_response = self._get_mock_data(**params)

        # Cache response
        self._cache[cache_key] = (mock_response, utc_now())

        return mock_response

    def _get_mock_data(self, **params) -> Dict[str, Any]:
        """Get mock data for testing."""
        return {
            "note": "Mock SEC EDGAR data. Replace with actual HTTP request.",
            "params": params,
            "timestamp": utc_now().isoformat()
        }

    def search_company(self, company_name: str) -> Optional[Dict[str, Any]]:
        """
        Search for company by name to get CIK (Central Index Key).

        Args:
            company_name: Company name to search

        Returns:
            Company information including CIK or None if not found
        """
        print(f"[SEC EDGAR] Searching for company: {company_name}")

        try:
            # In production, would search SEC's company database
            # For now, return mock data
            return {
                "company_name": company_name,
                "cik": "0000000000",  # Mock CIK
                "note": "Mock data. In production, would search SEC database."
            }
        except Exception as e:
            print(f"[SEC EDGAR] Error searching for {company_name}: {e}")
            return None

    def get_company_filings(
        self,
        cik: str,
        filing_type: str = "10-K",
        count: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get recent filings for a company.

        Args:
            cik: Company's CIK (Central Index Key)
            filing_type: Type of filing (10-K, 10-Q, 8-K, etc.)
            count: Number of filings to return

        Returns:
            List of filing metadata
        """
        print(f"[SEC EDGAR] Fetching {filing_type} filings for CIK {cik}...")

        try:
            params = {
                "action": "getcompany",
                "CIK": cik,
                "type": filing_type,
                "count": count,
                "output": "atom"
            }

            data = self._make_request(**params)

            # In production, would parse XML/JSON response
            return [
                {
                    "filing_type": filing_type,
                    "filing_date": "2024-01-31",
                    "accession_number": "0000000000-00-000000",
                    "url": f"{self.base_url}/Archives/edgar/data/{cik}/...",
                    "note": "Mock filing data"
                }
            ]
        except Exception as e:
            print(f"[SEC EDGAR] Error fetching filings: {e}")
            return []

    def get_latest_10k(self, cik: str) -> Optional[Dict[str, Any]]:
        """
        Get the most recent 10-K (annual report) for a company.

        Args:
            cik: Company's CIK

        Returns:
            10-K filing data or None if not found
        """
        filings = self.get_company_filings(cik, "10-K", count=1)
        return filings[0] if filings else None

    def get_latest_10q(self, cik: str) -> Optional[Dict[str, Any]]:
        """
        Get the most recent 10-Q (quarterly report) for a company.

        Args:
            cik: Company's CIK

        Returns:
            10-Q filing data or None if not found
        """
        filings = self.get_company_filings(cik, "10-Q", count=1)
        return filings[0] if filings else None

    def parse_financial_statement(self, filing_url: str) -> Dict[str, Any]:
        """
        Parse financial statement from filing.

        Extracts key financial metrics from the filing document.

        Args:
            filing_url: URL to the filing document

        Returns:
            Parsed financial data
        """
        print(f"[SEC EDGAR] Parsing financial statement from {filing_url}")

        # In production, would:
        # 1. Fetch the filing HTML/XBRL
        # 2. Parse financial tables
        # 3. Extract key metrics
        # 4. Normalize data

        return {
            "note": "Mock parsed financial data",
            "source": filing_url,
            "revenue": None,
            "net_income": None,
            "assets": None,
            "liabilities": None,
            "equity": None
        }

    def get_company_financials(
        self,
        company_name: str
    ) -> Dict[str, Any]:
        """
        Get comprehensive financial data from SEC filings.

        Workflow:
        1. Search for company to get CIK
        2. Fetch latest 10-K (annual)
        3. Fetch latest 10-Q (quarterly)
        4. Parse financial statements
        5. Extract key metrics

        Args:
            company_name: Name of the company

        Returns:
            Dictionary with financial data from SEC filings
        """
        print(f"[SEC EDGAR] Getting financials for {company_name}...")

        # Search for company
        company_info = self.search_company(company_name)
        if not company_info:
            return {
                "available": False,
                "reason": f"Company '{company_name}' not found in SEC database"
            }

        cik = company_info["cik"]

        # Get latest filings
        latest_10k = self.get_latest_10k(cik)
        latest_10q = self.get_latest_10q(cik)

        # In production, would parse the filings
        financials = {
            "available": True,
            "company_name": company_name,
            "cik": cik,
            "fetched_at": utc_now().isoformat(),
            "latest_10k": latest_10k,
            "latest_10q": latest_10q,
            "annual_financials": None,  # Would be parsed from 10-K
            "quarterly_financials": None,  # Would be parsed from 10-Q
            "note": "Mock data. In production, would parse actual filings."
        }

        print(f"[SEC EDGAR] Financials fetched for {company_name}")

        return financials


# ==============================================================================
# Helper Functions
# ==============================================================================

def extract_revenue_trends(financials: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract revenue trends from SEC filings.

    Args:
        financials: Output from get_company_financials()

    Returns:
        Revenue trend analysis
    """
    if not financials.get("available"):
        return {"available": False}

    # In production, would parse actual financial statements
    # and calculate trends (YoY growth, CAGR, etc.)

    return {
        "available": True,
        "company": financials["company_name"],
        "annual_revenue": [],  # List of (year, revenue) tuples
        "quarterly_revenue": [],  # List of (quarter, revenue) tuples
        "yoy_growth": None,
        "cagr_3_year": None,
        "note": "Mock data. In production, would calculate from actual filings."
    }


def extract_profitability_metrics(financials: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract profitability metrics from SEC filings.

    Args:
        financials: Output from get_company_financials()

    Returns:
        Profitability metrics
    """
    if not financials.get("available"):
        return {"available": False}

    return {
        "available": True,
        "company": financials["company_name"],
        "gross_margin": None,
        "operating_margin": None,
        "net_margin": None,
        "ebitda": None,
        "ebitda_margin": None,
        "note": "Mock data. In production, would calculate from actual filings."
    }


def extract_financial_health(financials: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract financial health indicators from SEC filings.

    Args:
        financials: Output from get_company_financials()

    Returns:
        Financial health metrics
    """
    if not financials.get("available"):
        return {"available": False}

    return {
        "available": True,
        "company": financials["company_name"],
        "cash_and_equivalents": None,
        "total_debt": None,
        "debt_to_equity": None,
        "current_ratio": None,
        "quick_ratio": None,
        "free_cash_flow": None,
        "note": "Mock data. In production, would calculate from actual filings."
    }


def is_public_company(company_name: str) -> bool:
    """
    Check if a company is publicly traded (has SEC filings).

    Args:
        company_name: Name of the company

    Returns:
        True if company has SEC filings (is public), False otherwise
    """
    parser = SECEdgarParser()
    company_info = parser.search_company(company_name)

    # In production, would actually check SEC database
    # For now, return True for mock data
    return company_info is not None
