from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram import types
from database.db import cursor
from services.ai_limit import check_ai_limit
from services.ai_stats import get_today_stats
import logging

# Настройка логгера для middleware
logger = logging.getLogger(__name__)

class AiLimitMidd(BaseMiddleware):
    async def on_pre_process_message(self, message: types.Message, data: dict):
        DEVELOPER_ID = 1628601883

        # Пропускаем разработчика без проверок
        if message.from_user.id == DEVELOPER_ID:
            return

        # Проверяем наличие пользователя в БД
        try:
            cursor.execute("SELECT id FROM users WHERE id = ?", (message.from_user.id,))
            if not cursor.fetchone():
                # Пользователь не найден — пропускаем, он попадёт в /start
                return
        except Exception as e:
            logger.error(f"Ошибка БД в middleware: {e}")
            # В случае ошибки лучше пропустить сообщение, чтобы не блокировать пользователя
            return

        # Список команд, требующих проверки лимита
        ai_commands = [
            "Анализ BTC",
            "Анализ ETH",
            "Анализ Портфеля",
            "/ask",
        ]

        # Получаем текущее состояние FSM
        state = data.get("state")
        if state:
            try:
                current_state = await state.get_state()
            except Exception as e:
                logger.error(f"Ошибка получения состояния: {e}")
                current_state = None
        else:
            current_state = None

        need_check = False

        # Проверяем, нужно ли проверять это сообщение
        if message.text and message.text in ai_commands:
            need_check = True

        if current_state == "AskStates:waiting_for_question":
            need_check = True

        if not need_check:
            return

        user_id = message.from_user.id

        # Проверяем индивидуальный лимит пользователя
        try:
            if not check_ai_limit(user_id):
                await message.answer(
                    "❌ **Лимит запросов исчерпан**\n"
                    "Вы использовали все 10 запросов к ИИ на сегодня.\n"
                    "Завтра лимит обновится!",
                    parse_mode="Markdown"
                )
                return {"result": False}
        except Exception as e:
            logger.error(f"Ошибка в check_ai_limit для {user_id}: {e}")
            await message.answer(
                "⚠️ **Ошибка проверки лимита**\n"
                "Пожалуйста, попробуйте позже.",
                parse_mode="Markdown"
            )
            return {"result": False}

        # Проверяем общий лимит OpenRouter (или BotHub)
        try:
            total, _ = get_today_stats()
            if total is None:
                total = 0
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            total = 0

        openrouter_limit = 50  # дневной лимит (можно вынести позже)
        if total >= openrouter_limit * 0.8:
            remaining = openrouter_limit - total
            # Показываем предупреждение только один раз за сессию
            if state:
                try:
                    user_data = await state.get_data()
                    if not user_data.get("warned_about_limit"):
                        await state.update_data(warned_about_limit=True)
                        await message.answer(
                            f"⚠️ **Внимание!**\n"
                            f"Осталось всего **{remaining}** запросов к ИИ на сегодня.\n"
                            f"Старайтесь формулировать вопросы точнее.",
                            parse_mode="Markdown"
                        )
                except Exception as e:
                    logger.error(f"Ошибка при сохранении предупреждения: {e}")

        return True