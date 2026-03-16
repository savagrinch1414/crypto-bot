from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

class BuyOrSellStates(StatesGroup):
    waiting_coin = State()
    waiting_amount = State()
    confirming_trade = State()