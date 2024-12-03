from aiogram import Router, F
from aiogram.types import Message, ContentType
from bd.database import save_user_contact, get_program
from app.admin import get_data_for_admin
from app.text import program_1, program_2, program_3, program_4, program_5, program_6, program_7, program_8
from app.keyboards import inline_keyboard_back

router = Router()


@router.message(F.content_type == ContentType.CONTACT)
async def handle_contact(message: Message):
    contact = message.contact
    user_id = message.from_user.id
    phone_number = contact.phone_number
    first_name = contact.first_name
    username = message.from_user.username
    save_user_contact(user_id, phone_number, first_name, username)
    await get_data_for_admin(user_id=message.from_user.id)
    program = get_program(user_id=message.from_user.id)
    match program:
        case "Тренировки для подростка 12-14лет от Владимира Мелтникова":
            await message.answer(text=program_1, reply_markup=inline_keyboard_back)
        case "Сила и выносливость ног: комплекс для настоящих бойцов от Сергея Бронникова":
            await message.answer(text=program_2, reply_markup=inline_keyboard_back)
        case "Тонус и рельеф: путь к идеальному телу от Анастасии Мельниковой":
            await message.answer(text=program_3, reply_markup=inline_keyboard_back)
        case "Красивые и соблазнительные ягодицы от Анастасии Мельниковой":
            await message.answer(text=program_4, reply_markup=inline_keyboard_back)
        case "Архитектура спины: создаем идеальные дельты от Любовь Сткляниной":
            await message.answer(text=program_5, reply_markup=inline_keyboard_back)
        case "Сила и форма: трансформация широчайшей мышцы":
            await message.answer(text=program_6, reply_markup=inline_keyboard_back)
        case "Бицепс на максимум: раскрой свой потенциал от Рузиля Газизова":
            await message.answer(text=program_7, reply_markup=inline_keyboard_back)
        case "Прокачай свои грудные» от тренера Рузиля Газизова":
            await message.answer(text=program_8, reply_markup=inline_keyboard_back)
