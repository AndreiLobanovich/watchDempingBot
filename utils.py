import json
import os
from enum import Enum, auto
import requests
from bs4 import BeautifulSoup


class Origin(Enum):
    HOME = auto()
    OTHER = auto()


class Website(Enum):
    HOME = 'HOME_SITE'
    OTHER = 'OTHER_SITE'


def get_dollar_rate():
    url = 'https://www.cbr.ru/currency_base/daily/'

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    dollar_rate = None
    for row in soup.find_all('tr'):
        cols = row.find_all('td')
        if len(cols) > 3 and 'USD' in cols[1].text:
            dollar_rate = float(cols[4].text.replace(',', '.'))
            break
    return dollar_rate


def update_chat_ids():
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    r = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getUpdates')
    with open('chat_ids_to_post_to') as f:
        lines = list(map(lambda line: line.replace('\n', ''), f.readlines()))
        for message in json.loads(r.content.decode('utf-8'))['result']:
            chat_id = str(message['message']['chat']['id'])
            if chat_id not in lines:
                lines.append(chat_id)
    with open('chat_ids_to_post_to', 'w') as f:
        f.write('\n'.join(lines))
    return lines


def send_telegram_message(chat_id, message):
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message
    }
    requests.post(url, data=data)
