from aiogram import Bot
from aiogram.types import BotCommand

# Функция для настройки кнопки Menu бота
async def set_menu(bot: Bot):
    main_menu_command = [BotCommand(
        command="/start",
        description="Стартовое меню бота"
        ),
                         BotCommand(
                             command="/help",
                             description="Получить справку по работе бота"
                             )
                         ]
    await bot.set_my_commands(main_menu_command)