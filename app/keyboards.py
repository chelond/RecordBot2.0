from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

inline_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="1", callback_data='program_1'),
            InlineKeyboardButton(text="2", callback_data='program_2'),
            InlineKeyboardButton(text="3", callback_data='program_3'),
            InlineKeyboardButton(text="4", callback_data='program_4'),
        ],
        [
            InlineKeyboardButton(text="5", callback_data='program_5'),
            InlineKeyboardButton(text="6", callback_data='program_6'),
            InlineKeyboardButton(text="7", callback_data='program_7'),
            InlineKeyboardButton(text="8", callback_data='program_8'),   
        ]
    ]
)

inline_keyboard_back = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Поменять программу", callback_data='back'),]
    ]
)

contact_button = [
    [
        KeyboardButton(text="Отправить контакт", request_contact=True, one_time_keyboard=True)
    ]
]
contact_keyboard = ReplyKeyboardMarkup(keyboard=contact_button, resize_keyboard=True)