from fastapi import APIRouter, Depends, HTTPException, status, Query, Response, Request
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from schema.cc_schema import CityCreate, CityResponse

from model.database import get_db
from model.cc_model import CountryCodeCity

router = APIRouter(prefix="", tags=["City"])

ENDPOINT_TEMPLATE = "/countrycode/{city}"


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


@router.get("/countrycode/{city}")
async def get_country_code(
    city: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):

    cache = request.app.state.city_cache
    kafka_logger = request.app.state.kafka_logger

    normalized_city = city.strip()

    cached_country_code = await cache.get(normalized_city)
    if cached_country_code is not None:
        await kafka_logger.log(
            {
                "event": "cache_hit",
                "city": normalized_city,
                "countrycode": cached_country_code,
                "endpoint": ENDPOINT_TEMPLATE,
                "source": "cache",
            },
            key=normalized_city.lower(),
        )
        return {
            "city": normalized_city,
            "countrycode": cached_country_code,
            "source": "cache",
        }

    result = await db.execute(
        select(CountryCodeCity).where(
            func.lower(CountryCodeCity.city) == normalized_city.lower()
        )
    )
    city_obj = result.scalar_one_or_none()

    if city_obj is None:
        await kafka_logger.log(
            {
                "event": "city_not_found",
                "city": normalized_city,
                "endpoint": ENDPOINT_TEMPLATE,
                "source": "database",
            },
            key=normalized_city.lower(),
        )
        raise HTTPException(status_code=404, detail="City not found")

    await cache.set(normalized_city, city_obj.countrycode)

    await kafka_logger.log(
        {
            "event": "cache_miss",
            "city": normalized_city,
            "countrycode": city_obj.countrycode,
            "endpoint": ENDPOINT_TEMPLATE,
            "source": "database",
        },
        key=normalized_city.lower(),
    )

    return {
        "city": normalized_city,
        "countrycode": city_obj.countrycode,
        "source": "database",
    }
