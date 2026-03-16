import os
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from services.crypto_services import CryptoServices
from dotenv import load_dotenv

load_dotenv()




BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)




crypto_service = CryptoServices()
dp['crypto_service'] = crypto_service