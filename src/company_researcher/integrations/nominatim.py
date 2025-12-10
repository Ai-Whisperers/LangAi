"""
Nominatim (OpenStreetMap) Geocoding Client.

FREE - No API key required!
Provides: Geocoding using OpenStreetMap data

Documentation: https://nominatim.org/release-docs/latest/api/Overview/

IMPORTANT: Nominatim has a strict usage policy:
- Max 1 request/second
- Provide a valid User-Agent
- For heavy usage, host your own instance
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

from .base_client import BaseAPIClient

logger = logging.getLogger(__name__)


@dataclass
class NominatimResult:
    """Nominatim geocoding result."""
    place_id: int
    osm_type: str
    osm_id: int
    display_name: str
    latitude: float
    longitude: float
    type: str
    importance: float
    address: Dict[str, str]
    boundingbox: List[str]

    @classmethod
    def from_dict(cls, data: Dict) -> "NominatimResult":
        return cls(
            place_id=data.get("place_id", 0),
            osm_type=data.get("osm_type", ""),
            osm_id=data.get("osm_id", 0),
            display_name=data.get("display_name", ""),
            latitude=float(data.get("lat", 0)),
            longitude=float(data.get("lon", 0)),
            type=data.get("type", ""),
            importance=data.get("importance", 0),
            address=data.get("address", {}),
            boundingbox=data.get("boundingbox", [])
        )


class NominatimClient(BaseAPIClient):
    """
    Nominatim (OpenStreetMap) Geocoding Client.

    FREE - No API key required!

    Usage Policy:
    - Max 1 request/second
    - Must provide User-Agent
    - No heavy batch usage
    - Consider self-hosting for production

    Features:
    - Forward geocoding (search)
    - Reverse geocoding
    - Structured search
    - Worldwide coverage via OpenStreetMap
    """

    BASE_URL = "https://nominatim.openstreetmap.org"
    USER_AGENT = "CompanyResearcher/1.0 (https://github.com/company-researcher)"

    def __init__(self):
        # No API key needed - it's free!
        super().__init__(
            api_key="free",  # Placeholder
            cache_ttl=86400,  # 24 hour cache
            rate_limit_calls=1,
            rate_limit_period=1.0  # Strict: 1/second
        )

    def is_available(self) -> bool:
        """Always available - no API key needed."""
        return True

    def _get_headers(self) -> Dict[str, str]:
        """Add required User-Agent header."""
        headers = super()._get_headers()
        headers["User-Agent"] = self.USER_AGENT
        return headers

    async def search(
        self,
        query: str,
        country_codes: Optional[List[str]] = None,
        limit: int = 5,
        addressdetails: bool = True
    ) -> List[NominatimResult]:
        """
        Search for a location (forward geocoding).

        Args:
            query: Search query (address, place name, etc.)
            country_codes: Limit to specific countries (ISO codes)
            limit: Max results (1-50)
            addressdetails: Include address breakdown

        Returns:
            List of NominatimResult objects
        """
        params = {
            "q": query,
            "format": "json",
            "limit": min(limit, 50),
            "addressdetails": 1 if addressdetails else 0
        }

        if country_codes:
            params["countrycodes"] = ",".join(country_codes)

        data = await self._request("search", params)
        return [NominatimResult.from_dict(item) for item in (data or [])]

    async def reverse(
        self,
        latitude: float,
        longitude: float,
        zoom: int = 18,
        addressdetails: bool = True
    ) -> Optional[NominatimResult]:
        """
        Reverse geocode coordinates.

        Args:
            latitude: Latitude
            longitude: Longitude
            zoom: Detail level (3=country, 10=city, 18=building)
            addressdetails: Include address breakdown

        Returns:
            NominatimResult or None
        """
        params = {
            "lat": latitude,
            "lon": longitude,
            "format": "json",
            "zoom": zoom,
            "addressdetails": 1 if addressdetails else 0
        }

        data = await self._request("reverse", params)
        if data and "error" not in data:
            return NominatimResult.from_dict(data)
        return None

    async def structured_search(
        self,
        street: Optional[str] = None,
        city: Optional[str] = None,
        county: Optional[str] = None,
        state: Optional[str] = None,
        country: Optional[str] = None,
        postalcode: Optional[str] = None
    ) -> List[NominatimResult]:
        """
        Search with structured address components.

        Args:
            street: Street address
            city: City name
            county: County/district
            state: State/province
            country: Country name
            postalcode: Postal/ZIP code

        Returns:
            List of NominatimResult objects
        """
        params = {
            "format": "json",
            "addressdetails": 1
        }

        if street:
            params["street"] = street
        if city:
            params["city"] = city
        if county:
            params["county"] = county
        if state:
            params["state"] = state
        if country:
            params["country"] = country
        if postalcode:
            params["postalcode"] = postalcode

        data = await self._request("search", params)
        return [NominatimResult.from_dict(item) for item in (data or [])]

    async def lookup(
        self,
        osm_ids: List[str]
    ) -> List[NominatimResult]:
        """
        Look up OSM objects by ID.

        Args:
            osm_ids: List of OSM IDs (e.g., ["N123", "W456", "R789"])
                     N=node, W=way, R=relation

        Returns:
            List of NominatimResult objects
        """
        params = {
            "osm_ids": ",".join(osm_ids),
            "format": "json",
            "addressdetails": 1
        }

        data = await self._request("lookup", params)
        return [NominatimResult.from_dict(item) for item in (data or [])]

    async def geocode_city(
        self,
        city: str,
        country: Optional[str] = None
    ) -> Optional[NominatimResult]:
        """
        Geocode a city.

        Args:
            city: City name
            country: Country name or code

        Returns:
            NominatimResult or None
        """
        results = await self.structured_search(city=city, country=country)
        return results[0] if results else None

    async def get_country_center(
        self,
        country: str
    ) -> Optional[NominatimResult]:
        """
        Get approximate center of a country.

        Args:
            country: Country name

        Returns:
            NominatimResult or None
        """
        results = await self.structured_search(country=country)
        return results[0] if results else None
