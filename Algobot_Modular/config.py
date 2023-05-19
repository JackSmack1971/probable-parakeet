import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    Configuration class for the application.
    """

    def __init__(self):
        """
        Initialize configuration variables.
        """

        # RSI_BUY_THRESHOLD: The threshold for the Relative Strength Index (RSI) below which the bot should consider buying.
        self.RSI_BUY_THRESHOLD = 30

        # RSI_SELL_THRESHOLD: The threshold for the RSI above which the bot should consider selling.
        self.RSI_SELL_THRESHOLD = 70

        # RETRY_DELAY: The delay (in seconds) before the bot should retry after a failed operation.
        self.RETRY_DELAY = 5

        # ASSET: The type of asset the bot is trading.
        self.ASSET = 'USDT'

        # MONGO_CONNECTION_STRING: The connection string for the MongoDB database. Sensitive data, loaded from environment variable.
        self.MONGO_CONNECTION_STRING = self.get_env_variable('MONGO_CONNECTION_STRING', 'mongodb://localhost:27017/')

        # SYMBOL: The symbol for the asset the bot is trading. Loaded from environment variable.
        self.SYMBOL = self.get_env_variable('SYMBOL', 'BTCUSDT')

    @staticmethod
    def get_env_variable(var_name, default_value):
        """
        Get the value of the environment variable named var_name or return the default_value if it's not set.
        Raise an error if the environment variable is not set and no default value is provided.
        """

        value = os.getenv(var_name, default_value)
        if value == default_value:
            print(f"Warning: Using default value for {var_name}")
        return value
