async def main():
    """
    Main function that runs the script asynchronously
    """
    try:
        config = Config()
        # 4. Change the `validate` method to raise an exception if there is an error
        config.validate()

        bot = telegram.Bot(token=config.telegram_bot_token)
        await schedule_posting(bot, config.telegram_channel_id, config, 3600)
    except ConfigurationError as error:
        # 5. Properly handle the `ConfigurationError` exception
        logging.error(str(error))
    except Exception as error:
        logging.error(f'Unhandled exception occurred: {error}')


if __name__ == '__main__':
    asyncio.run(main())
