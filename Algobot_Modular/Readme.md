provided is a modular algorithmic trading bot, which is designed to automate trading on a cryptocurrency exchange. Here's a summary of what each file does:

config.py: This file sets up the configuration for the trading bot, including the Relative Strength Index (RSI) buy and sell thresholds, the delay for retrying failed operations, the asset to be traded (USDT), and the symbol for the cryptocurrency to be traded (default is BTCUSDT). It also sets up the connection string for MongoDB, which is used for data storage.

data_retrieval.py: This file contains functions for retrieving and processing trading data. It includes functions to get klines (a type of data used in cryptocurrency trading), calculate various trading indicators (Average True Range, Moving Average Convergence Divergence, Exponential Moving Average, and RSI), and retrieve and preprocess data for multiple intervals.

trading_logic.py: This file contains the trading logic for the bot. It includes functions to determine whether to trade based on the current data and condition (buy or sell), calculate the optimal quantity to buy based on the available balance and current price, and place an order while handling partial fills.

main.py: This is the main script that runs the trading bot. It retrieves high volume periods, gets the data for the specified intervals, and then checks if it should trade. If it should, it calculates the optimal quantity to trade and places the order. If the order is partially filled, it continues to place orders until the remaining quantity is zero. It also stores the data in MongoDB and saves plots of the closing prices and indicators over time.

The bot uses the Binance API (not explicitly shown in the code but implied by the use of functions like client.get_klines and client.create_order) to interact with the exchange. It uses pandas for data manipulation and TA-Lib (Technical Analysis Library) for calculating trading indicators. It also uses matplotlib and seaborn for data visualization.
