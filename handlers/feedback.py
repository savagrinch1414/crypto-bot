from aiogram import types, Dispatcher

async def feedback(message: types.Message):
    await message.answer(
        "📬 Обратная связь\n\n"
        "Сейчас обратная связь мне важна как никогда. Поможешь мне?\n\n"
        "👉 Заполни форму – это займёт всего 2 минуты: "
        "<a href='https://forms.gle/jD5juEbtSr9EF3wL8'>жми сюда</a>\n\n"
        "Твои ответы помогут сделать CrypTeach реально крутым! 🚀",
        parse_mode="HTML"
    )


def register_feedback(dp: Dispatcher):
    dp.register_message_handler(feedback, commands="feedback")
