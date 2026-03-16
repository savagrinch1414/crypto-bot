from database.db import conn, cursor
from datetime import date
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_cached_answer(question, days=3):
    """Получить ответ из кеша, если есть свежий."""
    try:
        cursor.execute(
            "SELECT answer FROM ai_cache WHERE question = ? AND created_at >= date('now', ?)",
            (question, f'-{days} days')
        )
        result = cursor.fetchone()
        if result:
            answer = result[0]
            # Очистка от кавычек, если вдруг сохранились
            if answer.startswith('"') and answer.endswith('"'):
                answer = answer[1:-1]
            elif answer.startswith("'") and answer.endswith("'"):
                answer = answer[1:-1]
            logger.info(f"✅ Найден ответ в кеше для вопроса: {question[:50]}...")
            return answer
        else:
            logger.info(f"❌ Кеш промах для вопроса: {question[:50]}...")
            return None
    except Exception as e:
        logger.error(f"Ошибка в get_cached_answer: {e}")
        return None

def save_to_cache(question, answer):
    """Сохранить ответ в кеш."""
    try:
        today = date.today().isoformat()  # явно в строку YYYY-MM-DD
        cursor.execute(
            "INSERT INTO ai_cache (question, answer, created_at) VALUES (?, ?, ?)",
            (question, answer, today)
        )
        conn.commit()
        logger.info(f"💾 Сохранено в кеш: {question[:30]}...")
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения в кеш: {e}")
        # Можно также откатить транзакцию, если нужно
        conn.rollback()

def clean_old_cache(days=3):
    """Удалить записи старше указанного числа дней."""
    try:
        cursor.execute(
            "DELETE FROM ai_cache WHERE created_at < date('now', ?)",
            (f'-{days} days',)
        )
        deleted = cursor.rowcount
        conn.commit()
        logger.info(f"🧹 Очистка кеша: удалено {deleted} записей старше {days} дней")
        return deleted
    except Exception as e:
        logger.error(f"❌ Ошибка при очистке кеша: {e}")
        return 0