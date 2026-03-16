from aiogram import Dispatcher
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram import types

class LoggingMiddleware(BaseMiddleware):
    async def on_pre_process_message(self, message: types.Message, data: dict):
        user_id = message.from_user.id
        text = message.text
        print(f"[LOG] {user_id}: {text}")
