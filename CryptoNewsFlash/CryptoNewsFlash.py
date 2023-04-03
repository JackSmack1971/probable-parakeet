#v4.0.0
import os
import logging
import requests
import telegram
import time
import json
import schedule
from typing import List, Set, Dict, Tuple
from dotenv import load_dotenv
from threading import Thread, Lock
from queue import Queue 

import aiohttp
import asyncio 

load_dotenv() 

class Config:
    """
    Class for handling configuration and input validation
    """
    def __init__(self):
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_channel_id = os.getenv('TELEGRAM_CHANNEL_ID')
        self.crypto_compare_api_key = os.getenv('CRYPTO_COMPARE_API_KEY') 

    def validate(self) -> bool:
        """
        Validate input data 

        Returns:
        bool: True if all inputs are valid, False otherwise
        """
        if not self.telegram_bot_token:
            logging.error('Error: TELEGRAM_BOT_TOKEN is not set.')
            return False 

        if not self.telegram_channel_id:
            logging.error('Error: TELEGRAM_CHANNEL_ID is not set.')
            return False 

        if not self.crypto_compare_api_key:
            logging.error('Error: CRYPTO_COMPARE_API_KEY is not set.')
            return False 

        return True 

async def get_crypto_compare_news(api_key: str) -> Tuple[List[dict], int]:
    """
    Retrieve news articles from CryptoCompare API using asynchronous requests 

    Parameters:
    api_key (str): CryptoCompare API Key 

    Returns:
    Tuple[List[dict], int]: Tuple containing list of news articles and rate limit reset time
    """
    url = f'https://min-api.cryptocompare.com/data/v2/news/?lang=EN&api_key={api_key}' 

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                news_data = data['Data']
                rate_limit_reset = int(response.headers.get('X-RateLimit-Reset', 3600)) 

                if not isinstance(news_data, list):
                    raise ValueError('API response is not a list.') 

                return news_data, rate_limit_reset
    except (aiohttp.ClientError, requests.exceptions.RequestException) as request_error:
        logging.error(f'Request error occurred: {request_error}')
        return [], 3600
    except (ValueError, KeyError, TypeError) as json_error:
        logging.error(f'JSON decoding error occurred: {json_error}')
        return [], 3600 

async def get_all_news(config: Config) -> Tuple[List[dict], int]:
    """
    Retrieve news articles from multiple news sources using asynchronous requests 

    Parameters:
    config (Config): Configuration object containing API keys 

    Returns:
    Tuple[List[dict], int]: Tuple containing list of news articles and minimum rate limit reset time
    """
    crypto_compare_news, crypto_compare_reset = await get_crypto_compare_news(config.crypto_compare_api_key) 

    all_news = crypto_compare_news
    min_reset_time = crypto_compare_reset 

    return all_news, min_reset_time 

def post_news(bot: telegram.Bot, channel_id: str, news_data: List[dict], posted_articles: Set[str]) -> Set[str]:
    """
    Post news articles to Telegram channel 

    Parameters:
    bot (telegram.Bot): Telegram bot instance
    channel_id (str): Telegram channel id
    news_data (List[dict]): List of news articles
    posted_articles (Set[str]): Set of already posted article ids 

    Returns:
    Set[str]: Updated set of posted article ids
    """
    new_posted_articles = set() 

    for article in news_data:
        article_id = article['id']
        if article_id not in posted_articles:
            title = article['title']
            url = article['url']
            description = article['body'] 

            message = f'<b>{title}</b>\n{description}\n<a href="{url}">Read more</a>' 

            try:
                bot.send_message(chat_id=channel_id, text=message, parse_mode=telegram.ParseMode.HTML)
                new_posted_articles.add(article_id)
            except telegram.TelegramError as telegram_error:
                logging.error(f'Telegram error occurred while posting article: {telegram_error}')
            except Exception as error:
                logging.error(f'Error occurred while posting article: {error}')
            time.sleep(1) 

    return posted_articles.union(new_posted_articles) 

async def schedule_posting(bot: telegram.Bot, channel_id: str, config: Config, interval: int):
    """
    Schedule news articles posting at regular intervals using asynchronous requests 

    Parameters:
    bot (telegram.Bot): Telegram bot instance
    channel_id (str): Telegram channel id
    config (Config): Configuration object containing API keys
    interval (int): Interval between posting news articles in seconds
    """
    posted_articles = set() 

    async def job():
        nonlocal posted_articles
        try:
            news_data, rate_limit_reset = await get_all_news(config)
            posted_articles = post_news(bot, channel_id, news_data, posted_articles)
            nonlocal interval
            interval = rate_limit_reset
        except Exception as error:
            logging.error(f'Error occurred while running job: {error}') 

    # Run the job immediately on startup
    await job() 

    # Schedule the job to run at regular intervals
    while True:
        try:
            await asyncio.sleep(interval)
            await job()
        except Exception as error:
            logging.error(f'Error occurred while running job: {error}') 

async def main():
    """
    Main function that runs the script asynchronously
    """
    try:
        config = Config()
        if not config.validate():
            return 

        bot = telegram.Bot(token=config.telegram_bot_token) 

        await schedule_posting(bot, config.telegram_channel_id, config, 3600)
    except Exception as error:
        logging.error(f'Unhandled exception occurred: {error}') 

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    asyncio.run(main())
