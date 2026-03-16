from aiogram import Dispatcher, types

async def donate_pls(message: types.Message):
    await message.answer("""
Поддержать проект

Если бот тебе помог и ты хочешь, чтобы он развивался — можно задонатить любую сумму.

Все донаты пойдут на:

· оплату AI-запросов (чтобы бот отвечал быстрее)
· сервера (чтобы не лагал)
· новые фичи (Mini Apps, графики, страховка)

Даже 50 рублей — это вклад в общее дело. Спасибо, что ты со мной 🙏

https://dalink.to/sawl1414
""")


def register_donate(dp: Dispatcher):
    dp.register_message_handler(donate_pls, commands="donate")