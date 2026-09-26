import httpx
import asyncio
import logging
from app.logger import setup_logging
from app.notifications.base import Notifier

setup_logging()
logger=logging.getLogger(__name__)

class TelegramNotifier(Notifier):
    def __init__(
            self,
            bot_token:str,
            chat_id:str,
            retry_count: int = 3,
            retry_delay: float = 1.0,
            ):
        self.bot_token=bot_token
        self.chat_id=chat_id
        self.retry_count=retry_count
        self.retry_delay=retry_delay
        self.api_url=f"https://api.telegram.org/bot{bot_token}/sendMessage"

    async def send(self, message) -> None:
        for attempt in range(1,self.retry_count+1):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response=await client.post(
                        self.api_url,
                        json={
                            "chat_id": self.chat_id,
                            "text": message 
                        },
                    )

                    response.raise_for_status()
                    logger.info(f"Nottification sent to Telegram chat {self.chat_id}")
                    return

            except httpx.HTTPError as error:
                logger.warning(
                    f"Faild to send notification (attempt {attempt}/{self.retry_count}): {error}"
                )
                if attempt == self.retry_count:
                    logger.error("Giving up on sending this notification.")
                    raise
                await asyncio.sleep(self.retry_delay)