from aiogram import types, Dispatcher
from database.db import conn, cursor
from handlers.kb_buy_handlers import DEVELOPER_ID
from services.ai_limit import increment_ai_requests, check_ai_limit
from services.ai_service import ask_openrouter
from services.prompts import PORTFEL_EXPLANATION
from loader import dp


async def myadvice(message: types.Message):
    """
    Анализ портфеля пользователя с помощью ИИ
    """
    user_id = message.from_user.id

    # Проверка лимита ИИ
    try:
        if not check_ai_limit(user_id):
            await message.answer(
                "❌ **Лимит исчерпан**\n"
                "Вы использовали все 10 запросов к ИИ на сегодня.\n"
                "Завтра лимит обновится!",
                parse_mode="Markdown"
            )
            return
    except Exception as e:
        print(f"❌ Ошибка проверки лимита для пользователя {user_id}: {e}")
        await message.answer(
            "⚠️ **Ошибка проверки лимита**\n"
            "Пожалуйста, попробуйте позже.",
            parse_mode="Markdown"
        )
        return

    # Получаем данные пользователя из БД
    try:
        cursor.execute("SELECT balance, btc_balance, eth_balance FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
    except Exception as e:
        print(f"❌ Ошибка БД для пользователя {user_id}: {e}")
        await message.answer(
            "⚠️ **Ошибка базы данных**\n"
            "Пожалуйста, нажмите /start и попробуйте снова.",
            parse_mode="Markdown"
        )
        return

    if not result:
        await message.answer(
            "👋 **Добро пожаловать!**\n"
            "Сначала нажмите /start, чтобы зарегистрироваться.",
            parse_mode="Markdown"
        )
        return

    balance, btc, eth = result

    # Получаем актуальные цены
    try:
        crypto_service = dp['crypto_service']
        btc_price = crypto_service.get_btc_price()
        eth_price = crypto_service.get_eth_price()

        if not btc_price or not eth_price:
            raise ValueError("Не удалось получить цены криптовалют")
    except Exception as e:
        print(f"❌ Ошибка получения цен: {e}")
        await message.answer(
            "⚠️ **Временные трудности**\n"
            "Не удалось получить актуальные цены. Попробуйте позже.",
            parse_mode="Markdown"
        )
        return

    # Рассчитываем стоимость портфеля в USD
    try:
        btc_usd = btc * btc_price
        eth_usd = eth * eth_price
        total_usd = balance + btc_usd + eth_usd
    except Exception as e:
        print(f"❌ Ошибка расчёта стоимости портфеля: {e}")
        await message.answer(
            "⚠️ **Ошибка расчёта**\n"
            "Пожалуйста, попробуйте позже.",
            parse_mode="Markdown"
        )
        return

    # Формируем промпт для ИИ
    user_prompt = f"""
    Проанализируй портфель пользователя и дай персонализированный совет.

    📊 **ТЕКУЩИЙ ПОРТФЕЛЬ:**
    • 💵 Доллары: ${balance:,.2f}
    • ₿ Bitcoin: {btc:.6f} BTC (${btc_usd:,.2f})
    • Ξ Ethereum: {eth:.6f} ETH (${eth_usd:,.2f})

    💰 **ОБЩАЯ СТОИМОСТЬ:** ${total_usd:,.2f}

    Дай совет по управлению портфелем для новичка в криптотрейдинге.
    Учти текущее распределение активов и рыночную ситуацию.
    """

    # Отправляем запрос к ИИ
    try:
        await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
        answer = ask_openrouter(PORTFEL_EXPLANATION, user_prompt, max_tokens=200)

        # Проверяем, не вернул ли ИИ ошибку
        if answer.startswith("❌") or "ошибк" in answer.lower() or "error" in answer.lower():
            await message.answer(
                f"⚠️ **ИИ временно недоступен**\n\n{answer}",
                parse_mode="Markdown"
            )
        else:
            # Успешный ответ
            portfolio_summary = (
                f"📊 **АНАЛИЗ ПОРТФЕЛЯ**\n\n"
                f"💵 Доллары: ${balance:,.2f}\n"
                f"₿ BTC: {btc:.6f} (${btc_usd:,.2f})\n"
                f"Ξ ETH: {eth:.6f} (${eth_usd:,.2f})\n"
                f"💰 **Итого: ${total_usd:,.2f}**\n\n"
                f"🤖 **Совет ИИ:**\n{answer}"
            )
            await message.answer(portfolio_summary, parse_mode="Markdown")

            # Увеличиваем счётчик запросов (только для обычных пользователей)
            if user_id != DEVELOPER_ID:
                try:
                    increment_ai_requests(user_id)
                except Exception as e:
                    print(f"❌ Ошибка увеличения счётчика для {user_id}: {e}")

    except Exception as e:
        print(f"❌ Ошибка вызова ИИ для пользователя {user_id}: {e}")
        await message.answer(
            "⚠️ **Ошибка при обращении к ИИ**\n"
            "Пожалуйста, попробуйте позже.",
            parse_mode="Markdown"
        )


def register_handlers_portfelio(dp: Dispatcher):
    """Регистрация хендлера анализа портфеля"""
    dp.register_message_handler(
        myadvice,
        lambda message: message.text == "📋 Анализ Портфеля"
    )