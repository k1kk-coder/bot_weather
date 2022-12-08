import os
import requests
import datetime
from dotenv import load_dotenv

load_dotenv()

code_to_smile = {
        'Clear': 'Clear \U00002600',
        "Clouds": 'Clouds \U00002601',
        'Rain': "Rain \U00002614",
        'Drizzle': 'Drizzle \U00002614',
        'Thunderstorm': 'Thunderstorm \U000026A1',
        'Snow': 'Snow \U0001F328',
        'Mist': 'Mist \U0001f32B'
    }


def get_weather_in_the_city(city):
    try:
        request = requests.get(
            f'https://api.openweathermap.org/data/2.5/weather?q={city}'
            f'&appid={os.getenv("WEATHER_TOKEN")}&units=metric'
        )
        data = request.json()

        city = data['name']
        cur_weather = data['main']['temp']

        weather_description = data['weather'][0]['main']
        if weather_description in code_to_smile:
            wd = code_to_smile[weather_description]
        else:
            wd = ''
        feels_like = data['main']['feels_like']
        temp_max = data['main']['temp_max']
        temp_min = data['main']['temp_min']
        wind = data['wind']['speed']
        sunrise_timestamp = datetime.datetime.fromtimestamp(
            data['sys']['sunrise']).strftime("%H:%M")
        sunset_timestamp = datetime.datetime.fromtimestamp(
            data['sys']['sunset']).strftime("%H:%M")
        length_of_the_day = datetime.datetime.fromtimestamp(
            data['sys']['sunset']) - datetime.datetime.fromtimestamp(
                data['sys']['sunrise'])
        data = {"city": city,
                "cur_weather": cur_weather,
                "wd": wd,
                "feels_like": feels_like,
                "temp_max": temp_max,
                "temp_min": temp_min,
                "sunrise_timestamp": sunrise_timestamp,
                "sunset_timestamp": sunset_timestamp,
                "length_of_the_day": length_of_the_day,
                "wind": wind}
        return data

    except Exception:
        return None
