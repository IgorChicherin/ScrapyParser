from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector

from ScrapyParser.items import WisellItemLoader, SpidersItem


class WisellSpider(CrawlSpider):
    name = 'wisell'

    start_urls = ['https://wisell.ru/catalog/platya/']
    allowed_domains = ['wisell.ru']

    rules = [Rule(LinkExtractor(restrict_xpaths=['//*[@id="catalog-lements-id"]'],
                                allow='https://wisell.ru/catalog/platya/([A-Za-z0-9-]+)'),
                  callback='parse_item'),
             Rule(LinkExtractor(restrict_xpaths=['//*[@id="main-catalog"]/footer[1]/div/ul/li[6]']), follow=True)]


    def parse_item(self, response):
        selector = Selector(response)
        loader = WisellItemLoader(SpidersItem(), selector)
        loader.add_value('url', response.url)
        loader.add_xpath('name', '//h1/text()')
        loader.add_xpath('price', '//*[@id="currency_tab-1"]/div/div[2]/span/span/text()')
        sizes_list = selector.xpath('//*[@id="size_rang-1"]/div/ul/li/label//span/text()').extract()
        sizes_list.remove(sizes_list[0])
        loader.add_value('sizes', sizes_list)
        loader.add_value('site', 'wisell')
        return loader.load_item()