from playwright.async_api import async_playwright

class Browser:
    def __init__(self):
        self.playwright=None
        self.browser=None
        self.context=None
        self.page=None

    async def conect(self):
        self.playwright=await async_playwright().start()
        self.browser=await self.playwright.chromium.launch(headless=False)
        self.context=await self.browser.new_context()
        self.page=await self.context.new_page()

    async def close(self):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        