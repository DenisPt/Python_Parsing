# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class UrlMixin(scrapy.Item):
    url = scrapy.Field()


class DescriptionMixin(scrapy.Item):
    description = scrapy.Field()


class HhVacancyItem(UrlMixin, DescriptionMixin, scrapy.Item):
    _id = scrapy.Field()
    vacancy = scrapy.Field()
    salary = scrapy.Field()
    skills = scrapy.Field()
    employer_url = scrapy.Field()
    pass


class HhEmployerItem(UrlMixin, DescriptionMixin, scrapy.Item):
    _id = scrapy.Field()
    name = scrapy.Field()
    site = scrapy.Field()
    fields = scrapy.Field()
    pass
