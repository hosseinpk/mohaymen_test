from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from schema.cc_schema import CityCreate,CityResponse

from model.database import get_db
from model.cc_model import CountryCodeCity


router = APIRouter(prefix="/cities", tags=["City"])


@router.post("/cities", response_model=CityResponse, status_code=status.HTTP_201_CREATED)
async def create_city(
    payload: CityCreate,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(CountryCodeCity).where(
        CountryCodeCity.city == payload.city,
        CountryCodeCity.country_code == payload.country_code
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="City with this country code already exists"
        )

    obj = CountryCodeCity(
        city=payload.city,
        country_code=payload.country_code
    )

    db.add(obj)
    await db.commit()
    await db.refresh(obj)

    return obj