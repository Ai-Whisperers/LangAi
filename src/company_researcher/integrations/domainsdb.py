"""
Domainsdb.info API Client.

FREE - No API key required
Provides: Domain search across 260M+ registered domains

Documentation: https://api.domainsdb.info/v1/
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

from ..utils import get_logger
from .base_client import BaseAPIClient

logger = get_logger(__name__)


@dataclass
class DomainInfo:
    """Domain information."""

    domain: str
    create_date: Optional[str]
    update_date: Optional[str]
    country: Optional[str]
    is_dead: bool
    a_record: Optional[List[str]]
    ns_record: Optional[List[str]]
    cname_record: Optional[List[str]]
    mx_record: Optional[List[str]]
    txt_record: Optional[List[str]]

    @classmethod
    def from_dict(cls, data: Dict) -> "DomainInfo":
        return cls(
            domain=data.get("domain", ""),
            create_date=data.get("create_date"),
            update_date=data.get("update_date"),
            country=data.get("country"),
            is_dead=data.get("isDead", False),
            a_record=data.get("A"),
            ns_record=data.get("NS"),
            cname_record=data.get("CNAME"),
            mx_record=data.get("MX"),
            txt_record=data.get("TXT"),
        )


class DomainsDBClient(BaseAPIClient):
    """
    Domainsdb.info API Client.

    FREE - No API key required!
    Database: 260M+ domains, 1000+ TLDs
    Max results: 100 per query

    Features:
    - Search domains by keyword
    - Filter by TLD (com, net, org, io, etc.)
    - Get DNS records
    - Find related domains
    """

    BASE_URL = "https://api.domainsdb.info/v1"

    def __init__(self):
        # No API key needed - it's free!
        super().__init__(
            api_key="free",  # Placeholder
            cache_ttl=3600,  # 1 hour cache
            rate_limit_calls=10,
            rate_limit_period=1.0,  # Be nice to free API
        )

    def is_available(self) -> bool:
        """Always available - no API key needed."""
        return True

    async def search_domains(
        self,
        query: str,
        zone: str = "com",
        page: int = 1,
        limit: int = 50,
        is_dead: Optional[bool] = None,
    ) -> List[DomainInfo]:
        """
        Search for domains containing query string.

        Args:
            query: Search term (e.g., company name)
            zone: TLD to search (com, net, org, io, co, ai, etc.)
            page: Pagination page number
            limit: Results per page (max 100)
            is_dead: Filter by domain status

        Returns:
            List of DomainInfo objects

        Example:
            # Find all domains containing "techcorp" with .com TLD
            results = await client.search_domains("techcorp", zone="com")
        """
        params = {"domain": query, "zone": zone, "page": page, "limit": min(limit, 100)}

        if is_dead is not None:
            params["isDead"] = str(is_dead).lower()

        data = await self._request("domains/search", params)
        domains = data.get("domains", []) if data else []
        return [DomainInfo.from_dict(d) for d in domains]

    async def find_related_domains(
        self, company_name: str, zones: Optional[List[str]] = None
    ) -> Dict[str, List[DomainInfo]]:
        """
        Find all related domains across popular TLDs.

        Args:
            company_name: Company or brand name
            zones: TLDs to search (defaults to common ones)

        Returns:
            Dict mapping zone to list of matching domains
        """
        zones = zones or ["com", "net", "org", "io", "co", "ai", "app"]
        results = {}

        for zone in zones:
            try:
                domains = await self.search_domains(company_name, zone=zone, limit=20)
                if domains:
                    results[zone] = domains
            except Exception as e:
                logger.warning(f"Error searching {zone}: {e}")

        return results

    async def find_company_domains(
        self, company_name: str, include_variations: bool = True
    ) -> List[DomainInfo]:
        """
        Find domains that might belong to a company.

        Args:
            company_name: Company name
            include_variations: Include common variations

        Returns:
            List of potential company domains
        """
        # Clean company name
        clean_name = company_name.lower().replace(" ", "").replace(",", "").replace(".", "")

        # Search variations
        search_terms = [clean_name]
        if include_variations:
            # Add variations
            words = company_name.lower().split()
            if len(words) > 1:
                search_terms.append(words[0])  # First word
                search_terms.append("".join(w[0] for w in words))  # Acronym

        all_domains = []
        seen = set()

        for term in search_terms:
            if len(term) < 3:  # Skip very short terms
                continue

            domains = await self.search_domains(term, zone="com", limit=30)
            for domain in domains:
                if domain.domain not in seen:
                    seen.add(domain.domain)
                    all_domains.append(domain)

        return all_domains

    async def check_domain_availability(self, domain_name: str) -> Dict[str, bool]:
        """
        Check if a domain name is available across TLDs.

        Note: This checks if it's in the database (registered).
        Absence doesn't guarantee availability.

        Args:
            domain_name: Domain name without TLD

        Returns:
            Dict mapping TLD to registered status
        """
        zones = ["com", "net", "org", "io", "co", "ai"]
        availability = {}

        for zone in zones:
            domains = await self.search_domains(domain_name, zone=zone, limit=10)

            # Check for exact match
            exact_match = f"{domain_name}.{zone}"
            is_registered = any(d.domain == exact_match for d in domains)
            availability[zone] = is_registered

        return availability

    async def get_competitor_domains(
        self, company_domain: str, limit: int = 20
    ) -> List[DomainInfo]:
        """
        Find similar/competitor domains.

        Args:
            company_domain: Your company's domain
            limit: Max results

        Returns:
            List of similar domains
        """
        # Extract name from domain
        name = company_domain.split(".")[0]

        # Search for similar
        domains = await self.search_domains(name, zone="com", limit=limit + 5)

        # Filter out the original domain
        return [d for d in domains if d.domain != company_domain][:limit]
