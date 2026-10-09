from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base


class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    records = relationship("WeatherRecord", back_populates="city", cascade="all, delete-orphan")


class WeatherRecord(Base):
    __tablename__ = "weather_records"

    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False)
    date = Column(Date, nullable=False)
    temperature_max = Column(Float)
    temperature_min = Column(Float)
    precipitation_sum = Column(Float)
    windspeed_max = Column(Float)
    humidity_mean = Column(Float)

    city = relationship("City", back_populates="records")

    __table_args__ = (
        UniqueConstraint("city_id", "date", name="uq_city_date"),
    )
