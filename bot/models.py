from datetime import datetime
from sqlalchemy import ForeignKey, Column, String, Integer, DateTime
from sqlalchemy import BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column("id", Integer, primary_key=True)
    tg_id = Column("tg-id", BigInteger, unique=True)
    city = Column("city", String, nullable=True)
    join_date = Column("join_date", DateTime, default=datetime.now())
    reports = relationship(
        "WeatherReports", backref="report", lazy=True,
        cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return self.city


class WeatherReports(Base):
    __tablename__ = "reports"

    id = Column("id", Integer, primary_key=True)
    owner = Column("owner", Integer, ForeignKey("users.id"))
    date = Column("date", DateTime, default=datetime.now())
    city = Column("city", String)
    temp = Column("temp", String)
    feels_like = Column("feels_like", String)
    temp_max = Column("temp_max", String)
    temp_min = Column("temp_min", String)
    sunrise_time = Column("sunrise", String)
    sunset_time = Column("sunset", String)
    duration = Column("duration", String)
    wind_speed = Column("wind_speed", String)

    def __repr__(self) -> str:
        return self.city
