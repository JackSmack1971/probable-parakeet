import asyncio
import aiohttp
import json
import pandas as pd
from aiohttp import TCPConnector
from contextlib import asynccontextmanager
from requests_cache import install_cache
from typing import Dict, List, Tuple, Union
import logging
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

# Constants
CONFIG_FILE = "config.json"
CACHE_EXPIRE_TIME = 300
TIME_INTERVAL = 5
QUOTE_ASSET_AMOUNT = 1000
CHUNK_SIZE = 50

log = logging.getLogger(__name__)

# TheGraph API endpoints
UNISWAP_API = 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2'
SUSHISWAP_API = 'https://api.thegraph.com/subgraphs/name/sushiswap/exchange'
PANCAKESWAP_API = 'https://api.thegraph.com/subgraphs/name/pancakeswap/exchange-v2'

# GraphQL client setup
async def get_graphql_client(url):
    transport = AIOHTTPTransport(url=url)
    client = Client(transport=transport, fetch_schema_from_transport=True)
    return client
# ... (previous part of the code)

async def get_symbols(session: aiohttp.ClientSession, exchange: str) -> List[Dict]:
    if exchange not in ['uniswap', 'sushiswap', 'pancakeswap']:
        raise ValueError('Unsupported exchange')

    if exchange == 'uniswap':
        url = UNISWAP_API
    elif exchange == 'sushiswap':
        url = SUSHISWAP_API
    else:
        url = PANCAKESWAP_API

    client = await get_graphql_client(url)
    query = gql("""
    {
      pairs(first: 1000) {
        id
        token0 {
          symbol
        }
        token1 {
          symbol
        }
      }
    }
    """)

    result = await client.execute_async(query)
    pairs = result['pairs']

    symbols = [
        {
            'symbol_id': pair['id'],
            'symbol_type': 'SPOT',
            'base_asset': pair['token0']['symbol'],
            'quote_asset': pair['token1']['symbol']
        }
        for pair in pairs
    ]

    return symbols

# Replace the following functions with new implementations
# ... (get_exchange_rate, calculate_triangular_profit, calculate_average_percentage_change, get_average_percentage_change)

# ... (previous part of the code)

async def get_exchange_rate(session: aiohttp.ClientSession, exchange: str, base_asset: str, quote_asset: str) -> float:
    cache_key = f"{exchange}_{base_asset}_{quote_asset}"
    if cache_key in exchange_rate_cache:
        return exchange_rate_cache[cache_key]
    else:
        if exchange not in ['uniswap', 'sushiswap', 'pancakeswap']:
            raise ValueError('Unsupported exchange')

        if exchange == 'uniswap':
            url = UNISWAP_API
        elif exchange == 'sushiswap':
            url = SUSHISWAP_API
        else:
            url = PANCAKESWAP_API

        client = await get_graphql_client(url)
        query = gql("""
        query GetExchangeRate($baseAsset: String!, $quoteAsset: String!) {
          pairs(where: {token0: $baseAsset, token1: $quoteAsset}) {
            token0Price
          }
        }
        """)

        variables = {'baseAsset': base_asset, 'quoteAsset': quote_asset}
        result = await client.execute_async(query, variable_values=variables)

        if len(result['pairs']) == 0:
            raise ValueError(f"No exchange rate found for {base_asset} and {quote_asset}")

        exchange_rate = float(result['pairs'][0]['token0Price'])
        exchange_rate_cache[cache_key] = exchange_rate
        return exchange_rate

# Replace the following functions with new implementations
# ... (calculate_triangular_profit, calculate_average_percentage_change, get_average_percentage_change)
# ... (previous part of the code)

async def calculate_triangular_profit(quote_asset_amount: int, exchange_rate_a: float, exchange_rate_b: float, exchange_rate_c: float) -> float:
    base_asset_amount_a = quote_asset_amount / exchange_rate_a
    base_asset_amount_b = base_asset_amount_a * exchange_rate_b
    base_asset_amount_c = base_asset_amount_b * exchange_rate_c
    profit_percentage = (base_asset_amount_c - quote_asset_amount) / quote_asset_amount
    return profit_percentage

async def calculate_average_percentage_change(symbol_id: str, ohlcv_data: Dict) -> float:
    price_data = [c for _, _, _, c, _ in ohlcv_data['data']]
    percentage_changes = [(price_data[i] - price_data[i-1]) / price_data[i-1] for i in range(1, len(price_data))]
    average_percentage_change = sum(percentage_changes) / len(percentage_changes)
    return average_percentage_change

async def get_average_percentage_change(session: aiohttp.ClientSession, exchange: str, symbol_id: str, period_id: str='1DAY', limit: int=30) -> float:
    cache_key = f"{exchange}_{symbol_id}_{period_id}_{limit}"
    if cache_key in average_percentage_change_cache:
        return average_percentage_change_cache[cache_key]
    else:
        query_params = {'symbol_id': symbol_id, 'period_id': period_id, 'limit': limit}
        try:
            ohlcv_data = await make_request(session, exchange, 'ohlcv', query_params)
            average_percentage_change = await calculate_average_percentage_change(symbol_id, ohlcv_data)
            average_percentage_change_cache[cache_key] = average_percentage_change
            return average_percentage_change
        except Exception as e:
            log.error(f"Error calculating average percentage change for symbol {symbol_id}: {e}")
            return 0.0

# Replace the following functions with new implementations
# ... (check_for_profitable_trades)

# ... (previous part of the code)

async def check_for_profitable_trades() -> pd.DataFrame:
    async with aiohttp_session() as session:
        tasks = []
        for exchange in ['uniswap', 'sushiswap', 'pancakeswap']:
            symbols = []
            try:
                symbols = await get_symbols(session, exchange)
            except Exception as e:
                log.error(f"Error getting symbols for {exchange}: {e}")
                continue
            symbol_ids = [symbol['symbol_id'] for symbol in symbols if symbol['symbol_type'] == 'SPOT']

            tasks = []
            for symbol_id in symbol_ids:
                tasks.append(get_average_percentage_change(session, exchange, symbol_id))
            try:
                average_percentage_changes = await asyncio.gather(*tasks)
            except Exception as e:
                log.error(f"Error getting average percentage changes for symbols {symbol_ids} on {exchange}: {e}")
                continue

            for symbol, average_percentage_change in zip(symbol_ids, average_percentage_changes):
                if average_percentage_change < 0:
                    continue
                base_asset, quote_asset = symbol.split('_')
                exchange_rate_a = await get_exchange_rate(session, exchange, quote_asset, 'USD')
                exchange_rate_b = await get_exchange_rate(session, exchange, base_asset, quote_asset)
                for other_exchange in [e for e in ['uniswap', 'sushiswap', 'pancakeswap'] if e != exchange]:
                    common_asset = set(ENDPOINTS[exchange]).intersection(set(ENDPOINTS[other_exchange]))
                    if len(common_asset) == 0:
                        continue
                    common_asset = common_asset.pop().split('/')[-1]
                    exchange_rate_c = await get_exchange_rate(session, other_exchange, common_asset, 'USD')
                    quote_asset_amount = QUOTE_ASSET_AMOUNT
                    profit_percentage = await calculate_triangular_profit(quote_asset_amount, exchange_rate_a, exchange_rate_b, exchange_rate_c)
                    if profit_percentage > PROFIT_THRESHOLD:
                        results.append({
                            'exchange_a': exchange,
                            'exchange_b': other_exchange,
                            'symbol_a': symbol,
                            'base_asset_a': base_asset,
                            'quote_asset_a': quote_asset,
                            'symbol_b': f"{common_asset}_{quote_asset}",
                            'base_asset_b': common_asset,
                            'quote_asset_b': quote_asset,
                            'symbol_c': f"{common_asset}_{base_asset}",
                            'base_asset_c': common_asset,
                            'quote_asset_c': base_asset,
                            'quote_asset_amount': quote_asset_amount,
                            'profit_percentage': profit_percentage
                        })

    return pd.DataFrame(results)

# ... (main function and other parts of the code)


