from aiogram import types, Dispatcher
from loader import dp
import logging

logger = logging.getLogger(__name__)


async def show_price(message: types.Message):
    """
    Показывает актуальные цены BTC и ETH
    """
    try:
        # Получаем сервис криптовалют
        try:
            crypto_service = dp['crypto_service']
            btc_price = crypto_service.get_btc_price()
            eth_price = crypto_service.get_eth_price()
            btc_rsi = crypto_service.get_rsi('BTCUSDT', period=14, interval='1h')
            eth_rsi = crypto_service.get_rsi('ETHUSDT', period=14, interval='1h')

            # Проверяем, что цены получены
            if btc_price is None or eth_price is None:
                raise ValueError("Не удалось получить цены")

        except Exception as e:
            logger.error(f"❌ Ошибка получения цен: {e}")
            await message.answer(
                "⚠️ **Временные трудности**\n"
                "Не удалось получить актуальные цены. Попробуйте позже.",
                parse_mode="Markdown"
            )
            return

        # Красивое форматирование цен
        text = f"💵 **Актуальные цены и RSI** 💵\n\n"
        text += f"₿ **BTC:** ${btc_price:,.2f}\n"
        if btc_rsi:
            text += f"   📊 RSI (14): {btc_rsi} "
            if btc_rsi > 70:
                text += "⚡ перекуплен"
            elif btc_rsi < 30:
                text += "🧊 перепродан"
            else:
                text += "➖ нейтрально"
        text += f"\n\nΞ **ETH:** ${eth_price:,.2f}\n"
        if eth_rsi:
            text += f"   📊 RSI (14): {eth_rsi} "
            if eth_rsi > 70:
                text += "⚡ перекуплен"
            elif eth_rsi < 30:
                text += "🧊 перепродан"
            else:
                text += "➖ нейтрально"
        text += "\n\n📈 Данные обновляются каждый час"

        await message.answer(text, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"❌ Критическая ошибка в show_price: {e}")
        await message.answer(
            "⚠️ **Что-то пошло не так**\n"
            "Пожалуйста, попробуйте позже.",
            parse_mode="Markdown"
        )


def register_handlers_price(dp: Dispatcher):
    """Регистрация хендлера для показа цен"""
    dp.register_message_handler(
        show_price,
        lambda message: message.text == "💵 Цены валют"  # добавил пробел для красоты
    )