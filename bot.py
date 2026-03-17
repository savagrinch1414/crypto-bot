from loader import dp
from aiohttp import web
from aiohttp import web
from handlers.kb_buy_handlers import register_handlers
from handlers.start import register_handlers2
from handlers.profile import register_handlers_profile
from handlers.rating import register_rating
from aiogram import executor
from handlers.ai_portfelio import register_handlers_portfelio
from middlewares.ai_limit_middleware import AiLimitMidd
from middlewares.logging import LoggingMiddleware
from handlers.ask_ai import register_handlers_ask_ai
from handlers.ai_advice import register_handlers_aiai
from handlers.stats import register_stats_handlers
from aiogram import Dispatcher
import asyncio
import logging
from services.ai_cache import clean_old_cache
from services.crypto_services import CryptoServices
from handlers.donate import register_donate
from handlers.feedback import register_feedback
from handlers.show_price import register_handlers_price
from aiogram.types import ParseMode
from loader import bot
import os
import logging
import threading

async def health_check(request):
    return web.Response(text="OK", status=200)


async def run_health_server():
    app = web.Application()
    app.router.add_get('/', health_check)
    app.router.add_get('/health', health_check)
    app.router.add_get('/healthz', health_check)

    runner = web.AppRunner(app)
    await runner.setup()
    # Используем порт 10000, он точно не занят основным приложением
    site = web.TCPSite(runner, '0.0.0.0', 10000)
    await site.start()
    print("✅ Health check server running on port 10000")

async def health_check(request): return web.Response(text='OK', status=200)






# Настраиваем логгер для этого файла
logger = logging.getLogger(__name__)

async def on_shutdown(dp: Dispatcher):
    """Действия при остановке бота"""
    logger.info("🔄 Останавливаем бота...")
    await dp.storage.close()
    await dp.storage.wait_closed()
    logger.info("✅ Бот остановлен")

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,  # можно оставить ERROR, но для отладки INFO полезнее
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("errors.log"),
        logging.StreamHandler()  # выводим в консоль тоже
    ]
)

# Регистрируем middleware
try:
    dp.middleware.setup(AiLimitMidd())
    dp.middleware.setup(LoggingMiddleware())
    logger.info("✅ Middleware установлены")
except Exception as e:
    logger.error(f"❌ Ошибка при установке middleware: {e}")
    raise

# Регистрируем все хендлеры
try:
    register_handlers(dp)
    register_handlers2(dp)
    register_handlers_profile(dp)
    register_rating(dp)
    register_handlers_ask_ai(dp)
    register_handlers_aiai(dp)
    register_stats_handlers(dp)
    register_handlers_portfelio(dp)
    register_donate(dp)
    register_feedback(dp)
    register_handlers_price(dp)
    logger.info("✅ Все хендлеры зарегистрированы")
except Exception as e:
    logger.error(f"❌ Ошибка при регистрации хендлеров: {e}")
    raise


WEBHOOK_HOST = 'https://crypto-bot-7gps.onrender.com'
WEBHOOK_PATH = '/webhook'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

WEBAPP_HOST = '0.0.0.0'  # Для Render обязательно 0.0.0.0
WEBAPP_PORT = int(os.getenv('PORT', 8000))

async def on_startup(dp):


    """Действия при запуске"""
    bot = dp.bot
    # Устанавливаем вебхук
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Вебхук установлен: {WEBHOOK_URL}")

    asyncio.create_task(run_health_server())
    logger.info("✅ Health check server запущен на порту 10000")

    dp.bot._app.router.add_get('/', health_check)
    dp.bot._app.router.add_get('/health', health_check)
    dp.bot._app.router.add_get('/healthz', health_check)
    logger.info("✅ Health check endpoints добавлены в основное приложение")


async def on_shutdown1(dp):
    """Действия при остановке"""
    bot = dp.bot
    # Удаляем вебхук и закрываем сессию
    await bot.delete_webhook()
    await dp.storage.close()
    await dp.storage.wait_closed()
    logging.info("Бот остановлен")



if __name__ == "__main__":
    try:
        # Очищаем старый кеш
        try:
            deleted = clean_old_cache(days=3)
            logger.info(f"🧹 Очищено {deleted} старых записей кеша")
        except Exception as e:
            logger.error(f"❌ Ошибка при очистке кеша: {e}")

        logger.info("🚀 Запуск бота...")
        executor.start_webhook(
            dispatcher=dp,
            webhook_path=WEBHOOK_PATH,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT,
            skip_updates=True,
        )
    except Exception as e:
        logger.critical(f"💥 Критическая ошибка при запуске бота: {e}", exc_info=True)
        raise
    finally:
        logger.info("👋 Бот завершил работу")