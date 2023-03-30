import logging
import requests
from typing import List, Dict
from urllib.parse import quote
from cachetools import cached, TTLCache 

logger = logging.getLogger(__name__) 

BASE_URL = "https://openapi.etsy.com"
MAX_RESULTS_PER_PAGE = 100 

cache = TTLCache(maxsize=1000, ttl=600) 

class EtsyApiWrapper:
    """
    A wrapper for the Etsy API that handles authentication and requests.
    """
    def __init__(self, api_key: str, version: str = "v2"):
        self.api_key = api_key
        self.version = version 

    @cached(cache)
    def get_shop_listings(self, shop_id: str, limit: int = MAX_RESULTS_PER_PAGE, offset: int = 0) -> List[Dict[str, any]]:
        """
        Returns a list of active listings for the given shop ID.
        """
        url = f"{BASE_URL}/{self.version}/shops/{quote(shop_id)}/listings/active"
        params = {
            "api_key": self.api_key,
            "limit": limit,
            "offset": offset,
        }
        response = requests.get(url, params=params)
        data = response.json() 

        if response.status_code != requests.codes.ok:
            error_message = data.get('error', 'Unknown error')
            raise ValueError(f"Error retrieving listings for shop {shop_id}: {error_message} (status code: {response.status_code})") 

        return data["results"] 

    def get_all_shop_listings(self, shop_id: str) -> List[Dict[str, any]]:
        """
        Returns a list of all active listings for the given shop ID, using pagination.
        """
        all_listings = []
        url = f"{BASE_URL}/{self.version}/shops/{quote(shop_id)}/listings/active" 

        while url:
            response = requests.get(url, params={"api_key": self.api_key})
            data = response.json() 

            if response.status_code != requests.codes.ok:
                error_message = data.get('error', 'Unknown error')
                raise ValueError(f"Error retrieving listings for shop {shop_id}: {error_message} (status code: {response.status_code})")
            elif response.status_code == requests.codes.too_many_requests:
                retry_after_seconds = int(response.headers.get('Retry-After', '60'))
                logger.warning(f"Rate limited by Etsy API, retrying after {retry_after_seconds} seconds...")
                time.sleep(retry_after_seconds)
                continue 

            all_listings.extend(data["results"])
            url = data.get("pagination", {}).get("next_url") 

        return all_listings
