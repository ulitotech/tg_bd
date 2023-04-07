import sqlite3
from pathlib import Path
from environs import Env


env = Env()
env.read_env()


SUPERUSERID = env('SUPER_USER_ID')
PATH_DB = Path("database", "users.db")

async def creating_db():
    """Создает стартовую базу данных"""
    base = sqlite3.connect(PATH_DB)
    cursor = base.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS main_table ('name' TEXT DEFAULT\
        'No_Name','surname' TEXT DEFAULT 'No_Surname','date' TEXT DEFAULT\
        'YYYY-MM-DD','id' TEXT DEFAULT 'No_Id','status_walley' TEXT DEFAULT\
        'True','status' TEXT DEFAULT 'User','cash' INTEGER DEFAULT 250)")
    base.commit()
    cursor.execute("CREATE TABLE IF NOT EXISTS notification ('phone_number' TEXT,\
        'bank'	TEXT)")
    base.commit()
    cursor.execute("DELETE FROM notification")
    base.commit()
    cursor.execute("INSERT INTO notification VALUES (?,?)",('8-999-777-66-55','СБЕР'))
    base.commit()

async def edit_notification_info(param, new_value):
    "Изменяет значения для рассылки"
    base = sqlite3.connect(PATH_DB)
    cursor = base.cursor()
    cursor.execute("UPDATE notification SET {param} = '{new_value}'".format(param, new_value))
    base.commit()    
    
async def del_db():
    """Чистит базу данных c пользователями"""
    base = sqlite3.connect(PATH_DB)
    cursor = base.cursor()
    cursor.execute("DELETE FROM main_table WHERE id != '{0}'".format(SUPERUSERID))
    base.commit()

async def add_user(name:str = "No_Name", surname:str = "No_Surname",
             date:str = "No_Date", id_:str = "No_Id", status_walley:str="True",
             status:str = "User", cash:int = 250):
    """Создание записи о пользователе с проверкой на уникальность.
    name:str - Имя пользователя,
    surname:str - Фамилия пользователя,
    Дата рождения - date:st,
    ИД пользователя - id:str,
    Статус сбора средств - status_walley:str = True/False,
    Статус пользователя - status:str = User/Admin/SuperUser
    Стандартная сумма сбора - cash:int = 250 по умолчанию
    """
    base = sqlite3.connect(PATH_DB)
    cursor = base.cursor()
    cursor.execute("INSERT INTO main_table VALUES (?,?,?,?,?,?,?)",(f"{name}", f"{surname}",
                                                                  f"{date}", f"{id_}",
                                                                  f"{status_walley}",f"{status}", f"{cash}"))
    base.commit()

async def del_user(id_:str):
    """Удаляет юзера по id"""
    base = sqlite3.connect("database/users.db")
    cursor = base.cursor()
    cursor.execute("DELETE FROM main_table WHERE id = '{0}'".format(id_))
    base.commit()

async def change_user(id_:str, param:str, new_value:str):
    """Изменение данных о пользователе, по id с указанием параметра и нового значения
    name:str - Имя пользователя,
    surname:str - Фамилия пользователя,
    Дата рождения - date:st,
    ИД пользователя - id:str,
    Статус сбора средств - status_walley:str
    Стандартная сумма сбора - cash:int
    """
    base = sqlite3.connect(PATH_DB)
    cursor = base.cursor()
    cursor.execute("UPDATE main_table SET {0} = '{1}' WHERE id = {2}".format(param, new_value, id_))
    base.commit()

def get_user_in_status(status:str = "None"):
    """Получение юзеров по статусу"""
    base = sqlite3.connect(PATH_DB)
    cursor = base.cursor()
    if status in ("for_deleting", "for_show", "for_editing"):
        result = cursor.execute("SELECT name, surname, date, id, status_walley, cash FROM main_table ORDER BY surname, name") 
    elif status != "None":
        result = cursor.execute("SELECT name, surname, id FROM main_table WHERE status = '{0}' ORDER BY surname, name".format(status))
    else:
        result = [c for c in cursor.execute("SELECT name, surname, date, id, status_walley, cash FROM main_table ORDER BY surname, name")] 
        result_list = {}
        i = 1
        flag = True
        while flag:
            group = []
            for _ in range(6):
                if result:
                    group.append(result.pop(0))
                else:
                    flag = False
                    break
            result_list[i] = group
            i+=1
        result = result_list
    base.commit()

    return result

def get_month_bd(date:str):
    """Получение дней рождений в месяце
    date = 'now'/'next'
    now - этот месяц;
    next - следующий месяц
    """
    base = sqlite3.connect(PATH_DB)
    cursor = base.cursor()
    if date == "now":
        result = cursor.execute("SELECT name, surname, date FROM main_table WHERE strftime('%m', main_table.date) = strftime('%m', 'now')")
    elif date == "next":
        result = cursor.execute("SELECT name, surname, date FROM main_table WHERE strftime('%m', main_table.date)\
            = strftime('%m', 'now', 'start of month', '+1 month') ORDER BY date")
    base.commit()
    return result

def todays_bd():
    """Получение дней рождений сегодня"""
    base = sqlite3.connect(PATH_DB)
    cursor = base.cursor()
    result = cursor.execute("SELECT name, surname FROM main_table where strftime('%m-%d',main_table.date) = strftime('%m-%d','now'))")
    base.commit()
    return [r for r in result]

def todays_bd():
    """Получение дней рождений сегодня"""
    base = sqlite3.connect(PATH_DB)
    cursor = base.cursor()
    result = cursor.execute("SELECT name, surname FROM main_table where strftime('%m-%d',main_table.date) = strftime('%m-%d','now'))")
    base.commit()
    return [r for r in result]

def get_notif_param(param):
    """Получение действующего значения оповещения"""
    base = sqlite3.connect(PATH_DB)
    cursor = base.cursor()
    prep_result = cursor.execute("SELECT * FROM notification")
    base.commit()
    result = [r for r in prep_result]
    if param == "phone":
        return result[0][0]
    elif param == "bank":
        return result[0][1]

async def change_notif(param:str, new_value:str):
    """Изменение данных оповещения"""
    with sqlite3.connect(PATH_DB) as base:
        cursor = base.cursor()
        cursor.execute("UPDATE notification SET {0} = '{1}' ".format(param, new_value))
        base.commit()

async def get_user_in_surname(surname:str):
    with sqlite3.connect(PATH_DB) as base:
        cursor = base.cursor()
        result = [c for c in cursor.execute("SELECT name, surname, date, id, status_walley, cash FROM main_table WHERE surname = '{0}' ORDER BY surname, name".format(surname.capitalize()))]
        base.commit()
    return result