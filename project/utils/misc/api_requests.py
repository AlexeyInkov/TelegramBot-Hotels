import json
import requests
from loguru import logger
from config_data import config


def api_request(method_endswith: str, params: dict, method_type: str):
    url = f"https://hotels4.p.rapidapi.com/{method_endswith}"
    try:
        if method_type == 'GET':
            return json.loads(get_request(url=url, params=params))
        else:
            return json.loads(post_request(url=url, params=params))
    except TypeError:
        logger.debug('API ответил не корректно')
        return None
    except requests.exceptions.ReadTimeout:
        logger.debug('Не дождались ответа от API')
        return None


def get_request(url: str, params: dict) -> str:
    headers = {
        "X-RapidAPI-Key": config.RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }
    getresponse = requests.get(url, headers=headers, params=params, timeout=10)
    logger.debug('Выполнен GET запрос')
    if getresponse.status_code == requests.codes.ok:
        return getresponse.text


def post_request(url: str, params: dict) -> str:
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": config.RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"}
    postresponse = requests.post(url, headers=headers, json=params, timeout=10)
    logger.debug('Выполнен POST запрос')
    if postresponse.status_code == requests.codes.ok:
        return postresponse.text
