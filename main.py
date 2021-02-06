from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from hh_parsing.spiders.hh_spider import HhSpider

if __name__ == "__main__":
    crawler_settings = Settings()
    crawler_settings.setmodule("hh_parsing.settings")
    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(HhSpider)
    crawler_process.start()

print(1)