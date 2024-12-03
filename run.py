import asyncio
from aiogram import Bot, Dispatcher
from setings import TOKEN
from app.handlers import comands, callback_data, contact, feadback
from app.admin import admin_router
from bd.database import init_db


async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    init_db()
    dp.include_routers(comands.router, callback_data.router, contact.router, admin_router, feadback.feedback_router)
    await dp.start_polling(bot)
    
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('exit')
