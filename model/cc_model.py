from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy.ext.asyncio import AsyncSession
from model.database import Base,engine,AsyncSessionLocal
from sqlalchemy import Integer,select,String,DateTime,func
from datetime import datetime


class BaseModel(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())



class CountryCodeCity(BaseModel):
    __tablename__ = "ccode"

    countrycode: Mapped[str] = mapped_column(String,nullable=False)
    city: Mapped[str] = mapped_column(String,nullable=False)
    
