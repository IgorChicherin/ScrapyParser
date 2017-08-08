import re

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy.http import Request, Response

from ScrapyParser.items import SpidersItem


class WisellSpider(CrawlSpider):
    name = 'wisell'

    start_urls = ['https://wisell.ru/catalog/platya/']
    allowed_domains = ['wisell.ru']

    rules = [Rule(LinkExtractor(restrict_xpaths=['//*[@id="catalog-lements-id"]'],
                                allow='https://wisell.ru/catalog/([A-Za-z0-9-_]+)/([A-Za-z0-9-]+)'
                                 ),
                  callback='parse_item'),
             Rule(LinkExtractor(restrict_xpaths=['//*[@id="main-catalog"]/footer[1]/div/ul/li[6]']), follow=True)]

    def parse_item(self, response):
        Item = SpidersItem()
        selector = Selector(response)
        small_url = selector.xpath('//*[@id="size-interval-tabs"]/li/@data-url').extract()
        is_big = True if selector.xpath('//*[@id="size-interval-tabs"]'
                                        '/li/a/@href').extract()[0] == '#size_rang-2' else False

        if small_url[0] and len(small_url) > 1:
            Item['url'] = response.url
            Item['name'] = selector.xpath('//h1/text()').extract()[0]
            Item['price'] = selector.xpath('//*[@id="currency_tab-1"]/div/div[2]/span/span/text()').extract()
            Item['price'] = re.search(r'(\d+)', Item['price'][0].strip().replace(' ', '')).group(0)
            sizes_list = selector.xpath('//*[@id="size_rang-1"]/div/ul/li/label//span/text()').extract()
            sizes_list.remove(sizes_list[0])
            Item['sizes'] = sizes_list
            Item['site'] = 'wisell'
            small_size_link = 'https://wisell.ru%s' % (small_url[0])
            request = Request(small_size_link, callback=self.parse_small_size)
            request.meta['item'] = Item
            yield request
        elif len(small_url) == 1 and is_big:
            Item['url'] = response.url
            Item['name'] = selector.xpath('//h1/text()').extract()[0]
            print(Item['name'])
            Item['price'] = selector.xpath('//*[@id="currency_tab-1"]/div/div[2]/span/span/text()').extract()
            Item['price'] = re.search(r'(\d+)', Item['price'][0].strip().replace(' ', '')).group(0)
            sizes_list = selector.xpath('//*[@id="size_rang-1"]/div/ul/li/label//span/text()').extract()
            sizes_list.remove(sizes_list[0])
            Item['sizes'] = sizes_list
            Item['site'] = 'wisell'
        yield Item if Item else None

    def parse_small_size(self, response):
        Item = response.meta['item']
        selector = Selector(response)
        Item['url2'] = response.url
        big_name = Item['name'].split(' ')[1]
        small_name = selector.xpath('//h1/text()').extract()[0].split(' ')[1]
        small_sizes = selector.xpath('//*[@id="size_rang-1"]/div/ul/li/label//span/text()').extract()
        small_sizes.remove(small_sizes[0])
        for size in small_sizes:
            if int(size) > 46:
                Item['sizes'].append(size)
        Item['sizes'].sort()
        Item['name'] = '%s %s' % (big_name, small_name)
        yield Item
