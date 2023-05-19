from data_retrieval import get_data
from trading_logic import should_trade, get_optimal_quantity, place_order
from config import *
import sys

def place_order_with_handling(symbol, side, quantity):
    """
    This function places an order with the specified parameters and handles any remaining quantity.

    Parameters:
    symbol (str): The symbol for the asset to be traded.
    side (str): The side of the trade, either 'buy' or 'sell'.
    quantity (float): The quantity of the asset to be traded.

    Returns:
    None
    """
    remaining_quantity = place_order(symbol, side, quantity)
    while remaining_quantity > 0:
        remaining_quantity = place_order(symbol, side, remaining_quantity)

def main(plot=False, iterations=sys.maxsize):
    """
    The main function of the trading bot.

    Parameters:
    plot (bool): Whether or not to plot the closing prices and indicators over time.
    iterations (int): The number of iterations to run the main loop for.

    Returns:
    None
    """
    high_volume_periods = get_high_volume_periods(SYMBOL, INTERVALS[0])
    for _ in range(iterations):
        try:
            data = get_data(SYMBOL, INTERVALS)
        except Exception as e:
            print(f"Error getting data: {e}")
            break

        if data[INTERVALS[0]]['time'].iloc[-1] in high_volume_periods.values:
            if should_trade(data, 'buy'):
                place_order_with_handling(SYMBOL, Client.SIDE_BUY, get_optimal_quantity(SYMBOL))
            elif should_trade(data, 'sell'):
                place_order_with_handling(SYMBOL, Client.SIDE_SELL, get_optimal_quantity(SYMBOL))

            try:
                db[SYMBOL].insert_one(data[INTERVALS[0]].to_dict())
            except Exception as e:
                print(f"Error inserting data into database: {e}")

            if plot:
                plt.figure(figsize=(14, 7))
                sns.lineplot(data=data[INTERVALS[0]], x='time', y='close')
                sns.lineplot(data=data[INTERVALS[0]], x='time', y='macd')
                sns.lineplot(data=data[INTERVALS[0]], x='time', y='ema')
                sns.lineplot(data=data[INTERVALS[0]], x='time', y='rsi')
                plt.title(f'Closing Prices and Indicators of {SYMBOL} Over Time')
                plt.savefig(f'{SYMBOL}_plot.png')

if __name__ == "__main__":
    main()
