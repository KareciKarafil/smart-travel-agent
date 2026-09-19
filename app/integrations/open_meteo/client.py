from typing import Any

import httpx
from pydantic import ValidationError

from app.core.exceptions import (
    ExternalServiceError,
    LocationNotFoundError,
)
from app.schemas.location import (
    CityLocation,
    CitySearchResult,
)


class OpenMeteoClient:
    """Client for communicating with Open-Meteo APIs."""

    def __init__(
        self,
        http_client: httpx.AsyncClient,
        geocoding_url: str,
    ) -> None:
        self._http_client = http_client
        self._geocoding_url = geocoding_url

    async def search_city(
        self,
        city_name: str,
        language: str = "en",
        result_count: int = 5,
    ) -> CitySearchResult:
        query = city_name.strip()

        if len(query) < 2:
            raise ValueError(
                "City name must contain at least two characters."
            )

        if not 1 <= result_count <= 10:
            raise ValueError(
                "Result count must be between 1 and 10."
            )

        params = {
            "name": query,
            "count": result_count,
            "language": language.lower(),
            "format": "json",
        }

        payload = await self._get_json(params)

        raw_results = payload.get("results", [])

        if not raw_results:
            raise LocationNotFoundError(
                f"No city was found for '{query}'."
            )

        try:
            matches = [
                self._parse_location(item)
                for item in raw_results
            ]
        except (
            KeyError,
            TypeError,
            ValidationError,
        ) as exc:
            raise ExternalServiceError(
                "Open-Meteo returned invalid location data."
            ) from exc

        return CitySearchResult(
            query=query,
            matches=matches,
        )

    async def _get_json(
        self,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            response = await self._http_client.get(
                self._geocoding_url,
                params=params,
            )

            response.raise_for_status()

        except httpx.TimeoutException as exc:
            raise ExternalServiceError(
                "The Open-Meteo request timed out."
            ) from exc

        except httpx.HTTPStatusError as exc:
            raise ExternalServiceError(
                "Open-Meteo returned HTTP status "
                f"{exc.response.status_code}."
            ) from exc

        except httpx.RequestError as exc:
            raise ExternalServiceError(
                "Could not connect to Open-Meteo."
            ) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise ExternalServiceError(
                "Open-Meteo returned invalid JSON."
            ) from exc

        if not isinstance(payload, dict):
            raise ExternalServiceError(
                "Open-Meteo returned an unexpected response."
            )

        if payload.get("error"):
            reason = payload.get(
                "reason",
                "Unknown Open-Meteo error.",
            )

            raise ExternalServiceError(str(reason))

        return payload

    @staticmethod
    def _parse_location(
        data: dict[str, Any],
    ) -> CityLocation:
        return CityLocation(
            name=data["name"],
            country=data.get("country", ""),
            country_code=data.get("country_code", ""),
            admin1=data.get("admin1"),
            latitude=data["latitude"],
            longitude=data["longitude"],
            timezone=data["timezone"],
        )