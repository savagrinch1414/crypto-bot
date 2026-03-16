from aiogram.dispatcher.filters.state import State, StatesGroup

class AskStates(StatesGroup):
    waiting_for_question = State()