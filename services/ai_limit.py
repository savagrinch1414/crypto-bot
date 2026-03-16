from datetime import date, timedelta
import logging
from services.ai_stats import record_daily_stats
from database.db import cursor, conn

# Настраиваем логгер
logger = logging.getLogger(__name__)

def check_ai_limit(user_id):
    """
    Проверяет, может ли пользователь сделать запрос к ИИ.
    Возвращает True, если запрос разрешён, иначе False.
    """
    DEVELOPER_ID = 1628601883
    # Разработчик не ограничен
    if user_id == DEVELOPER_ID:
        return True

    try:
        # Получаем текущие данные о запросах пользователя
        cursor.execute("SELECT ai_requests_today, last_request_date FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
    except Exception as e:
        logger.error(f"❌ Ошибка БД в check_ai_limit для {user_id}: {e}")
        # В случае ошибки лучше запретить запрос, чтобы не превысить лимит
        return False

    if not result:
        logger.warning(f"⚠️ Пользователь {user_id} не найден в БД")
        return False

    requests_today, last_date = result
    today = date.today()

    # Если последний запрос был не сегодня — обнуляем счётчик
    if last_date != today:
        # Сохраняем статистику за вчерашний день (если были запросы)
        if requests_today > 0:
            try:
                record_daily_stats()
            except Exception as e:
                logger.error(f"❌ Ошибка записи дневной статистики: {e}")
                # Не прерываем обнуление, статистика не критична

        requests_today = 0
        try:
            cursor.execute(
                "UPDATE users SET ai_requests_today = ?, last_request_date = ? WHERE id = ?",
                (requests_today, today, user_id)
            )
            conn.commit()
        except Exception as e:
            logger.error(f"❌ Ошибка обновления лимитов для {user_id}: {e}")
            return False

        # После обнуления лимит заведомо не исчерпан
        return True

    # Если сегодняшний день — проверяем, не превышен ли лимит
    if requests_today >= 10:
        return False

    return True

def increment_ai_requests(user_id):
    """
    Увеличивает счётчик использованных запросов пользователя.
    """
    DEVELOPER_ID = 1628601883
    if user_id == DEVELOPER_ID:
        return

    try:
        cursor.execute(
            "UPDATE users SET ai_requests_today = ai_requests_today + 1 WHERE id = ?",
            (user_id,)
        )
        conn.commit()
    except Exception as e:
        logger.error(f"❌ Ошибка увеличения счётчика запросов для {user_id}: {e}")