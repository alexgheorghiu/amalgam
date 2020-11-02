"""
Based on:
https://docs.scrapy.org/en/latest/intro/tutorial.html
https://www.linode.com/docs/development/python/use-scrapy-to-extract-data-from-html-tags/
https://medium.com/@pknerd/develop-your-first-web-crawler-in-python-scrapy-6b2ee4baf954 
https://www.digitalocean.com/community/tutorials/how-to-crawl-a-web-page-with-scrapy-and-python-3
https://towardsdatascience.com/how-to-run-scrapy-from-a-script-ff07fd6b792b
"""

import scrapy
from scrapy.crawler import CrawlerProcess

class BrickSetSpider(scrapy.spiders.CrawlSpider):
    name  = "amalgam_spider"
    # custom_settings = { 'DOWNLOD_DELAY': 1 }
    # headers = {} 
    # params = {}
    start_urls = ['https://en.wikipedia.org/wiki/Romania']

    # def start_requests(self):
    #     yield scrapy.Request(self.start_urls[0], headers=self.headers, callback = self.parse)

    # def parse(self, response):
    #     SET_SELECTOR = '.toctext'
    #     for brickset in response.css(SET_SELECTOR):
    #         NAME_SELECTOR = '::text'
    #         yield {
    #             'name' : brickset.css(NAME_SELECTOR).extract_first(),
    #         }
        # print(response.body)

    def parse(self, response):
        for link in self.link_extractor.extract_links(response):
            yield Request(link.url, callback=self.parse)    

if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(BrickSetSpider)
    process.start()
