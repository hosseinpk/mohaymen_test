from pydantic import BaseModel


class CityCreate(BaseModel):
    city: str
    countrycode: str


class CityResponse(BaseModel):
    id: int
    city: str
    countrycode: str

    class Config:
        from_attributes = True
