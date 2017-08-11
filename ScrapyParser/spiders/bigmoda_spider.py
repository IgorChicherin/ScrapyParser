from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector

from ScrapyParser.items import BigmodaItemLoader, SpidersItem


class BigmodaSpider(CrawlSpider):
    name = 'bigmoda'

    start_urls = ['http://big-moda.com/product-category/platya-bolshih-razmerov/',
                  'http://big-moda.com/product-category/bluzki-bolshih-razmerov/']
    allowed_domains = ['big-moda.com']

    rules = [
        Rule(LinkExtractor(
            restrict_xpaths=['//*[@id="main"]/ul'],
            allow=r'http://big-moda.com/shop/([A-Za-z0-9-]+)/([A-Za-z0-9-]+)'
        ),
            callback='parse_item'
        ),
        Rule(LinkExtractor(
            restrict_xpaths=['//*[@id="main"]/nav[2]/ul/li/a[@class="next page-numbers"]']), follow=True),
    ]

    def parse_item(self, response):
        selector = Selector(response)
        loader = BigmodaItemLoader(SpidersItem(), selector)
        loader.add_value('url', response.url)
        loader.add_xpath('name', '//*/div[3]/div[3]/span[1]/span/text()')
        loader.add_xpath('price', '//*/div[3]/p[1]/span/text()')
        loader.add_xpath('sizes', '//*[@id="ivpa-content"]/div[2]/span/text()')
        loader.add_value('site', 'bigmoda')
        item_type = selector.xpath('//h1/text()').extract()[0].split(' ')[0]
        loader.add_value('_type', item_type)
        loader.add_value('is_new', False)
        return loader.load_item()