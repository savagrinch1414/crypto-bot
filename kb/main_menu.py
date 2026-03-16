from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# ==================== ГЛАВНОЕ МЕНЮ ====================
menu_kb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    row_width=2  # по 2 кнопки в ряду
)

# Кнопки с эмодзи для наглядности
btn_profile = KeyboardButton("👤 Профиль")
btn_rating = KeyboardButton("🏆 Рейтинг")
btn_buy = KeyboardButton("💰 Купить")
btn_sell = KeyboardButton("💸 Продать")
btn_analise_btc = KeyboardButton("📊 Анализ BTC")
btn_analise_eth = KeyboardButton("📈 Анализ ETH")
btn_analise_portfel = KeyboardButton("📋 Анализ Портфеля")
btn_ask = KeyboardButton("🤖 Задать вопрос")
prices_btn = KeyboardButton("💵 Цены валют")


# Добавляем кнопки в меню (по 2 в ряд)
menu_kb.add(btn_profile, btn_rating)
menu_kb.add(btn_buy, btn_sell)
menu_kb.add(btn_analise_btc, btn_analise_eth)
menu_kb.add(btn_analise_portfel, btn_ask)
menu_kb.add(prices_btn)
# добавили кнопку вопроса

# ==================== КЛАВИАТУРА ОТМЕНЫ ====================
cancel_kb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    row_width=1
)
cancel_kb.add(KeyboardButton("❌ Отмена"))