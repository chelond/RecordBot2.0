from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bd.database import save_question
from setings import TOKEN, ADMIN_ID

from app.fsm_clases.feadback_class import Feedback

feedback_router = Router()
bot = Bot(TOKEN)


@feedback_router.callback_query(lambda c: c.data == "feedback")
async def feedback_callback(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Пожалуйста, задайте ваш вопрос:")
    await state.set_state(Feedback.ask_question)


@feedback_router.message(Feedback.ask_question)
async def process_question(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = message.from_user.username
    question = message.text
    message_id = message.message_id  # Получаем message_id

    # Сохраняем вопрос в базе данных с message_id
    save_question(user_id=user_id, question=question, message_id=message_id)

    # Отправляем вопрос всем администраторам
    for admin_id in ADMIN_ID:
        await bot.send_message(chat_id=admin_id, text=f"Новый вопрос от пользователя @{user_name}:\n\n{question}")

    # Уведомляем пользователя о том, что его вопрос принят
    await message.answer("Ваш вопрос принят. Ожидайте ответа.")
    await state.clear()