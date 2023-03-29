import os
import asyncio
import threading
import logging
import time
import requests
import aiohttp
import pandas as pd
from typing import List, Dict, Tuple, Any, Optional
from concurrent.futures import ThreadPoolExecutor
from argparse import ArgumentParser
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dataclasses import dataclass
import configparser 

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
    async def call_api_async(self, url: str, params: Dict[str, str]): """Call the API with the given URL and parameters and return the response data.""" cache_key = f'{url}-{str(params)}' cache_data = self.get_cache(cache_key) if cache_data is not None: return cache_data async with aiohttp.ClientSession() as session: async with session.get(url, params=params) as response: if response.status == 429: raise aiohttp.ClientResponseError(response.request_info, response.history, status=response.status) response.raise_for_status() data = await response.json() if 'error' in data: raise aiohttp.ClientResponseError(response.request_info, response.history, status=response.status, message=data["error"]["message"]) self.set_cache(cache_key, data) return data 

    async def get_trending_shops(self, limit: int = 10, offset: Optional[int] = None) -> List[Shop]: """Get a list of trending shops from the Etsy API.""" url = f'{ETSY_API_BASE_URL}{ETSY_API_TRENDING}' params = { 'api_key': self.api_key, 'region': self.region, 'limit': limit, 'fields': ETSY_API_FIELDS_SHOP, } if offset is not None: params['offset'] = offset data = await self.call_api_async(url, params) return [Shop(**shop_data) for shop_data in data['results']] 

    async def get_shop_listings(self, shop_id: str) -> List[Listing]: """Get a list of listings for a given shop ID.""" url = f'{ETSY_API_BASE_URL}{ETSY_API_SHOPS}/{shop_id}{ETSY_API_SHOP_LISTINGS}' params = { 'api_key': self.api_key, 'fields': ETSY_API_FIELDS_LISTING, } data = await self.call_api_async(url, params) return [Listing(**listing_data, shop_id=shop_id) for listing_data in data['results']] 

    async def get_shop_sales(self, shop_id: str, limit: int = 100, offset: Optional[int] = None) -> List[Sale]: """Get a list of sales for a given shop ID.""" url = f'{ETSY_API_BASE_URL}{ETSY_API_SHOPS}/{shop_id}{ETSY_API_SHOP_RECEIPTS}' params = { 'api_key': self.api_key, 'was_paid': 'true', 'limit': limit, 'fields': ETSY_API_FIELDS_SALE, } 

        if offset is not None:             params['offset'] = offset         data = await self.call_api_async(url, params)         return [Sale(**sale_data, shop_id=shop_id) for sale_data in data['results']] 

    async def get_top_five_listings(self, shop_id: str) -> List[Listing]:         """Get a list of top five listings for a given shop ID."""         url = f'{ETSY_API_BASE_URL}{ETSY_API_SHOPS}/{shop_id}{ETSY_API_SHOP_LISTINGS}'         params = {             'api_key': self.api_key,             'fields': ETSY_API_FIELDS_LISTING,             'limit': 5,             'sort_on': 'num_favorers',             'sort_order': 'desc'         }         data = await self.call_api_async(url, params)         return [Listing(**listing_data, shop_id=shop_id) for listing_data in data['results']] 

    async def download_listing_data(self, listing: Listing, store_name: str) -> None: """Download listing data (including image) and save it to a folder.""" folder_name = f'{store_name}_{listing.title}' folder_path = os.path.join(os.getcwd(), 'data', folder_name) os.makedirs(folder_path, exist_ok=True) 

# Download and save the listing image
image_url = listing.get_image_url()
image_response = requests.get(image_url)
image_extension = os.path.splitext(image_url)[1]
image_filename = f'{listing.title}{image_extension}'
image_path = os.path.join(folder_path, image_filename)
with open(image_path, 'wb') as image_file:
    image_file.write(image_response.content) 

# Save the listing data to a JSON file
data = {
    'title': listing.title,
    'description': listing.description,
    'price': listing.price,
    'currency_code': listing.currency_code,
    'shop_id': listing.shop_id,
    'shop_name': listing.shop_name,
    'image_filename': image_filename,
    'image_url': image_url,
}
data_path = os.path.join(folder_path, 'listing_data.json')
with open(data_path, 'w') as data_file:
    json.dump(data, data_file)
    
logging.info(f"Downloaded data for listing '{listing.title}' to folder '{folder_name}'") 

with ThreadPoolExecutor(max_workers=1) as executor: # Download image image_url = listing.image_url image_path = os.path.join(folder_path, 'image.jpg') executor.submit(self.download_image, image_url, image_path) 

        # Download product description
        description_url = f'https://openapi.etsy.com/v2/listings/{listing.id}?api_key={self.api_key}'
        description_data = await self.call_api_async(description_url, {})
        if 'error' in description_data:
            raise ValueError(f"Failed to retrieve product description: {description_data['error']['message']}")
        description_html = description_data['results'][0]['description']
        description_text = BeautifulSoup(description_html, 'html.parser').text
        description_path = os.path.join(folder_path, 'description.txt')
        with open(description_path, 'w') as file:
            file.write(description_text[:5000]) # Limit to first 5000 characters to prevent excessively large files 

    logging.info(f'Downloaded data for {listing.title} in {folder_name}') 

async def download_shop_listings(self, shop: Shop, store_name: str) -> None: """Download a shop's top listings (up to 5) and save them to folders.""" listings = await self.get_shop_listings(shop.id) top_listings = sorted(listings, key=lambda l: float(l.price.replace(',', '')), reverse=True)[:5] for listing in top_listings: await self.download_listing_data(listing, store_name) 

async def download_all(self) -> None:
    """Download top listings for all trending shops."""
    trending_shops = await self.get_trending_shops()
    for shop in trending_shops:
        await self.download_shop_listings(shop, self.store_name) 

async def main(api_key: str, region: str):
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    client = APIClient(api_key, region)

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

# Create an API client
client = APIClient(api_key, region) 

# Set the store name
client.store_name = store_name 

# Download the top listings for all trending shops
try:
    await client.download_all()
except requests.exceptions.RequestException as e:
    logger.error(f"An error occurred while making a request to the Etsy API: {e}")
except aiohttp.ClientResponseError as e:
    logger.error(f"The Etsy API returned an error: {e}")
except Exception as e:
    logger.error(f"An unexpected error occurred: {e}")
async def download_listing_data(self, listing: Listing, store_name: str) -> None: """Download listing data (including image) and save it to a folder.""" folder_name = f'{store_name}_{listing.title}' folder_path = os.path.join(os.getcwd(), 'data', folder_name)
    # Check if the folder exists; if not, create it
    if not os.path.exists(folder_path):
        os.makedirs(folder_path) 

    # Download the image
    image_url = listing.image_url
    async with self.session.get(image_url) as response:
        if response.status == 200:
            image_data = await response.read() 

            # Save the image
            image_path = os.path.join(folder_path, f'{listing.title}.jpg')
            with open(image_path, 'wb') as f:
                f.write(image_data) 

    # Save the listing data to a JSON file
    listing_data = {
        'title': listing.title,
        'description': listing.description,
        'price': listing.price,
        'currency_code': listing.currency_code,
        'shop_id': listing.shop_id,
        'shop_name': listing.shop_name,
        'image_path': image_path
    }
    listing_path = os.path.join(folder_path, 'listing.json')
    with open(listing_path, 'w') as f:
        json.dump(listing_data, f) 

async def main(api_key: str, region: str, spreadsheet_id: str, sheet_name: str, store_name: str): # Set up logging logging.basicConfig(level=logging.INFO) logger = logging.getLogger(name) 

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
    with ThreadPoolExecutor() as pool:
        futures = []
        for shop in trending_shops:
            futures.append(pool.submit(client.get_shop_listings, shop.id))
            futures.append(pool.submit(client.get_shop_sales, shop.id, 5)) 

        for future in futures:
            try:
                data = await future
                if isinstance(data[0], Listing):
                    for listing in data[:5]:
                        await client.download_listing_data(listing, store_name)
                elif isinstance(data[0], Sale):
                    pass
            except Exception as e:
                logger.error(f"An error occurred while processing data: {e}") 

except requests.exceptions.RequestException as e:
    logger.error(f"An error occurred while making a request to the Etsy API: {e}")
except aiohttp.ClientResponseError as e:
    logger.error(f"The Etsy API returned an error: {e}")
except Exception as e:
    logger.error(f"An unexpected error occurred: {e}") 

if name == "main": parser = ArgumentParser() parser.add_argument('--api_key', required=True, help='Etsy API key') parser.add_argument('--region', required=True, help='Etsy region') parser.add_argument('--spreadsheet_id', required=True, help='Google Sheets spreadsheet ID') parser.add_argument('--sheet_name', required=True, help='Google Sheets sheet name') parser.add_argument('--store_name', required=True, help='Store name') 

args = parser.parse_args()
api_key = args.api_key
region = args.region
spreadsheet_id = args.spreadsheet_id
sheet_name = args.sheet_name
store_name = args.store_name 

try:
    credentials, project = google.auth.default()
    service = build('sheets', 'v4', credentials=credentials) 

except HttpError as error:
    logger.error(f"An error occurred: {error}") 

asyncio.run(main(api_key, region, spreadsheet_id, sheet_name, store_name))
