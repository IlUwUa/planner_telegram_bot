import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import TOKEN
from handlers import router
import database as db
import scheduler


logging.basicConfig(level=logging.INFO)

async def main():
    db.init_db()
    

    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    
    dp.include_router(router)

    asyncio.create_task(scheduler.start_scheduler(bot))
    print("Бот запущен!")

    await dp.start_polling(bot, drop_pending_updates=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")