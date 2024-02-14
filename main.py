import os
import asyncio
from lxml import etree as ET
import requests
import dotenv

from WatchSet import WatchSet
from utils import Website, send_telegram_message, update_chat_ids, process_watches, get_watch_from_home_item

dotenv.load_dotenv()

watch_set = WatchSet()

other_url = 'https://lombard-perspectiva.ru/clocks_today/?sort=date&page={page_number}&per-page=400'
for i in range(1, 20):
    try:
        print(other_url.format(page_number=i))
        other_data_raw = ET.HTML(requests.get(other_url.format(page_number=i)).text)
        other_items = other_data_raw.xpath("//a[contains(@class, 'product-list-item catalog-item')]")
        other_links = [watch_raw.attrib['href'] for watch_raw in other_items]
        other_watches = asyncio.run(process_watches(other_links))
        for watch in other_watches:
            watch_set.add_watch(watch)
        print(f'page {i} done')
    except Exception as e:
        print(e)


home_data_raw = ET.fromstring(requests.get(os.environ.get(Website.HOME.value)).content)
home_items = home_data_raw.findall('.//Ad')
for watch_raw in home_items:
    watch = get_watch_from_home_item(watch_raw)
    watch_set.add_watch(watch)


demping_cases = watch_set.get_demping_cases()
message = ''
for i, (our, their) in enumerate(demping_cases.items()):
    for chat_id in update_chat_ids():
        send_telegram_message(
            chat_id,
            f'{i + 1}) [{our.brand} | {our.ref}] {our.price} -> {their[0].price}\n'
            f'{our.url}\n'
            f'{their[0].url}'
        )
