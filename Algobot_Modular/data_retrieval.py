import pandas as pd
import time
import traceback
from ta.volatility import AverageTrueRange
from ta.trend import MACD, EMAIndicator
from ta.momentum import RSIIndicator
from config import *
from binance.exceptions import BinanceAPIException, BinanceRequestException

# Assuming COLUMN_NAMES is defined in config.py
from config import COLUMN_NAMES

def get_klines(symbol: str, interval: str, retries: int = 3) -> list:
    """
    Retrieve klines data from Binance API.

    Parameters:
    symbol (str): The ticker symbol to get klines for.
    interval (str): The interval of klines.
    retries (int): The number of times to retry the request if it fails.

    Returns:
    list: A list of klines data.
    """
    logger.info(f"Starting get_klines for {symbol} at {interval}")
    for _ in range(retries):
        try:
            klines: list = client.get_klines(symbol=symbol, interval=interval)
            logger.info(f"Successfully retrieved klines for {symbol} at {interval}")
            return klines
        except (BinanceAPIException, BinanceRequestException) as e:
            logger.error(f"Failed to get klines: {e}\n{traceback.format_exc()}")
            if 'rate limit' in str(e):
                time.sleep(RETRY_DELAY * 10) # Wait longer if rate limit error
            else:
                time.sleep(RETRY_DELAY)
    raise Exception("Max retries exceeded for get_klines")

def calculate_indicator(data: pd.DataFrame, indicator, column: str, new_column: str) -> pd.DataFrame:
    """
    Calculate a specific indicator and add it to the dataframe.

    Parameters:
    data (pd.DataFrame): The dataframe to add the indicator to.
    indicator: The indicator to calculate.
    column (str): The column to calculate the indicator on.
    new_column (str): The name of the new column to add the indicator to.

    Returns:
    pd.DataFrame: The dataframe with the new indicator added.
    """
    ind = indicator(data[column])
    data[new_column] = ind.calculate_indicator()
    return data

def calculate_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate ATR, MACD, EMA, and RSI indicators and add them to the dataframe.

    Parameters:
    data (pd.DataFrame): The dataframe to add the indicators to.

    Returns:
    pd.DataFrame: The dataframe with the new indicators added.
    """
    logger.info("Calculating indicators")
    data = calculate_indicator(data, AverageTrueRange, 'close', 'atr')
    data = calculate_indicator(data, MACD, 'close', 'macd')
    data = calculate_indicator(data, EMAIndicator, 'close', 'ema')
    data = calculate_indicator(data, RSIIndicator, 'close', 'rsi')
    logger.info("Finished calculating indicators")
    return data

def get_data(symbol: str, intervals: list) -> dict:
    """
    Retrieve and preprocess data for multiple intervals.

    Parameters:
    symbol (str): The ticker symbol to get data for.
    intervals (list): The list of intervals to get data for.

    Returns:
    dict: A dictionary where the keys are the intervals and the values are dataframes of the data for that interval.
    """
    logger.info(f"Getting data for {symbol} at intervals {intervals}")
    data: dict = {}
    for interval in intervals:
        frame = get_klines(symbol, interval)
        df: pd.DataFrame = pd.DataFrame(frame, columns=COLUMN_NAMES
        df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
        df = calculate_indicators(df)
        data[interval] = df
    logger.info(f"Finished getting data for {symbol} at intervals {intervals}")
    return data
