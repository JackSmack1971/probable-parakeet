import argparse
import logging
from configparser import ConfigParser
from typing import List, Dict
from google.oauth2 import service_account
import gspread 

from etsy_api_wrapper import EtsyApiWrapper
from data_processing import DataProcessing 

SCOPES = ['https://www.googleapis.com/auth/spreadsheets'] 

logger = logging.getLogger(__name__) 

class GoogleSheetsIntegration:
    def __init__(self, service_account_file, spreadsheet_id):
        self.creds = service_account.Credentials.from_service_account_file(service_account_file, SCOPES)
        self.client = gspread.authorize(self.creds)
        self.spreadsheet_id = spreadsheet_id
        self.sheet = self.client.open_by_key(spreadsheet_id).sheet1 

    def update_sheet(self, processed_data):
        self.sheet.clear()
        self.sheet.append_rows(processed_data) 

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="config.ini", help="path to configuration file")
    args = parser.parse_args() 

    config = ConfigParser()
    config.read(args.config) 

    api_key = config.get("ETSY", "API_KEY")
    shop_id = config.get("ETSY", "SHOP_ID")
    etsy_api = EtsyApiWrapper(api_key, shop_id) 

    credentials_file = config.get("GOOGLE_SHEET", "service_account_file")
    spreadsheet_id = config.get("GOOGLE_SHEET", "spreadsheet_id")
    sheets_integration = GoogleSheetsIntegration(credentials_file, spreadsheet_id) 

    data_processor = DataProcessing(etsy_api)
    processed_data = data_processor.process_listings(shop_id) 

    sheets_integration.update_sheet(processed_data)
