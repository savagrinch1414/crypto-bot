import os
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from services.crypto_services import CryptoServices
from dotenv import load_dotenv

storage = MemoryStorage()
TOKEN = os.getenv("TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)

crypto_service = CryptoServices()
dp['crypto_service'] = crypto_service