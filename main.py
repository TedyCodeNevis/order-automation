from app.logger import setup_logging
from app.notifications.telegram import TelegramNotifier
from app.api import APIClient
from app.config import settings
from app.database import upsert_order,init_db,get_order_status
from app.processor import clean_orders,Order
from app.exporter import format_order
import asyncio
import httpx 
import sys
import logging

setup_logging()
logger=logging.getLogger(__name__)

def is_new_or_changed(order:Order) -> bool:
    previous_status=get_order_status(order.id)
    return previous_status is None or previous_status != order.status.value

async def process_and_notify(order:Order,notifier:TelegramNotifier):
    """پردازش و نوتیفای یک سفارش. خطا در اینجا کل برنامه را متوقف نمی‌کند."""
    try:
        message = format_order(order)
        await notifier.send(message)
        upsert_order(order)
    except httpx.HTTPError as error:
        logger.error(f"Failed to notify order {order.id} after retries: {error}") 

async def run():
    
    logger.info("starting application")
    init_db()

    notifier=TelegramNotifier(bot_token=settings.BOT_TOKEN,chat_id=settings.CHAT_ID)

    async with APIClient(base_url=settings.BASE_URL) as client:
        logger.info("Fetching orders from api...")
        raw_response=await client.get_orders_api()

        orders=clean_orders(raw_response)
        logger.info(f"Fetched and validate {len(orders)} orders")

        new_or_changed = [order for order in orders if is_new_or_changed(order)]
        logger.info(f"{len(new_or_changed)} order is new or changed ")

        for order in new_or_changed:
            await process_and_notify(order,notifier)

    logger.info("aplication finished successfuly")

async def main():
    try:
        await run()
    except Exception as error:
        logger.critical(f"Application crashed: {error}", exc_info=True)
        sys.exit(1)

asyncio.run(main())

