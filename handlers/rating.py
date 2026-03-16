from aiogram import Dispatcher, types
from services.user_services import get_top_users_service
from handlers.kb_buy_handlers import DEVELOPER_ID


async def rating(message: types.Message):
    """
    Показывает топ пользователей по балансу
    """
    try:
        # Получаем топ пользователей
        try:
            top_users = await get_top_users_service(limit=10)
        except Exception as e:
            print(f"❌ Ошибка получения топа пользователей: {e}")
            await message.answer(
                "⚠️ **Ошибка загрузки рейтинга**\n"
                "Не удалось получить данные. Пожалуйста, попробуйте позже.",
                parse_mode="Markdown"
            )
            return

        if not top_users:
            await message.answer(
                "📊 **Рейтинг пуст**\n\n"
                "Пока нет пользователей в рейтинге. "
                "Станьте первым, начав торговлю! 🚀",
                parse_mode="Markdown"
            )
            return

        # Формируем заголовок рейтинга
        text = "🏆 **ТОП ПОЛЬЗОВАТЕЛЕЙ** 🏆\n\n"

        # Добавляем информацию о разработчике (для проверки)
        is_developer = message.from_user.id == DEVELOPER_ID

        # Обрабатываем каждого пользователя
        successful_entries = 0
        for i, user_data in enumerate(top_users, start=1):
            try:
                # Проверяем структуру данных
                if not isinstance(user_data, (tuple, list)) or len(user_data) < 2:
                    print(f"❌ Неверный формат данных пользователя: {user_data}")
                    continue

                user_id, balance = user_data

                # Получаем информацию о пользователе
                try:
                    chat = await message.bot.get_chat(user_id)
                    name = chat.full_name

                    # Экранируем специальные символы для Markdown
                    name = name.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("`", "\\`")

                except Exception as e:
                    print(f"❌ Не удалось получить имя пользователя {user_id}: {e}")
                    # Если не удалось получить имя, используем ID
                    name = f"Пользователь {user_id}"

                    # Для разработчика показываем ID в любом случае
                    if is_developer:
                        name = f"User {user_id}"

                # Определяем медаль в зависимости от места
                if i == 1:
                    medal = "🥇"
                elif i == 2:
                    medal = "🥈"
                elif i == 3:
                    medal = "🥉"
                else:
                    medal = "📌"

                # Форматируем баланс
                formatted_balance = f"${balance:,.2f}"

                # Добавляем запись в рейтинг
                text += f"{medal} **{i}.** {name}\n"
                text += f"   💰 Баланс: {formatted_balance}\n\n"

                successful_entries += 1

            except Exception as e:
                print(f"❌ Ошибка обработки пользователя {i}: {e}")
                continue

        # Проверяем, удалось ли добавить хоть кого-то
        if successful_entries == 0:
            await message.answer(
                "⚠️ **Ошибка формирования рейтинга**\n"
                "Не удалось загрузить данные пользователей.",
                parse_mode="Markdown"
            )
            return

        # Добавляем подвал
        text += "📊 **Обновляется ежедневно**\n"
        text += "💡 Хотите быть в топе? Больше сделок — выше рейтинг!"

        # Отправляем результат
        try:
            await message.answer(text, parse_mode="Markdown")
        except Exception as e:
            print(f"❌ Ошибка отправки рейтинга (Markdown): {e}")
            # Если Markdown вызывает ошибку, отправляем без форматирования
            clean_text = text.replace("*", "").replace("_", "").replace("`", "")
            await message.answer(clean_text)

    except Exception as e:
        print(f"❌ Критическая ошибка в rating: {e}")
        import traceback
        traceback.print_exc()
        await message.answer(
            "⚠️ **Что-то пошло не так**\n"
            "Мы уже работаем над исправлением.",
            parse_mode="Markdown"
        )


def register_rating(dp: Dispatcher):
    """Регистрация хендлера рейтинга"""
    dp.register_message_handler(
        rating,
        lambda message: message.text == "🏆 Рейтинг"
    )