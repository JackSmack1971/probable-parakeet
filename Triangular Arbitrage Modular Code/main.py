import asyncio
import json
import logging
import os
from contextlib import suppress
from typing import Dict, List, Union 

import aiohttp
from aiohttp import TCPConnector 

from app.cache import AsyncCache
from app.exceptions import ApiRequestError
from app.exchange import Exchange
from app.logging import configure_logging
from app.tasks import (
    calculate_average_percentage_change,
    check_for_profitable_trades,
    get_exchange_rate,
    get_symbols,
) 

log = logging.getLogger(__name__) 

async def main() -> None:
    """
    Main asynchronous function that runs the event loop.
    """
    try:
        config = load_config()
    except Exception as e:
        log.error(f"Error loading config: {e}")
        return
    configure_logging(config["logging"])
    async with aiohttp.ClientSession(
        connector=TCPConnector(ssl=False)
    ) as session:
        exchanges = [
            Exchange(
                name,
                os.environ.get(f"{name.upper()}_API_KEY"),
                config["base_urls"][name],
                config["endpoints"][name],
                session,
            )
            for name in config["api_keys"]
        ]
        exchange_rate_cache = AsyncCache(
            config["cache"]["exchange_rate"]
        )
        average_percentage_change_cache = AsyncCache(
            config["cache"]["average_percentage_change"]
        )
        while True:
            log.info("Checking for profitable trades...")
            trade_check_tasks = [
                check_for_profitable_trades(
                    exchanges=exchanges,
                    quote_assets=config["quote_assets"],
                    quote_asset_amount=config["quote_asset_amount"],
                    chunk_size=config["chunk_size"],
                    profit_threshold=config["profit_threshold"],
                    exchange_rate_cache=exchange_rate_cache,
                    average_percentage_change_cache=(
                        average_percentage_change_cache
                    ),
                )
            ]
            results = await asyncio.gather(
                *trade_check_tasks, return_exceptions=True
            )
            for result in results:
                if isinstance(result, Exception):
                    log.error(f"An exception occurred: {result}")
                elif not result.empty:
                    log.info(
                        f"Found {len(result)} profitable trades!"
                    )
                    log.info(result.to_string())
                else:
                    log.info("No profitable trades found.")
            await asyncio.sleep(config["time_interval"]) 

def load_config() -> Dict[str, Union[Dict, List, str, int]]:
    """
    Load configuration from the JSON file.
    """
    try:
        with open("config.json") as f:
            return json.load(f)
    except Exception as e:
        log.error(f"Error loading config file: {e}")
        raise e
if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
