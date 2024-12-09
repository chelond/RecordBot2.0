from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from app.fsm_clases.feadback_class import Feedback
from bd.database import save_question, create_ticket, \
    save_ticket_message, close_ticket, get_ticket_history, get_user_data, get_ticket_id_by_message_id, \
    get_user_id_by_ticket_id, is_ticket_open
from setings import TOKEN, ADMIN_ID

feedback_router = Router()
bot = Bot(TOKEN)


# Состояние для отслеживания активного вопроса
class TicketState:
    active_ticket = {}


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

    # Создаем новый вопрос
    ticket_id = create_ticket(user_id)
    if ticket_id:
        TicketState.active_ticket[user_id] = ticket_id

        # Сохраняем вопрос в базе данных с message_id и ticket_id
        save_question(user_id=user_id, question=question, message_id=message_id, ticket_id=ticket_id)

        ticket_id = get_ticket_id_by_message_id(message_id)
        # Отправляем вопрос всем администраторам
        for admin_id in ADMIN_ID:
            await bot.send_message(chat_id=admin_id,
                                   text=f"Номер вопроса: {ticket_id}\nНовый вопрос от пользователя @{user_name}:\n\n{question} \n",
                                   reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                       [InlineKeyboardButton(text="Закрыть вопрос",
                                                             callback_data=f"close_ticket_{ticket_id}")],
                                       [InlineKeyboardButton(text="История сообщений",
                                                             callback_data=f"history_{ticket_id}")],
                                   ]))

        # Уведомляем пользователя о том, что его вопрос принят
        await message.answer(
            "Ваш вопрос принят. Ожидайте ответа.\n\n В случае если Вы получили ответ на свой вопрос или он стал не "
            "актуален нажмите на кнопку ниже",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Закрыть вопрос", callback_data=f"user_close_ticket_{ticket_id}")]
            ]))
        await state.clear()


@feedback_router.callback_query(F.data.startswith("user_close_ticket_"))
async def user_close_ticket_callback(callback_query: CallbackQuery):
    ticket_id = int(callback_query.data.split("_")[3])
    user_id = callback_query.from_user.id

    if close_ticket(ticket_id):
        await callback_query.message.answer("Ваш вопрос закрыт.")
        if user_id in TicketState.active_ticket:
            del TicketState.active_ticket[user_id]

        # Уведомление администраторов о закрытии вопроса пользователем
        for admin_id in ADMIN_ID:
            await bot.send_message(chat_id=admin_id,
                                   text=f"Пользователь @{callback_query.from_user.username} закрыл свой вопрос (ID: {ticket_id}).")
    else:
        await callback_query.message.answer("Ошибка при закрытии вопрос.")


@feedback_router.message(F.text)
async def forward_message_to_admin(message: Message):
    user_id = message.from_user.id
    if user_id in TicketState.active_ticket:
        ticket_id = TicketState.active_ticket[user_id]

        # Проверка статуса вопроса
        if not is_ticket_open(ticket_id):
            await message.answer(
                "Ваш вопрос закрыт. Чтобы задать новый вопрос, воспользуйтесь кнопкой 'Обратная связь'.")
            return

        message_id = message.message_id
        save_ticket_message(ticket_id, user_id, message.text, message_id)
        for admin_id in ADMIN_ID:
            ticket_id = get_ticket_id_by_message_id(message_id)
            await bot.send_message(chat_id=admin_id,
                                   text=f"Номер вопроса: {ticket_id}\nСообщение от пользователя @{message.from_user.username}:\n\n{message.text}",
                                   reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                       [InlineKeyboardButton(text="Закрыть вопрос",
                                                             callback_data=f"close_ticket_{ticket_id}")],
                                       [InlineKeyboardButton(text="История сообщений",
                                                             callback_data=f"history_{ticket_id}")],
                                       [InlineKeyboardButton(text="Данные пользователя",
                                                             callback_data=f"user_data_{user_id}")]
                                   ]))

        await message.answer(
            "Ваше сообщение принято. Ожидайте ответа\n\n В случае если Вы получили ответ на свой вопрос или он стал не актуален нажмите на кнопку ниже",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Закрыть вопрос", callback_data=f"user_close_ticket_{ticket_id}")]
            ]))
    else:
        await message.answer("Вы еще не задали вопрос. Чтобы это исправить воспользуйтесь кнопкой 'Обратная связь'")


@feedback_router.callback_query(F.data.startswith("close_ticket_"))
async def close_ticket_callback(callback_query: CallbackQuery):
    ticket_id = int(callback_query.data.split("_")[2])
    if close_ticket(ticket_id):
        await callback_query.message.answer("вопрос закрыт.")

        # Уведомление пользователя о закрытии вопроса
        user_id = get_user_id_by_ticket_id(ticket_id)
        if user_id:
            await bot.send_message(chat_id=user_id, text=f"Ваш вопрос (ID: {ticket_id}) был закрыт администратором.")
    else:
        await callback_query.message.answer("Ошибка при закрытии вопроса.")


@feedback_router.callback_query(F.data.startswith("history_"))
async def history_callback(callback_query: CallbackQuery):
    ticket_id = int(callback_query.data.split("_")[1])
    messages = get_ticket_history(ticket_id)
    if messages:
        history = []
        for msg in messages:
            user_message = f"{msg[2]}: {msg[0]} ({msg[1]})"
            history.append(user_message)
            if msg[3]:  # Check if there is an answer
                admin_message = f"Администратор {msg[5]}: {msg[3]} ({msg[4]})"
                history.append(admin_message)
        history_text = "\n".join(history)
        await callback_query.message.answer(f"История сообщений вопроса {ticket_id}:\n\n{history_text}")
    else:
        await callback_query.message.answer("История сообщений пуста.")


@feedback_router.callback_query(F.data.startswith("user_data_"))
async def user_data_callback(callback_query: CallbackQuery):
    user_id = int(callback_query.data.split("_")[2])
    user_data = get_user_data(user_id)
    if user_data:
        response = (
            f"Данные пользователя {user_id}:\n\n"
            f"User ID: {user_data[1]}\n"
            f"Номер телефона: {user_data[2]}\n"
            f"Имя: {user_data[3]}\n"
            f"Вид программы: {user_data[4]}\n"
            f"Никнейм в телеграмме: @{user_data[5]}"
        )
        await callback_query.message.answer(response)
    else:
        await callback_query.message.answer("Данные пользователя не найдены.")
