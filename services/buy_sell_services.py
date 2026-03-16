import logging
from database.db import conn, cursor

# Настройка логгера для этого модуля
logger = logging.getLogger(__name__)

async def buy(user_id, coin, amount, price):
    """
    Обрабатывает покупку криптовалюты.
    Возвращает (success, message).
    """
    try:
        total_cost = amount * price

        # Получаем текущие балансы пользователя
        try:
            cursor.execute("SELECT balance, btc_balance, eth_balance FROM users WHERE id = ?", (user_id,))
            result = cursor.fetchone()
        except Exception as e:
            logger.error(f"Ошибка БД при получении баланса для покупки (user_id={user_id}): {e}")
            return False, "❌ Ошибка базы данных. Попробуйте позже."

        if not result:
            return False, "❌ Пользователь не найден. Нажмите /start для регистрации."

        balance, btc_balance, eth_balance = result

        # Проверяем, достаточно ли USD
        if total_cost > balance:
            return False, f"❌ Недостаточно USD.\nНужно {total_cost:.2f}, у вас {balance:.2f} USD"

        # Обновляем балансы
        new_balance = balance - total_cost
        if coin == "BTC":
            btc_balance += amount
        elif coin == "ETH":
            eth_balance += amount
        else:
            return False, f"❌ Неизвестная монета: {coin}"

        # Сохраняем изменения
        try:
            cursor.execute(
                "UPDATE users SET balance=?, btc_balance=?, eth_balance=? WHERE id=?",
                (new_balance, btc_balance, eth_balance, user_id)
            )
            conn.commit()
        except Exception as e:
            logger.error(f"Ошибка БД при обновлении баланса после покупки (user_id={user_id}): {e}")
            return False, "❌ Ошибка при сохранении данных. Попробуйте позже."

        return True, f"✅ Куплено {amount:.6f} {coin} за {total_cost:.2f} USD"

    except Exception as e:
        logger.error(f"Непредвиденная ошибка в buy (user_id={user_id}): {e}")
        return False, "❌ Произошла ошибка при обработке покупки."


async def sell(user_id, coin, amount, price):
    """
    Обрабатывает продажу криптовалюты.
    Возвращает (success, message).
    """
    try:
        total_earn = amount * price

        # Получаем текущие балансы
        try:
            cursor.execute("SELECT balance, btc_balance, eth_balance FROM users WHERE id = ?", (user_id,))
            result = cursor.fetchone()
        except Exception as e:
            logger.error(f"Ошибка БД при получении баланса для продажи (user_id={user_id}): {e}")
            return False, "❌ Ошибка базы данных. Попробуйте позже."

        if not result:
            return False, "❌ Пользователь не найден. Нажмите /start для регистрации."

        balance, btc_balance, eth_balance = result

        # Проверяем наличие достаточного количества монет
        if coin == "BTC":
            if amount > btc_balance:
                return False, f"❌ Недостаточно BTC.\nУ вас {btc_balance:.6f} BTC"
            btc_balance -= amount
        elif coin == "ETH":
            if amount > eth_balance:
                return False, f"❌ Недостаточно ETH.\nУ вас {eth_balance:.6f} ETH"
            eth_balance -= amount
        else:
            return False, f"❌ Неизвестная монета: {coin}"

        # Обновляем баланс USD
        balance += total_earn

        # Сохраняем изменения
        try:
            cursor.execute(
                "UPDATE users SET balance=?, btc_balance=?, eth_balance=? WHERE id=?",
                (balance, btc_balance, eth_balance, user_id)
            )
            conn.commit()
        except Exception as e:
            logger.error(f"Ошибка БД при обновлении баланса после продажи (user_id={user_id}): {e}")
            return False, "❌ Ошибка при сохранении данных. Попробуйте позже."

        return True, f"✅ Продано {amount:.6f} {coin} за {total_earn:.2f} USD"

    except Exception as e:
        logger.error(f"Непредвиденная ошибка в sell (user_id={user_id}): {e}")
        return False, "❌ Произошла ошибка при обработке продажи."


async def update_rating(user_id):
    """
    Увеличивает рейтинг пользователя на 1 и обновляет лигу.
    """
    try:
        # Получаем текущий рейтинг
        try:
            cursor.execute("SELECT rating FROM users WHERE id = ?", (user_id,))
            result = cursor.fetchone()
        except Exception as e:
            logger.error(f"Ошибка БД при получении рейтинга (user_id={user_id}): {e}")
            return

        if not result or result[0] is None:
            logger.warning(f"Пользователь {user_id} не найден в update_rating")
            return

        rating = result[0]
        rating += 1

        # Определяем новую лигу
        if rating >= 1000:
            league = "diamond"
        elif rating >= 500:
            league = "gold"
        elif rating >= 250:
            league = "silver"
        else:
            league = "bronze"

        # Сохраняем
        try:
            cursor.execute(
                "UPDATE users SET rating = ?, league = ? WHERE id = ?",
                (rating, league, user_id)
            )
            conn.commit()
        except Exception as e:
            logger.error(f"Ошибка БД при обновлении рейтинга (user_id={user_id}): {e}")

    except Exception as e:
        logger.error(f"Непредвиденная ошибка в update_rating (user_id={user_id}): {e}")

