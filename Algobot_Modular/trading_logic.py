from config import *
from typing import Dict
import logging

# Initialize logger
logger = logging.getLogger(__name__)

def check_buy_conditions(df: Dict) -> bool:
    """Check the conditions for buying.
    
    Parameters:
    df (Dict): The data frame containing the current data.
    
    Returns:
    bool: True if all conditions are met, False otherwise.
    """
    return df['macd'].iloc[-1] <= 0 and df['ema'].iloc[-1] <= df['close'].iloc[-1] and df['rsi'].iloc[-1] <= RSI_BUY_THRESHOLD

def check_sell_conditions(df: Dict) -> bool:
    """Check the conditions for selling.
    
    Parameters:
    df (Dict): The data frame containing the current data.
    
    Returns:
    bool: True if all conditions are met, False otherwise.
    """
    return df['macd'].iloc[-1] >= 0 and df['ema'].iloc[-1] >= df['close'].iloc[-1] and df['rsi'].iloc[-1] >= RSI_SELL_THRESHOLD

def should_trade(data: Dict, condition: str) -> bool:
    """Determine whether to trade based on the current data and condition.
    
    Parameters:
    data (Dict): The data frame containing the current data.
    condition (str): The condition to check ('buy' or 'sell').
    
    Returns:
    bool: True if the condition is met, False otherwise.
    """
    logger.info(f'Starting should_trade function with condition: {condition}')
    for df in data.values():
        if condition == 'buy' and not check_buy_conditions(df):
            return False
        elif condition == 'sell' and not check_sell_conditions(df):
            return False
    logger.info(f'Ending should_trade function with condition: {condition}')
    return True

def get_optimal_quantity(symbol: str) -> float:
    """Calculate the optimal quantity to buy based on the available balance and current price.
    
    Parameters:
    symbol (str): The symbol of the asset to trade.
    
    Returns:
    float: The optimal quantity to buy.
    """
    logger.info(f'Starting get_optimal_quantity function with symbol: {symbol}')
    try:
        balance = client.get_asset_balance(asset=ASSET)
        price = client.get_symbol_ticker(symbol=symbol)
    except Exception as e:
        logger.error(f'Error getting balance or price: {e}')
        return 0
    logger.info(f'Ending get_optimal_quantity function with symbol: {symbol}')
    return float(balance['free']) / float(price['price'])

def place_order(symbol: str, side: str, quantity: float) -> float:
    """Place an order and handle partial fills.
    
    Parameters:
    symbol (str): The symbol of the asset to trade.
    side (str): The side of the trade ('buy' or 'sell').
    quantity (float): The quantity to trade.
    
    Returns:
    float: The remaining quantity if the order is partially filled, 0 otherwise.
    """
    logger.info(f'Starting place_order function with symbol: {symbol}, side: {side}, quantity: {quantity}')
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
from config import *
from typing import Dict
import logging

# Initialize logger
logger = logging.getLogger(__name__)

def check_buy_conditions(df: Dict) -> bool:
    """Check the conditions for buying.
    
    Parameters:
    df (Dict): The data frame containing the current data.
    
    Returns:
    bool: True if all conditions are met, False otherwise.
    """
    return df['macd'].iloc[-1] <= 0 and df['ema'].iloc[-1] <= df['close'].iloc[-1] and df['rsi'].iloc[-1] <= RSI_BUY_THRESHOLD

def check_sell_conditions(df: Dict) -> bool:
    """Check the conditions for selling.
    
    Parameters:
    df (Dict): The data frame containing the current data.
    
    Returns:
    bool: True if all conditions are met, False otherwise.
    """
    return df['macd'].iloc[-1] >= 0 and df['ema'].iloc[-1] >= df['close'].iloc[-1] and df['rsi'].iloc[-1] >= RSI_SELL_THRESHOLD

def should_trade(data: Dict, condition: str) -> bool:
    """Determine whether to trade based on the current data and condition.
    
    Parameters:
    data (Dict): The data frame containing the current data.
    condition (str): The condition to check ('buy' or 'sell').
    
    Returns:
    bool: True if the condition is met, False otherwise.
    """
    logger.info(f'Starting should_trade function with condition: {condition}')
    for df in data.values():
        if condition == 'buy' and not check_buy_conditions(df):
            return False
        elif condition == 'sell' and not check_sell_conditions(df):
            return False
    logger.info(f'Ending should_trade function with condition: {condition}')
    return True

def get_optimal_quantity(symbol: str) -> float:
    """Calculate the optimal quantity to buy based on the available balance and current price.
    
    Parameters:
    symbol (str): The symbol of the asset to trade.
    
    Returns:
    float: The optimal quantity to buy.
    """
    logger.info(f'Starting get_optimal_quantity function with symbol: {symbol}')
    try:
        balance = client.get_asset_balance(asset=ASSET)
        price = client.get_symbol_ticker(symbol=symbol)
    except Exception as e:
        logger.error(f'Error getting balance or price: {e}')
        return 0
    logger.info(f'Ending get_optimal_quantity function with symbol: {symbol}')
    return float(balance['free']) / float(price['price'])

def place_order(symbol: str, side: str, quantity: float) -> float:
    """Place an order and handle partial fills.
    
    Parameters:
    symbol (str): The symbol of the asset to trade.
    side (str): The side of the trade ('buy' or 'sell').
    quantity (float): The quantity to trade.
    
    Returns:
    float: The remaining quantity if the order is partially filled, 0 otherwise.
    """
    logger.info(f'Starting place_order function with symbol: {symbol}, side: {side}, quantity: {quantity}')
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
        logger.info('Order fully filled.')
        return 0

