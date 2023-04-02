from typing import Dict, Union, List, Any 

import aiohttp 

from app.exceptions import ApiRequestError


class Exchange:
    """
    A class that represents an exchange and provides methods for making API requests
    to the exchange and retrieving market data.
    """ 

    def __init__(
        self,
        name: str,
        api_key: str,
        base_url: str,
        endpoints: Dict[str, str],
        session: aiohttp.ClientSession,
    ):
        self.name: str = name
        self.api_key: str = api_key
        self.base_url: str = base_url
        self.endpoints: Dict[str, str] = endpoints
        self.session: aiohttp.ClientSession = session
        self.headers: Dict[str, str] = {"X-API-Key": api_key} 

    async def make_request(self, endpoint: str, params: Dict[str, Union[str, int]]) -> Dict:
        """
        Make an API request to the exchange. 

        :param endpoint: The endpoint for the request.
        :param params: The query parameters for the request.
        :return: The JSON response as a dictionary.
        """
        url = f"{self.base_url}{self.endpoints[endpoint]}"
        async with self.session.get(url, params=params, headers=self.headers) as response:
            if response.status != 200:
                raise ApiRequestError(
                    f"Request to {url} failed with status {response.status}: {response.reason}."
                )
            return await response.json() 

    async def get_symbols(self) -> Dict:
        """Retrieve symbols for the exchange."""
        return await self.make_request("symbols", {})
    async def get_exchange_rate(
        self, base_asset: str, quote_asset: str, exchange_rate_cache
    ) -> float:
        """
        Retrieve the exchange rate for a given base and quote asset. 

        :param base_asset: The base asset.
        :param quote_asset: The quote asset.
        :param exchange_rate_cache: The cache for exchange rates.
        :return: The exchange rate as a float.
        """
        cache_key = f"{self.name}_{base_asset}_{quote_asset}"
        exchange_rate = await exchange_rate_cache.get(cache_key)
        if exchange_rate is None:
            params = {"base_asset": base_asset, "quote_asset": quote_asset}
            response = await self.make_request("exchangerate", params)
            exchange_rate = float(response["data"]["rate"])
            await exchange_rate_cache.set(cache_key, exchange_rate)
        return exchange_rate 

    async def get_ohlcv_data(
        self, symbol_id: str, period_id: str, limit: int
    ) -> Dict:
        """
        Retrieve the OHLCV data for a given symbol, period, and limit. 

        :param symbol_id: The symbol ID.
        :param period_id: The period ID.
        :param limit: The limit on the number of data points.
        :return: The JSON response as a dictionary.
        """
        query_params = {
            "symbol_id": symbol_id,
            "period_id": period_id,
            "limit": limit,
        }
        return await self.make_request("ohlcv", query_params)
