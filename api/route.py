from fastapi import APIRouter, Depends, HTTPException, status,Query,Response
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from schema.cc_schema import CityCreate,CityResponse

from model.database import get_db
from model.cc_model import CountryCodeCity


router = APIRouter(prefix="", tags=["City"])


@router.post("/cities", response_model=CityResponse)
async def create_or_update_city(
    payload: CityCreate,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CountryCodeCity).where(CountryCodeCity.city == payload.city)
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.countrycode = payload.countrycode
        await db.commit()
        await db.refresh(existing)
        response.status_code = status.HTTP_200_OK
        return existing

    obj = CountryCodeCity(city=payload.city, countrycode=payload.countrycode)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    response.status_code = status.HTTP_201_CREATED
    return obj


@router.get("/cities", response_model=list[CityResponse])
async def get_cities(
    countrycode: str = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(CountryCodeCity)

    if countrycode:
        stmt = stmt.where(CountryCodeCity.countrycode == countrycode)

    stmt = stmt.offset(offset).limit(limit)

    result = await db.execute(stmt)
    return result.scalars().all()