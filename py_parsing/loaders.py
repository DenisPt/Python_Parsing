import re
from urllib.parse import urljoin
from urllib.parse import unquote
from base64 import b64decode
from scrapy import Selector
from scrapy.loader import ItemLoader
from .items import AutoyoulaItem
from itemloaders.processors import TakeFirst, MapCompose

def get_first(items):
    for itm in items:
        if itm is not None and not itm == "":
            return itm
    return None

def decode_phone(item):
    item = unquote(item)
    item = b64decode(item)
    item = b64decode(item)
    item = item.decode("utf-8")
    return item


def get_info_from_script(item, fword, eword):
    re_pattern = re.compile(fword + r"%22%2C%22([a-zA-Z|\d|\%]+)%22%2C%22" + eword)
    result = re.findall(re_pattern, item)
    return result

def clear_unicode(itm):
    return itm.replace("\u2009", "")


def get_specifications(item):
    tag = Selector(text=item)
    name = tag.xpath("//div[@class='AdvertSpecs_label__2JHnS']/text()").get()
    value = tag.xpath("//div[@class='AdvertSpecs_data__xK2Qx']//text()").get()
    return {name: value}


def flat_dict(items):
    result = {}
    for itm in items:
        result.update(itm)
    return result


class AutoyoulaLoader(ItemLoader):
    default_item_class = AutoyoulaItem
    url_out = get_first
    title_out = get_first
    price_in = MapCompose(clear_unicode, float)
    price_out = TakeFirst()
    author_in = MapCompose(lambda a_id: get_info_from_script(a_id, "youlaId", "avatar"),
                           lambda a_id: urljoin("https://youla.ru/user/", a_id))
    phone_in = MapCompose(lambda ph: get_info_from_script(ph, "phone", "time"), decode_phone)
    phone_out = TakeFirst()
    author_out = TakeFirst()
    description_out = TakeFirst()
    specifications_in = MapCompose(get_specifications)
    specifications_out = flat_dict
