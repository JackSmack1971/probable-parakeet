import os
import logging
import aiohttp
import asyncio
import json
from typing import List, Set, Dict
from dotenv import load_dotenv
import telegram 

load_dotenv() 

# Use the `logging.config.dictConfig` method to configure the logging
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
            # Add more sources here
        ]
        for source in sources:
            try:
                news_data = await source['function'](*source['args'])
                yield news_data
            except Exception as error:
                logging.exception(f'Error occurred while fetching news source ({source["name"]}): {error}') 

async def post_news(bot: telegram.Bot, channel_id: str, news_data: List[Dict], posted_articles: Set[str], timeout: int) -> Set[str]:
    """
    Post news articles to Telegram channel asynchronously. 

    Parameters:
    bot (telegram.Bot): Telegram bot instance
    channel_id (str): Telegram channel id
    news_data (List[Dict]): List of news articles
    posted_articles (Set[str]): Set of already posted article ids
    timeout (int): Timeout for the request in seconds 

    Returns:
    Set[str]: Updated set of posted article ids
    """
    new_posted_articles = set()
    async with aiohttp.ClientSession() as session:
        for article in news_data:
            article_id = article['id']
            if article_id not in posted_articles:
                title = article['title']
                url = article['url']
                description = article['body'] 

                message = f'<b>{title}</b>\n{description}\n<a href="{url}">Read more</a>' 

                try:
                    await bot.send_message(
                        chat_id=channel_id,
                        text=message,
                        parse_mode=telegram.ParseMode.HTML,
                        timeout=timeout
                    )
                    new_posted_articles.add(article_id)
                except telegram.TelegramError as telegram_error:
                    logging.exception(f'Telegram error occurred while posting article: {telegram_error}')
                except Exception as error:
                    logging.exception(f'Error occurred while posting article: {error}')
                await asyncio.sleep(1) 

    return posted_articles | new_posted_articles 

async def schedule_posting(bot: telegram.Bot, channel_id: str, config: Config, interval: int, timeout: int):
    """
    Schedule news articles posting at regular intervals using asynchronous requests. 

    Parameters:
    bot (telegram.Bot): Telegram bot instance
    channel_id (str): Telegram channel id
    config (Config): Configuration object containing API keys
    interval (int): Interval between posting news articles in seconds
    timeout (int): Timeout for the request in seconds
    """
    posted_articles = set()
    message_queue = asyncio.Queue() 

    async def job():
        nonlocal posted_articles
        try:
            async for news_data in get_all_news(config):
                await message_queue.put(news_data)
        except Exception as error:
            logging.exception(f'Error occurred while running job: {error}') 

    async def send_messages():
        while True:
            news_data = await message_queue.get()
            posted_articles = await post_news(bot, channel_id, news_data, posted_articles, timeout)
            message_queue.task_done() 

    # Run the job immediately on startup
    await job() 

    # Schedule the job to run at regular intervals
    while True:
        try:
            await asyncio.sleep(interval)
            asyncio.create_task(job())
        except Exception as error:
            logging.exception(f'Error occurred while running job: {error}') 

async def main():
    """
    Main function that runs the script asynchronously
    """
    try:
        config = Config()
        config.validate() 

        bot = telegram.Bot(token=config.telegram_bot_token)
        await schedule_posting(bot, config.telegram_channel_id, config, interval=3600, timeout=10)
    except ConfigurationError as error:
        logging.exception(str(error))
    except Exception as error:
        logging.exception(f'Unhandled exception occurred: {error}')


if __name__ == '__main__':
    asyncio.run(main())
