# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class HhParsingPipeline:
    def process_item(self, item, spider):
        return item


class SaveToMongoPipeline:
    def __init__(self):
        client = pymongo.MongoClient()
        self.db = client["py_parsing"]

    def process_item(self, item, spider):
        self.db[type(item).__name__].insert_one(item)
        return item
