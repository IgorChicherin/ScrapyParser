from scrapy.spiders import CrawlSpider, Rule
from scrapy.contrib.spiders.init import InitSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy.http import FormRequest, Request

from ScrapyParser.items import PrimalineaItemLoader, PrimalineaItem


class PrimalineaSpider(CrawlSpider):
    name = 'prima'

    login_page = 'http://primalinea.ru/customers/login'
    start_urls = ['http://primalinea.ru/catalog/category/42/all/0']
    # allowed_domains = ['primalinea.ru']

    rules = [Rule(LinkExtractor(restrict_xpaths=['//*[@id="catalog-items-list"]'], allow=r'catalog/item/\d+'),
                  callback='parse_item')]

    # def init_request(self):
    #     return Request(url=self.login_page, callback=self.login)

    def start_requests(self):
        yield Request(url=self.login_page, callback=self.login, dont_filter=True)

    def login(self, response):
        return FormRequest.from_response(response,
                                         formdata={'login_name': 'mail@big-moda.com'},
                                         callback=self.check_login_response)

    def check_login_response(self, response):
        # if 'Добро пожаловать, Евгений !' in response.body:
        #     self.log('Login failed')
        # else:
        #     self.log('Successfully logged in. Let\'s start crawling!')
        return Request(url=self.start_urls[0])

    def parse_item(self, response):
        selector = Selector(response)
        loader = PrimalineaItemLoader(PrimalineaItem(), selector)
        loader.add_value('url', response.url)
        loader.add_xpath('price', '//*[@id="catalog-item-description"]/p[1]')
        return loader.load_item()
