//v1.2.0//
import os
import logging
import requests
import telegram
import time
import json
import schedule
from typing import List, Set 

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

def get_news(api_key: str) -> List[dict]:
    """
    Retrieve news articles from CryptoCompare API 

    Parameters:
    api_key (str): CryptoCompare API Key 

    Returns:
    List[dict]: List of news articles
    """
    url = f'https://min-api.cryptocompare.com/data/v2/news/?lang=EN&api_key={api_key}' 

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()['Data']
        if not isinstance(data, list):
            raise ValueError('API response is not a list.')
        return data
    except requests.exceptions.RequestException as request_error:
        logging.error(f'Request error occurred: {request_error}')
        return []
    except (ValueError, KeyError, TypeError) as json_error:
        logging.error(f'JSON decoding error occurred: {json_error}')
        return [] 

def post_news(bot: telegram.Bot, channel_id: str, api_key: str, posted_articles: Set[str]) -> Set[str]:
    """
    Retrieve and post news articles to Telegram channel 

    Parameters:
    bot (telegram.Bot): Telegram bot instance
    channel_id (str): Telegram channel id
    api_key (str): CryptoCompare API Key
    posted_articles (Set[str]): Set of already posted article ids 

    Returns:
    Set[str]: Updated set of posted article ids
    """
    data = get_news(api_key)
    new_posted_articles = set() 

    for article in data:
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

def schedule_posting(bot: telegram.Bot, channel_id: str, api_key: str, interval: int):
    """
    Schedule news articles posting at regular intervals 

    Parameters:
    bot (telegram.Bot): Telegram bot instance
    channel_id (str): Telegram channel id
    api_key (str): CryptoCompare API Key
    interval (int): Interval between posting news articles in seconds
    """
    posted_articles = set() 

    def job():
        nonlocal posted_articles
        try:
            posted_articles = post_news(bot, channel_id, api_key, posted_articles)
        except Exception as error:
            logging.error(f'Error occurred while running job: {error}') 

    # Run the job immediately on startup
    job() 

    # Schedule the job to run at regular intervals
    schedule.every(interval).seconds.do(job) 

    # Keep running the scheduler
    while True:
        try:
            schedule.run_pending()
        except Exception as error:
            logging.error(f'Error occurred while running job: {error}')
        time.sleep(1) 

def main():
    """
    Main function that runs the script
    """
    try:
        config = Config()
        if not config.validate():
            return 

        bot = telegram.Bot(token=config.telegram_bot_token) 

        schedule_posting(bot, config.telegram_channel_id, config.crypto_compare_api_key, 3600)
    except Exception as error:
        logging.error(f'Unhandled exception occurred: {error}')


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    main()
