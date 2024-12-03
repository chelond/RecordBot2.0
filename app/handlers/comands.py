from aiogram import Router, F
from aiogram.types import Message
from app.keyboards import general_menu
from app.text import welcome
from bd.database import add_user_if_not_exists

router = Router()


@router.message(F.text == "/start")
async def send_welcome(message: Message):
    user_id = message.from_user.id
    add_user_if_not_exists(user_id)
    await message.reply(welcome, reply_markup=general_menu)
