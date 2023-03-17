import requests


def get_currency_price() -> float:
	"""
	The function get the dollar exchange rate
	By API the Central Bank's request restriction
	:return: float
	"""
	data = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()
	return data['Valute']['USD']['Value']
