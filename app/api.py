import httpx , asyncio, logging
from app.logger import setup_logging
from app.config import settings

class APIClient:
    RETRY_STATUS_CODE={
        408,
        425,
        429,
        500,
        502,
        503,
        504,
    }
    setup_logging()
    logger=logging.getLogger(__name__)
    def __init__(
            self,
            base_url:str,
            retry_count:int=3,
            retry_delay:float=1.0,
            timeout:float=10.0):
        self.base_url=base_url.rstrip("/")
        self.retry_count=retry_count
        self.retry_delay=retry_delay

        self.client=httpx.AsyncClient(timeout=timeout)
        self._token:str | None=None

    async def authenticate(self):
        response=await self.client.post(
            f"{self.base_url}/login",
            json={
                "username":settings.PANEL_USERNAME,
                "password":settings.PANEL_PASSWORD,})
        response.raise_for_status()
        data=response.json()
        self._token=data.get("token")
        if not self._token:
            raise RuntimeError("Authentication succeeded but no token was returned")
        self.client.headers["Authorization"]=f"Bearer {self._token}"
        self.logger.info("Authenticated successfully")

    async def get(self,endpoint:str,params:dict | None = None) -> dict|list:
        url=f"{self.base_url}/{endpoint.lstrip("/")}"
        for attept in range(1,self.retry_count+1):
            try:
                response=await self.client.get(url,params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                status_code=e.response.status_code
                if status_code not in self.RETRY_STATUS_CODE:
                    self.logger.info(f"none-retryble HTTP error {status_code} on {url}")
                    raise
                self.logger.warning(
                    f"Retryble HTTP error {status_code} on {url}"
                    f"attempt {attept}/{self.retry_count}")
                if attept == self.retry_count:
                    raise
                delay=2**attept
                await asyncio.sleep(self.retry_delay+delay)


    async def get_orders_api(self) -> list|dict:
        return await self.get("api/orders",params={"limit":100})
    async def get_order_api(self,order_id:int):
        return await self.get(f"api/orders/{order_id}")
    async def get_orders(self) -> list|dict:
        return await self.get("orders")
    async def get_order(self,order_id:int):
        return await self.get(f"orders/{order_id}")
    async def close(self):
        await self.client.aclose()
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
    how_use="""\n
    async def main():
    async with APIClient(base_url=settings.PANEL_URL) as client:
        await client.authenticate()
        orders = await client.get_orders()
        print(orders)"""


                