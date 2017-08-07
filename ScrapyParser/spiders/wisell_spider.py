from _cffi_backend import callback

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy.http import Request, Response


from ScrapyParser.items import WisellItemLoader, SpidersItem


class WisellSpider(CrawlSpider):
    name = 'wisell'

    start_urls = ['https://wisell.ru/catalog/platya/']
    allowed_domains = ['wisell.ru']

    rules = [Rule(LinkExtractor(restrict_xpaths=['//*[@id="catalog-lements-id"]'],
                                allow='https://wisell.ru/catalog/\w+/([A-Za-z0-9-]+)'),
                  callback='parse_item'),
             # Rule(LinkExtractor(restrict_xpaths=['//*[@id="size-interval-tabs"]/li[1]/a'],
             #                    allow='https://wisell.ru/catalog/platya/([A-Za-z0-9-]+)'),
             #      callback='parse_item'),
             Rule(LinkExtractor(restrict_xpaths=['//*[@id="main-catalog"]/footer[1]/div/ul/li[6]']), follow=True)]

    # def start_requests(self):
    #     for url in self.start_urls:
    #         yield Request(url, callback=self.parse_item)

    def parse_item(self, response):
        Item = SpidersItem()
        selector = Selector(response)
        loader = WisellItemLoader(SpidersItem(), selector)
        Item['name'] = selector.xpath('//h1/text()').extract()[0]
        # loader.add_value('url', response.url)
        # loader.add_xpath('name', '//h1/text()')
        # loader.add_xpath('price', '//*[@id="currency_tab-1"]/div/div[2]/span/span/text()')
        # sizes_list = selector.xpath('//*[@id="size_rang-1"]/div/ul/li/label//span/text()').extract()
        # sizes_list.remove(sizes_list[0])
        # loader.add_value('sizes', sizes_list)
        # loader.add_value('site', 'wisell')
        small_url = selector.xpath('//*[@id="size-interval-tabs"]/li/@data-url').extract()
        # self.log(small_url)
        if small_url[0]:
            small_size_link = 'http://wisell.ru%s' % (small_url[0])
            request = Request(small_size_link, callback=self.parse_small_size)
            request.meta['item'] = Item
            yield request
        elif len(small_url) == 1:
            yield Item
        # response = Response(url=small_size_link)
        # self.log(response.body)
        # loader.add_value('url2', response.url)
        # loader.add_xpath('name2', '//h1/text()')
        # return loader.load_item()


    def parse_small_size(self, response):
        Item = response.meta['item']
        selector = Selector(response)
        Item['name2'] = selector.xpath('//h1/text()').extract()[0]
        # self.log(Item)
        yield Item
