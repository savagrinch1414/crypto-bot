from loader import dp
from binance.spot import Spot
import time


def get_coin_usd_value(coin, amount):

    crypto_service = dp['crypto_service']
    btc_price = crypto_service.get_btc_price()
    eth_price = crypto_service.get_eth_price()

    if coin == 'BTC':
        return amount * btc_price
    elif coin == 'ETH':
        return amount * eth_price
    else:
        return 0


class CryptoServices:
    def __init__(self):
        self.client = Spot()

        self.price_cache = {}
        self.cache_time = {}
        self.cache_ttl = 10


    def get_price(self, symbol):
        current_time = time.time()
        if symbol in self.price_cache:
            if current_time - self.cache_time[symbol] < self.cache_ttl:
                return self.price_cache[symbol]

        try:
            ticker = self.client.ticker_price(symbol)
            price = float(ticker["price"])

            self.price_cache[symbol] = price
            self.cache_time[symbol] = current_time

            return price
        except Exception as e:
            print(f"Ошибка получения цены {symbol}: {e}")
            return self.price_cache.get(symbol, 0)

    def get_btc_price(self):
        return self.get_price('BTCUSDT')

    def get_eth_price(self):
        return self.get_price('ETHUSDT')

    def get_coin_usd_value(self, coin, amount):
        if coin == 'BTC':
            price = self.get_btc_price()
        elif coin == 'ETH':
            price = self.get_eth_price()
        else:
            return 0
        return amount * price







    def get_rsi(self, symbol, period=14, interval='1h'):
        try:

            klines = self.client.klines(symbol, interval, limit=period + 1)
            closes = [float(k[4]) for k in klines]
            return self._compute_rsi(closes, period)
        except Exception as e:
            print(f"❌ Ошибка при получении RSI для {symbol}: {e}")
            return None

    def _compute_rsi(self, closes, period):
        deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
        gain = [d if d > 0 else 0 for d in deltas]
        loss = [-d if d < 0 else 0 for d in deltas]

        avg_gain = sum(gain[:period]) / period
        avg_loss = sum(loss[:period]) / period

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - 100 / (1 + rs)
        return round(rsi, 2)

