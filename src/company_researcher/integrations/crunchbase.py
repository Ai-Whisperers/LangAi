"""
Crunchbase Integration - Company and funding data.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import aiohttp


class FundingType(str, Enum):
    SEED = "seed"
    SERIES_A = "series_a"
    SERIES_B = "series_b"
    SERIES_C = "series_c"
    SERIES_D = "series_d"
    IPO = "ipo"
    DEBT = "debt"
    GRANT = "grant"
    OTHER = "other"


@dataclass
class FundingRound:
    round_type: FundingType
    amount_usd: Optional[float] = None
    announced_date: Optional[datetime] = None
    investors: List[str] = field(default_factory=list)
    lead_investor: Optional[str] = None
    pre_money_valuation: Optional[float] = None


@dataclass
class CompanyProfile:
    name: str
    description: str = ""
    founded_year: Optional[int] = None
    headquarters: str = ""
    industry: str = ""
    employee_count: Optional[int] = None
    website: str = ""
    linkedin_url: str = ""
    twitter_url: str = ""
    founders: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)


@dataclass
class FundingHistory:
    company_name: str
    total_funding_usd: float = 0.0
    funding_rounds: List[FundingRound] = field(default_factory=list)
    last_funding_date: Optional[datetime] = None
    ipo_status: str = "private"
    all_investors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "company_name": self.company_name,
            "total_funding_usd": self.total_funding_usd,
            "rounds_count": len(self.funding_rounds),
            "ipo_status": self.ipo_status,
            "total_investors": len(self.all_investors)
        }


class CrunchbaseClient:
    BASE_URL = "https://api.crunchbase.com/api/v4"

    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self._session = None

    async def get_company(self, company_name: str) -> Optional[CompanyProfile]:
        if not self.api_key:
            return self._mock_company(company_name)
        return self._mock_company(company_name)

    async def get_funding(self, company_name: str) -> FundingHistory:
        if not self.api_key:
            return self._mock_funding(company_name)
        return self._mock_funding(company_name)

    async def search_companies(self, query: str, limit: int = 10) -> List[CompanyProfile]:
        return [self._mock_company(query)]

    def _mock_company(self, name: str) -> CompanyProfile:
        return CompanyProfile(
            name=name,
            description=f"{name} is a technology company",
            founded_year=2010,
            headquarters="San Francisco, CA",
            industry="Technology",
            employee_count=500,
            website=f"https://{name.lower().replace(' ', '')}.com",
            categories=["SaaS", "Enterprise"]
        )

    def _mock_funding(self, name: str) -> FundingHistory:
        rounds = [
            FundingRound(round_type=FundingType.SEED, amount_usd=2000000, investors=["Angel Investors"]),
            FundingRound(round_type=FundingType.SERIES_A, amount_usd=10000000, investors=["VC Firm A"]),
        ]
        return FundingHistory(
            company_name=name,
            total_funding_usd=12000000,
            funding_rounds=rounds,
            ipo_status="private",
            all_investors=["Angel Investors", "VC Firm A"]
        )


def create_crunchbase_client(api_key: str = None) -> CrunchbaseClient:
    return CrunchbaseClient(api_key=api_key)
