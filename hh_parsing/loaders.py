from scrapy.loader import ItemLoader
from .items import HhVacancyItem, HhEmployerItem
from itemloaders.processors import TakeFirst, MapCompose
from urllib.parse import urljoin


def join_str(itm):
    itm = [(word.replace(u'\xa0', '')).strip() for word in itm if word.strip()]
    itm = ' '.join(itm)
    return itm


class HhVacancyLoader(ItemLoader):
    default_item_class = HhVacancyItem
    salary_in = join_str
    description_in = join_str
    employer_url_in = MapCompose(lambda emp_id: urljoin("https://hh.ru/employer/", emp_id))

    url_out = TakeFirst()
    vacancy_out = TakeFirst()
    salary_out = TakeFirst()
    description_out = TakeFirst()
    employer_url_out = TakeFirst()


class HhEmployerLoader(ItemLoader):
    default_item_class = HhEmployerItem
    name_in = join_str
    fields_in = MapCompose(lambda field: field.split(", "))
    description_in = join_str

    url_out = TakeFirst()
    name_out = TakeFirst()
    site_out = TakeFirst()
    description_out = TakeFirst()
