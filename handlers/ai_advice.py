from aiogram import types, Dispatcher
from loader import dp
from handlers.kb_buy_handlers import DEVELOPER_ID
from services.ai_service import ask_openrouter
from services.ai_limit import check_ai_limit, increment_ai_requests
from database.db import cursor
from services.crypto_services import CryptoServices


async def btc_analyse(message: types.Message):
    """
    Анализ BTC с помощью ИИ
    """
    try:
        # Получаем сервис криптовалют
        try:
            crypto_service = dp['crypto_service']
            btc_price = crypto_service.get_btc_price()
            #btc_rsi = crypto_service.get_rsi("BTCUSDT")
            btc_rsi = 50
            if not btc_price:
                raise ValueError("Не удалось получить цену BTC")
        except Exception as e:
            print(f"❌ Ошибка получения цены BTC: {e}")
            await message.answer(
                "⚠️ **Временные трудности**\n"
                "Не удалось получить актуальную цену BTC. Попробуйте позже.",
                parse_mode="Markdown"
            )
            return

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
            print(f"❌ Ошибка проверки лимита: {e}")
            await message.answer(
                "⚠️ **Ошибка проверки лимита**\n"
                "Пожалуйста, попробуйте позже.",
                parse_mode="Markdown"
            )
            return

        # Системный промпт для ИИ
        system_prompt = """
        Ты крипто-ассистент для новичков. Отвечай кратко, но информативно.
        Структура ответа:
        - Вывод (да/нет/осторожно)
        - Почему
        - Риски
        - Отказ от ответственности
        """

        # Получаем данные пользователя из БД
        try:
            cursor.execute("SELECT balance, btc_balance, eth_balance FROM users WHERE id = ?", (user_id,))
            result = cursor.fetchone()
        except Exception as e:
            print(f"❌ Ошибка БД: {e}")
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

        # Формируем промпт для пользователя
        user_prompt = f"""
        Пользователь хочет узнать, стоит ли покупать BTC.
        
        Текущая ситуация:
        • Цена BTC: {btc_price:,.2f} USD
        • RSI (14): {btc_rsi} {'(перекуплен)' if btc_rsi > 70 else '(перепродан)' if btc_rsi < 30 else '(нейтрален)'}
        • Баланс пользователя: {balance:,.2f} USD, {btc} BTC, {eth} ETH.
        
        Дай персональный совет с учётом баланса пользователя и технического индикатора RSI.
        """

        # Отправляем запрос к ИИ
        try:
            await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
            answer = ask_openrouter(system_prompt, user_prompt, max_tokens=150)

            if answer.startswith("❌") or "ошибк" in answer.lower():
                # Если ИИ вернул ошибку
                await message.answer(
                    f"⚠️ **ИИ временно недоступен**\n\n{answer}",
                    parse_mode="Markdown"
                )
            else:
                # Успешный ответ
                await message.answer(
                    f"📊 **Анализ BTC**\n\n{answer}",
                    parse_mode="Markdown"
                )

                # Увеличиваем счётчик запросов
                if message.from_user.id != DEVELOPER_ID:
                    increment_ai_requests(user_id)

        except Exception as e:
            print(f"❌ Ошибка вызова ИИ: {e}")
            await message.answer(
                "⚠️ **Ошибка при обращении к ИИ**\n"
                "Пожалуйста, попробуйте позже.",
                parse_mode="Markdown"
            )

    except Exception as e:
        print(f"❌ Критическая ошибка в btc_analyse: {e}")
        import traceback
        traceback.print_exc()
        await message.answer(
            "⚠️ **Что-то пошло не так**\n"
            "Мы уже работаем над исправлением.",
            parse_mode="Markdown"
        )


async def eth_analyse(message: types.Message):
    """
    Анализ ETH с помощью ИИ
    """
    try:
        # Получаем сервис криптовалют
        try:
            crypto_service = dp['crypto_service']
            eth_price = crypto_service.get_eth_price()
            #eth_rsi = crypto_service.get_rsi("ETHUSDT")
            eth_rsi = 50
            if not eth_price:
                raise ValueError("Не удалось получить цену ETH")
        except Exception as e:
            print(f"❌ Ошибка получения цены ETH: {e}")
            await message.answer(
                "⚠️ **Временные трудности**\n"
                "Не удалось получить актуальную цену ETH. Попробуйте позже.",
                parse_mode="Markdown"
            )
            return

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
            print(f"❌ Ошибка проверки лимита: {e}")
            await message.answer(
                "⚠️ **Ошибка проверки лимита**\n"
                "Пожалуйста, попробуйте позже.",
                parse_mode="Markdown"
            )
            return

        # Системный промпт для ИИ
        system_prompt = """
        Ты крипто-ассистент для новичков. Отвечай кратко, но информативно.
        Структура ответа:
        - Вывод (да/нет/осторожно)
        - Почему
        - Риски
        - Отказ от ответственности
        """

        # Получаем данные пользователя из БД
        try:
            cursor.execute("SELECT balance, btc_balance, eth_balance FROM users WHERE id = ?", (user_id,))
            result = cursor.fetchone()
        except Exception as e:
            print(f"❌ Ошибка БД: {e}")
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

        # Формируем промпт для пользователя
        user_prompt = f"""
        Пользователь хочет узнать, стоит ли покупать ETH.
        
        Текущая ситуация:
        • Цена ETH: {eth_price:,.2f} USD
        • RSI (14): {eth_rsi} {'(перекуплен)' if eth_rsi > 70 else '(перепродан)' if eth_rsi < 30 else '(нейтрален)'}
        • Баланс пользователя: {balance:,.2f} USD, {btc} BTC, {eth} ETH.
        
        Дай персональный совет с учётом баланса пользователя и технического индикатора RSI.
        """

        # Отправляем запрос к ИИ
        try:
            await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
            answer = ask_openrouter(system_prompt, user_prompt, max_tokens=150)

            if answer.startswith("❌") or "ошибк" in answer.lower():
                # Если ИИ вернул ошибку
                await message.answer(
                    f"⚠️ **ИИ временно недоступен**\n\n{answer}",
                    parse_mode="Markdown"
                )
            else:
                # Успешный ответ
                await message.answer(
                    f"📊 **Анализ ETH**\n\n{answer}",
                    parse_mode="Markdown"
                )

                # Увеличиваем счётчик запросов
                if message.from_user.id != DEVELOPER_ID:
                    increment_ai_requests(user_id)

        except Exception as e:
            print(f"❌ Ошибка вызова ИИ: {e}")
            await message.answer(
                "⚠️ **Ошибка при обращении к ИИ**\n"
                "Пожалуйста, попробуйте позже.",
                parse_mode="Markdown"
            )

    except Exception as e:
        print(f"❌ Критическая ошибка в eth_analyse: {e}")
        import traceback
        traceback.print_exc()
        await message.answer(
            "⚠️ **Что-то пошло не так**\n"
            "Мы уже работаем над исправлением.",
            parse_mode="Markdown"
        )


def register_handlers_aiai(dp: Dispatcher):
    """Регистрация хендлеров анализа монет"""
    dp.register_message_handler(
        btc_analyse,
        lambda message: message.text == "📊 Анализ BTC"
    )
    dp.register_message_handler(
        eth_analyse,
        lambda message: message.text == "📈 Анализ ETH"
    )



