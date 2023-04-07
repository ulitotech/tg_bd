from aiogram.filters import BaseFilter
from aiogram.types import Message
import sqlite3 as sq
from environs import Env

class Superuser(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        env = Env()
        env.read_env()
        superuser_id=env('SUPER_USER_ID')
        return str(message.from_user.id) == str(superuser_id)
    
class Is_Superuser(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        with sq.connect("database/users.db") as con:
            cur = con.cursor()   
            cur.execute(f"SELECT COUNT(*) FROM main_table WHERE id = {message.from_user.id} AND status = 'SuperUser'")
            result = 1 == list(cur)[0][0]
            return result
     
class Is_Admin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        with sq.connect("database/users.db") as con:
            cur = con.cursor()   
            cur.execute(f"SELECT COUNT(*) FROM main_table WHERE id = {message.from_user.id} AND status IN ('Admin', 'SuperAdmin')")
            result = 1 == list(cur)[0][0]
            return result

class DateCheck(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        try:
            date_in_list = message.text.split(".")
        except:
            return False
        else:
            result = (date_in_list[0].isdigit() and len(date_in_list[0]) == 4) \
                and (date_in_list[1].isdigit() and 1 <= int(date_in_list[1]) <= 12 and len(date_in_list[1]) == 2) \
                    and (date_in_list[2].isdigit() and 1 <= int(date_in_list[2]) <= 31 and len(date_in_list[2]) == 2)   
        return result

class IsContact(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        with sq.connect("database/users.db") as con:
            try:
                cur = con.cursor()   
                cur.execute(f"SELECT COUNT(*) FROM main_table WHERE id = {message.contact.user_id}")
                result = 1 != list(cur)[0][0]
                return message.contact != None and result
            except:
                return False
    