import logging
from typing import List, Dict
from decimal import Decimal
from etsy_api_wrapper import EtsyApiWrapper 

logger = logging.getLogger(__name__) 

KEY_TITLE = "title"
KEY_LISTING_ID = "listing_id"
KEY_PRICE = "price"
KEY_CURRENCY_CODE = "currency_code"
KEY_QUANTITY = "quantity"
KEY_VIEWS = "views"
KEY_NUM_FAVORERS = "num_favorers"


class DataProcessing:
    """
    A class for processing raw Etsy API listing data into a standardized format.
    """
    def __init__(self, etsy_api_wrapper: EtsyApiWrapper):
        self.etsy_api = etsy_api_wrapper 

    def process_listings(self, shop_id: str, batch_size: int = 1000) -> List[Dict[str, any]]:
        """
        Retrieves and processes all active listings for the given shop ID.
        """
        if not isinstance(batch_size, int) or batch_size < 1:
            raise ValueError(f"Invalid batch size: {batch_size}") 

        logger.info("Retrieving listings for shop ID %s", shop_id) 

        all_listings = self.etsy_api.get_all_shop_listings(shop_id)
        processed_data = [] 

        for i in range(0, len(all_listings), batch_size):
            batch_listings = all_listings[i:i+batch_size]
            processed_batch = self._process_listings_batch(batch_listings)
            processed_data.extend(processed_batch) 

        return processed_data 

    def _process_listings_batch(self, batch_listings: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """
        Processes a batch of raw Etsy API listings into a standardized format.
        """
        processed_data = [] 

        for listing in batch_listings:
            try:
                processed_listing = {
                    KEY_TITLE: listing.get(KEY_TITLE, "N/A"),
                    KEY_LISTING_ID: listing.get(KEY_LISTING_ID, "N/A"),
                    KEY_PRICE: Decimal(str(listing.get(KEY_PRICE, 0))),
                    KEY_CURRENCY_CODE: listing.get(KEY_CURRENCY_CODE, "N/A"),
                    KEY_QUANTITY: int(listing.get(KEY_QUANTITY, 0)),
                    KEY_VIEWS: int(listing.get(KEY_VIEWS, 0)),
                    KEY_NUM_FAVORERS: int(listing.get(KEY_NUM_FAVORERS, 0)),
                }
            except (ValueError, TypeError) as e:
                logger.warning("Error processing listing: %s", e)
                continue 

            processed_data.append(processed_listing) 

        return processed_data
