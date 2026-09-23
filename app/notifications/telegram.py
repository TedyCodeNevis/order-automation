import httpx
import logging
from app.logger import setup_logging
from app.notifications.base import Notifier

setup_logging()
logger=logging.getLogger(__name__)

class TelegramNotifier(Notifier):
    def __init__(self,bot_token:str,chat_id:str):
        self.bot_token=bot_token
        self.chat_id=chat_id
        self.api_url=f"https://api.telegram.org/bot{bot_token}/sendMessage"

    async def send(self, message) -> None:
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

    