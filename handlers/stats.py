from aiogram import Dispatcher, types
from services.ai_stats import get_today_stats


DEVELOPER_ID = 1628601883

async def show_stats(message: types.Message):
    # Только для разработчика
    if message.from_user.id != DEVELOPER_ID:
        await message.answer("Эта команда только для создателя бота")
        return

    total, top_users = get_today_stats()

    # Лимиты OpenRouter (для бесплатного аккаунта)
    openrouter_limit = 50
    remaining = max(0, openrouter_limit - total)

    stats_text = f"""
📊 **Статистика запросов к ИИ**

📈 Сегодня использовано: **{total}** из {openrouter_limit}
⏳ Осталось: **{remaining}** запросов

👑 **Топ-3 пользователя сегодня:**
"""

    for i, (user_id, requests) in enumerate(top_users, 1):
        stats_text += f"{i}. ID {user_id}: {requests} запросов\n"

    if not top_users:
        stats_text += "   Пока нет активности\n"

    stats_text += f"\n🔄 Обновляется каждый день в 00:00"

    await message.answer(stats_text, parse_mode="Markdown")


def register_stats_handlers(dp: Dispatcher):
    dp.register_message_handler(show_stats, commands="stats")