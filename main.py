from app.logger import setup_logging
from app.notifications.telegram import TelegramNotifier
from app.api import APIClient
from app.config import settings
from app.processor import clean_orders
from app.exporter import format_order
import asyncio
import logging
async def main():
    setup_logging()
    logger=logging.getLogger(__name__)
    notifier=TelegramNotifier(bot_token=settings.BOT_TOKEN,chat_id=settings.CHAT_ID)

    async with APIClient(base_url=settings.BASE_URL) as client:
        logger.info("Fetching orders from api...")
        raw_response=await client.get_orders_api()

        orders=clean_orders(raw_response)
        logger.info(f"Fetched and validate {len(orders)} orders")

        for order in orders:
            message=format_order(order)
            await notifier.send(message)

    logger.info("aplication finished successfuly")

asyncio.run(main())

