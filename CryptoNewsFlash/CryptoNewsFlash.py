import os
import logging
import aiohttp
import asyncio
import json
from typing import List, Set, Dict
from dotenv import load_dotenv
import telegram 

load_dotenv() 

LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(levelname)s - %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
    },
    'loggers': {
        '': {
            'level': 'INFO',
            'handlers': ['console'],
        },
    },
} 

logging.config.dictConfig(LOGGING_CONFIG)


class Config:
    """
    Class for handling configuration and input validation
    """ 

    def __init__(self):
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_channel_id = os.getenv('TELEGRAM_CHANNEL_ID')
        self.crypto_compare_api_key = os.getenv('CRYPTO_COMPARE_API_KEY') 

    def validate(self) -> None:
        """
        Validate input data 

        Raises:
        ConfigError: if any input is invalid
        """
        if not self.telegram_bot_token:
            raise ConfigError('Error: TELEGRAM_BOT_TOKEN is not set.') 

        if not self.telegram_channel_id:
            raise ConfigError('Error: TELEGRAM_CHANNEL_ID is not set.') 

        if not self.crypto_compare_api_key:
            raise ConfigError('Error: CRYPTO_COMPARE_API_KEY is not set.')


async def fetch_news_source(session: aiohttp.ClientSession, url: str, timeout: int) -> List[Dict]:
    """
    Retrieve news articles from a specific URL using asynchronous requests. 

    Parameters:
    session (aiohttp.ClientSession): aiohttp ClientSession for making requests
    url (str): URL of the news source
    timeout (int): Timeout for the request in seconds 

    Returns:
    List[Dict]: List of news articles as dictionaries
    """
    try:
        async with session.get(url, timeout=timeout) as response:
            response.raise_for_status()
            data = await response.json()
            news_data = data['Data'] 

            if not isinstance(news_data, list):
                raise ValueError('API response is not a list.') 

            return news_data
    except aiohttp.ClientError as error:
        logging.exception(f'Error occurred while fetching news source ({url}): {error}')
    except (ValueError, KeyError, TypeError) as error:
        logging.exception(f'Error occurred while processing news source ({url}): {error}')
    except Exception as error:
        logging.exception(f'Unhandled exception occurred while fetching news source ({url}): {error}')
    return []


async def get_crypto_compare_news(session: aiohttp.ClientSession, api_key: str, timeout: int) -> List[Dict]:
    """
    Retrieve news articles from CryptoCompare API using asynchronous requests. 

    Parameters:
    session (aiohttp.ClientSession): aiohttp ClientSession for making requests
    api_key (str): CryptoCompare API Key
    timeout (int): Timeout for the request in seconds 

    Returns:
    List[Dict]: List of news articles as dictionaries
    """
    url = f'https://min-api.cryptocompare.com/data/v2/news/?lang=EN&api_key={api_key}'
    return await fetch_news_source(session, url, timeout) 

async def get_example_news(session: aiohttp.ClientSession, timeout: int) -> List[Dict]:
    url = 'https://example.com/api/news'
    return await fetch_news_source(session, url, timeout) 

async def get_all_news(config: Config) -> List[List[Dict]]:
    """
    Retrieve news articles from multiple news sources using asynchronous requests 

    Parameters:
    config (Config): Configuration object containing API keys 

    Yields:
    List[Dict]: List of news articles as dictionaries
    """
    async with aiohttp.ClientSession() as session:
        sources = [
            {
                'name': 'CryptoCompare',
                'function': get_crypto_compare_news,
                'args': [session, config.crypto_compare_api_key, 10],
            },
            {
                'name': 'ExampleNews',
                'function': get_example_news,
                'args': [session, 10],
            },
            # Add more sources here
        ]
        for source in sources:
            try:
                news_data = await source['function'](*source['args'])
                yield news_data
            except Exception as error:
                logging.exception(f'Error occurred while fetching news source ({source["name"]}): {error}')


def format_telegram_message(news: Dict) -> str:
    """
    Format a news article as a Telegram message 

    Parameters:
    news (Dict): News article as a dictionary 

    Returns:
    str: Formatted Telegram message
    """
    title = news.get('title', 'N/A')
    url = news.get('url', 'N/A')
    return f'{title}\n{url}'


def send_telegram_message(bot: telegram.Bot, chat_id: str, text: str) -> None:
    """
    Send a Telegram message 

    Parameters:
    bot (telegram.Bot): Telegram bot instance
    chat_id (str): Telegram chat ID
    text (str): Message text
    """
    bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML', disable_web_page_preview=True)


async def main() -> None:
    config = Config()
    config.validate() 

    bot = telegram.Bot(token=config.telegram_bot_token) 

    async for news_data in get_all_news(config):
        for news in news_data:
            message = format_telegram_message(news)
            send_telegram_message(bot, config.telegram_channel_id, message)
            await asyncio.sleep(1)


if __name__ == '__main__':
    asyncio.run(main())
