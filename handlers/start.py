from kb.main_menu import menu_kb
from aiogram import Dispatcher, types
from database.db import cursor, conn
from datetime import datetime


async def start(message: types.Message):
    """
    Обработчик команды /start - регистрация нового пользователя или приветствие существующего
    """
    user_id = message.from_user.id
    username = message.from_user.username or "Пользователь"
    first_name = message.from_user.first_name or ""

    try:
        # Проверяем существование пользователя в БД
        try:
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
        except Exception as e:
            print(f"❌ Ошибка БД при проверке пользователя {user_id}: {e}")
            await message.answer(
                "⚠️ **Ошибка базы данных**\n"
                "Пожалуйста, попробуйте позже.",
                parse_mode="Markdown"
            )
            return

        # Если пользователь новый - создаём запись
        if user is None:
            try:
                cursor.execute(
                    "INSERT INTO users (id, balance, rating, league, btc_balance, eth_balance) "
                    "VALUES (?, 1000, 0, 'bronze', 0, 0)",
                    (user_id,)
                )
                conn.commit()
                print(f"✅ Новый пользователь зарегистрирован: {user_id} (@{username})")

                # Приветствие для нового пользователя
                welcome_text = (
                    f"👋 **Добро пожаловать, {first_name}!**\n\n"
                    f"🎉 **Вы успешно зарегистрированы в Крипто-ассистенте!**\n\n"
                    f"💰 **Вам начислено 1000 виртуальных USD** для начала торговли.\n\n"
                    f"📚 **Что вы можете делать:**\n"
                    f"• 📊 Анализировать BTC и ETH\n"
                    f"• 💰 Покупать и продавать криптовалюту\n"
                    f"• 🤖 Задавать вопросы ИИ-ассистенту\n"
                    f"• 📈 Отслеживать свой рейтинг и прогресс\n\n"
                    f"🚀 **Начните с кнопки «Купить» или «Анализ BTC»!**"
                )
                await message.answer(welcome_text, parse_mode="Markdown", reply_markup=menu_kb)

            except Exception as e:
                print(f"❌ Ошибка создания пользователя {user_id}: {e}")
                await message.answer(
                    "⚠️ **Ошибка регистрации**\n"
                    "Не удалось создать профиль. Пожалуйста, попробуйте позже.",
                    parse_mode="Markdown"
                )
                return
        else:
            # Приветствие для существующего пользователя
            try:
                # Получаем баланс пользователя для приветствия
                cursor.execute("SELECT balance FROM users WHERE id = ?", (user_id,))
                balance = cursor.fetchone()[0]

                welcome_back_text = (
                    f"👋 **С возвращением, {first_name}!**\n\n"
                    f"💰 **Ваш баланс:** ${balance:,.2f}\n\n"
                    f"📊 **Используйте меню ниже для навигации.**"
                )
                await message.answer(welcome_back_text, parse_mode="Markdown", reply_markup=menu_kb)

            except Exception as e:
                print(f"❌ Ошибка получения данных пользователя {user_id}: {e}")
                await message.answer(
                    f"👋 **С возвращением, {first_name}!**\n\n"
                    f"Используйте меню ниже для навигации.",
                    parse_mode="Markdown",
                    reply_markup=menu_kb
                )

    except Exception as e:
        print(f"❌ Критическая ошибка в start для пользователя {user_id}: {e}")
        import traceback
        traceback.print_exc()
        await message.answer(
            "⚠️ **Что-то пошло не так**\n"
            "Пожалуйста, попробуйте позже.",
            parse_mode="Markdown"
        )


def register_handlers2(dp: Dispatcher):
    """Регистрация хендлера команды /start"""
    dp.register_message_handler(start, commands="start")