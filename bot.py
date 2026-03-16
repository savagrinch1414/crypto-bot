from loader import dp
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

if __name__ == "__main__":
    try:
        # Очищаем старый кеш
        try:
            deleted = clean_old_cache(days=3)
            logger.info(f"🧹 Очищено {deleted} старых записей кеша")
        except Exception as e:
            logger.error(f"❌ Ошибка при очистке кеша: {e}")

        logger.info("🚀 Запуск бота...")
        executor.start_polling(dp, skip_updates=True, on_shutdown=on_shutdown)
    except Exception as e:
        logger.critical(f"💥 Критическая ошибка при запуске бота: {e}", exc_info=True)
        raise
    finally:
        logger.info("👋 Бот завершил работу")