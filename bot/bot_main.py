import os
import math
import datetime
from get_weather import get_weather_in_the_city
from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from dotenv import load_dotenv
from db import add_user, set_user_city, create_report, get_user_city
from db import get_reports, delete_user_report, get_all_users
from db import delete_all_user_reports


load_dotenv()

bot = Bot(token=os.getenv("TOKEN"))
admin_id = int(os.getenv("BOT_ADMIN"))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class ChoiceCityWeather(StatesGroup):
    waiting_city = State()


class SetUserCity(StatesGroup):
    waiting_current_city = State()


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    add_user(message.from_user.id)
    start_buttons = [
        "Weather in my city", "Weather in another city",
        "History", "Set my current city"
    ]
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(*start_buttons)
    await message.answer(
        f"Hello, {message.from_user.username}, im weather bot who can tell "
        "you about weather around the world.", reply_markup=keyboard)


@dp.message_handler(commands=["menu"])
async def main_menu(message: types.Message):
    add_user(message.from_user.id)
    start_buttons = [
        "Weather in my city", "Weather in another city",
        "History", "Set my current city"
    ]
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(*start_buttons)
    await message.answer("You are in the main menu", reply_markup=keyboard)


@dp.message_handler(commands=["clear_history"])
async def clear_history(message: types.Message):
    delete_all_user_reports(message.from_user.id)
    await message.answer("History cleared")


@dp.message_handler(Text(equals="Weather in another city"))
async def city_weather(message: types.Message):
    await message.answer("Enter your city name")
    await ChoiceCityWeather.waiting_city.set()


@dp.message_handler(state=ChoiceCityWeather.waiting_city)
async def city_chosen(message: types.Message, state: FSMContext):
    if message.text[0].islower():
        await message.answer("Enter the city name with a capital letter")
        return
    await state.update_data(waiting_city=message.text)
    city = await state.get_data()
    data = get_weather_in_the_city(city.get("waiting_city"))
    if data is None:
        await message.answer("Check city name")
        return
    create_report(
        message.from_user.id, data["city"], data["cur_weather"],
        data["feels_like"], data["temp_max"], data["temp_min"],
        data["sunrise_timestamp"], data["sunset_timestamp"],
        data["length_of_the_day"], data["wind"])
    await message.answer(
        f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}\n'
        f'Weather in the city:  {data["city"]}\n'
        f'Temperature:  {data["cur_weather"]}C° {data["wd"]}\n'
        f'Feels like:  {data["feels_like"]}C°\n'
        f'Temp max:  {data["temp_max"]}C°\nTemp min:  {data["temp_min"]}C°\n'
        f'Sunrise time:  {data["sunrise_timestamp"]}\n'
        f'Sunset time:  {data["sunset_timestamp"]}\n'
        f'Duration of the day:  {data["length_of_the_day"]}\n'
        f'Wind speed:  {data["wind"]}mps\n'
        f'Have a good day!')
    await state.finish()


@dp.message_handler(Text(equals="Set my current city"))
async def set_current_city(message: types.Message):
    await message.answer("What city are you in now")
    await SetUserCity.waiting_current_city.set()


@dp.message_handler(state=SetUserCity.waiting_current_city)
async def current_city(message: types.Message, state: FSMContext):
    if message.text[0].islower():
        await message.answer("Enter the city name with a capital letter")
        return
    await state.update_data(waiting_current_city=message.text)
    city = await state.get_data()
    set_user_city(message.from_user.id, city.get("waiting_current_city"))
    await message.answer(
        f"Now your current city is {city.get('waiting_current_city')}")
    await state.finish()


@dp.message_handler(Text(equals="Weather in my city"))
async def weather_in_user_city(message: types.Message):
    city = get_user_city(message.from_user.id)
    if city is None:
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        btn1 = types.KeyboardButton("Set my current city")
        markup.add(btn1)
        await message("Please set your current city", reply_markup=markup)
        return
    data = get_weather_in_the_city(city)
    if data is None:
        await message.answer("Check city name")
        return
    create_report(
        message.from_user.id, data["city"], data["cur_weather"],
        data["feels_like"], data["temp_max"], data["temp_min"],
        data["sunrise_timestamp"], data["sunset_timestamp"],
        data["length_of_the_day"], data["wind"])
    await message.answer(
        f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}\n'
        f'Weather in the city:  {data["city"]}\n'
        f'Temperature:  {data["cur_weather"]}C° {data["wd"]}\n'
        f'Feels like:  {data["feels_like"]}C°\n'
        f'Temp max:  {data["temp_max"]}C°\nTemp min:  {data["temp_min"]}C°\n'
        f'Sunrise time:  {data["sunrise_timestamp"]}\n'
        f'Sunset time:  {data["sunset_timestamp"]}\n'
        f'Duration of the day:  {data["length_of_the_day"]}\n'
        f'Wind speed:  {data["wind"]}mps\n'
        f'Have a good day!')


@dp.message_handler(Text(equals="History"))
async def get_reports_(message: types.Message):
    current_page = 1
    reports = get_reports(message.from_user.id)
    total_pages = math.ceil(len(reports) / 4)
    inline_markup = types.InlineKeyboardMarkup()
    for report in reports[:current_page*4]:
        inline_markup.add(types.InlineKeyboardButton(
            f'{report.city} {report.date.month}.'
            f'{report.date.day}   '
            f'{report.date.hour}:{report.date.minute}',
            callback_data=f'report_ {report.id}'
        ))
    current_page += 1
    inline_markup.row(
        types.InlineKeyboardButton(
            text=f'{current_page-1}/{total_pages}',
            callback_data='None'),
        types.InlineKeyboardButton(
            text='next', callback_data=f'next_{current_page}')
    )
    await message.answer("Requests history:", reply_markup=inline_markup)


@dp.callback_query_handler(lambda call: 'users' not in call.data)
async def callback_query(call, state: FSMContext):
    query_type = call.data.split('_')[0]
    if query_type == 'delete' and call.data.split("_")[1] == 'report':
        report_id = int(call.data.split('_')[2])
        current_page = 1
        delete_user_report(report_id)
        reports = get_reports(call.from_user.id)
        total_pages = math.ceil(len(reports) / 4)
        inline_markup = types.InlineKeyboardMarkup()
        for report in reports[:current_page * 4]:
            inline_markup.add(types.InlineKeyboardButton(
                text=f'{report.city} {report.date.month}.'
                     f'{report.date.day}   '
                     f'{report.date.hour}:{report.date.minute}',
                callback_data=f'report_{report.id}'))
        current_page += 1
        inline_markup.row(
            types.InlineKeyboardButton(
                text=f"{current_page-1}/{total_pages}",
                callback_data='None'),
            types.InlineKeyboardButton(
                text='next', callback_data=(
                    f'next_{current_page}'))
        )
        await call.message.edit_text(
            text="Requests history:", reply_markup=inline_markup)
    async with state.proxy() as data:
        data["current_page"] = int(call.data.split('_')[1])
        await state.update_data(current_page=data["current_page"])
        if query_type == 'next':
            reports = get_reports(call.from_user.id)
            total_pages = math.ceil(len(reports) / 4)
            inline_markup = types.InlineKeyboardMarkup()
            if data['current_page'] * 4 >= len(reports):
                for report in reports[
                    data['current_page'] * 4 - 4:len(reports) + 1
                ]:
                    inline_markup.add(types.InlineKeyboardButton(
                        text=f'{report.city} {report.date.month}.'
                             f'{report.date.day}   '
                             f'{report.date.hour}:{report.date.minute}',
                        callback_data=f'report_ {report.id}'))
                data['current_page'] -= 1
                inline_markup.row(
                    types.InlineKeyboardButton(
                        text='previous',
                        callback_data=f'prev_{data["current_page"]}'),
                    types.InlineKeyboardButton(
                        text=f"{data['current_page'] + 1}/{total_pages}",
                        callback_data='None')
                )
                await call.message.edit_text(
                    text="Requests history:", reply_markup=inline_markup)
                return
            for report in reports[
                data["current_page"] * 4 - 4:data["current_page"] * 4
            ]:
                inline_markup.add(types.InlineKeyboardButton(
                    text=f'{report.city} {report.date.month}.'
                         f'{report.date.day}   '
                         f'{report.date.hour}:{report.date.minute}',
                    callback_data=f'report_ {report.id}'))
            data['current_page'] += 1
            inline_markup.row(
                types.InlineKeyboardButton(text='previous',
                                           callback_data=(
                                            f'prev_{data["current_page"]-2}')),
                types.InlineKeyboardButton(
                    text=f"{data['current_page']-1}/{total_pages}",
                    callback_data='None'),
                types.InlineKeyboardButton(text='next',
                                           callback_data=(
                                            f'next_{data["current_page"]}'))
            )
            await call.message.edit_text(
                text="Requests history:", reply_markup=inline_markup)
        if query_type == 'prev':
            reports = get_reports(call.from_user.id)
            total_pages = math.ceil(len(reports) / 4)
            inline_markup = types.InlineKeyboardMarkup()
            if data['current_page'] == 1:
                for report in reports[0:data['current_page'] * 4]:
                    inline_markup.add(types.InlineKeyboardButton(
                        text=f'{report.city} {report.date.month}.'
                             f'{report.date.day}   '
                             f'{report.date.hour}:{report.date.minute}',
                        callback_data=f'report_ {report.id}'))
                data['current_page'] += 1
                inline_markup.row(
                    types.InlineKeyboardButton(
                        text=f"{data['current_page']-1}/{total_pages}",
                        callback_data='None'),
                    types.InlineKeyboardButton(
                        text='next', callback_data=(
                            f'next_{data["current_page"]}'))
                )
                await call.message.edit_text(
                    text="Requests history:", reply_markup=inline_markup)
                return
            for report in reports[
                data["current_page"] * 4 - 8:data["current_page"] * 4 - 4
            ]:
                inline_markup.add(types.InlineKeyboardButton(
                    text=f'{report.city} {report.date.month}.'
                         f'{report.date.day}   '
                         f'{report.date.hour}:{report.date.minute}',
                    callback_data=f'report_ {report.id}'))
            data['current_page'] -= 1
            inline_markup.row(
                types.InlineKeyboardButton(text='previous',
                                           callback_data=(
                                            f'prev_{data["current_page"]}')),
                types.InlineKeyboardButton(
                    text=f"{data['current_page'] + 1}/{total_pages}",
                    callback_data='None'),
                types.InlineKeyboardButton(text='next',
                                           callback_data=(
                                            f'next_{data["current_page"]}'))
            )
            await call.message.edit_text(
                text="Requests history:", reply_markup=inline_markup)
        if query_type == 'report':
            reports = get_reports(call.from_user.id)
            report_id = int(call.data.split('_')[1])
            inline_markup = types.InlineKeyboardMarkup()
            for report in reports:
                if report.id == int(report_id):
                    inline_markup.add(types.InlineKeyboardButton(
                        text='back',
                        callback_data=f'reports_{data["current_page"]}'),
                        types.InlineKeyboardButton(
                        text='delete',
                        callback_data=f'delete_report_{report_id}'))
                    await call.message.edit_text(
                        text=f'Data on request:\n'
                        f'Weather in the city:  {report.city}\n'
                        f'Temperature:  {report.temp}C°\n'
                        f'Feels like:  {report.feels_like}C°\n'
                        f'Temp max:  {report.temp_max}C°\n'
                        f'Temp min:  {report.temp_min}C°\n'
                        f'Sunrise time:  {report.sunrise_time}\n'
                        f'Sunset time:  {report.sunset_time}\n'
                        f'Duration of the day:  {report.duration}\n'
                        f'Wind speed:  {report.wind_speed}mps\n',
                        reply_markup=inline_markup)
                    break
        if query_type == 'reports':
            reports = get_reports(call.from_user.id)
            total_pages = math.ceil(len(reports) / 4)
            inline_markup = types.InlineKeyboardMarkup()
            data['current_page'] = 1
            for report in reports[0:data['current_page'] * 4]:
                inline_markup.add(types.InlineKeyboardButton(
                    text=f'{report.city} {report.date.month}.'
                         f'{report.date.day}   '
                         f'{report.date.hour}:{report.date.minute}',
                    callback_data=f'report_ {report.id}'))
            data['current_page'] += 1
            inline_markup.row(
                types.InlineKeyboardButton(
                    text=f"{data['current_page']-1}/{total_pages}",
                    callback_data='None'),
                types.InlineKeyboardButton(
                    text='next', callback_data=(
                        f'next_{data["current_page"]}'))
            )
            await call.message.edit_text(
                text="Requests history:", reply_markup=inline_markup)


@dp.message_handler(
    lambda message: message.from_user.id == admin_id and
    message.text == 'Admin')
async def admin(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Users')
    markup.add(btn1)
    await message.answer('Admin panel', reply_markup=markup)


@dp.message_handler(
    lambda message: message.from_user.id == admin_id and
    message.text == 'Users')
async def get_all_users_(message: types.Message):
    current_page = 1
    users = get_all_users()
    total_pages = math.ceil(len(users) / 4)
    inline_markup = types.InlineKeyboardMarkup()
    for user in users[:current_page * 4]:
        inline_markup.add(types.InlineKeyboardButton(text=(
            f'{user.id}) id: {user.tg_id} added: {user.join_date.day}.'
            f'{user.join_date.month}.{user.join_date.year} '
            f'Requests: {len(user.reports)}'),
                callback_data='None'))
    current_page += 1
    inline_markup.row(
        types.InlineKeyboardButton(
            text=f"{current_page-1}/{total_pages}",
            callback_data='None'),
        types.InlineKeyboardButton(
            text='next', callback_data=f'next_{current_page}')
    )
    await message.answer('Users:', reply_markup=inline_markup)


@dp.callback_query_handler(lambda call: 'users' in call.data)
async def callback_query_(call, state: FSMContext):
    query_type = call.data.split('_')[0]
    async with state.proxy() as data:
        data['current_page'] = int(call.data.split('_')[2])
        await state.update_data(current_page=data['current_page'])
        if query_type == 'next':
            users = get_all_users()
            total_pages = math.ceil(len(users) / 4)
            inline_markup = types.InlineKeyboardMarkup()
            if data['current_page'] * 4 >= len(users):
                for user in users[
                    data['current_page'] * 4 - 4:len(users) + 1
                ]:
                    inline_markup.add(types.InlineKeyboardButton(text=(
                        f'{user.id}) id: {user.tg_id} added: '
                        f'{user.join_date.day}.{user.join_date.month}.'
                        f'{user.join_date.year} '
                        f'Requests: {len(user.reports)}'),
                        callback_data='None'))
                data['current_page'] -= 1
                inline_markup.row(
                    types.InlineKeyboardButton(
                        text='previous', callback_data=(
                            f'prev_users_{data["current_page"]-2}')),
                    types.InlineKeyboardButton(
                        text=f"{data['current_page']}/{total_pages}",
                        callback_data='None')
                )
                await call.message.edit_text(
                    text="Users:", reply_markup=inline_markup)
                return
            for user in users[
                data["current_page"] * 4 - 4:data["current_page"] * 4
            ]:
                inline_markup.add(types.InlineKeyboardButton(text=(
                    f'{user.id}) id: {user.tg_id} added: '
                    f'{user.join_date.day}.{user.join_date.month}.'
                    f'{user.join_date.year} Requests: {len(user.reports)}'),
                    callback_data='None'))
            data['current_page'] += 1
            inline_markup.row(
                types.InlineKeyboardButton(text='previous',
                                           callback_data=(
                                            f'prev_users_'
                                            f'{data["current_page"]-2}')),
                types.InlineKeyboardButton(
                    text=f"{data['current_page'] - 1}/{total_pages}",
                    callback_data='None'),
                types.InlineKeyboardButton(text='next_users_',
                                           callback_data=(
                                            f'next_{data["current_page"]}'))
            )
            await call.message.edit_text(
                text="Users:", reply_markup=inline_markup)
        if query_type == 'prev':
            users = get_all_users()
            total_pages = math.ceil(len(users) / 4)
            inline_markup = types.InlineKeyboardMarkup()
            if data['current_page'] == 1:
                for user in users[0:data['current_page'] * 4]:
                    inline_markup.add(types.InlineKeyboardButton(text=(
                        f'{user.id}) id: {user.tg_id} added: '
                        f'{user.join_date.day}.{user.join_date.month}.'
                        f'{user.join_date.year} '
                        f'Requests: {len(user.reports)}'),
                        callback_data='None'))
                data['current_page'] += 1
                inline_markup.row(
                    types.InlineKeyboardButton(
                        text=f"{data['current_page']-1}/{total_pages}",
                        callback_data='None'),
                    types.InlineKeyboardButton(
                        text='next', callback_data=(
                            f'next_users_{data["current_page"]}'))
                )
                await call.message.edit_text(
                    text="Users:", reply_markup=inline_markup)
                return
            for user in users[
                data["current_page"] * 4 - 4:data["current_page"] * 4
            ]:
                inline_markup.add(types.InlineKeyboardButton(text=(
                    f'{user.id}) id: {user.tg_id} added: '
                    f'{user.join_date.day}.{user.join_date.month}.'
                    f'{user.join_date.year} Requests: {len(user.reports)}'),
                    callback_data='None'))
            data['current_page'] -= 1
            inline_markup.row(
                types.InlineKeyboardButton(text='previous',
                                           callback_data=(
                                            f'prev_users_'
                                            f'{data["current_page"]}')),
                types.InlineKeyboardButton(
                    text=f"{data['current_page'] + 1}/{total_pages}",
                    callback_data='None'),
                types.InlineKeyboardButton(text='next_users_',
                                           callback_data=(
                                            f'next_users_'
                                            f'{data["current_page"]}'))
            )
            await call.message.edit_text(
                text="Users:", reply_markup=inline_markup)


def main():
    executor.start_polling(dp, skip_updates=True)


if __name__ == "__main__":
    main()
