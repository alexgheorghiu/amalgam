"""https://www.tutorialspoint.com/scrapy/scrapy_spiders.htm"""

from scrapy.spiders import CrawlSpider, Rule
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors import LinkExtractor
from scrapy.item import Item, Field 


class DemoItem(Item): 
   product_title = Field() 
   product_link = Field() 
   product_description = Field() 


class AmalgamSpider(CrawlSpider):
    name = "AmalgamSpider"
    allowed_domains = ["www.abctimetracking.com"]
    start_urls = ["http://www.abctimetracking.com"]

    rules = (
        Rule(LinkExtractor(),
         callback = "parse_item", follow = True),
    )

    def parse_item(self, response):
        item = DemoItem()
        item["product_title"] = response.xpath("a/text()").extract()
        item["product_link"] = response.xpath("a/@href").extract()
    #   item["product_description"] = response.xpath("div[@class = 'desc']/text()").extract()
        print("------------------------->", item)
        return item

if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(AmalgamSpider)
    process.start()