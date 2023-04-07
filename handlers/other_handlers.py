from aiogram import Router
from aiogram.types import Message
from filters.filters import Is_Admin, Is_Superuser
from environs import Env


env = Env()
env.read_env()

router: Router = Router()
STICKER_ID = "CAACAgIAAxkBAAEIQndkHVLSswuvSdX36rpXc4Y8ZV6vcgACGwMAAs-71A7CHN2zMqnsdS8E"

@router.message(~Is_Admin(),~Is_Superuser(), lambda message:message.chat.id!=f"-100{env('MAIN_CHAT')}")
async def message_for_other(message: Message):
    """Отвечает на сообщения обычных юзеров"""
    await message.answer_sticker(sticker=STICKER_ID)
    await message.answer("Не для тебя моя приборная панель создавалась\)")
    await message.delete()
