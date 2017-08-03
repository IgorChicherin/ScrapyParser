from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy.http import Request, FormRequest

from ScrapyParser.items import AvigalItemLoader, SpidersItem

from bs4 import BeautifulSoup


def _get_sizes_list(body):
    soup = BeautifulSoup(body, 'lxml')
    sizes_list = soup.find_all('label', {'class': 'optid-13'})
    sizes_list = [item.text.strip() for item in sizes_list if r':n\a' not in item['title']]
    return sizes_list


class AvigalSpider(CrawlSpider):
    name = 'avigal'

    login_page = 'http://avigal.ru/login/'
    start_urls = ['http://avigal.ru/dress/', 'http://avigal.ru/blouse-tunic/']
    allowed_domais = ['avigal.ru']

    rules = [Rule(LinkExtractor(restrict_xpaths=['//*[@id="res-products"]/div[1]'],
                                allow=r'product&path=(\d+)&product_id=(\d+)'),
                  callback='parse_item'),
             Rule(LinkExtractor(restrict_xpaths=['//ul[@class="pagination"]/li[6]', '//ul[@class="pagination"]/li[9]']),
                  follow=True)]

    def start_requests(self):
        yield Request(url=self.login_page, callback=self.login, dont_filter=True)

    def login(self, response):
        return FormRequest.from_response(response,
                                         formdata={'email': 'Bigmoda.com@gmail.com', 'password': '010101'},
                                         callback=self.check_login_response)

    def check_login_response(self, response):
        if bytes('Основные данные', 'utf-8') in response.body:
            self.log('Successfully logged in. Let\'s start crawling!')
            for url in self.start_urls:
                yield Request(url)
        else:
            self.log('Login failed')

    def parse_item(self, response):
        selector = Selector(response)
        loader = AvigalItemLoader(SpidersItem(), selector)
        loader.add_value('url', response.url)
        loader.add_xpath('name', '//span[@itemprop="model"]/text()')
        loader.add_xpath('price', '//*[@id="update_price"]/text()')
        loader.add_value('sizes', _get_sizes_list(response.body))
        loader.add_value('site', 'avigal')
        return loader.load_item()
