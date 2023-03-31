CryptoNewsFlash v2.0.0 

CryptoNewsFlash is a Python program that retrieves news articles related to cryptocurrencies from multiple sources, and posts them to a specified Telegram channel at regular intervals. The program supports the following news APIs: 

• CryptoCompare News API 

• CoinPaprika News API (TBD) 

• CoinGecko News API (TBD) 

Installation 

• Clone the repository to your local machine. 

• Create a virtual environment and activate it: 

python3 -m venv venv source venv/bin/activate 

Install the required dependencies: 

pip3 install -r requirements.txt 

Set the required environment variables by creating a .env file in the root directory of the project and adding the following lines: 

TELEGRAM_BOT_TOKEN=<your telegram bot token>
TELEGRAM_CHANNEL_ID=<your telegram channel id>
CRYPTO_COMPARE_API_KEY=<your CryptoCompare API key>
COIN_PAPRIKA_API_KEY=<your CoinPaprika API key>
COIN_GECKO_API_KEY=<your CoinGecko API key> 

Run the program: 

python3 CryptoNewsFlash.py 

Usage 

The program automatically retrieves and posts news articles to the specified Telegram channel at regular intervals (by default, every hour). 

Configuration 

You can configure the program by setting the following environment variables in the .env file: 

• TELEGRAM_BOT_TOKEN: The API token for your Telegram bot. 

• TELEGRAM_CHANNEL_ID: The ID of the Telegram channel where you want to post the news articles. 

• CRYPTO_COMPARE_API_KEY: The API key for the CryptoCompare News API. 

• COIN_PAPRIKA_API_KEY: The API key for the CoinPaprika News API (TBD). 

• COIN_GECKO_API_KEY: The API key for the CoinGecko News API (TBD). 

Contributing 

Pull requests and bug reports are welcome! 

License 

This program is licensed under the MIT license. See the LICENSE file for details.
