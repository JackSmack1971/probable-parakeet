import os
import aiohttp
import logging
import threading
import time
import asyncio
import requests
import pandas as pd
import google.auth
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dataclasses import dataclass
import configparser
from typing import List, Dict, Tuple, Any, Optional
from concurrent.futures import ThreadPoolExecutor
from argparse import ArgumentParser
# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')
ETSY_API_KEY = config.get('ETSY', 'API_KEY')
ETSY_REGION = config.get('ETSY', 'REGION')
CACHE_EXPIRATION = int(config.get('CACHE', 'EXPIRATION')) 

# Constants
ETSY_API_BASE_URL = 'https://openapi.etsy.com/v2'
ETSY_API_TRENDING = '/trending/get'
ETSY_API_SHOPS = '/shops'
ETSY_API_SHOP_LISTINGS = '/listings/active'
ETSY_API_SHOP_RECEIPTS = '/receipts'
ETSY_API_FIELDS_SHOP = 'Shop(id,user_id,shop_name)'
ETSY_API_FIELDS_LISTING = 'title,description,price,currency_code'
ETSY_API_FIELDS_SALE = 'creation_tsz,total_price,currency_code'
# Data classes
@dataclass
class Shop:
    """A class representing an Etsy shop."""
    id: str
    user_id: str
    shop_name: str 

@dataclass
class Listing:
    """A class representing an Etsy listing."""
    title: str
    description: str
    price: str
    currency_code: str
    shop_id: str
    shop_name: str 

@dataclass
class Sale:
    """A class representing an Etsy sale."""
    creation_tsz: int
    total_price: str
    currency_code: str
    shop_id: str
    shop_name: str 

class APIClient:
    """A class representing an API client for Etsy.""" 

    def __init__(self, api_key: str, region: str):
        """Initialize the API client with an API key and region."""
        self.api_key = api_key
        self.region = region
        self.lock = threading.Lock()
        self.cache = {}
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__) 

    def get_cache(self, cache_key: str) -> Optional[Any]:
        """Get the cache entry for a given key if it exists and has not expired."""
        with self.lock:
            if cache_key in self.cache:
                cache_entry = self.cache[cache_key]
                if time.time() - cache_entry['timestamp'] < CACHE_EXPIRATION:
                    return cache_entry['data']
            return None 

    def set_cache(self, cache_key: str, data: Any):
        """Set the cache entry for a given key."""
        with self.lock:
            self.cache[cache_key] = {
                'timestamp': time.time(),
                'data': data
            } 

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def call_api_async(self, url: str, params: Dict[str, str]) -> Any:
        """Call the API with the given URL and parameters and return the response data."""
        cache_key = f'{url}-{str(params)}'
        cache_data = self.get_cache(cache_key)
        if cache_data is not None:
            return cache_data
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 429:
                    raise aiohttp.ClientResponseError(response.request_info, response.history, status=response.status)
                response.raise_for_status()
                data = await response.json()
                if 'error' in data:
                    raise aiohttp.ClientResponseError(response.request_info, response.history, status=response.status, message=data["error"]["message"])
                self.set_cache(cache_key, data)
                return data
    async def get_trending_shops(self, limit: int = 10, offset: Optional[int] = None) -> List[Shop]:
        """Get a list of trending shops from the Etsy API."""
        url = f'{ETSY_API_BASE_URL}{ETSY_API_TRENDING}'
        params = {
            'api_key': self.api_key,
            'region': self.region,
            'limit': limit,
            'fields': ETSY_API_FIELDS_SHOP,
        }
        if offset is not None:
            params['offset'] = offset
        data = await self.call_api_async(url, params)
        return [Shop(**shop_data) for shop_data in data['results']] 

    async def get_shop_listings(self, shop_id: str) -> List[Listing]:
        """Get a list of listings for a given shop ID."""
        url = f'{ETSY_API_BASE_URL}{ETSY_API_SHOPS}/{shop_id}{ETSY_API_SHOP_LISTINGS}'
        params = {
            'api_key': self.api_key,
            'fields': ETSY_API_FIELDS_LISTING,
        }
        data = await self.call_api_async(url, params)
        return [Listing(**listing_data, shop_id=shop_id) for listing_data in data['results']] 

    async def get_shop_sales(self, shop_id: str, limit: int = 100, offset: Optional[int] = None) -> List[Sale]:
        """Get a list of sales for a given shop ID."""
        url = f'{ETSY_API_BASE_URL}{ETSY_API_SHOPS}/{shop_id}{ETSY_API_SHOP_RECEIPTS}'
        params = {
            'api_key': self.api_key,
            'was_paid': 'true',
            'limit': limit,
            'fields': ETSY_API_FIELDS_SALE,
        }
        if offset is not None:
            params['offset'] = offset
        data = await self.call_api_async(url, params)
        return [Sale(**sale_data, shop_id=shop_id) for sale_data in data['results']] 

async def main(api_key: str, region: str, spreadsheet_id: str, sheet_name: str):
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__) 

    client = APIClient(api_key, region) 

    try:
        credentials, project = google.auth.default()
        service = build('sheets', 'v4', credentials=credentials)
    except HttpError as error:
        logger.error(f"An error occurred while authenticating with Google Sheets API: {error}") 

    try:
        trending_shops = await client.get_trending_shops()
        logger.info(f"Found {len(trending_shops)} trending shops") 

        # Fetch shop listings and sales concurrently
        for shop in trending_shops:
            listings_future = asyncio.create_task(client.get_shop_listings(shop.id))
            sales_future = asyncio.create_task(client.get_shop_sales(shop.id))
            listings = await listings_future
            logger.info(f"Fetched {len(listings)} listings for shop {shop.shop_name}")
            sales = await sales_future
            logger.info(f"Fetched {len(sales)} sales for shop {shop.shop_name}")
    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred while making a request to the Etsy API: {e}")
    except aiohttp.ClientResponseError as e:
        logger.error(f"The Etsy API returned an error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}") 

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--api_key', required=True, help='Etsy API key')
    parser.add_argument('--region', required=True, help='Etsy region') 

    args = parser.parse_args()
    api_key = args.api_key
    region = args.region 

    try:
        credentials, project = google.auth.default()
        service = build('sheets', 'v4', credentials=credentials) 

    except HttpError as error:
        logger.error(f"An error occurred: {error}")
    except Exception as e:
        logger.error(f"Error: {e}") 

    asyncio.run(main(api_key, region)) 

async def main(api_key: str, region: str, spreadsheet_id: str, sheet_name: str):
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__) 

    client = APIClient(api_key, region) 

    try:
        credentials, project = google.auth.default()
        service = build('sheets', 'v4', credentials=credentials)
    except HttpError as error:
        logger.error(f"An error occurred while authenticating with Google Sheets API: {error}") 

    try:
        trending_shops = await client.get_trending_shops()
        logger.info(f"Found {len(trending_shops)} trending shops") 

        # Fetch shop listings and sales concurrently
        with ThreadPoolExecutor(max_workers=10) as executor:
            shop_data = []
            for shop in trending_shops:
                listings_future = executor.submit(client.get_shop_listings, shop.id)
                sales_future = executor.submit(client.get_shop_sales, shop.id)
                shop_data.append({
                    'shop': shop,
                    'listings_future': listings_future,
                    'sales_future': sales_future,
                }) 

            for data in shop_data:
                shop = data['shop']
                listings = await data['listings_future']
                logger.info(f"Fetched {len(listings)} listings for shop {shop.shop_name}")
                sales = await data['sales_future']
                logger.info(f"Fetched {len(sales)} sales for shop {shop.shop_name}") 

                # Write data to Google Sheets
                spreadsheet_body = {
                    'values': [
                        [shop.shop_name, listing.title, listing.description, listing.price, sale.creation_tsz, sale.total_price]
                        for listing in listings
                        for sale in sales
                        if sale.shop_id == shop.id and sale.currency_code == listing.currency_code
                    ]
                }
                result = service.spreadsheets().values().append(
                    spreadsheetId=spreadsheet_id,
                    range=f"{sheet_name}!A:B",
                    valueInputOption='USER_ENTERED',
                    insertDataOption='INSERT_ROWS',
                    body=spreadsheet_body
                ).execute()
                logger.info(f"Added {result['updates']['updatedRows']} rows to Google Sheets for shop {shop.shop_name}")
    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred while making a request to the Etsy API: {e}")
    except aiohttp.ClientResponseError as e:
        logger.error(f"The Etsy API returned an error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}") 

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--api_key', required=True, help='Etsy API key')
    parser.add_argument('--region', required=True, help='Etsy region')
    parser.add_argument('--spreadsheet_id', required=True, help='Google Sheets spreadsheet ID')
    parser.add_argument('--sheet_name', required=True, help='Google Sheets sheet name') 

    args = parser.parse_args()
    api_key = args.api_key
    region = args.region
    spreadsheet_id = args.spreadsheet_id
    sheet_name = args.sheet_name 

    try:
        credentials, project = google.auth.default()
        service = build('sheets', 'v4', credentials=credentials) 

    except HttpError as error:
        logger.error(f"An error occurred: {error}")
    except Exception as e:
        logger.error(f"Error: {e}") 

    asyncio.run(main(api_key, region, spreadsheet_id, sheet_name))
