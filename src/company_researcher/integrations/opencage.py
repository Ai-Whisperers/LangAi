"""
OpenCage Geocoding API Client.

Free tier: 2,500 requests/day
Provides: Forward and reverse geocoding worldwide

Documentation: https://opencagedata.com/api
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

from .base_client import BaseAPIClient
from ..utils import get_logger

logger = get_logger(__name__)


@dataclass
class GeocodingResult:
    """Geocoding result."""
    formatted: str
    latitude: float
    longitude: float
    country: str
    country_code: str
    state: str
    city: str
    postcode: str
    road: str
    confidence: int
    bounds: Dict[str, float]
    timezone: str
    currency: Dict[str, str]

    @classmethod
    def from_dict(cls, data: Dict) -> "GeocodingResult":
        components = data.get("components", {})
        annotations = data.get("annotations", {})
        geometry = data.get("geometry", {})

        return cls(
            formatted=data.get("formatted", ""),
            latitude=geometry.get("lat", 0),
            longitude=geometry.get("lng", 0),
            country=components.get("country", ""),
            country_code=components.get("country_code", ""),
            state=components.get("state", ""),
            city=components.get("city", components.get("town", components.get("village", ""))),
            postcode=components.get("postcode", ""),
            road=components.get("road", ""),
            confidence=data.get("confidence", 0),
            bounds=data.get("bounds", {}),
            timezone=annotations.get("timezone", {}).get("name", ""),
            currency=annotations.get("currency", {})
        )


class OpenCageClient(BaseAPIClient):
    """
    OpenCage Geocoding API Client.

    Free tier: 2,500 requests/day
    Small: $50/mo (10,000/day)
    Medium: $100/mo (25,000/day)

    Features:
    - Forward geocoding (address → coordinates)
    - Reverse geocoding (coordinates → address)
    - Worldwide coverage
    - Rich annotations (timezone, currency, etc.)
    """

    BASE_URL = "https://api.opencagedata.com/geocode/v1"

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            api_key=api_key,
            env_var="OPENCAGE_API_KEY",
            cache_ttl=86400,  # 24 hour cache (addresses don't change)
            rate_limit_calls=1,
            rate_limit_period=1.0  # Free tier: 1/second
        )

    async def geocode(
        self,
        query: str,
        country_code: Optional[str] = None,
        language: str = "en",
        limit: int = 5,
        min_confidence: int = 0
    ) -> List[GeocodingResult]:
        """
        Forward geocoding: address/place name → coordinates.

        Args:
            query: Address or place name
            country_code: ISO country code to restrict results
            language: Response language
            limit: Max results (1-100)
            min_confidence: Minimum confidence level (1-10)

        Returns:
            List of GeocodingResult objects

        Examples:
            - "Av. Paulista 1578, São Paulo, Brazil"
            - "Microsoft headquarters, Redmond"
            - "Eiffel Tower, Paris"
        """
        params = {
            "q": query,
            "key": self.api_key,
            "language": language,
            "limit": limit,
            "no_annotations": 0
        }

        if country_code:
            params["countrycode"] = country_code
        if min_confidence > 0:
            params["min_confidence"] = min_confidence

        data = await self._request("json", params)
        results = data.get("results", []) if data else []
        return [GeocodingResult.from_dict(item) for item in results]

    async def reverse_geocode(
        self,
        latitude: float,
        longitude: float,
        language: str = "en"
    ) -> Optional[GeocodingResult]:
        """
        Reverse geocoding: coordinates → address.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            language: Response language

        Returns:
            GeocodingResult or None
        """
        params = {
            "q": f"{latitude},{longitude}",
            "key": self.api_key,
            "language": language,
            "no_annotations": 0
        }

        data = await self._request("json", params)
        results = data.get("results", []) if data else []

        if results:
            return GeocodingResult.from_dict(results[0])
        return None

    async def get_company_location(
        self,
        company_name: str,
        country: Optional[str] = None
    ) -> Optional[GeocodingResult]:
        """
        Get company headquarters location.

        Args:
            company_name: Company name
            country: Country name or code to narrow results

        Returns:
            GeocodingResult or None
        """
        query = f"{company_name} headquarters"
        if country:
            query += f", {country}"

        results = await self.geocode(query, limit=1, min_confidence=3)
        return results[0] if results else None

    async def geocode_address(
        self,
        street: str,
        city: str,
        country: str,
        postcode: Optional[str] = None
    ) -> Optional[GeocodingResult]:
        """
        Geocode a structured address.

        Args:
            street: Street address
            city: City name
            country: Country name or code
            postcode: Postal code (optional)

        Returns:
            GeocodingResult or None
        """
        parts = [street, city]
        if postcode:
            parts.append(postcode)
        parts.append(country)

        query = ", ".join(parts)
        results = await self.geocode(query, limit=1)
        return results[0] if results else None

    async def get_timezone(
        self,
        latitude: float,
        longitude: float
    ) -> Optional[str]:
        """
        Get timezone for coordinates.

        Args:
            latitude: Latitude
            longitude: Longitude

        Returns:
            Timezone name (e.g., "America/New_York")
        """
        result = await self.reverse_geocode(latitude, longitude)
        return result.timezone if result else None
