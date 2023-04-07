import datetime
import requests
from bs4 import BeautifulSoup
import random
from aiogram import Bot
from lexicon.lexicon import remind_text
import sqlite3
from environs import Env
from pathlib import Path

env = Env()
env.read_env()
PATH_DB = Path("database", "users.db")

async def get_wish_text()->str:
    '''Функция для получения поздравления с сайта в формате строки'''
    
    pg = random.randint(1,50)
    url = f"https://pozdravok.com/pozdravleniya/den-rozhdeniya/proza{f'-{pg}' if pg!=1 else ''}.htm"

    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
    }
    
    req = requests.get(url, headers=headers)
    src = req.text
        
    soup = BeautifulSoup(src, "lxml")
    wishes = soup.find_all(class_="sfst")
    number_wish = random.randint(0,9)
    return wishes[number_wish].text

async def get_wish_photo(name:str = "")->str:
    """Функция возвращает ссылку на фото с именным поздравлением"""
    
    url = "https://otkritkiok.ru/den-rozhdeniya/imena"

    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
    }
    
    "Получаем ссылку на страницу с фото"
    req = requests.get(url, headers=headers)
    src = req.text
    soup = BeautifulSoup(src,"lxml")
    part_of_link = soup.find(class_="label label_name",string=name.capitalize()).get("href")
    page_with_photos = "".join(["https://otkritkiok.ru",part_of_link]).strip()
    
    "Получаем ссылку на рандомное фото"
    req = requests.get(page_with_photos, headers=headers)
    src = req.text
    soup = BeautifulSoup(src,"lxml")
    photo_links  = soup.find_all(class_="link postcard-snippet__link")
    photo_link = photo_links[random.randint(0,len(photo_links))].find_next("img").get("src")
    
    return photo_link

async def bcongratulation(bot:Bot,chat_id,name):
    """Функция отправляет сообщение с поздравлением в чат"""
    link = await get_wish_photo(name[0])
    text = await get_wish_text()
    await bot.send_message(chat_id=chat_id, text=f"Сегодня свой день рождения отмечает {name[0]} {name[1]}\!")
    await bot.send_photo(chat_id = chat_id, photo=link, caption=text, parse_mode = None)

async def todays_bd():
    """Получение дней рождений сегодня"""
    base = sqlite3.connect(PATH_DB)
    cursor = base.cursor()
    result = cursor.execute("SELECT name, surname FROM main_table where strftime('%m-%d',main_table.date) = strftime('%m-%d','now')")
    base.commit()
    return [r for r in result]

async def users_for_notification(users_not_for_notif):
    """Получение юзеров для отправки сообщений о сборе денег"""
    base = sqlite3.connect(PATH_DB)
    cursor = base.cursor()
    result = cursor.execute(f"SELECT id, cash FROM main_table where id NOT IN ({','.join('?' for _ in users_not_for_notif)}) AND status_walley = 'True'", users_not_for_notif)
    base.commit()
    return [r for r in result]
    
async def next_week_bd():
    """Получение дней рождений на сл. неделе"""
    base = sqlite3.connect(PATH_DB)
    cursor = base.cursor()
    result = cursor.execute("SELECT name, surname, id, date, cash FROM main_table where strftime('%m-%d',main_table.date) \
        BETWEEN strftime('%m-%d','now', '+7 day') AND strftime('%m-%d','now', '+13 day')")
    base.commit()
    return [r for r in result]

async def event_check(bot:Bot):
    """Проверка событий каждый день"""
    now = datetime.datetime.now()
    now_bd_list = await todays_bd()
    if len(now_bd_list) != 0:
        for bd in now_bd_list:
            await bcongratulation(bot, chat_id=f'-100{env("MAIN_CHAT")}', name=(bd[0],bd[1]))
    if now.weekday()+1 == 1:
        next_week = await next_week_bd()
        if len(next_week) != 0:
            users_not_for_notif = [u[2] for u in next_week]
            users_for_notif = await users_for_notification(users_not_for_notif)
            bd_param = [p for p in next_week]
            for u in users_for_notif: 
                #chat_id поменять на u[0]
                await bot.send_message(chat_id=f'-100{env("MAIN_CHAT")}', 
                                       text=remind_text(users_for_cong=bd_param, own_cash=u[1]))