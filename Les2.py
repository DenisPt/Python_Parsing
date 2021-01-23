import os
import requests
from urllib.parse import urljoin
import bs4
import pymongo
from dotenv import load_dotenv
import time
import datetime as dt


class ParseError(Exception):
    def __init__(self, text):
        self.text = text
months = {"янв": 1, "фев": 2, "мар": 3, "апр": 4, "май": 5, "мая": 5, "июн": 6, "июл": 7,
          "авг": 8, "сен": 9, "окт": 10, "ноя": 11, "дек": 12}


def text_to_date(text):
    text = text.split(' ')
    text = dt.datetime.strptime(text[1] + " " + str(months[text[2][:3]]) + " " + str(dt.datetime.now().year), '%d %m %Y')
    return text

class MagnitParser:
    def __init__(self, start_url, data_client):
        self.start_url = start_url
        self.data_client = data_client
        self.data_base = self.data_client["MagnitParse"]

    @staticmethod
    def _get_response(url: str, *args, **kwargs) -> requests.Response:
        while True:
            try:
                response = requests.get(url, *args, **kwargs)
                if response.status_code > 399:
                    raise ParseError(response.status_code)
                time.sleep(0.1)
                return response
            except (requests.RequestException, ParseError):
                time.sleep(0.5)
                continue

    @staticmethod
    def _get_soup(response):
        return bs4.BeautifulSoup(response.text, "lxml")

    def run(self):
        for product in self.parse(self.start_url):
            self.save(product)

    def parse(self, url) -> dict:
        soup = self._get_soup(self._get_response(url))
        catalog_main = soup.find("div", attrs={"class": "сatalogue__main"})
        for product_tag in catalog_main.find_all("a", attrs={"class": "card-sale"}):
            yield self._get_product_data(product_tag)

    @staticmethod
    def _get_price(tag, price_class):
        try:
            a = int(tag.find('div', attrs={"class": price_class}).find(attrs={"class": "label__price-integer"}).text)
            b = int(tag.find('div', attrs={"class": price_class}).find(attrs={"class": "label__price-decimal"}).text)
            return a + b * 0.01
        except ValueError:
            return None

    @staticmethod
    def _get_date(tag, n):
        try:
            return text_to_date(tag.find('div', attrs={"class": "card-sale__date"}).find_all('p')[n].text)
        except IndexError:
            if n == 1:
                try:
                    return text_to_date(tag.find('div', attrs={"class": "card-sale__date"}).find_all('p')[0].text)
                except:
                    return None

    @property
    def data_template(self):
        return {
            "url": lambda tag: urljoin(self.start_url, tag.attrs.get("href")),
            "promo_name": lambda tag: tag.find('div', attrs={"class": "card-sale__header"}).text,
            "product_name": lambda tag: tag.find('div', attrs={"class": "card-sale__title"}).text,
            "old_price": lambda tag: self._get_price(tag, "label__price_old"),
            "new_price": lambda tag: self._get_price(tag, "label__price_new"),
            "image_url": lambda tag: urljoin(self.start_url, tag.find('source').attrs.get("data-srcset")),
            "date_from": lambda tag: self._get_date(tag, 0),
            "date_to": lambda tag: self._get_date(tag, 1)
        }

    def _get_product_data(self, product_tag: bs4.Tag) -> dict:
        data = {}
        for key, pattern in self.data_template.items():
            try:
                data[key] = pattern(product_tag)
            except AttributeError:
                pass
        return data

    def save(self, data):
        collection = self.data_base["magnit"]
        collection.insert_one(data)
        pass


if __name__ == '__main__':
    load_dotenv(".env")
    data_base_url = os.getenv("DATA_BASE_URL")
    data_client = pymongo.MongoClient(data_base_url)
    url = "https://magnit.ru/promo/?geo=moskva"
    parser = MagnitParser(url, data_client)
    parser.run()
