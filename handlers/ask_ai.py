from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from database.db import cursor
from handlers.kb_buy_handlers import DEVELOPER_ID  # Импортируем из одного места
from services.ai_limit import check_ai_limit, increment_ai_requests
from services.ai_service import ask_openrouter
from services.prompts import ASK_PROMPT
from states.ask_states import AskStates
from kb.main_menu import menu_kb  # Для возврата в меню


async def ask_ai(message: types.Message):
    """
    Начало диалога с ИИ - команда /ask
    """
    user_id = message.from_user.id

    # Проверяем наличие пользователя в БД
    try:
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not cursor.fetchone():
            await message.answer(
                "👋 **Добро пожаловать!**\n"
                "Сначала нажмите /start, чтобы зарегистрироваться.",
                parse_mode="Markdown"
            )
            return
    except Exception as e:
        print(f"❌ Ошибка БД при проверке пользователя {user_id}: {e}")
        await message.answer(
            "⚠️ **Ошибка базы данных**\n"
            "Пожалуйста, попробуйте позже.",
            parse_mode="Markdown"
        )
        return

    # Проверяем лимит запросов (кроме разработчика)
    try:
        if user_id != DEVELOPER_ID:
            if not check_ai_limit(user_id):
                await message.answer(
                    "❌ **Лимит исчерпан**\n"
                    "Вы использовали все 10 запросов к ИИ на сегодня.\n"
                    "Завтра лимит обновится!",
                    parse_mode="Markdown"
                )
                return
    except Exception as e:
        print(f"❌ Ошибка проверки лимита для {user_id}: {e}")
        await message.answer(
            "⚠️ **Ошибка проверки лимита**\n"
            "Пожалуйста, попробуйте позже.",
            parse_mode="Markdown"
        )
        return

    # Переходим в состояние ожидания вопроса
    await message.answer(
        "🤖 **Задайте вопрос про криптовалюты**\n\n"
        "Напишите ваш вопрос, и я постараюсь дать понятный ответ для новичка.\n\n"
        "Например:\n"
        "• Что такое блокчейн?\n"
        "• Как работает майнинг?\n"
        "• Стоит ли сейчас инвестировать?\n\n"
        "✏️ **Ожидаю ваш вопрос...**",
        parse_mode="Markdown"
    )
    await AskStates.waiting_for_question.set()


async def process_ask(message: types.Message, state: FSMContext):
    """
    Обработка вопроса пользователя и получение ответа от ИИ
    """
    try:
        user_id = message.from_user.id
        user_question = message.text

        # Проверяем, не пустой ли вопрос
        if not user_question or len(user_question.strip()) < 3:
            await message.answer(
                "❌ **Слишком короткий вопрос**\n"
                "Пожалуйста, задайте более содержательный вопрос (минимум 3 символа).",
                parse_mode="Markdown"
            )
            return

        # Ещё раз проверяем лимит (на случай, если прошло много времени)
        try:
            if user_id != DEVELOPER_ID:
                if not check_ai_limit(user_id):
                    await message.answer(
                        "❌ **Лимит исчерпан**\n"
                        "Вы использовали все 10 запросов к ИИ на сегодня.\n"
                        "Завтра лимит обновится!",
                        parse_mode="Markdown"
                    )
                    await state.finish()
                    return
        except Exception as e:
            print(f"❌ Ошибка повторной проверки лимита для {user_id}: {e}")
            await message.answer(
                "⚠️ **Ошибка проверки лимита**\n"
                "Пожалуйста, попробуйте позже.",
                parse_mode="Markdown"
            )
            await state.finish()
            return

        # Получаем информацию о пользователе для контекста (опционально)
        try:
            cursor.execute("SELECT balance, btc_balance, eth_balance FROM users WHERE id = ?", (user_id,))
            result = cursor.fetchone()
            if result:
                balance, btc, eth = result
                user_context = f"\n\nКонтекст пользователя: баланс {balance:.2f} USD, {btc:.6f} BTC, {eth:.6f} ETH."
            else:
                user_context = ""
        except Exception as e:
            print(f"❌ Ошибка получения контекста пользователя: {e}")
            user_context = ""

        # Формируем промпт с вопросом пользователя
        system_prompt = ASK_PROMPT
        user_prompt = f"""
        Вопрос пользователя: {user_question}{user_context}

        Дай понятный ответ для новичка в криптотрейдинге.
        """

        # Отправляем запрос к ИИ
        try:
            await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
            answer = ask_openrouter(system_prompt, user_prompt, max_tokens=200)

            # Проверяем, не вернул ли ИИ ошибку
            if answer.startswith("❌") or "ошибк" in answer.lower() or "error" in answer.lower():
                await message.answer(
                    f"⚠️ **ИИ временно недоступен**\n\n{answer}",
                    parse_mode="Markdown"
                )
            else:
                # Успешный ответ
                response_text = f"🤖 **Ответ ИИ:**\n\n{answer}"
                await message.answer(response_text, parse_mode="Markdown")

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

    except Exception as e:
        print(f"❌ Критическая ошибка в process_ask для пользователя {message.from_user.id}: {e}")
        import traceback
        traceback.print_exc()
        await message.answer(
            "⚠️ **Что-то пошло не так**\n"
            "Мы уже работаем над исправлением.",
            parse_mode="Markdown"
        )
    finally:
        # Всегда завершаем состояние, даже при ошибке
        await state.finish()
        # Возвращаем клавиатуру меню (опционально)
        await message.answer(
            "✅ **Готово!**\nМожете продолжить работу с ботом.",
            reply_markup=menu_kb,
            parse_mode="Markdown"
        )


def register_handlers_ask_ai(dp: Dispatcher):
    """Регистрация хендлеров для /ask"""
    dp.register_message_handler(ask_ai, lambda message: message.text == "🤖 Задать вопрос")
    dp.register_message_handler(process_ask, state=AskStates.waiting_for_question)