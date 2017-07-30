from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector

from ScrapyParser.items import NovitaItem, NovitaItemLoader


class NovitaSpider(CrawlSpider):
    name = 'novita'

    start_urls = ['http://novita-nsk.ru/shop/zhenskie-platja-optom/']
    allowed_domains = ['novita-nsk.ru']

    rules = [
        Rule(LinkExtractor(
            restrict_xpaths=['//*[@id="content"]/div[5]/div[1]//div'],
            allow=r'product_id=\d+'
        ),
            callback='parse_item'
        )
    ]

    def parse_item(self, response):
        selector = Selector(response)
        loader = NovitaItemLoader(NovitaItem(), selector)
        loader.add_value('url', response.url)
        loader.add_xpath('name', '//h1/text()')
        loader.add_xpath('price', '//div[@class="price-value"]/div[@class="value"]/text()')
        loader.add_xpath('color', '//tr/td[@class="col-color"]/text()')
        loader.add_xpath('sizes', '//td[@class="inv"]/text()')
        loader.add_xpath('availability', '//table/tbody/tr[2]/td')
        loader.add_value('site', 'novita')
        return loader.load_item()
