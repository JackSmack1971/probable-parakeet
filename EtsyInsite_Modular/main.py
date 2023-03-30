from pytrends.request import TrendReq
import logging
import argparse
from dotenv import load_dotenv
from configparser import ConfigParser
from etsy_api_wrapper import EtsyApiWrapper
from google_sheets_integration import GoogleSheetsIntegration
from data_processing import DataProcessing 

load_dotenv() 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__) 

CONFIG_FILE = "config.ini"
API_SECTION = "ETSY"
SHEET_SECTION = "GOOGLE_SHEET"
ETSY_API_KEY = "API_KEY"
SHOP_ID = "SHOP_ID"
SPREADSHEET_ID = "SPREADSHEET_ID"
SERVICE_ACCOUNT_FILE = "SERVICE_ACCOUNT_FILE"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", help="path to config file")
    return parser.parse_args()


def read_config_file(config_file):
    config = ConfigParser()
    config.read(config_file)
    if not config.has_section(API_SECTION) or not config.has_option(API_SECTION, ETSY_API_KEY) or not config.has_option(API_SECTION, SHOP_ID):
        raise ValueError("Config file must have [ETSY] section with API_KEY and SHOP_ID options")
    if not config.has_section(SHEET_SECTION) or not config.has_option(SHEET_SECTION, SPREADSHEET_ID) or not config.has_option(SHEET_SECTION, SERVICE_ACCOUNT_FILE):
        raise ValueError("Config file must have [GOOGLE_SHEET] section with SPREADSHEET_ID and SERVICE_ACCOUNT_FILE options")
    return config 

def get_trends_data(keyword):
    # Authenticate and connect to the Google Trends API
    pytrends = TrendReq() 

    # Set the date range
    date_range = 'today 5-y'  # 5 years of daily data 

    # Build the payload and retrieve the data
    pytrends.build_payload(kw_list=[keyword], timeframe=date_range)
    trends_data = pytrends.interest_over_time() 

    # Rename the column to the keyword for consistency
    trends_data.rename(columns={keyword: 'trends_data'}, inplace=True) 

    return trends_data 

def main(config):
    # Retrieve the API key, shop ID, spreadsheet ID, and service account file from the config file
    api_key = config.get(API_SECTION, ETSY_API_KEY)
    shop_id = config.get(API_SECTION, SHOP_ID)
    spreadsheet_id = config.get(SHEET_SECTION, SPREADSHEET_ID)
    service_account_file = config.get(SHEET_SECTION, SERVICE_ACCOUNT_FILE) 

    # Initialize the API wrapper, data processor, and sheets integration objects
    etsy_api = EtsyApiWrapper(api_key)
    data_processor = DataProcessing(etsy_api)
    sheets_integration = GoogleSheetsIntegration(spreadsheet_id, service_account_file) 

    # Retrieve the processed data from the Etsy API and update with Google Trends data
    processed_data = data_processor.process_listings(shop_id)
    for i in range(len(processed_data)):
        listing_title = processed_data[i]['title']
        trends_data = get_trends_data(listing_title)
        if not trends_data.empty:
            processed_data[i]['trends_data'] = trends_data['trends_data'].values[0] 

    # Update the Google Sheets with the processed data
    sheets_integration.update_sheet(processed_data)


if __name__ == "__main__":
    args = parse_args()
    config = read_config_file(args.config_file) 

    try:
        main(config)
    except ValueError as e:
        logger.error(str(e))
    except Exception as e:
        logger.error("An unexpected error occurred: %s", str(e))
