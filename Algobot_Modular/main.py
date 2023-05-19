from data_retrieval import get_data
from trading_logic import should_trade, get_optimal_quantity, place_order
from config import *

def main():
    high_volume_periods = get_high_volume_periods(SYMBOL, INTERVALS[0])
    while True:
        data = get_data(SYMBOL, INTERVALS)
        if data is not None:
            # Only trade during high volume periods
            if data[INTERVALS[0]]['time'].iloc[-1] in high_volume_periods.values:
                if should_trade(data, 'buy'):
                    quantity = get_optimal_quantity(SYMBOL)
                    remaining_quantity = place_order(SYMBOL, Client.SIDE_BUY, quantity)
                    while remaining_quantity > 0:
                        remaining_quantity = place_order(SYMBOL, Client.SIDE_BUY, remaining_quantity)
                elif should_trade(data, 'sell'):
                    quantity = get_optimal_quantity(SYMBOL)
                    remaining_quantity = place_order(SYMBOL, Client.SIDE_SELL, quantity)
                    while remaining_quantity > 0:
                        remaining_quantity = place_order(SYMBOL, Client.SIDE_SELL, remaining_quantity)
            # Store data in MongoDB
            db[SYMBOL].insert_one(data[INTERVALS[0]].to_dict())
            # Save plots to a file
            plt.figure(figsize=(14, 7))
            sns.lineplot(data=data[INTERVALS[0]], x='time', y='close')
            sns.lineplot(data=data[INTERVALS[0]], x='time', y='macd')
            sns.lineplot(data=data[INTERVALS[0]], x='time', y='ema')
            sns.lineplot(data=data[INTERVALS[0]], x='time', y='rsi')
            plt.title(f'Closing Prices and Indicators of {SYMBOL} Over Time')
            plt.savefig(f'{SYMBOL}_plot.png')
        else:
            break  # Exit the loop if there's an error getting data

if __name__ == "__main__":
    main()
