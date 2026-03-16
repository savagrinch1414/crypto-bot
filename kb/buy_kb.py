from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.callback import trade_cb

buy_kb = InlineKeyboardMarkup(row_width=2)
buy_kb.add(
    InlineKeyboardButton(
        text="₿ Купить BTC",
        callback_data=trade_cb.new(action="buy", coin="BTC")
    ),
    InlineKeyboardButton(
        text="Ξ Купить ETH",
        callback_data=trade_cb.new(action="buy", coin="ETH")
    )
)






