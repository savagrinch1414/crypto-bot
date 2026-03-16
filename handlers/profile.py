from loader import dp
from aiogram import Dispatcher, types
from services.user_services import get_user_profile_service
from kb.main_menu import menu_kb  # для возврата в меню при ошибке


async def profile(message: types.Message):
    """
    Показывает профиль пользователя с балансами и рейтингом
    """
    user_id = message.from_user.id

    # Получаем актуальные цены криптовалют
    try:
        crypto_service = dp['crypto_service']
        btc_price = crypto_service.get_btc_price()
        eth_price = crypto_service.get_eth_price()

        if not btc_price or not eth_price:
            raise ValueError("Не удалось получить цены криптовалют")
    except Exception as e:
        print(f"❌ Ошибка получения цен для пользователя {user_id}: {e}")
        await message.answer(
            "⚠️ **Временные трудности**\n"
            "Не удалось получить актуальные цены. Попробуйте позже.\n\n"
            "🔄 Ваши балансы будут показаны без USD-эквивалента.",
            parse_mode="Markdown"
        )
        # Устанавливаем цены в 0, чтобы показать хотя бы балансы
        btc_price = 0
        eth_price = 0

    # Получаем профиль пользователя из БД
    try:
        profile = await get_user_profile_service(user_id)
    except Exception as e:
        print(f"❌ Ошибка получения профиля пользователя {user_id}: {e}")
        await message.answer(
            "⚠️ **Ошибка базы данных**\n"
            "Не удалось загрузить профиль. Пожалуйста, попробуйте позже.",
            parse_mode="Markdown"
        )
        return

    if profile is None:
        await message.answer(
            "👋 **Добро пожаловать!**\n"
            "Сначала нажмите /start, чтобы зарегистрироваться.",
            parse_mode="Markdown"
        )
        return

    # Извлекаем данные профиля
    try:
        balance = profile["balance"]
        rating = profile["rating"]
        league = profile["league"]
        btc_balance = profile["btc_balance"]
        eth_balance = profile["eth_balance"]
    except KeyError as e:
        print(f"❌ Ошибка структуры профиля: отсутствует ключ {e}")
        await message.answer(
            "⚠️ **Ошибка данных**\n"
            "Повреждённый профиль. Пожалуйста, нажмите /start для восстановления.",
            parse_mode="Markdown"
        )
        return

    # Рассчитываем USD-эквиваленты
    try:
        btc_usd = btc_balance * btc_price
        eth_usd = eth_balance * eth_price
        total_usd = balance + btc_usd + eth_usd
    except Exception as e:
        print(f"❌ Ошибка расчёта USD-эквивалентов: {e}")
        btc_usd = eth_usd = total_usd = 0

    # Определяем эмодзи для лиги
    league_emojis = {
        "bronze": "🥉",
        "silver": "🥈",
        "gold": "🥇",
        "diamond": "💎"
    }
    league_emoji = league_emojis.get(league.lower(), "🏆")

    # Форматируем текст профиля
    user_prof = (
        f"👤 **ВАШ ПРОФИЛЬ**\n\n"
        f"💰 **Доллары:** ${balance:,.2f}\n\n"
        f"₿ **Bitcoin:**\n"
        f"   • Количество: {btc_balance:.6f} BTC\n"
    )

    # Добавляем USD-эквивалент, если есть цены
    if btc_price > 0:
        user_prof += f"   • Стоимость: ${btc_usd:,.2f}\n"

    user_prof += f"\nΞ **Ethereum:**\n"
    user_prof += f"   • Количество: {eth_balance:.6f} ETH\n"

    if eth_price > 0:
        user_prof += f"   • Стоимость: ${eth_usd:,.2f}\n"

    # Добавляем итог, если есть хотя бы одна цена
    if btc_price > 0 or eth_price > 0:
        user_prof += f"\n💵 **ИТОГО:** ${total_usd:,.2f}\n\n"
    else:
        user_prof += f"\n"

    user_prof += (
        f"📊 **Рейтинг:** {rating} очков\n"
        f"{league_emoji} **Лига:** {league.capitalize()}"
    )

    # Отправляем сообщение
    try:
        await message.answer(user_prof, parse_mode="Markdown")
    except Exception as e:
        print(f"❌ Ошибка отправки профиля: {e}")
        # Если Markdown вызывает ошибку, отправляем без форматирования
        await message.answer(
            user_prof.replace("*", "").replace("**", ""),
            parse_mode=None
        )


def register_handlers_profile(dp: Dispatcher):
    """Регистрация хендлера профиля"""
    dp.register_message_handler(
        profile,
        lambda message: message.text == "👤 Профиль"
    )