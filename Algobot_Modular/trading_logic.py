from config import *
from typing import Dict
import logging

# Initialize logger
logger = logging.getLogger(__name__)

def check_buy_conditions(df: Dict) -> bool:
    return df['macd'].iloc[-1] <= 0 and df['ema'].iloc[-1] <= df['close'].iloc[-1] and df['rsi'].iloc[-1] <= RSI_BUY_THRESHOLD

def check_sell_conditions(df: Dict) -> bool:
    return df['macd'].iloc[-1] >= 0 and df['ema'].iloc[-1] >= df['close'].iloc[-1] and df['rsi'].iloc[-1] >= RSI_SELL_THRESHOLD

def should_buy(data: Dict) -> bool:
    for df in data.values():
        if not check_buy_conditions(df):
            return False
    return True

def should_sell(data: Dict) -> bool:
    for df in data.values():
        if not check_sell_conditions(df):
            return False
    return True

def get_optimal_quantity(symbol: str) -> float:
    try:
        balance = client.get_asset_balance(asset=ASSET)
        price = client.get_symbol_ticker(symbol=symbol)
    except Exception as e:
        logger.error(f'Error getting balance or price: {e}')
        return 0
    return float(balance['free']) / float(price['price'])

def place_order(symbol: str, side: str, quantity: float) -> float:
    try:
        order = client.create_order(
            symbol=symbol,
            side=side,
            type=Client.ORDER_TYPE_MARKET,
            quantity=quantity
        )
        if order['status'] == Client.ORDER_STATUS_PARTIALLY_FILLED:
            filled_quantity = float(order['executedQty'])
            remaining_quantity = quantity - filled_quantity
            return remaining_quantity
        else:
            return 0
    except Exception as e:
        logger.error(f'Error placing order: {e}')
        return quantity
