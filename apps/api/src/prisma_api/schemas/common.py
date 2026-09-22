from pydantic import BaseModel


class CoordinatesSchema(BaseModel):
    lat: float
    lng: float
