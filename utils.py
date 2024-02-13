import json
import os
import re
from enum import Enum, auto

import asyncio
from lxml import etree as ET

import requests
from aiohttp import ClientSession
from bs4 import BeautifulSoup


class Origin(Enum):
    HOME = auto()
    OTHER = auto()


class Website(Enum):
    HOME = 'HOME_SITE'
    OTHER = 'OTHER_SITE'


class Watch:
    brand: str = ''
    ref: str = ''
    price: str = 0
    origin: Origin | None = None
    link: str = ''
    url: str

    def is_set(self):
        return self.brand != '' and self.ref != '' and self.price != 0

    def __eq__(self, other: 'Watch'):
        return self.ref == other.ref

    def __hash__(self):
        return hash(self.ref)

    def __repr__(self):
        return self.ref

    def __str__(self):
        return f'{self.ref}: {self.price}$'





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


async def fetch_watch_details(session: ClientSession, watch_url: str, semaphore: asyncio.Semaphore) -> Watch:
    async with semaphore:
        async with session.get(f'https://lombard-perspectiva.ru{watch_url}') as response:
            try:
                text = await response.text()
                watch_page = ET.HTML(text)
                watch = Watch()
                watch.ref = watch_page.xpath(".//div[contains(@class, 'text-gray flex-shrink-1')]")[0].text.split()[1]
                watch.brand = ' '.join(watch_page.xpath(".//div[contains(@class, 'catalog-item--brand-title flex-shrink-1 text-spectral')]")[0].text.split())
                watch.price = int(re.sub(r'\D', '', watch_page.xpath(".//p[contains(@class, 'item-price--text')]")[0].text))
                watch.origin = Origin.OTHER
                watch.url = f'https://lombard-perspectiva.ru{watch_url}'
                return watch
            except:
                return Watch()


async def process_watches(urls):
    tasks = []
    semaphore = asyncio.Semaphore(10)
    async with ClientSession() as session:
        for watch_url in urls:
            task = asyncio.create_task(fetch_watch_details(session, watch_url, semaphore))
            tasks.append(task)
        watches = await asyncio.gather(*tasks)
        return watches


def get_watch_from_home_item(home_item):
    watch = Watch()
    watch_description = home_item.find('Description').text

    brand_search = re.search(r'<p><strong>(.*?)</strong><br></p>',watch_description)
    brand = brand_search.group(1) if brand_search else 'unknown brand'

    ref_search = re.search(r'<p>Ref: (.*?)</p>', watch_description)
    ref = ref_search.group(1) if ref_search else ''
    watch.url = home_item.find('Url').text
    try:
        price = int(home_item.find('PriceUsd').text)
    except AttributeError:
        price = 0
    watch.brand, watch.ref, watch.price, watch.origin = brand, ref, price, Origin.HOME
    return watch
