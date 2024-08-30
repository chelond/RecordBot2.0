from aiogram import Bot
from bd.database import get_user_data
from setings import ADMIN_ID, TOKEN

bot = Bot(TOKEN)

async def get_data_for_admin(user_id):
    user_data = get_user_data(user_id)
    if user_data:
        response = f"Новая заявка для пользователя: {user_id}:\n\n"
        response += f"User ID: {user_data[1]}\n\n номер телефона: {user_data[2]}, Имя: {user_data[3]}\n\n Вид программы: {user_data[4]}\n\n Никнейм в телеграмме: @{user_data[5]}\n"
    else:
        response = f"Данные для user_id {user_id} не найдены."
    await bot.send_message(chat_id=ADMIN_ID, text=response,)