import asyncio
import requests
from src.config import Config as config

async def get_fake_news_from_confia_portal() -> list[dict]:
    """Endpoint: 'Obter notificações de fake news'

    Returns:
        list[dict]: a list in JSON format containing all the fake news available in both CMS and project's site.
    """
    
    loop = asyncio.get_event_loop()
    request = loop.run_in_executor(None, requests.get, f"{config.CONFIA_API.CMS_URL}fake-news-notifications")
    
    print("Getting all fake news from CONFIA's portal...")
    await asyncio.sleep(5)
    response = await request
    
    return response.json()