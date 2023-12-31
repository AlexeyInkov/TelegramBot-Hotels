import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
RAPID_API_KEY = os.getenv("RAPID_API_KEY")
DEFAULT_COMMANDS = (
    ("start", "Запустить бота"),
    ("lowprice", "ТОП дешевых отелей"),
    ("highprice", "ТОП дорогих отелей"),
    ("bestdeal", "Подбор по параметрам"),
    ("history", "История поиска"),
    ("help", "Вывести справку")
)
CUSTOMS_COMMANDS = (
    ("hello", "Поздороваться"),
    ("lowprice", "ТОП дешевых отелей"),
    ("highprice", "ТОП дорогих отелей"),
    ("bestdeal", "подбор по параметрам"),
    ("history", "история поиска")
)
