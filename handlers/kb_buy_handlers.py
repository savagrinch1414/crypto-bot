from kb.main_menu import cancel_kb, menu_kb
from loader import dp
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from database.db import conn, cursor
from services.ai_limit import check_ai_limit, increment_ai_requests
from services.ai_service import ask_openrouter
from services.prompts import TRADE_EXPLANATION
from states.buy_or_sell_states import BuyOrSellStates
from kb.buy_kb import buy_kb
from kb.sell_kb import sell_kb
from services.buy_sell_services import buy, sell, update_rating

DEVELOPER_ID = 1628601883


async def buy_crypto(message: types.Message):
    """Показывает меню выбора монеты для покупки"""
    await message.answer(
        "🛒 **Что хотите купить?**\n\n"
        "Выберите монету из списка ниже:",
        reply_markup=buy_kb,
        parse_mode="Markdown"
    )


async def sell_crypto(message: types.Message):
    """Показывает меню выбора монеты для продажи"""
    await message.answer(
        "💰 **Что хотите продать?**\n\n"
        "Выберите монету из списка ниже:",
        reply_markup=sell_kb,
        parse_mode="Markdown"
    )


async def process_trade_callback(callback: types.CallbackQuery, state: FSMContext):
    """Обрабатывает выбор монеты для покупки/продажи"""
    print(f"=== process_trade_callback, data: {callback.data} ===")

    try:
        _, action, coin = callback.data.split(":")

        # Получаем актуальные цены
        try:
            crypto_service = dp['crypto_service']
            btc_price = crypto_service.get_btc_price()
            eth_price = crypto_service.get_eth_price()
        except Exception as e:
            print(f"❌ Ошибка получения цен: {e}")
            await callback.message.answer(
                "⚠️ **Временные трудности**\n"
                "Не удалось получить актуальные цены. Попробуйте позже.",
                parse_mode="Markdown"
            )
            await callback.answer()
            return

        if coin == "BTC":
            price = btc_price
            rsi = crypto_service.get_rsi('BTCUSDT')
        elif coin == "ETH":
            price = eth_price
            rsi = crypto_service.get_rsi('ETHUSDT')
        else:
            await callback.message.answer("❌ **Неизвестная монета**")
            await callback.answer()
            return

        if rsi is not None:
            if rsi > 70:
                rsi_text = f"⚡ **RSI (14):** {rsi} – перекупленность (осторожно)"
            elif rsi < 30:
                rsi_text = f"🧊 **RSI (14):** {rsi} – перепроданность (возможен отскок)"
            else:
                rsi_text = f"📊 **RSI (14):** {rsi} – нейтрально"
        else:
            rsi_text = "📊 RSI временно недоступен"


        action_word = "покупки" if action == "buy" else "продажи"
        action_emoji = "🛒" if action == "buy" else "💰"

        # Получаем данные пользователя
        try:
            cursor.execute("SELECT balance, btc_balance, eth_balance FROM users WHERE id = ?", (callback.from_user.id,))
            result = cursor.fetchone()
        except Exception as e:
            print(f"❌ Ошибка БД: {e}")
            await callback.message.answer(
                "⚠️ **Ошибка базы данных**\n"
                "Попробуйте позже или нажмите /start",
                parse_mode="Markdown"
            )
            await callback.answer()
            return

        if not result:
            await callback.message.answer(
                "👋 **Добро пожаловать!**\n"
                "Сначала нажмите /start, чтобы зарегистрироваться.",
                parse_mode="Markdown"
            )
            await callback.answer()
            return

        balance, btc_balance, eth_balance = result

        # Считаем USD-эквивалент
        btc_usd = btc_balance * price if coin == "BTC" else btc_balance * btc_price
        eth_usd = eth_balance * price if coin == "ETH" else eth_balance * eth_price

        await state.update_data(action=action, coin=coin)
        await BuyOrSellStates.waiting_amount.set()

        await callback.message.answer(
            f"{action_emoji} **{action_word.upper()} {coin}**\n\n"
            f"💵 **Текущая цена:** {price:,.2f} USD за 1 {coin}\n"
            f"{rsi_text}\n\n"
            f"💰 **Ваш баланс:** {balance:,.2f} USD\n\n"
            f"📊 **Ваши активы:**\n"
            f"• BTC: {btc_balance:.6f} (${btc_usd:,.2f})\n"
            f"• ETH: {eth_balance:.6f} (${eth_usd:,.2f})\n\n"
            f"✏️ **Введите сумму в USD**, которую хотите {action_word[:-1]}ть:\n"
            f"(или нажмите кнопку «❌ Отмена»)",
            reply_markup=cancel_kb,
            parse_mode="Markdown"
        )
        await callback.answer()

    except Exception as e:
        print(f"❌ Критическая ошибка в process_trade_callback: {e}")
        import traceback
        traceback.print_exc()
        await callback.message.answer(
            "⚠️ **Что-то пошло не так**\n"
            "Пожалуйста, начните заново.",
            parse_mode="Markdown"
        )
        await callback.answer()


async def give_amount(message: types.Message, state: FSMContext):
    """Обрабатывает ввод суммы для сделки"""

    # Проверка на отмену
    if message.text == "❌ Отмена":
        await state.finish()
        await message.answer(
            "❌ **Действие отменено**\n"
            "Возвращаю в главное меню.",
            reply_markup=menu_kb,
            parse_mode="Markdown"
        )
        return

    print(f"=== GIVE_AMOUNT START ===")
    current_state = await state.get_state()
    print(f"Состояние в give_amount: {current_state}")
    user_id = message.from_user.id
    print(f"give_amount triggered, message: {message.text}")

    # Получаем актуальные цены
    try:
        crypto_service = dp['crypto_service']
        btc_price = crypto_service.get_btc_price()
        eth_price = crypto_service.get_eth_price()
    except Exception as e:
        print(f"❌ Ошибка получения цен: {e}")
        await message.answer(
            "⚠️ **Временные трудности**\n"
            "Не удалось получить актуальные цены. Попробуйте позже.",
            parse_mode="Markdown"
        )
        await state.finish()
        return

    # Валидация введённой суммы
    amount_str = message.text.replace(",", ".")
    try:
        amount = float(amount_str)
        if amount <= 0:
            await message.answer(
                "❌ **Некорректная сумма**\n"
                "Сумма должна быть больше нуля. Попробуйте ещё раз:",
                reply_markup=cancel_kb
            )
            return
        if amount > 1_000_000:
            await message.answer(
                "⚠️ **Слишком большая сумма**\n"
                "Максимальная сумма для одной сделки — 1 000 000 USD.\n"
                "Введите меньшую сумму:",
                reply_markup=cancel_kb
            )
            return
    except ValueError:
        await message.answer(
            "❌ **Некорректный ввод**\n"
            "Пожалуйста, введите число (например: 100 или 50.5):",
            reply_markup=cancel_kb
        )
        return

    # Получаем данные из состояния
    try:
        data = await state.get_data()
        action = data.get("action")
        coin = data.get("coin")
    except Exception as e:
        print(f"❌ Ошибка получения данных состояния: {e}")
        await message.answer(
            "⚠️ **Ошибка сессии**\n"
            "Пожалуйста, начните заново.",
            reply_markup=menu_kb
        )
        await state.finish()
        return

    if not action or not coin:
        await message.answer(
            "❌ **Ошибка данных**\n"
            "Не найдены данные сделки. Начните заново.",
            reply_markup=menu_kb
        )
        await state.finish()
        return

    # Определяем цену
    if coin == "BTC":
        price = btc_price
    elif coin == "ETH":
        price = eth_price
    else:
        await message.answer("❌ **Неизвестная монета**")
        await state.finish()
        return

    # Выполняем сделку
    try:
        if action == "buy":
            usd_amount = amount
            coin_amount = usd_amount / price
            success, text = await buy(user_id, coin, coin_amount, price)

        elif action == "sell":
            usd_amount = amount
            coin_amount = usd_amount / price
            success, text = await sell(user_id, coin, coin_amount, price)

        else:
            await message.answer("❌ **Неизвестное действие**")
            await state.finish()
            return
    except Exception as e:
        print(f"❌ Ошибка выполнения сделки: {e}")
        await message.answer(
            "⚠️ **Ошибка при выполнении сделки**\n"
            "Пожалуйста, попробуйте позже.",
            reply_markup=menu_kb
        )
        await state.finish()
        return

    # Отправляем результат сделки
    await message.answer(text, parse_mode="Markdown")

    # Если сделка успешна — запрашиваем объяснение от ИИ
    if success:
        # Проверяем лимит ИИ
        try:
            can_use_ai = check_ai_limit(user_id)
        except Exception as e:
            print(f"❌ Ошибка проверки лимита ИИ: {e}")
            can_use_ai = False

        if can_use_ai:
            try:
                await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

                # Получаем обновлённый баланс
                cursor.execute("SELECT balance, btc_balance, eth_balance FROM users WHERE id = ?", (user_id,))
                balance, btc, eth = cursor.fetchone()

                try:
                    if coin == "BTC":
                        rsi = crypto_service.get_rsi('BTCUSDT')
                    else:
                        rsi = crypto_service.get_rsi('ETHUSDT')
                except Exception as e:
                    print(f"Ошибка получения RSI: {e}")
                    rsi = None

                rsi_line = f"📊 RSI (14): {rsi} – {'перекупленность' if rsi > 70 else 'перепроданность' if rsi < 30 else 'нейтрально'}" if rsi else "📊 RSI временно недоступен"



                user_prompt = f"""
                Пользователь {action} {coin} на сумму {usd_amount:,.2f} USD (получено {coin_amount:.6f} {coin}) по цене {price:,.2f} USD.
                Его баланс после сделки: {balance:,.2f} USD, {btc:.6f} BTC, {eth:.6f} ETH.
                {rsi_line}
                Объясни, разумно ли это решение для новичка в криптотрейдинге с учётом технического индикатора RSI.
                """

                explanation = ask_openrouter(TRADE_EXPLANATION, user_prompt, max_tokens=150)
                await message.answer(
                    f"🤖 **Мнение ИИ-ассистента:**\n\n{explanation}",
                    parse_mode="Markdown"
                )

                if message.from_user.id != DEVELOPER_ID:
                    increment_ai_requests(user_id)

            except Exception as e:
                print(f"❌ Ошибка получения объяснения от ИИ: {e}")
                await message.answer(
                    "⚠️ Не удалось получить объяснение от ИИ, но сделка выполнена успешно.",
                    parse_mode="Markdown"
                )
        else:
            await message.answer(
                "ℹ️ **Лимит запросов к ИИ исчерпан**\n"
                "Вы использовали все 10 запросов на сегодня.\n"
                "Завтра лимит обновится!",
                parse_mode="Markdown"
            )

        # Обновляем рейтинг
        if success and amount > 0:
            try:
                await update_rating(user_id)
            except Exception as e:
                print(f"Ошибка в update_rating: {e}")

    # Завершаем состояние
    await state.finish()
    await message.answer(
        "✅ **Готово!**\n"
        "Можете продолжить работу с ботом.",
        reply_markup=menu_kb,
        parse_mode="Markdown"
    )


async def cancel_trade(message: types.Message, state: FSMContext):
    """Отмена сделки в любом состоянии"""
    try:
        current_state = await state.get_state()
        if current_state is not None:
            await state.finish()
            await message.answer(
                "❌ **Действие отменено**\n"
                "Возвращаю в главное меню.",
                reply_markup=menu_kb,
                parse_mode="Markdown"
            )
    except Exception as e:
        print(f"❌ Ошибка при отмене: {e}")
        await message.answer(
            "✅ **Возврат в меню**",
            reply_markup=menu_kb
        )


def register_handlers(dp: Dispatcher):
    """Регистрация всех хендлеров модуля"""
    dp.register_message_handler(buy_crypto, lambda message: message.text == "💰 Купить")
    dp.register_message_handler(sell_crypto, lambda message: message.text == "💸 Продать")
    dp.register_callback_query_handler(
        process_trade_callback,
        lambda c: c.data.startswith(("trade:buy:", "trade:sell:"))
    )
    dp.register_message_handler(give_amount, state=BuyOrSellStates.waiting_amount)
    dp.register_message_handler(cancel_trade, lambda message: message.text == "❌ Отмена", state="*")