import pandas as pd
from ta.volatility import AverageTrueRange
from ta.trend import MACD, EMAIndicator
from ta.momentum import RSIIndicator
from config import *

def get_klines(symbol: str, interval: str, retries: int = 3) -> list:
    """Retrieve klines data."""
    for _ in range(retries):
        try:
            return client.get_klines(symbol=symbol, interval=interval)
        except Exception as e:
            logger.error(f"Failed to get klines: {e}\n{traceback.format_exc()}")
            if 'rate limit' in str(e):
                time.sleep(RETRY_DELAY * 10)  # Wait longer if rate limit error
            else:
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
