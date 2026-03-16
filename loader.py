import os
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from services.crypto_services import CryptoServices
from dotenv import load_dotenv

load_dotenv()



storage = MemoryStorage()
BOT_TOKEN = os.getenv("BOT_TOKEN")
dp = Dispatcher(bot, storage=storage)
bot = Bot(token=BOT_TOKEN)


crypto_service = CryptoServices()
dp['crypto_service'] = crypto_service