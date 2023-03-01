import json
import requests
from config_data import config


def api_request(method_endswith: str,  # Меняется в зависимости от запроса. locations/v3/search либо properties/v2/list
                params: dict,  # Параметры, если locations/v3/search, то {'q': 'Рига', 'locale': 'ru_RU'}
                method_type: str  # тип запроса GET\POST
                ):
    url = f"https://hotels4.p.rapidapi.com/{method_endswith}"
    if method_type == 'GET':
        return json.loads(get_request(url=url, params=params))
    else:
        return json.loads(post_request(url=url, params=params))


def get_request(url: str, params: dict) -> str:
    headers = {
        "X-RapidAPI-Key": config.RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }
    getresponse = requests.get(url, headers=headers, params=params)
    if getresponse.status_code == requests.codes.ok:
        return getresponse.text


def post_request(url: str, params: dict) -> str:
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": config.RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"}
    postresponse = requests.post(url, headers=headers, json=params)
    if postresponse.status_code == requests.codes.ok:
        return postresponse.text
