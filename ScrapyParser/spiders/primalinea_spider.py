from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy.http import FormRequest, Request

from ScrapyParser.items import PrimalineaItemLoader, PrimalineaItem


def _prettify_sizes(sizes):
    sizes = str(sizes).split(',')
    return list(size.strip() for size in sizes)


class PrimalineaSpider(CrawlSpider):
    name = 'prima'

    login_page = 'http://primalinea.ru/customers/login'
    start_urls = ['http://primalinea.ru/catalog/category/42/all/0', 'http://primalinea.ru/catalog/category/43/all/0']
    allowed_domains = ['primalinea.ru']

    rules = [Rule(LinkExtractor(restrict_xpaths=['//*[@id="catalog-items-list"]'], allow=r'catalog/item/\d+'),
                  callback='parse_item')]

    def start_requests(self):
        yield Request(url=self.login_page, callback=self.login, dont_filter=True)

    def login(self, response):
        return FormRequest.from_response(response,
                                         formdata={'login_name': 'mail@big-moda.com'},
                                         callback=self.check_login_response)

    def check_login_response(self, response):
        if bytes('Выход', 'utf-8') not in response.body:
            self.log('Login failed')
        else:
            self.log('Successfully logged in. Let\'s start crawling!')
            for url in self.start_urls:
                yield Request(url)

    def parse_item(self, response):
        selector = Selector(response)
        loader = PrimalineaItemLoader(PrimalineaItem(), selector)
        loader.add_value('url', response.url)
        loader.add_xpath('name', '//h1/text()')
        loader.add_xpath('price', '//*[@id="catalog-item-description"]/p[1]/text()')
        sizes_list = selector.xpath('//*[@id="catalog-item-description"]/div[3]/text()').extract()[1]
        loader.add_value('sizes', _prettify_sizes(sizes_list))
        loader.add_value('site', 'primalinea')
        return loader.load_item()
