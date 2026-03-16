from database.db import conn, cursor
from datetime import date
import logging

# Настройка логгера
logger = logging.getLogger(__name__)

def get_today_stats():
    """
    Возвращает общее количество запросов к ИИ за сегодня
    и топ-3 пользователей по запросам.
    """
    total = 0
    top_ai_users = []

    # Получаем общее количество запросов
    try:
        cursor.execute("SELECT SUM(ai_requests_today) FROM users")
        result = cursor.fetchone()
        total = result[0] if result and result[0] is not None else 0
    except Exception as e:
        logger.error(f"Ошибка получения суммы запросов: {e}")

    # Получаем топ-3 пользователей
    try:
        cursor.execute("""
            SELECT id, ai_requests_today 
            FROM users 
            WHERE ai_requests_today > 0 
            ORDER BY ai_requests_today DESC 
            LIMIT 3
        """)
        top_ai_users = cursor.fetchall()
    except Exception as e:
        logger.error(f"Ошибка получения топа пользователей: {e}")

    return total, top_ai_users

def record_daily_stats():
    """Записывает дневную статистику в таблицу ai_stats."""
    today = date.today()
    total, _ = get_today_stats()

    try:
        cursor.execute(
            "INSERT INTO ai_stats (date, total_requests) VALUES (?, ?)",
            (today, total)
        )
        conn.commit()
        logger.info(f"Дневная статистика записана: {today}, всего запросов {total}")
    except Exception as e:
        logger.error(f"Ошибка записи дневной статистики: {e}")
        conn.rollback()
