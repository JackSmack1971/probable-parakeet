import os
import time
import logging
import pandas as pd
import numpy as np
import traceback
from binance.client import Client
from ta.volatility import AverageTrueRange
from ta.trend import MACD, EMAIndicator
from ta.momentum import RSIIndicator
from pymongo import MongoClient
import matplotlib.pyplot as plt
import seaborn as sns

# Constants
RETRY_DELAY = 5
RSI_BUY_THRESHOLD = 30
RSI_SELL_THRESHOLD = 70
ASSET = 'USDT'
MONGO_CONNECTION_STRING = os.getenv('MONGO_CONNECTION_STRING', 'mongodb://localhost:27017/')
SYMBOL = os.getenv('SYMBOL', 'BTCUSDT')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Binance API initialization
api_key = os.getenv('BINANCE_API_KEY')
api_secret = os.getenv('BINANCE_API_SECRET')

if not api_key or not api_secret:
    raise Exception("API keys not found in environment variables")

client = Client(api_key, api_secret)

mongo_client = MongoClient(MONGO_CONNECTION_STRING)
db = mongo_client['trading_data']

COLUMN_NAMES = ['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore']
INTERVALS = [Client.KLINE_INTERVAL_1MINUTE, Client.KLINE_INTERVAL_5MINUTE, Client.KLINE_INTERVAL_15MINUTE]

def get_klines(symbol: str, interval: str, retries: int = 3) -> list:
    """Retrieve klines data."""
    for _ in range(retries):
        try:
            return client.get_klines(symbol=symbol, interval=interval)
        except Exception as e:
            logger.error(f"Failed to get klines: {e}\n{traceback.format_exc()}")
            time.sleep(RETRY_DELAY)
    raise Exception("Max retries exceeded for get_klines")

def calculate_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """Calculate ATR, MACD, EMA, and RSI indicators."""
    atr = AverageTrueRange(data['high'], data['low'], data['close'])
    data['atr'] = atr.average_true_range()

    macd = MACD(data['close'])
    data['macd'] = macd.macd_diff()

    ema = EMAIndicator(data['close'])
    data['ema'] = ema.ema_indicator()

    rsi = RSIIndicator(data['close'])
    data['rsi'] = rsi.rsi()

    return data

def get_data(symbol: str, intervals: list) -> dict:
    """Retrieve and preprocess data for multiple intervals."""
    data = {}
    for interval in intervals:
        frame = get_klines(symbol, interval)
        df = pd.DataFrame(frame, columns=COLUMN_NAMES)
        df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
        df = calculate_indicators(df)
        data[interval] = df
    return data

def should_buy(data: dict) -> bool:
    """Determine whether to buy based on the current data."""
    for df in data.values():
        if df['macd'].iloc[-1] <= 0 or df['ema'].iloc[-1] <= df['close'].iloc[-1] or df['rsi'].iloc[-1] >= RSI_BUY_THRESHOLD:
            return False
    return True

def should_sell(data: dict) -> bool:
    """Determine whether to sell based on the current data."""
    for df in data.values():
        if df['macd'].iloc[-1] >= 0 or df['ema'].iloc[-1] >= df['close'].iloc[-1] or df['rsi'].iloc[-1] <= RSI_SELL_THRESHOLD:
            return False
    return True

def get_high_volume_periods(symbol: str, interval: str, periods: int = 10) -> pd.Series:
    """Get the top N high volume periods."""
    klines = get_klines(symbol, interval)
    data = pd.DataFrame(klines, columns=COLUMN_NAMES)
    data['volume'] = pd.to_numeric(data['volume'])
    high_volume_periods = data.nlargest(periods, 'volume')['time']
    return high_volume_periods

def get_optimal_quantity(symbol: str) -> float:
    """Calculate the optimal quantity to buy based on the available balance and current price."""
    balance = client.get_asset_balance(asset=ASSET)
    price = client.get_symbol_ticker(symbol=symbol)
    return float(balance['free']) / float(price['price'])

def place_order(symbol: str, side: str, quantity: float) -> float:
    """Place an order and handle partial fills."""
    order = client.create_order(
        symbol=symbol,
        side=side,
        type=Client.ORDER_TYPE_MARKET,
        quantity=quantity
    )

    # Check if the order is partially filled
    if order['status'] == Client.ORDER_STATUS_PARTIALLY_FILLED:
        filled_quantity = float(order['executedQty'])
        remaining_quantity = quantity - filled_quantity
        logger.info(f'Order partially filled. Remaining quantity: {remaining_quantity}')
        return remaining_quantity
    else:
        return 0

def main():
    high_volume_periods = get_high_volume_periods(SYMBOL, INTERVALS[0])

    while True:
        data = get_data(SYMBOL, INTERVALS)

        if data is not None:
            # Only trade during high volume periods
            if data[INTERVALS[0]]['time'].iloc[-1] in high_volume_periods.values:
                if should_buy(data):
                    quantity = get_optimal_quantity(SYMBOL)
                    remaining_quantity = place_order(SYMBOL, Client.SIDE_BUY, quantity)
                    while remaining_quantity > 0:
                        remaining_quantity = place_order(SYMBOL, Client.SIDE_BUY, remaining_quantity)
                elif should_sell(data):
                    quantity = get_optimal_quantity(SYMBOL)
                                        remaining_quantity = place_order(SYMBOL, Client.SIDE_SELL, quantity)
                    while remaining_quantity > 0:
                        remaining_quantity = place_order(SYMBOL, Client.SIDE_SELL, remaining_quantity)

            # Store data in MongoDB
            db[SYMBOL].insert_one(data[INTERVALS[0]].to_dict())

            # Plot closing prices and indicators
            plt.figure(figsize=(14, 7))
            sns.lineplot(data=data[INTERVALS[0]], x='time', y='close')
            sns.lineplot(data=data[INTERVALS[0]], x='time', y='macd')
            sns.lineplot(data=data[INTERVALS[0]], x='time', y='ema')
            sns.lineplot(data=data[INTERVALS[0]], x='time', y='rsi')
            plt.title(f'Closing Prices and Indicators of {SYMBOL} Over Time')
            plt.show()
        else:
            break  # Exit the loop if there's an error getting data

if __name__ == "__main__":
    main()
