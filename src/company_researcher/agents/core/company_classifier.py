"""
Company Classifier - Detect company type, ticker, and route to data sources.

Features:
- Public vs Private detection
- Stock ticker symbol lookup
- Region detection (US, LATAM, EU, APAC)
- Smart routing to appropriate data sources

Data Source Hierarchy:
- US Public: SEC EDGAR → FMP → Finnhub → Yahoo Finance
- LATAM: Wikipedia → Google News (ES/PT) → Yahoo Finance
- EU/APAC: Wikipedia → Yahoo Finance → Regional sources
- Private: Wikipedia → Google News → Web Search
"""

import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from enum import Enum

logger = logging.getLogger(__name__)


class CompanyType(str, Enum):
    """Type of company entity."""
    PUBLIC = "public"
    PRIVATE = "private"
    SUBSIDIARY = "subsidiary"
    GOVERNMENT = "government"
    NONPROFIT = "nonprofit"
    UNKNOWN = "unknown"


class Region(str, Enum):
    """Geographic regions."""
    NORTH_AMERICA = "north_america"
    LATIN_AMERICA = "latin_america"
    EUROPE = "europe"
    ASIA_PACIFIC = "asia_pacific"
    MIDDLE_EAST = "middle_east"
    AFRICA = "africa"
    GLOBAL = "global"


@dataclass
class CompanyClassification:
    """Result of company classification."""
    company_name: str
    is_public: bool = False
    ticker: Optional[str] = None
    exchange: Optional[str] = None
    cik: Optional[str] = None  # SEC CIK for US companies
    isin: Optional[str] = None  # International Securities ID
    region: Region = Region.GLOBAL
    country: Optional[str] = None
    company_type: CompanyType = CompanyType.UNKNOWN
    industry: Optional[str] = None
    sector: Optional[str] = None
    data_sources: List[str] = field(default_factory=list)
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "company_name": self.company_name,
            "is_public": self.is_public,
            "ticker": self.ticker,
            "exchange": self.exchange,
            "cik": self.cik,
            "isin": self.isin,
            "region": self.region.value,
            "country": self.country,
            "company_type": self.company_type.value,
            "industry": self.industry,
            "sector": self.sector,
            "data_sources": self.data_sources,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }


# Stock exchanges by region
STOCK_EXCHANGES: Dict[Region, List[str]] = {
    Region.NORTH_AMERICA: ["NYSE", "NASDAQ", "TSX", "BMV", "AMEX"],
    Region.LATIN_AMERICA: ["B3", "BVSP", "BVC", "BCS", "BYMA", "BVL"],
    Region.EUROPE: ["LSE", "FRA", "XETRA", "EPA", "AMS", "SWX", "BME", "MIL"],
    Region.ASIA_PACIFIC: ["TSE", "HKEX", "SSE", "SZSE", "NSE", "BSE", "ASX", "KRX", "SGX"],
    Region.MIDDLE_EAST: ["TADAWUL", "DFM", "ADX", "TASE", "EGX"],
}

# Company suffixes by region
COMPANY_SUFFIXES: Dict[Region, List[str]] = {
    Region.NORTH_AMERICA: ["Inc.", "Inc", "Corp.", "Corp", "Corporation", "LLC", "LP", "Co."],
    Region.LATIN_AMERICA: ["S.A.", "SA", "S.A.B.", "SAPI", "S. de R.L.", "Ltda.", "Cia."],
    Region.EUROPE: ["PLC", "plc", "AG", "GmbH", "SE", "N.V.", "B.V.", "S.p.A.", "SARL", "SAS", "AB"],
    Region.ASIA_PACIFIC: ["Ltd", "Limited", "KK", "Pty", "Bhd", "Pte", "Co., Ltd."],
}

# Known LATAM conglomerates (for quick detection)
LATAM_CONGLOMERATES = [
    "GRUPO", "CEMEX", "FEMSA", "BIMBO", "TELEVISA", "PETROBRAS", "VALE",
    "ITAU", "BRADESCO", "AMBEV", "FALABELLA", "CENCOSUD", "COPEC", "CMPC",
    "ARCOR", "TECHINT", "ODEBRECHT", "CAMARGO", "ANDRADE", "JBS", "BRF",
    "GERDAU", "SUZANO", "EMBRAER", "WEG", "NATURA", "GLOBO", "VOTORANTIM",
    "LUKSIC", "MATTE", "ANGELINI", "SAIEH", "GILINSKI", "SANTO DOMINGO",
    "CARSO", "SLIM", "SALINAS", "ALFA", "GRUMA", "SORIANA", "ELEKTRA",
]

# Country to region mapping
COUNTRY_REGION_MAP = {
    # North America
    "US": Region.NORTH_AMERICA, "USA": Region.NORTH_AMERICA,
    "CA": Region.NORTH_AMERICA, "MX": Region.NORTH_AMERICA,
    # Latin America
    "BR": Region.LATIN_AMERICA, "AR": Region.LATIN_AMERICA,
    "CL": Region.LATIN_AMERICA, "CO": Region.LATIN_AMERICA,
    "PE": Region.LATIN_AMERICA, "VE": Region.LATIN_AMERICA,
    "EC": Region.LATIN_AMERICA, "UY": Region.LATIN_AMERICA,
    "PY": Region.LATIN_AMERICA, "BO": Region.LATIN_AMERICA,
    "CR": Region.LATIN_AMERICA, "PA": Region.LATIN_AMERICA,
    "GT": Region.LATIN_AMERICA, "HN": Region.LATIN_AMERICA,
    "SV": Region.LATIN_AMERICA, "NI": Region.LATIN_AMERICA,
    # Europe
    "GB": Region.EUROPE, "UK": Region.EUROPE,
    "DE": Region.EUROPE, "FR": Region.EUROPE,
    "ES": Region.EUROPE, "IT": Region.EUROPE,
    "NL": Region.EUROPE, "CH": Region.EUROPE,
    "SE": Region.EUROPE, "NO": Region.EUROPE,
    "DK": Region.EUROPE, "FI": Region.EUROPE,
    "BE": Region.EUROPE, "AT": Region.EUROPE,
    "PT": Region.EUROPE, "IE": Region.EUROPE,
    "PL": Region.EUROPE,
    # Asia Pacific
    "JP": Region.ASIA_PACIFIC, "CN": Region.ASIA_PACIFIC,
    "HK": Region.ASIA_PACIFIC, "IN": Region.ASIA_PACIFIC,
    "KR": Region.ASIA_PACIFIC, "SG": Region.ASIA_PACIFIC,
    "AU": Region.ASIA_PACIFIC, "NZ": Region.ASIA_PACIFIC,
    "TW": Region.ASIA_PACIFIC, "TH": Region.ASIA_PACIFIC,
    "ID": Region.ASIA_PACIFIC, "MY": Region.ASIA_PACIFIC,
    "PH": Region.ASIA_PACIFIC, "VN": Region.ASIA_PACIFIC,
    # Middle East
    "SA": Region.MIDDLE_EAST, "AE": Region.MIDDLE_EAST,
    "IL": Region.MIDDLE_EAST, "EG": Region.MIDDLE_EAST,
    "QA": Region.MIDDLE_EAST, "KW": Region.MIDDLE_EAST,
}


class CompanyClassifier:
    """
    Classifies companies and determines appropriate data sources.

    Uses multiple sources for classification:
    1. SEC EDGAR (FREE) - US public companies
    2. Wikipedia (FREE) - Company info, exchange, country
    3. FMP (if configured) - Ticker search
    4. Name pattern matching - Region/type detection
    """

    def __init__(self):
        """Initialize classifier with available integrations."""
        self._sec_edgar = None
        self._wikipedia = None
        self._fmp = None
        self._init_integrations()

    def _init_integrations(self):
        """Initialize available integrations."""
        # SEC EDGAR (FREE)
        try:
            from ...integrations.sec_edgar import get_sec_edgar
            self._sec_edgar = get_sec_edgar()
            logger.info("SEC EDGAR integration available")
        except ImportError:
            logger.debug("SEC EDGAR not available")

        # Wikipedia (FREE)
        try:
            from ...integrations.wikipedia_client import get_wikipedia_client
            self._wikipedia = get_wikipedia_client()
            logger.info("Wikipedia integration available")
        except ImportError:
            logger.debug("Wikipedia not available")

        # FMP (requires API key)
        try:
            from ...integrations.financial_modeling_prep import FMPClient
            from ...config import get_config
            config = get_config()
            if config.fmp_api_key:
                self._fmp = FMPClient(api_key=config.fmp_api_key)
                logger.info("FMP integration available")
        except (ImportError, Exception):
            logger.debug("FMP not available")

    def classify(self, company_name: str) -> CompanyClassification:
        """
        Classify a company and determine data sources.

        Args:
            company_name: Name of the company

        Returns:
            CompanyClassification with full details
        """
        result = CompanyClassification(company_name=company_name)

        logger.info(f"Classifying company: {company_name}")

        # Step 1: Try SEC EDGAR (best for US public companies)
        if self._sec_edgar:
            self._check_sec_edgar(company_name, result)

        # Step 2: Try Wikipedia (free, good for general info)
        if self._wikipedia and result.confidence < 0.8:
            self._check_wikipedia(company_name, result)

        # Step 3: Try FMP ticker search (if configured)
        if self._fmp and not result.ticker and result.confidence < 0.8:
            self._check_fmp(company_name, result)

        # Step 4: Pattern matching from company name
        if result.region == Region.GLOBAL:
            result.region = self._detect_region_from_name(company_name)

        if result.company_type == CompanyType.UNKNOWN:
            result.company_type = CompanyType.PUBLIC if result.is_public else CompanyType.PRIVATE

        # Step 5: Determine data sources
        self._determine_data_sources(result)

        logger.info(
            f"Classification: public={result.is_public}, "
            f"ticker={result.ticker}, region={result.region.value}, "
            f"confidence={result.confidence:.0%}"
        )

        return result

    def _check_sec_edgar(self, company_name: str, result: CompanyClassification):
        """Check SEC EDGAR for US public company."""
        try:
            sec_result = self._sec_edgar.search_company(company_name, max_results=1)

            if sec_result.success and sec_result.companies:
                company = sec_result.companies[0]
                result.is_public = True
                result.ticker = company.ticker
                result.cik = company.cik
                result.exchange = "NYSE/NASDAQ"
                result.region = Region.NORTH_AMERICA
                result.country = "US"
                result.company_type = CompanyType.PUBLIC
                result.industry = company.sic_description
                result.confidence = 0.95
                result.metadata["sec_name"] = company.name
                result.metadata["sic"] = company.sic

                logger.info(f"SEC match: {company.name} (CIK: {company.cik})")
        except Exception as e:
            logger.debug(f"SEC EDGAR check failed: {e}")

    def _check_wikipedia(self, company_name: str, result: CompanyClassification):
        """Check Wikipedia for company info."""
        try:
            wiki_result = self._wikipedia.get_company_info(company_name)

            if wiki_result:
                infobox = wiki_result.infobox or {}

                # Check for traded/listed info
                traded = infobox.get("traded", "") or infobox.get("listed", "")
                if traded:
                    result.is_public = True
                    result.company_type = CompanyType.PUBLIC

                    # Parse exchange
                    for region, exchanges in STOCK_EXCHANGES.items():
                        for exchange in exchanges:
                            if exchange.upper() in traded.upper():
                                result.exchange = exchange
                                result.region = region
                                break

                # Get ticker
                ticker = infobox.get("symbol", "") or infobox.get("ticker_symbol", "")
                if ticker and not result.ticker:
                    result.ticker = ticker.split()[0] if ticker else None

                # Get country/HQ
                hq = infobox.get("headquarters", "") or infobox.get("location", "")
                if hq:
                    result.country = self._extract_country(hq)
                    if result.region == Region.GLOBAL and result.country:
                        result.region = COUNTRY_REGION_MAP.get(result.country, Region.GLOBAL)

                # Get industry
                result.industry = infobox.get("industry")
                result.sector = infobox.get("products") or infobox.get("services")

                result.confidence = max(result.confidence, 0.75 if result.is_public else 0.6)
                result.metadata["wikipedia_summary"] = wiki_result.summary[:500] if wiki_result.summary else None

                logger.info(f"Wikipedia match: exchange={result.exchange}, country={result.country}")
        except Exception as e:
            logger.debug(f"Wikipedia check failed: {e}")

    def _check_fmp(self, company_name: str, result: CompanyClassification):
        """Check FMP for ticker symbol."""
        try:
            search_results = self._fmp.search_ticker(company_name)

            if search_results:
                best = search_results[0]
                result.is_public = True
                result.ticker = best.get("symbol")
                result.exchange = best.get("exchange")
                result.company_type = CompanyType.PUBLIC
                result.confidence = max(result.confidence, 0.85)

                logger.info(f"FMP match: {result.ticker} on {result.exchange}")
        except Exception as e:
            logger.debug(f"FMP check failed: {e}")

    def _detect_region_from_name(self, company_name: str) -> Region:
        """Detect region from company name patterns."""
        name_upper = company_name.upper()

        # Check for LATAM conglomerates
        for keyword in LATAM_CONGLOMERATES:
            if keyword in name_upper:
                return Region.LATIN_AMERICA

        # Check for region-specific suffixes
        for region, suffixes in COMPANY_SUFFIXES.items():
            for suffix in suffixes:
                if suffix.upper() in name_upper:
                    return region

        return Region.GLOBAL

    def _extract_country(self, location: str) -> Optional[str]:
        """Extract country code from location string."""
        if not location:
            return None

        location_upper = location.upper()

        country_patterns = {
            "UNITED STATES": "US", "U.S.": "US", "USA": "US", "AMERICA": "US",
            "BRAZIL": "BR", "BRASIL": "BR",
            "MEXICO": "MX", "MÉXICO": "MX",
            "ARGENTINA": "AR", "CHILE": "CL", "COLOMBIA": "CO", "PERU": "PE",
            "UNITED KINGDOM": "GB", "UK": "GB", "ENGLAND": "GB",
            "GERMANY": "DE", "DEUTSCHLAND": "DE",
            "FRANCE": "FR", "SPAIN": "ES", "ESPAÑA": "ES",
            "ITALY": "IT", "ITALIA": "IT",
            "NETHERLANDS": "NL", "SWITZERLAND": "CH",
            "JAPAN": "JP", "CHINA": "CN", "HONG KONG": "HK",
            "INDIA": "IN", "AUSTRALIA": "AU",
            "SOUTH KOREA": "KR", "KOREA": "KR",
            "SINGAPORE": "SG", "TAIWAN": "TW",
        }

        for pattern, code in country_patterns.items():
            if pattern in location_upper:
                return code

        return None

    def _determine_data_sources(self, result: CompanyClassification):
        """Determine appropriate data sources based on classification."""
        sources = []

        # Always available free sources
        sources.extend(["google_news", "wikipedia", "tavily"])

        if result.is_public:
            # Public company sources
            sources.append("yfinance")

            if result.region == Region.NORTH_AMERICA:
                sources.extend(["sec_edgar", "fmp", "finnhub"])

            if result.ticker:
                sources.extend(["polygon", "alpha_vantage"])

        if result.region == Region.LATIN_AMERICA:
            sources.extend(["google_news_es", "google_news_pt"])

        # Deduplicate
        result.data_sources = list(dict.fromkeys(sources))


# Singleton
_classifier: Optional[CompanyClassifier] = None


def get_company_classifier() -> CompanyClassifier:
    """Get singleton company classifier."""
    global _classifier
    if _classifier is None:
        _classifier = CompanyClassifier()
    return _classifier


def classify_company(company_name: str) -> CompanyClassification:
    """Quick function to classify a company."""
    return get_company_classifier().classify(company_name)


# For workflow integration
def classify_company_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node to classify company at workflow start (with caching).

    Classification results are cached for 30 days since company metadata
    rarely changes (public status, ticker, region).

    Args:
        state: Workflow state with company_name

    Returns:
        State update with classification results
    """
    company_name = state.get("company_name", "")

    print(f"\n[NODE] Classifying company: {company_name}")

    # Check cache first (30 day TTL)
    try:
        from ...integrations.result_cache import (
            cache_classification,
            get_cached_classification
        )
        cached = get_cached_classification(company_name)
        if cached:
            print(f"  [CACHE HIT] Classification cached for '{company_name}'")
            return {
                "company_classification": cached,
                "is_public_company": cached.get("is_public", False),
                "stock_ticker": cached.get("ticker"),
                "detected_region": cached.get("region", "global"),
                "available_data_sources": cached.get("data_sources", []),
            }
    except ImportError:
        pass  # Cache not available, proceed with classification

    # Classify company
    classifier = get_company_classifier()
    result = classifier.classify(company_name)

    print(f"  [RESULT] Type: {result.company_type.value}, "
          f"Public: {result.is_public}, "
          f"Ticker: {result.ticker}, "
          f"Region: {result.region.value}")
    print(f"  [SOURCES] {', '.join(result.data_sources)}")

    # Cache result for next time (30 days)
    try:
        from ...integrations.result_cache import cache_classification
        cache_classification(company_name, result.to_dict())
        print("  [CACHED] Classification saved for 30 days")
    except ImportError:
        pass

    return {
        "company_classification": result.to_dict(),
        "is_public_company": result.is_public,
        "stock_ticker": result.ticker,
        "detected_region": result.region.value,
        "available_data_sources": result.data_sources,
    }
