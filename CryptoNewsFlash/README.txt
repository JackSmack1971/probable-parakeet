# CryptoNewsFlash v4.0.0

CryptoNewsFlash is a Python script that retrieves news articles from various cryptocurrency news APIs and posts them to a Telegram channel. The script is designed to be efficient, secure, and easy to use. 

## Features 

- Retrieves news articles from multiple sources (currently only CryptoCompare API, but easily extensible to include others)
- Prevents duplicate news articles from being posted in the Telegram channel
- Utilizes environment variables to securely store sensitive information (API keys and bot tokens)
- Implements asyncio for better performance and asynchronous requests
- Robust error handling and logging
- Input validation for user-provided data
- PEP8 compliant code formatting 

## Installation 

1. Clone this repository or download the `CryptoNewsFlash.py` script.
2. Install the required Python libraries: 

pip install -r requirements.txt


3. Set up your environment variables for the API keys and bot tokens: 

TELEGRAM_BOT_TOKEN=your_telegram_bot_token TELEGRAM_CHANNEL_ID=your_telegram_channel_id CRYPTO_COMPARE_API_KEY=your_crypto_compare_api_key


Replace `your_telegram_bot_token`, `your_telegram_channel_id`, and `your_crypto_compare_api_key` with your actual keys and tokens. 

4. Run the script: 

python CryptoNewsFlash.py


## Usage 

After setting up the script with the proper API keys and bot tokens, simply run the script. The script will automatically retrieve news articles and post them to your configured Telegram channel at regular intervals. 

You can customize the interval between news posts by modifying the `interval` variable in the `schedule_posting` function. You can also add support for more news APIs by extending the `get_all_news` function and providing the necessary API keys in the `Config` class. 

## Contributing 

Contributions are welcome! Please submit a pull request or create an issue to propose changes or report bugs. 

## License 

This project is licensed under the MIT License. See the `LICENSE` file for details.
