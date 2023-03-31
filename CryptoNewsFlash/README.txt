CryptoNewsFlash v1.2.0 

Description:
------------
CryptoNewsFlash is a Python script that retrieves the latest cryptocurrency news articles from the CryptoCompare API and posts them to a specified Telegram channel. The script is designed to be efficient, secure, and user-friendly, making it easy for users to stay informed about the latest developments in the cryptocurrency world. 

Features:
---------
- Retrieves news articles from the CryptoCompare API.
- Posts news articles to a Telegram channel.
- Prevents duplicate articles from being posted.
- Includes error handling for API requests, JSON parsing, and Telegram API issues.
- Stores sensitive information securely using environment variables.
- Provides input validation and configuration management.
- Implements a robust scheduling mechanism for regular news updates.
- Modular and reusable code design. 

Requirements:
-------------
- Python 3.6+
- requests library
- python-telegram-bot library
- schedule library 

Installation:
-------------
1. Install the required Python libraries:
pip install -r requirements.txt 

2. Clone the repository or download the CryptoNewsFlash.py script. 

Configuration:
--------------
1. Set the following environment variables with the corresponding values: 

- TELEGRAM_BOT_TOKEN: Your Telegram bot token.
- TELEGRAM_CHANNEL_ID: The ID of your Telegram channel.
- CRYPTO_COMPARE_API_KEY: Your CryptoCompare API key. 

2. Run the CryptoNewsFlash.py script: 

python CryptoNewsFlash.py


Changelog:
----------
Refer to the changelog provided in the GitHub repository for a detailed list of updates and improvements made in version 1.1.0. 

Support:
--------
If you have any questions, issues, or suggestions, please create an issue on the GitHub repository or contact the maintainers.
