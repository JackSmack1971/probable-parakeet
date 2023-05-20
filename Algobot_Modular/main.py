from data_retrieval import get_data
from trading_logic import should_trade, get_optimal_quantity, place_order
from config import *
import sys
import logging

# Initialize logger
logger = logging.getLogger(__name__)

def place_order_with_handling(symbol: str, side: str, quantity: float):
    remaining_quantity = place_order(symbol, side, quantity)
    while remaining_quantity > 0:
        remaining_quantity = place_order(symbol, side, remaining_quantity)

def main(plot=False, iterations=sys.maxsize):
    high_volume_periods = get_high_volume_periods(SYMBOL, INTERVALS[0])
    for _ in range(iterations):
        try:
            data = get_data(SYMBOL, INTERVALS)
        except Exception as e:
            logger.error(f"Error getting data: {e}")
            break

        if data[INTERVALS[0]]['time'].iloc[-1] in high_volume_periods.values:
            if should_trade(data, 'buy'):
                place_order_with_handling(SYMBOL, Client.IDE_BUY, get_optimal_quantity(SYMBOL))
            elif should_trade(data, 'sell'):
                place_order_with_handling(SYMBOL, Client.SIDE_SELL, get_optimal_quantity(SYMBOL))

        try:
            insert_data_into_database(data)
        except Exception as e:
            logger.error(f"Error inserting data into database: {e}")
            break

        if plot:
            plot_data(data)

        time.sleep(60)
