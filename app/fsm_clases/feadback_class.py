from aiogram.fsm.state import State, StatesGroup


class Feedback(StatesGroup):
    ask_question = State()
    answer_question = State()


class Mailing(StatesGroup):
    text = State()
    photo = State()
    photo_send = State()
    caption = State()
    confirm = State()
