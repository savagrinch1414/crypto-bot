from loader import dp, bot
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
from handlers.donate import register_donate
from handlers.feedback import register_feedback
from handlers.show_price import register_handlers_price
from services.ai_cache import clean_old_cache
import logging
import os
from aiohttp import web
from threading import Thread

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ===== HEALTH CHECK - ОТДЕЛЬНЫЙ СЕРВЕР =====
async def health_check(request):
    return web.Response(text="OK")

def run_health_server():
    app = web.Application()
    app.router.add_get('/', health_check)
    app.router.add_get('/health', health_check)
    app.router.add_get('/healthz', health_check)
    # Запускаем на порту 10000
    web.run_app(app, host='0.0.0.0', port=10000)

# Запускаем health-сервер в фоновом потоке
Thread(target=run_health_server, daemon=True).start()
logger.info("✅ Health check server running on port 10000")

# ===== НАСТРОЙКИ ВЕБХУКА =====
WEBHOOK_HOST = 'https://crypto-bot-7gps.onrender.com'
WEBHOOK_PATH = '/webhook'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = int(os.getenv('PORT', 8000))

# ===== MIDDLEWARE И ХЕНДЛЕРЫ =====
dp.middleware.setup(AiLimitMidd())
dp.middleware.setup(LoggingMiddleware())

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

logger.info("✅ Бот зарегистрирован")

# ===== ДЕЙСТВИЯ ПРИ ЗАПУСКЕ =====
async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"🌐 Вебхук установлен: {WEBHOOK_URL}")

# ===== ДЕЙСТВИЯ ПРИ ОСТАНОВКЕ =====
async def on_shutdown(dp):
    await bot.delete_webhook()
    await dp.storage.close()
    await dp.storage.wait_closed()
    logger.info("👋 Бот остановлен")

# ===== ЗАПУСК =====
if __name__ == "__main__":
    clean_old_cache(days=3)
    executor.start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
        skip_updates=True,
        # Параметр 'app' ПОЛНОСТЬЮ УДАЛЁН
    )