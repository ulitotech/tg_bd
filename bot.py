import asyncio
from aiogram import Bot, Dispatcher
from config_data.config import Config, load_config
from handlers import main_handlers, other_handlers
from keyboards.main_menu_button import set_menu
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from services.working import event_check
from datetime import datetime, timedelta,time

def kek(ke):
    print(f"lol {ke}")

async def main():
    
    # Создаем объекты бота и диспетчера
    config: Config = load_config()
    bot: Bot = Bot(token=config.tg_bot.token, parse_mode="MarkdownV2")
    dp = Dispatcher(storage=main_handlers.storage)
    
    #Создаем расписание напоминаний
    scheduler = AsyncIOScheduler(timezone = "Europe/Moscow")
    # scheduler.add_job(event_check, trigger = "cron", hour=10, minute=00, args=({'bot':bot}))
    # scheduler.add_job(event_check, trigger='data', datetime = datetime.now(), args=({'bot':bot}))
    scheduler.start()
    
    # Настраиваем главное меню бота
    await set_menu(bot)
    
    # Регистриуем роутеры в диспетчере
    dp.include_router(main_handlers.router)
    dp.include_router(other_handlers.router)
    
    #Запускаем поллинг бота
    await dp.start_polling(bot)

#Запускаем основную функцию    
if __name__ == '__main__':
    asyncio.run(main())
    