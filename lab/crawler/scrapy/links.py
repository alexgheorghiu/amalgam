from scrapy.spiders import CrawlSpider
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors import LinkExtractor

class Linkoid(CrawlSpider):

	def parse(self, response):
		for link in self.link_extractor.extract_links(response):
			yield Request(link.url, callback=self.parse)


if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(Linkoid)
    process.start()
