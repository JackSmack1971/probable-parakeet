from binance.client import Client
from typing import Dict
import logging
import time

# Initialize logger
logger = logging.getLogger(__name__)

def get_klines(symbol: str, interval: str, limit: int = 500) -> Dict:
    retry_delay = 1
    while True:
        try:
            klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
            return klines
        except Exception as e:
            logger.error(f"Error getting klines: {e}")
            time.sleep(retry_delay)
            retry_delay *= 2

def calculate_indicator(df: Dict, indicator: str, new_column_name: str):
    df[new_column_name] = indicator(df)
    return df

def calculate_indicators(df: Dict):
    indicators = {
        'macd': 'macd',
        'ema': 'ema',
        'rsi': 'rsi'
    }
    for indicator, new_column_name in indicators.items():
        df = calculate_indicator(df, indicator, new_column_name)
    return df

def get_data(symbol: str, intervals: list) -> Dict:
    data = {}
    for interval in intervals:
        df = get_klines(symbol, interval)
        df = calculate_indicators(df)
        data[interval] = df
    return data
