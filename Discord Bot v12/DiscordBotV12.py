import argparse
import asyncio
import logging
import os
from typing import List, Tuple
import aiohttp
import discord
import uuid
from PIL import Image
from discord.ext import commands
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)
CHUNK_SIZE = 1024 * 10
class DiscordConnection:
    def __init__(self, token: str):
        self.bot = commands.Bot(command_prefix='$')
        self.token = token
        self.guild = None
        self.channel = None
    async def connect(self):
        await self.bot.login(self.token)
        await self.bot.connect()
    async def disconnect(self):
        await self.bot.logout()
class DiscordAttachmentDownloader:
    def __init__(self, connection: DiscordConnection):
        self.connection = connection
    async def connect_to_discord(self, server_name: str, channel_name: str) -> None:
        await self.connection.connect()
        self.connection.guild = discord.utils.get(self.connection.bot.guilds, name=server_name)
        if not self.connection.guild:
            raise ValueError(f"Could not find server with name {server_name}")
        self.connection.channel = discord.utils.get(self.connection.guild.text_channels, name=channel_name)
        if not self.connection.channel:
            raise ValueError(f"Could not find channel with name {channel_name}")
        LOGGER.info(f"Connected to server {server_name} and channel {channel_name}")
    async def download_attachments(self, min_resolution: Tuple[int, int], chunk_size: int = CHUNK_SIZE) -> None:
        """Downloads all attachments from the specified channel that meet the resolution criteria"""
        if not self.connection.channel:
            raise ValueError("Not connected to a channel")
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            headers = {}
            while True:
                async with session.get('https://discord.com/api/v9/gateway/bot', headers=headers) as response:
                    if response.status == 200:
                        headers = response.headers
                        reset_time = int(headers.get('X-Ratelimit-Reset', 0)) / 1000
                        LOGGER.info(f"Connected to Discord API. Rate limit reset time: {reset_time}")
                        break
                    elif response.status == 429:
                        await self._wait_for_rate_limit_reset(headers)
                    else:
                        raise ValueError("Error connecting to Discord API")
            async with self.connection.channel.typing():
                async with self.connection.channel.history(limit=None, oldest_first=True) as messages:
                    async for message in messages:
                        if message.attachments:
                            await self._process_message_attachments(session, message, headers, min_resolution, chunk_size)
            LOGGER.info("Download complete")
    async def _process_message_attachments(self, session: aiohttp.ClientSession, message: discord.Message, headers: dict, min_resolution: Tuple[int, int], chunk_size: int) -> None:
        tasks = [self._process_attachment(session, message_attachment, headers, min_resolution, chunk_size) for message_attachment in message.attachments]
        await asyncio.gather(*tasks)
    async def _process_attachment(self, session: aiohttp.ClientSession, message_attachment: discord.Attachment, headers: dict, min_resolution: Tuple[int, int], chunk_size: int) -> None:
        try:
            response = await session.head(message_attachment.url)
            if response.status != 200:
                LOGGER.error(f"Error downloading attachment {message_attachment.filename}. Response status: {response.status}")
                return
            content_type = response.headers.get('Content-Type', '').lower()
            content_length = response.headers.get('Content-Length')          
        if not content_type.startswith("image/") or not content_length:
            LOGGER.error(f"Skipping attachment {message_attachment.filename}. Invalid image: {message_attachment.url}")
            return
        async with asyncio.Semaphore(5):
            dimensions = await self._get_image_dimensions(session, message_attachment.url)
            if dimensions[0] >= min_resolution[0] and dimensions[1] >= min_resolution[1]:
                LOGGER.info(f"Downloading attachment {message_attachment.filename}")
                await self._download_attachment(session, message_attachment, chunk_size)
            else:
                LOGGER.info(f"Skipping attachment {message_attachment.filename}. Image dimensions {dimensions} are below minimum resolution {min_resolution}")
    except Exception as e:
        LOGGER.error(f"Error processing attachment {message_attachment.filename}: {e}")
async def _get_image_dimensions(self, session: aiohttp.ClientSession, url: str) -> Tuple[int, int]:
    async with session.get(url) as response:
        with Image.open(await response.content) as img:
            return img.size
async def _download_attachment(self, session: aiohttp.ClientSession, message_attachment: discord.Attachment, chunk_size: int) -> None:
    try:
        async with session.get(message_attachment.url, timeout=10) as response:
            if response.status != 200:
                LOGGER.error(f"Error downloading attachment {message_attachment.filename}. Response status: {response.status}")
                return
            unique_filename = str(uuid.uuid4()) + os.path.splitext(message_attachment.filename)[1]
            path = os.path.join("images", unique_filename)
            async with aiofiles.open(path, "wb") as file:
                async for data in response.content.iter_chunked(chunk_size):
                    await file.write(data)
            LOGGER.info(f"Downloaded attachment {unique_filename}")
    except Exception as e:
        LOGGER.error(f"Error downloading attachment {message_attachment.filename}: {e}")
async def _wait_for_rate_limit_reset(self, headers: dict) -> None:
    reset_time = int(headers.get('X-Ratelimit-Reset', 0)) / 1000
    delta = reset_time - asyncio.get_running_loop().time()
    LOGGER.info(f"Rate limit exceeded. Waiting {delta:.2f} seconds for reset.")
    await asyncio.sleep(delta)
def main(server_name: str, channel_name: str, min_resolution: Tuple[int, int], token: str, chunk_size: int = CHUNK_SIZE) -> None: connection = DiscordConnection(token) downloader = DiscordAttachmentDownloader(connection)
try:
    asyncio.run(connection.connect())
    asyncio.run(downloader.connect_to_discord(server_name, channel_name))    asyncio.run(downloader.download_attachments(min_resolution, chunk_size))
    print("Download complete")
except Exception as e:
    LOGGER.exception(e)
finally:
    asyncio.run(connection.disconnect())
if name == 'main': parser = argparse.ArgumentParser(description='Download all attachments from a Discord channel.') parser.add_argument('server', type=str, help='name of the server') parser.add_argument('channel', type=str, help='name of the channel') parser.add_argument('resolution', type=str, help='minimum resolution of images in the format "WxH"') parser.add_argument('--chunk-size', type=int, default=CHUNK_SIZE, help='size of chunks to download in bytes') parser.add_argument('--token', type=str, required=True, help='Discord bot token') args = parser.parse_args()
server_name = args.server
channel_name = args.channel
min_resolution = tuple(map(int, args.resolution.split('x')))
chunk_size = args.chunk_size
token = args.token
main(server_name, channel_name, min_resolution, token, chunk_size)
