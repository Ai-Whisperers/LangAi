"""
Hunter.io Email Finder API Client.

Free tier: 25 searches/month, 50 verifications/month
Provides: Email discovery and verification

Documentation: https://hunter.io/api-documentation
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

from .base_client import BaseAPIClient
from ..utils import get_logger

logger = get_logger(__name__)


@dataclass
class EmailResult:
    """Email search result."""
    email: str
    first_name: str
    last_name: str
    position: str
    department: str
    linkedin: Optional[str]
    twitter: Optional[str]
    phone: Optional[str]
    confidence: int
    sources: List[Dict]

    @classmethod
    def from_dict(cls, data: Dict) -> "EmailResult":
        return cls(
            email=data.get("value", data.get("email", "")),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            position=data.get("position", ""),
            department=data.get("department", ""),
            linkedin=data.get("linkedin"),
            twitter=data.get("twitter"),
            phone=data.get("phone_number"),
            confidence=data.get("confidence", 0),
            sources=data.get("sources", [])
        )


@dataclass
class DomainSearchResult:
    """Domain search result."""
    domain: str
    organization: str
    emails: List[EmailResult]
    total_emails: int
    webmail: bool
    pattern: Optional[str]

    @classmethod
    def from_dict(cls, data: Dict) -> "DomainSearchResult":
        emails = [EmailResult.from_dict(e) for e in data.get("emails", [])]
        return cls(
            domain=data.get("domain", ""),
            organization=data.get("organization", ""),
            emails=emails,
            total_emails=data.get("emails_count", len(emails)),
            webmail=data.get("webmail", False),
            pattern=data.get("pattern")
        )


@dataclass
class EmailVerification:
    """Email verification result."""
    email: str
    result: str
    score: int
    regexp: bool
    gibberish: bool
    disposable: bool
    webmail: bool
    mx_records: bool
    smtp_server: bool
    smtp_check: bool
    accept_all: bool
    block: bool
    sources: List[Dict]

    @classmethod
    def from_dict(cls, data: Dict) -> "EmailVerification":
        return cls(
            email=data.get("email", ""),
            result=data.get("result", "unknown"),
            score=data.get("score", 0),
            regexp=data.get("regexp", False),
            gibberish=data.get("gibberish", False),
            disposable=data.get("disposable", False),
            webmail=data.get("webmail", False),
            mx_records=data.get("mx_records", False),
            smtp_server=data.get("smtp_server", False),
            smtp_check=data.get("smtp_check", False),
            accept_all=data.get("accept_all", False),
            block=data.get("block", False),
            sources=data.get("sources", [])
        )


class HunterClient(BaseAPIClient):
    """
    Hunter.io Email Finder API Client.

    Free tier: 25 searches/month, 50 verifications/month
    Starter: $34/mo (500 searches)
    Growth: $104/mo (5,000 searches)

    Features:
    - Domain search (find all emails at a domain)
    - Email finder (find specific person's email)
    - Email verifier (check if email is valid)
    """

    BASE_URL = "https://api.hunter.io/v2"

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            api_key=api_key,
            env_var="HUNTER_API_KEY",
            cache_ttl=86400,  # 24 hour cache (data doesn't change often)
            rate_limit_calls=10,
            rate_limit_period=1.0
        )

    async def _request(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        **kwargs
    ):
        """Override to add API key and handle response format."""
        params = params or {}
        params["api_key"] = self.api_key
        data = await super()._request(endpoint, params, **kwargs)
        return data.get("data", data) if data else None

    async def domain_search(
        self,
        domain: str,
        department: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> Optional[DomainSearchResult]:
        """
        Find all emails associated with a domain.

        Args:
            domain: Company domain (e.g., "stripe.com")
            department: Filter by department (executive, it, finance, etc.)
            limit: Max emails to return
            offset: Pagination offset

        Returns:
            DomainSearchResult or None

        Departments:
            - executive, it, finance, management
            - sales, legal, support, hr, marketing, communication
        """
        params = {
            "domain": domain,
            "limit": limit,
            "offset": offset
        }

        if department:
            params["department"] = department

        data = await self._request("domain-search", params)
        if data:
            return DomainSearchResult.from_dict(data)
        return None

    async def email_finder(
        self,
        domain: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        full_name: Optional[str] = None
    ) -> Optional[EmailResult]:
        """
        Find a specific person's email.

        Args:
            domain: Company domain
            first_name: Person's first name
            last_name: Person's last name
            full_name: Full name (alternative to first/last)

        Returns:
            EmailResult or None
        """
        params = {"domain": domain}

        if full_name:
            params["full_name"] = full_name
        else:
            if first_name:
                params["first_name"] = first_name
            if last_name:
                params["last_name"] = last_name

        data = await self._request("email-finder", params)
        if data:
            return EmailResult.from_dict(data)
        return None

    async def email_verifier(self, email: str) -> Optional[EmailVerification]:
        """
        Verify if an email is valid and deliverable.

        Args:
            email: Email address to verify

        Returns:
            EmailVerification with validity scores

        Result values:
            - deliverable: Email is valid
            - undeliverable: Email is invalid
            - risky: Email might bounce
            - unknown: Could not determine
        """
        data = await self._request("email-verifier", {"email": email})
        if data:
            return EmailVerification.from_dict(data)
        return None

    async def email_count(self, domain: str) -> Dict:
        """
        Get email count for a domain (doesn't use credits).

        Args:
            domain: Company domain

        Returns:
            Dict with total, personal_emails, generic_emails, department counts
        """
        return await self._request("email-count", {"domain": domain}) or {}

    async def get_executive_emails(
        self,
        domain: str,
        limit: int = 5
    ) -> Optional[DomainSearchResult]:
        """
        Get executive/leadership emails.

        Args:
            domain: Company domain
            limit: Max results

        Returns:
            DomainSearchResult with executive emails
        """
        return await self.domain_search(domain, department="executive", limit=limit)

    async def find_decision_makers(
        self,
        domain: str,
        limit: int = 10
    ) -> List[EmailResult]:
        """
        Find decision-maker contacts (executives, management, sales).

        Args:
            domain: Company domain
            limit: Max contacts per department

        Returns:
            List of EmailResult objects
        """
        contacts = []

        for dept in ["executive", "management", "sales"]:
            result = await self.domain_search(
                domain,
                department=dept,
                limit=limit // 3
            )
            if result:
                contacts.extend(result.emails)

        # Sort by confidence and deduplicate
        seen = set()
        unique = []
        for contact in sorted(contacts, key=lambda x: x.confidence, reverse=True):
            if contact.email not in seen:
                seen.add(contact.email)
                unique.append(contact)

        return unique[:limit]
