import os
import logging
from binance.client import Client
from dotenv import load_dotenv

load_dotenv()

def get_env_variable(var_name):
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = f"Missing environment variable: {var_name}"
        logging.error(error_msg)
        raise Exception(error_msg)

class Config:
    BINANCE_API_KEY = get_env_variable("BINANCE_API_KEY")
    BINANCE_API_SECRET = get_env_variable("BINANCE_API_SECRET")
    DATABASE_HOST = get_env_variable("DATABASE_HOST")
    DATABASE_PORT = get_env_variable("DATABASE_PORT")
    DATABASE_NAME = get_env_variable("DATABASE_NAME")
    SYMBOL = get_env_variable("SYMBOL")
    INTERVALS = get_env_variable("INTERVALS")
    RSI_BUY_THRESHOLD = get_env_variable("RSI_BUY_THRESHOLD")
    RSI_SELL_THRESHOLD = get_env_variable("RSI_SELL_THRESHOLD")
    ASSET = get_env_variable("ASSET")
    LOG_LEVEL = get_env_variable("LOG_LEVEL")
