"""
Run it with:
    scrapy crawl quotes -s LOG_LEVEL=WARNING
"""
import scrapy
from sys import exit


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    allowed_domains = ['abctimetracking.com']

    def start_requests(self):
        urls = [
            'http://abctimetracking.com/',
            # 'http://quotes.toscrape.com/page/1/',
            # 'http://quotes.toscrape.com/page/2/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        print("********************************URL: " + response.request.url)

        # page = response.url.split("/")[-2]
        # filename = f'quotes-{page}.html'
        # with open(filename, 'wb') as f:
        #     f.write(response.body)
        # self.log(f'Saved file {filename}')
        # for quote in response.css('div.quote'):
        #     yield {
        #         'text' : quote.css('span.text::text').get(),
        #         'author' : quote.css('small.author::text').get(),
        #         'tags' : quote.css('div.tags a.tag::text').getall()
        #     }

        # next_page = response.css('a::attr(href)').get()
        next_pages = response.css('a::attr(href)').getall()
        for next_page in next_pages:
            print("href %s" % next_page )
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)
