from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector

from ScrapyParser.items import BigmodaItemloader, BigmodaItem


class BigmodaSpider(CrawlSpider):
    name = 'bigmoda'

    start_urls = ['http://big-moda.com/product-category/platya-bolshih-razmerov/']
    allowed_domains = ['big-moda.com']

    rules = [
        Rule(LinkExtractor(
            restrict_xpaths=['//*[@id="main"]/ul'],
            allow=r'http://big-moda.com/shop/platya-bolshih-razmerov/([A-Za-z0-9-]+)'
        ),
            callback='parse_item'
        )
    ]

    def parse_item(self, response):
        selector = Selector(response)
        loader = BigmodaItemloader(BigmodaItem(), selector)
        loader.add_value('url', response.url)
        loader.add_xpath('name', '//*/div[3]/div[3]/span[1]/span/text()')
        loader.add_xpath('price', '//*/div[3]/p[1]/span/text()')
        loader.add_xpath('sizes', '//*[@id="ivpa-content"]/div[2]/span/text()')
        return loader.load_item()