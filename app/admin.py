from aiogram import Bot, Router, F
from aiogram import Dispatcher, types
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiosqlite import connect
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
import structlog
from contextvars import ContextVar

from app.utils.schedule import admin_create_schedule
from bd.database import get_user_data, save_answer, get_user_id_by_question_id, get_question_by_message_id, \
    get_question_and_username_by_message_id
from app.fsm_clases.feadback_class import Mailing
from setings import ADMIN_ID, TOKEN, PHOTO_PATH

# Configure structured logging
logger = structlog.get_logger(__name__)

# Initialize core components
dp = Dispatcher(storage=MemoryStorage())
bot = Bot(TOKEN)
admin_router = Router()

# Database and caching setup
db_pool = ContextVar('db_pool', default=None)
cache = {}
CACHE_TIMEOUT = 300  # 5 minutes
BATCH_SIZE = 30  # Number of messages to send in one batch


async def get_data_for_admin(user_id: int) -> None:
    """Get and send user data to all admins with error handling"""
    try:
        user_data = get_user_data(user_id)
        if user_data:
            response = (
                f"Пользователь выбрал программу: {user_id}:\n\n"
                f"User ID: {user_data[1]}\n"
                f"Номер телефона: {user_data[2]}\n"
                f"Имя: {user_data[3]}\n"
                f"Вид программы: {user_data[4]}\n"
                f"Никнейм в телеграмме: @{user_data[5]}"
            )
        else:
            response = f"Данные для user_id {user_id} не найдены."

        for admin_id in ADMIN_ID:
            await bot.send_message(chat_id=admin_id, text=response)
    except Exception as e:
        logger.error(f"Error in get_data_for_admin: {e}")
        for admin_id in ADMIN_ID:
            await bot.send_message(
                chat_id=admin_id,
                text="Произошла ошибка при получении данных пользователя."
            )


@asynccontextmanager
async def get_db_connection():
    """Context manager for database connections with connection pooling"""
    if db_pool.get() is None:
        async with connect('users.db') as db:
            db_pool.set(db)
            yield db
    else:
        yield db_pool.get()


def handle_error(func):
    """Decorator for consistent error handling"""

    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(
                "operation_failed",
                function=func.__name__,
                error=str(e),
                args=args,
                kwargs=kwargs
            )
            raise

    return wrapper


async def get_cached_user_data(user_id: int) -> Optional[Tuple]:
    """Get user data with caching"""
    current_time = datetime.now()
    if user_id in cache:
        data, timestamp = cache[user_id]
        if current_time - timestamp < timedelta(seconds=CACHE_TIMEOUT):
            return data

    user_data = get_user_data(user_id)
    if user_data:
        cache[user_id] = (user_data, current_time)
    return user_data


async def send_message_to_user(user_id: int, data: Dict[str, Any]) -> bool:
    """Send a message to a single user with error handling"""
    try:
        if data.get("photo"):
            await bot.send_photo(
                chat_id=user_id,
                photo=data["photo"],
                caption=data.get("caption", "")
            )
        else:
            await bot.send_message(chat_id=user_id, text=data["text"])
        return True
    except Exception as e:
        logger.error(f"Failed to send message to {user_id}", error=str(e))
        return False


async def send_batch_messages(users: list, data: Dict[str, Any], batch_size: int = BATCH_SIZE):
    """Send messages in batches to avoid rate limiting"""
    for i in range(0, len(users), batch_size):
        batch = users[i:i + batch_size]
        tasks = [send_message_to_user(user_id[0], data) for user_id in batch]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        await asyncio.sleep(1)  # Rate limiting pause between batches
        yield sum(1 for r in results if r is True), sum(1 for r in results if r is False)


@admin_router.message(F.text == "/schedule", F.from_user.id.in_(ADMIN_ID))
@handle_error
async def schedule(message: Message):
    await admin_create_schedule()
    await message.answer_photo(types.FSInputFile(path="/home/chel/PycharmProjects/RecordBot2.0/schedule.png"))


@admin_router.message(F.text == "рассылка", F.from_user.id.in_(ADMIN_ID))
@handle_error
async def cmd_mailing(message: Message, state: FSMContext):
    """Start the mailing process"""
    await message.answer("Введите текст для рассылки:")
    await state.set_state(Mailing.text)


@admin_router.message(Mailing.text)
@handle_error
async def process_mailing_text(message: Message, state: FSMContext):
    """Process mailing text"""
    await state.update_data(text=message.text)
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Да"), types.KeyboardButton(text="Нет"))
    await message.answer(
        "Хотите добавить фотографию?",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )
    await state.set_state(Mailing.photo)


@admin_router.message(Mailing.photo)
@handle_error
async def process_mailing_photo(message: Message, state: FSMContext):
    """Handle the decision to add a photo"""
    if not message.text:
        await message.answer("Пожалуйста, используйте кнопки 'Да' или 'Нет'.")
        return

    if message.text.lower() == "да":
        await message.answer("Отправьте фотографию:")
        await state.set_state(Mailing.photo_send)
    elif message.text.lower() == "нет":
        await state.update_data(photo=None, caption=None)
        await confirm_mailing(message, state)
    else:
        await message.answer("Пожалуйста, используйте кнопки 'Да' или 'Нет'.")


@admin_router.message(Mailing.photo_send, F.photo)
@handle_error
async def process_photo(message: Message, state: FSMContext):
    """Process the uploaded photo"""
    photo = message.photo[-1].file_id
    await state.update_data(photo=photo)
    await message.answer("Введите подпись к фотографии (или отправьте пустое сообщение, если подпись не нужна):")
    await state.set_state(Mailing.caption)


@admin_router.message(Mailing.caption)
@handle_error
async def process_caption(message: Message, state: FSMContext):
    """Process the caption for the photo"""
    await state.update_data(caption=message.text or "")
    await confirm_mailing(message, state)


async def confirm_mailing(message: Message, state: FSMContext):
    """Show the mailing preview and ask for confirmation"""
    data = await state.get_data()

    if data.get("photo"):
        await message.answer_photo(
            photo=data["photo"],
            caption=data.get("caption", "")
        )
    else:
        await message.answer(data["text"])

    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Да"), types.KeyboardButton(text="Нет"))
    await message.answer(
        "Вы уверены, что хотите отправить это?",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )
    await state.set_state(Mailing.confirm)


@admin_router.message(Mailing.confirm)
@handle_error
async def send_mailing(message: Message, state: FSMContext):
    """Send the mailing to all users with batch processing"""
    if message.text.lower() != "да":
        await message.answer("Рассылка отменена.", reply_markup=types.ReplyKeyboardRemove())
        await state.clear()
        return

    data = await state.get_data()
    total_success = 0
    total_fail = 0

    try:
        async with get_db_connection() as db:
            async with db.execute("SELECT user_id FROM users") as cursor:
                users = await cursor.fetchall()

        async for success, fail in send_batch_messages(users, data):
            total_success += success
            total_fail += fail

        await message.answer(
            f"Рассылка завершена.\n"
            f"Успешно отправлено: {total_success}\n"
            f"Не удалось отправить: {total_fail}",
            reply_markup=types.ReplyKeyboardRemove()
        )
    except Exception as e:
        logger.error("Mailing failed", error=str(e))
        await message.answer("Произошла ошибка при рассылке.", reply_markup=types.ReplyKeyboardRemove())
    finally:
        await state.clear()


@admin_router.message(F.reply_to_message, F.from_user.id.in_(ADMIN_ID))
@handle_error
async def answer_question(message: Message, **kwargs):
    """Обработка ответа администратора на вопросы пользователей"""
    if message.from_user.id not in ADMIN_ID:
        await message.answer("У вас нет прав для выполнения этой команды.")
        return

    admin_index = ADMIN_ID.index(message.from_user.id)
    question_message_id = message.reply_to_message.message_id - (admin_index + 1)
    answer = message.text

    print(f"Handling answer for message_id={question_message_id}")

    # Получение user_id из базы данных
    user_id = get_user_id_by_question_id(question_message_id)

    if not user_id:
        print(f"User not found for message_id={question_message_id}")
        await message.answer("❌ Пользователь для этого вопроса не найден.")
        return

    print(f"Found user_id={user_id} for message_id={question_message_id}")

    # Получение вопроса и username из базы данных
    question, username = get_question_and_username_by_message_id(question_message_id)

    if not question:
        await message.answer("❌ Вопрос не найден в базе данных.")
        return

    # Попытка доставить сообщение пользователю
    try:
        await bot.send_message(
            chat_id=user_id,
            text=f"Ответ на ваш вопрос:\n\n{answer}"
        )
        await message.answer("✅ Ответ успешно доставлен пользователю.")
    except Exception as e:
        error_message = "❌ Не удалось доставить ответ пользователю.\n"

        if "Forbidden" in str(e):
            error_message += "Причина: Пользователь заблокировал бота."
        elif "ChatNotFound" in str(e):
            error_message += "Причина: Чат с пользователем не найден."
        else:
            error_message += f"Причина: {str(e)}"

        await message.answer(error_message)

    # Сохранение ответа в базе данных
    save_answer(question_message_id, answer)

    admin_info = await bot.get_chat(message.from_user.id)
    admin_username = admin_info.username or admin_info.first_name

    for other_admin_id in ADMIN_ID:
        if other_admin_id != message.from_user.id:
            await bot.send_message(
                chat_id=other_admin_id,
                text=(f"Администратор @{admin_username} ответил на вопрос от пользователя @{username}:\n\n"
                      f"Вопрос: {question}\n\n"
                      f"Ответ: {answer}")
            )