import requests, json
from typing import Tuple
from src.config import Config as config

class InvalidResponseError(Exception):
    
    def __init__(self, message: str) -> None:
        super().__init__(message)


def get_fake_news_from_confia_portal() -> list[dict]:
    """Endpoint: 'Obter notificações de fake news'

    Returns:
        list[dict]: a list in JSON format containing all the fake news available in both CMS and project's site.
    """
        
    response = requests.get(f"{config.CONFIA_API.CMS_URL}fake-news-notifications")
    
    if response.status_code != 200:
        raise InvalidResponseError(f"Get request denied: response status code: {response.status_code}")
        
    return response


def post_new_fake_news_in_confia_portal(payload: list[dict]) -> list[dict]:
    """Endpoint: 'Inserir notificação de fake news'. 
    
    Args: a payload containing the following structure:
        - title:   a brief text regarding the news;
        - slug:    the title in slug format to append in the URL;
        - content: the whole content of the news. It might be reduced in order to attend the Twitter's limit of 280 characters.

    Returns:
        list[dict]: a list in JSON format containing the new id assigned to the posted news.
    """
    
    response = requests.post(f"{config.CONFIA_API.CMS_URL}fake-news-notifications", data=payload)
    
    if response.status_code != 200:
        raise InvalidResponseError(f"Post request denied: response status code: {response.status_code}")
        
    return response


def update_fake_news_in_confia_portal(payload: list[dict]) -> Tuple[int, str]:
    """Endpoint: 'Atualizar página de notificação de fake news.'

    Args:
        payload (list[dict]): a JSON containing the id of the new persisted news in CONFIA's portal.
        
    Returns:
        a tuple containing (i) the URL with the slug concatenated for publishing in Twitter; (ii) the response's status code.
    """
    payload = json.loads(payload)
    slug = payload["slug"]
    
    payload = str({"fake_news_notifications": [payload]}).replace('\'', '\"').encode('utf-8')
    
    response = requests.put(f"{config.CONFIA_API.CMS_URL}fake-news-notification-list", data=payload)
    
    if response.status_code != 200:
        raise InvalidResponseError(f"Put request denied: response status code: {response.status_code}")

    return slug