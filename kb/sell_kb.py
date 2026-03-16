from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.callback import trade_cb, confirm_kb

sell_kb = InlineKeyboardMarkup(row_width=2)
sell_kb.add(
    InlineKeyboardButton(
        text="₿ Продать BTC",
        callback_data=trade_cb.new(action="sell", coin="BTC")
    ),
    InlineKeyboardButton(
        text="Ξ Продать ETH",
        callback_data=trade_cb.new(action="sell", coin="ETH")
    )
)






