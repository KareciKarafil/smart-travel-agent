import httpx
import pytest

from app.core.exceptions import LocationNotFoundError
from app.integrations.open_meteo import OpenMeteoClient


GEOCODING_URL = (
    "https://geocoding-api.open-meteo.com/v1/search"
)


@pytest.mark.asyncio
async def test_search_city_returns_locations() -> None:
    def handler(
        request: httpx.Request,
    ) -> httpx.Response:
        assert request.url.params["name"] == "Tirana"
        assert request.url.params["count"] == "3"

        return httpx.Response(
            status_code=200,
            json={
                "results": [
                    {
                        "name": "Tirana",
                        "country": "Albania",
                        "country_code": "AL",
                        "admin1": "Tirana",
                        "latitude": 41.3275,
                        "longitude": 19.8189,
                        "timezone": "Europe/Tirane",
                    }
                ]
            },
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(
        transport=transport
    ) as http_client:
        client = OpenMeteoClient(
            http_client=http_client,
            geocoding_url=GEOCODING_URL,
        )

        result = await client.search_city(
            city_name="Tirana",
            result_count=3,
        )

    assert result.query == "Tirana"
    assert len(result.matches) == 1
    assert result.matches[0].country_code == "AL"
    assert result.matches[0].timezone == "Europe/Tirane"


@pytest.mark.asyncio
async def test_search_city_raises_when_not_found() -> None:
    def handler(
        request: httpx.Request,
    ) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            json={"results": []},
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(
        transport=transport
    ) as http_client:
        client = OpenMeteoClient(
            http_client=http_client,
            geocoding_url=GEOCODING_URL,
        )

        with pytest.raises(LocationNotFoundError):
            await client.search_city("Unknown City")