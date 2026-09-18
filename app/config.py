import os
from dotenv import load_dotenv

load_dotenv()

def require_env(name=str) -> str:
    value=os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing environment variable: {name}")
    return value

PANEL_URL=require_env("PANEL_URL")
PANEL_USERNAME=require_env("PANEL_USERNAME")
PANEL_PASSWORD=require_env("PANEL_PASSWORD")

LOG_LEVEL=require_env("LOG_LEVEL")