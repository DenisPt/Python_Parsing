import scrapy
from ..loaders import HhVacancyLoader, HhEmployerLoader
import re


class HhSpider(scrapy.Spider):
    name = 'hh_spider'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113']

    xpath_query = {
        "vacancies": '//a[@data-qa="vacancy-serp__vacancy-title"]',
        'employers': '//a[@data-qa="vacancy-serp__vacancy-employer"]',
        'pagination': '//a[@data-qa="pager-page"]'
    }

    def gen_task(self, response, link_type, callback):
        links = response.xpath(self.xpath_query[link_type])
        for link in links:
            yield response.follow(link.attrib["href"], callback=callback)

    data_vacancy = {
        'vacancy': '//h1/text()',
        'salary': '//p[@class="vacancy-salary"]//span[contains(@class, "bloko-header-2")]/text()',
        'description': '//div[@data-qa="vacancy-description"]//text()',
        'skills': '//span[@data-qa="bloko-tag__text"]//text()',
        'employer_url': '//a[@data-qa="vacancy-company-name"]/@href'
    }

    data_employer = {
        'name': '//div[@class="company-header"]//span[@data-qa="company-header-title-name"]/text()',
        'site': '//a[@data-qa="sidebar-company-site"]/@href',
        'fields': '//div[text()="Сферы деятельности"]/../p/text()',
        'description': '//div[@class="g-user-content"]/p/text()'
    }

    def parse(self, response):
        yield from self.gen_task(response, 'vacancies', self.parse_vacancy)
        yield from self.gen_task(response, 'employers', self.parse_employer)
        yield from self.gen_task(response, 'pagination', self.parse)

    def parse_vacancy(self, response):
        loader = HhVacancyLoader(response=response)
        loader.add_value('url', response.url)
        for key, selector in self.data_vacancy.items():
            loader.add_xpath(key, selector)
        yield loader.load_item()

    def parse_employer(self, response):
        loader = HhEmployerLoader(response=response)
        loader.add_value('url', response.url)
        for key, selector in self.data_employer.items():
            loader.add_xpath(key, selector)
        yield loader.load_item()
        re_pattern = re.compile(r'(?<=employer\/)\d+')
        url = re.findall(re_pattern, response.url)
        url = 'https://hh.ru/search/vacancy?employer_id=' + url[0]
        yield response.follow(url, self.parse)
