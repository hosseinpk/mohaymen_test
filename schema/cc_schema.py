from pydantic import BaseModel

class CityCreate(BaseModel):
    city: str
    country_code: str


class CityResponse(BaseModel):
    id: int
    city: str
    country_code: str

    class Config:
        from_attributes = True