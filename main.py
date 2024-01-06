import os
import re
from lxml import etree as ET
import requests
import dotenv

from Watch import Watch
from WatchSet import WatchSet
from utils import Website, Origin, get_dollar_rate, send_telegram_message, update_chat_ids

dotenv.load_dotenv()
watch_set = WatchSet()
dollar_rate = get_dollar_rate()


home_data_raw = ET.fromstring(requests.get(os.environ.get(Website.HOME.value)).content)
other_data_raw = ET.HTML(requests.get(os.environ.get(Website.OTHER.value)).text)
home_items = home_data_raw.findall('.//Ad')
other_items = other_data_raw.xpath(".//li[contains(@class, 'b-rtile__item') and contains(@class, 'js-product-item')]")


for watch_raw in home_items:
    watch = Watch()
    watch_description = watch_raw.find('Description').text

    brand_search = re.search(r'<p><strong>(.*?)</strong><br></p>',watch_description)
    brand = brand_search.group(1) if brand_search else 'unknown brand'

    ref_search = re.search(r'<p>Ref: (.*?)</p>', watch_description)
    ref = ref_search.group(1) if ref_search else ''

    price_search = re.search(r'<p>([^<]+)</p>\s*$', watch_description, re.DOTALL)
    try:
        price = int(re.sub(r'\D', '', price_search.group(1).strip() if price_search else '0'))
        price = int(price / dollar_rate)
    except ValueError:
        price = 0

    watch.brand, watch.ref, watch.price, watch.origin = brand, ref, price, Origin.HOME
    watch_set.add_watch(watch)

for watch_raw in other_items:
    watch = Watch()

    data_parse_elements = watch_raw.xpath(".//p")
    if data_parse_elements:
        data_parse_element = data_parse_elements[0]
        watch.brand = data_parse_element.get('data-brand', 'unknown brand')
        watch.ref = data_parse_element.get('data-reference', 'unknown reference')
        price_str = data_parse_element.get('data-price', '0')
        try:
            watch.price = int(re.sub(r'\D', '', price_str))
        except ValueError:
            watch.price = 0
        watch.origin = Origin.OTHER

        watch_set.add_watch(watch)

demping_cases = watch_set.get_demping_cases()
message = ''
for our, their in demping_cases.items():
    message += f'[{our.brand} | {our.ref}] {our.price} -> {their[0].price}\n'

for chat_id in update_chat_ids():
    send_telegram_message(chat_id, message)
