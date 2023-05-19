from config import *

def should_trade(data: dict, condition: str) -> bool:
    """Determine whether to trade based on the current data and condition."""
    for df in data.values():
        if condition == 'buy':
            if df['macd'].iloc[-1] <= 0 or df['ema'].iloc[-1] <= df['close'].iloc[-1] or df['rsi'].iloc[-1] >= RSI_BUY_THRESHOLD:
                return False
        elif condition == 'sell':
            if df['macd'].iloc[-1] >= 0 or df['ema'].iloc[-1] >= df['close'].iloc[-1] or df['rsi'].iloc[-1] <= RSI_SELL_THRESHOLD:
                return False
    return True

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
