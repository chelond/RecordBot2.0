from aiogram import Router, Bot, types
from aiogram.types import CallbackQuery
from setings import TOKEN, PHOTO_PATH
from app.keyboards import contact_keyboard, inline_keyboard_back, inline_keyboard
from bd.database import save_user_program, get_phone_number
from app.text import program_1, program_2, program_3, program_4, program_5, program_6, program_7, program_8, \
    program_list
from app.utils.schedule import admin_create_schedule

router = Router()
bot = Bot(TOKEN)
text = """Для получения программы отправьте Ваш номер телефона
"""


@router.callback_query(lambda c: c.data == "program")
async def program(callback_query: CallbackQuery):
    await callback_query.message.answer(text=program_list, reply_markup=inline_keyboard)


@router.callback_query(lambda c: c.data == "schedule")
async def schedule(callback_query: CallbackQuery):
    await admin_create_schedule()
    await callback_query.message.answer_photo(types.FSInputFile(path=PHOTO_PATH))


@router.callback_query(lambda c: c.data == 'back')
async def back(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id,
                                text=program_list, reply_markup=inline_keyboard)


@router.callback_query(lambda c: c.data == 'program_1')
async def process_callback_program_1(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    is_phone = get_phone_number(callback_query.from_user.id)

    if is_phone:
        await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id,
                                    text=program_1, reply_markup=inline_keyboard_back)
    else:
        await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id,
                                    text=text)
        await bot.send_message(chat_id=callback_query.from_user.id,
                               text="Для отправки контакта нажмите на кнопку «Отправить контакт»",
                               reply_markup=contact_keyboard)
        save_user_program(user_id=callback_query.from_user.id,
                          program="Тренировки для подростка 12-14лет от Владимира Мелтникова")


@router.callback_query(lambda c: c.data == 'program_2')
async def process_callback_program_1(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    is_phone = get_phone_number(callback_query.from_user.id)

    if is_phone:
        await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id,
                                    text=program_2, reply_markup=inline_keyboard_back)
    else:
        await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id,
                                    text=text)
        await bot.send_message(chat_id=callback_query.from_user.id,
                               text="Для отправки контакта нажмите на кнопку «Отправить контакт»",
                               reply_markup=contact_keyboard)
        save_user_program(user_id=callback_query.from_user.id,
                          program="Сила и выносливость ног: комплекс для настоящих бойцов от Сергея Бронникова")


@router.callback_query(lambda c: c.data == 'program_3')
async def process_callback_program_1(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    is_phone = get_phone_number(callback_query.from_user.id)

    if is_phone:
        await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id,
                                    text=program_3, reply_markup=inline_keyboard_back)
    else:
        await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id,
                                    text=text)
        await bot.send_message(chat_id=callback_query.from_user.id,
                               text="Для отправки контакта нажмите на кнопку «Отправить контакт»",
                               reply_markup=contact_keyboard)
        save_user_program(user_id=callback_query.from_user.id,
                          program="Тонус и рельеф: путь к идеальному телу от Анастасии Мельниковой")


@router.callback_query(lambda c: c.data == 'program_4')
async def process_callback_program_1(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    is_phone = get_phone_number(callback_query.from_user.id)

    if is_phone:
        await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id,
                                    text=program_4, reply_markup=inline_keyboard_back)
    else:
        await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id,
                                    text=text)
        await bot.send_message(chat_id=callback_query.from_user.id,
                               text="Для отправки контакта нажмите на кнопку «Отправить контакт»",
                               reply_markup=contact_keyboard)
        save_user_program(user_id=callback_query.from_user.id,
                          program="Красивые и соблазнительные ягодицы от Анастасии Мельниковой")


@router.callback_query(lambda c: c.data == 'program_5')
async def process_callback_program_1(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    is_phone = get_phone_number(callback_query.from_user.id)

    if is_phone:
        await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id,
                                    text=program_5, reply_markup=inline_keyboard_back)
    else:
        await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id,
                                    text=text)
        await bot.send_message(chat_id=callback_query.from_user.id,
                               text="Для отправки контакта нажмите на кнопку «Отправить контакт»",
                               reply_markup=contact_keyboard)
        save_user_program(user_id=callback_query.from_user.id,
                          program="Архитектура спины: создаем идеальные дельты от Любовь Сткляниной")


@router.callback_query(lambda c: c.data == 'program_6')
async def process_callback_program_1(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    is_phone = get_phone_number(callback_query.from_user.id)

    if is_phone:
        await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id,
                                    text=program_6, reply_markup=inline_keyboard_back)
    else:
        await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id,
                                    text=text)
        await bot.send_message(chat_id=callback_query.from_user.id,
                               text="Для отправки контакта нажмите на кнопку «Отправить контакт»",
                               reply_markup=contact_keyboard)
        save_user_program(user_id=callback_query.from_user.id, program="Сила и форма: трансформация широчайшей мышцы")


@router.callback_query(lambda c: c.data == 'program_7')
async def process_callback_program_1(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    is_phone = get_phone_number(callback_query.from_user.id)

    if is_phone:
        await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id,
                                    text=program_7, reply_markup=inline_keyboard_back)
    else:
        await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id,
                                    text=text)
        await bot.send_message(chat_id=callback_query.from_user.id,
                               text="Для отправки контакта нажмите на кнопку «Отправить контакт»",
                               reply_markup=contact_keyboard)
        save_user_program(user_id=callback_query.from_user.id,
                          program="Бицепс на максимум: раскрой свой потенциал от Рузиля Газизова")


@router.callback_query(lambda c: c.data == 'program_8')
async def process_callback_program_1(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    is_phone = get_phone_number(callback_query.from_user.id)

    if is_phone:
        await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id,
                                    text=program_8, reply_markup=inline_keyboard_back)
    else:
        await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id,
                                    text=text)
        await bot.send_message(chat_id=callback_query.from_user.id,
                               text="Для отправки контакта нажмите на кнопку «Отправить контакт»",
                               reply_markup=contact_keyboard)
        save_user_program(user_id=callback_query.from_user.id,
                          program="«Прокачай свои грудные» от тренера Рузиля Газизова")
