from pydantic import BaseModel


class Location(BaseModel):
    lat: float
    lng: float


class DistanceResponse(BaseModel):
    origin: Location
    destination: Location
    distance: str
    duration: str
