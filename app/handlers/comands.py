import asyncio
from aiogram import Router, F
from aiogram.types import Message
from app.keyboards import inline_keyboard
from app.text import program_list, welcome

router = Router()

@router.message(F.text == "/start")
async def send_welcome(message: Message):
    await message.reply(welcome)
    await asyncio.sleep(5)
    await message.answer(text=program_list, reply_markup=inline_keyboard)

