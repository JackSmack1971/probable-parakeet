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


def main(config):
    api_key = config.get(API_SECTION, ETSY_API_KEY)
    shop_id = config.get(API_SECTION, SHOP_ID)
    spreadsheet_id = config.get(SHEET_SECTION, SPREADSHEET_ID)
    service_account_file = config.get(SHEET_SECTION, SERVICE_ACCOUNT_FILE) 

    if not api_key or not shop_id or not spreadsheet_id or not service_account_file:
        raise ValueError("Missing required values in config file") 

    etsy_api = EtsyApiWrapper(api_key)
    data_processor = DataProcessing(etsy_api) 

    processed_data = data_processor.process_listings(shop_id)
    logger.info("Processed %d listings", len(processed_data)) 

    sheets_integration = GoogleSheetsIntegration(spreadsheet_id, service_account_file)
    sheets_integration.update_sheet(processed_data)
    logger.info("Updated Google Sheets with %d rows", len(processed_data))


if __name__ == "__main__":
    args = parse_args()
    config = read_config_file(args.config_file) 

    try:
        main(config)
    except ValueError as e:
        logger.error(str(e))
    except Exception as e:
        logger.error("An unexpected error occurred: %s", str(e))
