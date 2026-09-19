from pydantic import BaseModel, Field


class CityLocation(BaseModel):
    name: str
    country: str
    country_code: str
    admin1: str | None = None
    latitude: float
    longitude: float
    timezone: str


class CitySearchResult(BaseModel):
    query: str
    matches: list[CityLocation] = Field(
        default_factory=list
    )