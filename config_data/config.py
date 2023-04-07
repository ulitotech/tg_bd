from dataclasses import dataclass
from environs import Env

@dataclass
class TgBot:
    token: str            # Токен для доступа к телеграм-боту
    superuser_id: int # id суперюзера

@dataclass
class Config:
    tg_bot: TgBot

# Создаем функцию, которая будет читать файл .env и возвращать
# экземпляр класса Config с заполненными полями
def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(
                    token=env('BOT_TOKEN'),
                    superuser_id=env('SUPER_USER_ID')))