from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector

from ScrapyParser.items import SpidersItem, WisellItemLoader

import requests


class WisellSpider(CrawlSpider):
    name = 'wisell'

    start_urls = ['https://wisell.ru/catalog/platya/']
    allowed_domains = ['wisell.ru']

    rules = [Rule(LinkExtractor(restrict_xpaths=['//*[@id="catalog-lements-id"]//li'
                                                 '//div[@class="item_cont price_composite_content"]'],
                                allow='/catalog/([A-Za-z0-9-_]+)/([A-Za-z0-9-]+)'),
                  callback='parse_item'),
             Rule(LinkExtractor(restrict_xpaths=['//*[@id="main-catalog"]/footer[1]/div/ul/li[6]']), follow=True)]

    def parse_item(self, response):
        selector = Selector(response)
        loader = WisellItemLoader(SpidersItem(), selector)
        loader.add_value('url', response.url)
        loader.add_xpath('price', '//*[@id="currency_tab-1"]/div/div[2]/span/span/text()')
        loader.add_value('is_new', True if selector.xpath('//*[@id="item1"]/div/span[2]/span/span').extract() else False)
        loader.add_value('site', 'wisell')
        small_url = selector.xpath('//*[@id="size-interval-tabs"]/li/@data-url').extract()
        is_big = True if selector.xpath('//*[@id="size-interval-tabs"]'
                                        '/li/a/@href').extract()[0] == '#size_rang-2' else False
        loader.add_value('_type', selector.xpath('//h1/text()').extract()[0].split(' ')[0])
        small_size_link = 'https://wisell.ru%s' % (small_url[0])
        if small_url[0] and len(small_url) > 1:
            big_name = selector.xpath('//h1/text()').extract()[0].split(' ')[1]
            sizes_list = selector.xpath('//*[@id="size_rang-1"]/div/ul/li/label//span/text()').extract()
            sizes_list.remove(sizes_list[0])
            small_size_link = 'https://wisell.ru%s' % (small_url[0])
            r = requests.get(small_size_link)
            selector = Selector(r)
            small_name = selector.xpath('//h1/text()').extract()[0].split(' ')[1]
            loader.add_value('name', '%s %s' % (big_name, small_name))
            small_sizes = selector.xpath('//*[@id="size_rang-1"]/div/ul/li/label//span/text()').extract()
            small_sizes.remove(small_sizes[0])
            for size in small_sizes:
                if int(size) > 46 and size not in sizes_list:
                    sizes_list.append(size)
            sizes_list.sort()
            loader.add_value('sizes', sizes_list)
            return loader.load_item()
        elif len(small_url) == 1 and is_big:
            loader.add_value('name', selector.xpath('//h1/text()').extract()[0].split(' ')[1])
            sizes_list = selector.xpath('//*[@id="size_rang-1"]/div/ul/li/label//span/text()').extract()
            sizes_list.remove(sizes_list[0])
            loader.add_value('sizes', sizes_list)
            return loader.load_item()