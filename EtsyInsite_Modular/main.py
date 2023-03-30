from pytrends.request import TrendReq
import logging
import argparse
from dotenv import load_dotenv
from configparser import ConfigParser
from pathlib import Path
from etsy_api_wrapper import EtsyApiWrapper
from google_sheets_integration import GoogleSheetsIntegration
from data_processing import DataProcessing 

load_dotenv() 

CONFIG_FILE = "config.ini"
API_SECTION = "ETSY"
SHEET_SECTION = "GOOGLE_SHEET"
ETSY_API_KEY = "API_KEY"
SHOP_ID = "SHOP_ID"
SPREADSHEET_ID = "SPREADSHEET_ID"
SERVICE_ACCOUNT_FILE = "SERVICE_ACCOUNT_FILE"


def configure_logging():
    """Configure logging for the script."""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    return logger


logger = configure_logging()


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", type=Path, help="path to config file")
    return parser.parse_args()


def read_config_file(config_file):
    """
    Read the configuration file. 

    :param config_file: Path to the configuration file.
    :return: ConfigParser object with the parsed configuration.
    """
    config = ConfigParser()
    config.read(config_file)
    if not config.has_section(API_SECTION) or not config.has_option(API_SECTION, ETSY_API_KEY) or not config.has_option(API_SECTION, SHOP_ID):
        raise ValueError("Config file must have [ETSY] section with API_KEY and SHOP_ID options")
    if not config.has_section(SHEET_SECTION) or not config.has_option(SHEET_SECTION, SPREADSHEET_ID) or not config.has_option(SHEET_SECTION, SERVICE_ACCOUNT_FILE):
        raise ValueError("Config file must have [GOOGLE_SHEET] section with SPREADSHEET_ID and SERVICE_ACCOUNT_FILE options")
    return config


def get_trends_data(keyword):
    """
    Get Google Trends data for the given keyword. 

    :param keyword: Keyword to retrieve the Google Trends data.
    :return: Google Trends data DataFrame.
    """
    pytrends = TrendReq()
    date_range = 'today 5-y'
    pytrends.build_payload(kw_list=[keyword], timeframe=date_range)
    trends_data = pytrends.interest_over_time()
    trends_data.rename(columns={keyword: 'trends_data'}, inplace=True)
    return trends_data 

def retrieve_and_process_data(config):
    """
    Retrieve and process data from the Etsy API and Google Trends. 

    :param config: ConfigParser object with the parsed configuration.
    :return: Processed data with Google Trends information.
    """
    api_key = config.get(API_SECTION, ETSY_API_KEY)
    shop_id = config.get(API_SECTION, SHOP_ID)
    spreadsheet_id = config.get(SHEET_SECTION, SPREADSHEET_ID)
    service_account_file = config.get(SHEET_SECTION, SERVICE_ACCOUNT_FILE) 

    etsy_api = EtsyApiWrapper(api_key)
    data_processor = DataProcessing(etsy_api)
    sheets_integration = GoogleSheetsIntegration(spreadsheet_id, service_account_file) 

    processed_data = data_processor.process_listings(shop_id)
    for i in range(len(processed_data)):
        listing_title = processed_data[i]['title']
        trends_data = get_trends_data(listing_title)
        if not trends_data.empty:
            processed_data[i]['trends_data'] = trends_data['trends_data'].values[0] 

    sheets_integration.update_sheet(processed_data)
    return processed_data


def main(config):
        """
    Main function to run the script. 

    :param config: ConfigParser object with the parsed configuration.
    """
    try:
        retrieve_and_process_data(config)
    except ValueError as e:
        logger.error(f"{e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    args = parse_args()
    config = read_config_file(args.config_file)
    main(config)
