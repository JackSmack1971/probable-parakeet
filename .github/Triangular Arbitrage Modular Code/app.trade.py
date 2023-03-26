from typing import Dict, List, Tuple, Union 

from app.exchange import Exchange
from app.exceptions import ApiRequestError
from app.cache import RedisCache


class TriangularTrade:
    """
    A class that represents a triangular trade and provides methods for calculating
    triangular profits and average percentage changes.
    """ 

    def __init__(
        self,
        exchanges: Dict[str, Exchange],
        quote_asset_amount: int,
        profit_threshold: float,
        cache: RedisCache,
    ):
        self.exchanges: Dict[str, Exchange] = exchanges
        self.quote_asset_amount: int = quote_asset_amount
        self.profit_threshold: float = profit_threshold
        self.cache: RedisCache = cache 

    async def calculate_triangular_profit(
        self, exchange_a: Exchange, exchange_b: Exchange, common_asset: str
    ) -> float:
        """
        Calculate the triangular profit between two exchanges and a common asset. 

        :param exchange_a: The first exchange.
        :param exchange_b: The second exchange.
        :param common_asset: The common asset.
        :return: The triangular profit as a float.
        """
        quote_asset = common_asset + exchange_a.name.split("exchange")[1].lower()
        base_asset_a = self.quote_asset_amount / await exchange_a.get_exchange_rate(quote_asset, "USD")
        base_asset_b = base_asset_a * await exchange_a.get_exchange_rate(quote_asset, common_asset)
        base_asset_c = base_asset_b * await exchange_b.get_exchange_rate(common_asset, "USD")
        profit_percentage = (base_asset_c - self.quote_asset_amount) / self.quote_asset_amount
        return profit_percentage
    async def get_average_percentage_change(
        self,
        exchange: Exchange,
        symbol_id: str,
        period_id: str = "1DAY",
        limit: int = 30,
    ) -> float:
        """
        Calculate the average percentage change for a given symbol and period. 

        :param exchange: The exchange.
        :param symbol_id: The symbol ID.
        :param period_id: The period ID (default: "1DAY").
        :param limit: The limit on the number of data points (default: 30).
        :return: The average percentage change as a float.
        """
        cache_key = f"{exchange.name}_{symbol_id}_{period_id}_{limit}"
        average_percentage_change = await self.cache.get(cache_key)
        if average_percentage_change is None:
            try:
                ohlcv_data = await exchange.get_ohlcv_data(symbol_id, period_id, limit)
                price_data = [c for _, _, _, c, _ in ohlcv_data["data"]]
                percentage_changes = [
                    (price_data[i] - price_data[i - 1]) / price_data[i - 1] for i in range(1, len(price_data))
                ]
                average_percentage_change = sum(percentage_changes) / len(percentage_changes)
                await self.cache.set(cache_key, average_percentage_change)
            except ApiRequestError as e:
                raise e
            except Exception as e:
                raise ApiRequestError(
                    f"Error calculating average percentage change for symbol {symbol_id} on {exchange.name}: {e}"
                )
        return average_percentage_change
