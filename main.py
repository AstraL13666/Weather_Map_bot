from list_tokens import token_tg, token_wm
from status_weather import ids
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup
from aiogram.dispatcher.filters import Text

import logging
import time
import requests
import datetime

api_token = token_tg

logging.basicConfig(level=logging.INFO)

bot = Bot(token=api_token)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def send_start(message: types.Message):
    text = ('Приветик {0.first_name} ☺️\n\n'
            'Я тестовый бот прогноза погоды.\n\n'
            '⬇️ Жмакай, не стесняйся')

    markup = ReplyKeyboardMarkup(resize_keyboard=True)

    but_info = 'Info'
    but_ver = 'Update'

    markup.add(but_info, but_ver)

    await message.answer(text.format(message.from_user), reply_markup=markup)


@dp.message_handler(Text(equals='Info'))
async def mes_info(message: types.Message):
    txt = ('🗺️ <b>Weather Bot v.: 1.1</b>\n\n'
           'ℹ️ Бот ищет город по названию, определяет его геопозицию и выдаёт данные о погоде.\n\n'
           'Поддерживаемые языки: Rus, Eng\n\n'
           '⚠️ Обо всех проблемах или багах пишите, учту, исправлю ☺\n\n'
           '🧑‍💻 Владимир: t.me/vlad_prin')
    await message.answer(txt, parse_mode=types.ParseMode.HTML)


@dp.message_handler(Text(equals='Update'))
async def mes_update(message: types.Message):
    txt = ('🤖 Список обновлений и фиксов:\n\n'
           '1️⃣ Бот переписан под другую библиотеку telegram_bot_api\n'
           '2️⃣ Исправлено отображение состояния (облачно, дождь и т.д.)\n'
           '3️⃣ Добавлена динамическая стикер-планета по геопозиции\n\n'
           '🗺️ <b>Weather Bot v.: 1.1</b>'
           )
    await message.answer(txt, parse_mode=types.ParseMode.HTML)


@dp.message_handler()
async def weather(message: types.Message):
    await message.reply('🔍 Производим поиск')

    # забираем смс
    cities = message.text

    # производим поиск городов по названию
    res_c = requests.get(f'http://api.openweathermap.org/geo/1.0/direct?q={cities}&limit=3&appid={token_wm}')
    date_c = res_c.json()

    # забираем позицию первого совпадения
    lat = date_c[0]['lat']
    lon = date_c[0]['lon']

    # производим поиск данных о погоде
    res = requests.get(
        f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={token_wm}&units=metric')
    data = res.json()

    # забираем данные о погоде
    # страна, город
    country = data['sys']['country']
    city = data['name']

    # время и продолжительность дня
    sun_rise = datetime.datetime.fromtimestamp(data['sys']['sunrise'])
    sun_set = datetime.datetime.fromtimestamp(data['sys']['sunset'])
    day = sun_set - sun_rise

    # состояние погоды
    temp = data['main']['temp']  # температура
    pres = data['main']['pressure']  # давление
    humd = data['main']['humidity']  # влажность
    wind = data['wind']['speed']
    weat = data['weather'][0]['id']
    status = ids[weat]

    # актуальность данных на промежуток времени
    date = datetime.datetime.today()
    t_me = date.strftime('%H:%M')

    # динамическая стикер-планета
    if 0 < lon < 120:
        p = '🌎'
    elif 121 < lon < 240:
        p = '🌎'
    else:
        p = '🌍'

    time.sleep(1)

    # Вывод данных по запросу
    txt = (f'📜 Информация актуальна на: {t_me}\n\n'
           f'🏙️ {country} | {city}\n'
           f'{p} {round(lat, 4)} с. ш. {round(lon, 4)} в. д.\n\n'
           f'🪁 Статус погоды: {status}\n\n'
           f'🌡️ Температура: {temp} °C\n'
           f'⬇️ Давление: {pres} мм. рт. ст.\n'
           f'💧 Влажность: {humd} %\n'
           f'💨 Ветер м/с: {wind}\n\n'
           f'🌇 Восход: {sun_rise}\n'
           f'🌆 Закат: {sun_set}\n\n'
           f'🕕 Продолжительность дня: {day}')

    await message.answer(txt)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
