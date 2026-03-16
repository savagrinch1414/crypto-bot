import requests
import os
import logging
from dotenv import load_dotenv
from pathlib import Path
from services.ai_cache import get_cached_answer, save_to_cache

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)
logger.info(f"Загружаем .env из: {env_path}")

BOTHUB_API_KEY = os.getenv("BOTHUB_API_KEY")
if not BOTHUB_API_KEY:
    logger.error("❌ BOTHUB_API_KEY не найден в .env файле!")
else:
    logger.info(f"✅ Ключ загружен, длина: {len(BOTHUB_API_KEY)}")


def ask_openrouter(system_prompt, user_prompt, max_tokens=150):
    """
    Отправляет запрос к BotHub API (DeepSeek R1) и возвращает ответ.
    Использует кеш для повторяющихся вопросов.
    """
    full_question = f"{system_prompt}\n{user_prompt}"

    # Проверка кеша
    try:
        cached = get_cached_answer(full_question)
        if cached:
            logger.info('🎯 Найден ответ в кеше!')
            return cached
    except Exception as e:
        logger.error(f"❌ Ошибка при проверке кеша: {e}")
        # При ошибке кеша продолжаем без него

    logger.info("🔄 Запрос к ИИ (кеш пуст)")

    # Проверка наличия ключа API
    if not BOTHUB_API_KEY:
        return "❌ Ошибка: отсутствует API-ключ BotHub. Проверьте файл .env"

    # Формирование сообщений
    try:
        if system_prompt and system_prompt.strip():
            combined_prompt = f"{system_prompt}\n\n{user_prompt}"
            messages = [{"role": "user", "content": combined_prompt}]
        else:
            messages = [{"role": "user", "content": user_prompt}]
    except Exception as e:
        logger.error(f"❌ Ошибка формирования сообщений: {e}")
        return "❌ Внутренняя ошибка при подготовке запроса"

    # BotHub API
    url = "https://bothub.chat/api/v2/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {BOTHUB_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-r1",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": max_tokens
    }

    try:
        logger.info(f"📤 Отправляем запрос на {url}")
        response = requests.post(url, headers=headers, json=data, timeout=30)

        if response.status_code == 200:
            try:
                result = response.json()
                answer = result["choices"][0]["message"]["content"]
                # Сохраняем в кеш (с обработкой ошибок)
                try:
                    save_to_cache(full_question, answer)
                except Exception as e:
                    logger.error(f"❌ Ошибка сохранения в кеш: {e}")
                return answer
            except (KeyError, IndexError, ValueError) as e:
                logger.error(f"❌ Ошибка парсинга ответа: {e}")
                return "❌ Не удалось обработать ответ от ИИ"
        else:
            error_msg = f"❌ Ошибка API: {response.status_code} - {response.text}"
            logger.error(error_msg)
            return error_msg

    except requests.exceptions.Timeout:
        logger.error("❌ Таймаут при запросе к ИИ")
        return "❌ Превышено время ожидания ответа от ИИ"
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Ошибка соединения: {e}")
        return f"❌ Ошибка соединения с сервером ИИ"
    except Exception as e:
        logger.error(f"❌ Непредвиденная ошибка: {e}")
        return "❌ Произошла непредвиденная ошибка"