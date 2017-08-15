import json
import re

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector

from ScrapyParser.items import BigmodaItemLoader, SpidersItem


class BigmodaSpider(CrawlSpider):
    name = 'bigmoda'

    start_urls = ['http://big-moda.com/product-category/platya-bolshih-razmerov/',
                  'http://big-moda.com/product-category/bluzki-bolshih-razmerov/',
                  'http://big-moda.com/product-category/rasprodazha-bolshie-razmery/']
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
        product_id = re.search(r'(\d+)', selector.xpath('//*[@id="main"]/div/@id').extract()[0]).group(0)
        sizes_id = re.findall(r'(?<="variation_id":)(\d+)',
                              selector.xpath('//*[@id="ivpa-content"]/@data-variations').extract()[0])
        sizes_key = re.findall(r'(?<="attribute_pa_size":)"(\d+)"',
                               selector.xpath('//*[@id="ivpa-content"]/@data-variations').extract()[0])
        product_size_id = dict(zip(sizes_key, sizes_id))
        if 'rasprodazha-bolshie-razmery' in response.url:
            item = dict()
            item['url'] = response.url
            item['name'] = selector.xpath('//*/div[3]/div[3]/span[1]/span/text()').extract()[0]
            price_in = selector.xpath('//*/div[3]/p/ins/span/text()').extract()[0]
            item['price'] = price_in.strip().replace(',', '').split('.')[0]
            sizes_in = selector.xpath('//*[@id="ivpa-content"]/div[2]/span/text()').extract()
            item['sizes'] = [size.strip() for size in sizes_in]
            item['site'] = 'bigmoda'
            item['item_type'] = selector.xpath('//h1/text()').extract()[0].split(' ')[0]
            item['is_new'] = False
            item['product_id'] = product_id
            item['product_size_id'] = product_size_id
            with open('exc.json', 'a') as exc_file:
                line = json.dumps(dict(item)) + "\n"
                exc_file.write(line)
        else:
            loader.add_value('url', response.url)
            loader.add_xpath('name', '//*/div[3]/div[3]/span[1]/span/text()')
            loader.add_xpath('price', '//*/div[3]/p[1]/span/text()')
            loader.add_xpath('sizes', '//*[@id="ivpa-content"]/div[2]/span/text()')
            loader.add_value('site', 'bigmoda')
            loader.add_value('product_id', product_id)
            loader.add_value('product_size_id', product_size_id)
            item_type = selector.xpath('//h1/text()').extract()[0].split(' ')[0]
            loader.add_value('_type', item_type)
            loader.add_value('is_new', False)
            return loader.load_item()
