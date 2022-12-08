import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User, Base, WeatherReports
from dotenv import load_dotenv

load_dotenv()


engine = create_engine(os.getenv("DB_CONFIG"), echo=True)
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()


def add_user(tg_id):
    user = session.query(User).filter(User.tg_id == tg_id).first()
    if user is None:
        new_user = User(tg_id=tg_id)
        session.add(new_user)
        session.commit()


def set_user_city(tg_id, city):
    user = session.query(User).filter(User.tg_id == tg_id).first()
    user.city = city
    session.commit()


def create_report(
    tg_id, city, temp, feels_like, temp_max, temp_min, sunrise_time,
    sunset_time, duration, wind_speed
):
    user = session.query(User).filter(User.tg_id == tg_id).first()
    new_report = WeatherReports(
        owner=user.id, city=city, temp=temp, feels_like=feels_like,
        temp_max=temp_max, temp_min=temp_min, sunrise_time=sunrise_time,
        sunset_time=sunset_time, duration=duration, wind_speed=wind_speed)
    session.add(new_report)
    session.commit()


def get_user_city(tg_id):
    user = session.query(User).filter(User.tg_id == tg_id).first()
    return user.city


def get_reports(tg_id):
    user = session.query(User).filter(User.tg_id == tg_id).first()
    reports = user.reports[::-1]
    return reports


def delete_user_report(report_id):
    report = session.get(WeatherReports, report_id)
    session.delete(report)
    session.commit()


def delete_all_user_reports(tg_id):
    user = session.query(User).filter(User.tg_id == tg_id).first()
    reports = user.reports
    for report in reports:
        session.delete(report)
    session.commit()


def get_all_users():
    users = session.query(User).all()
    return users
