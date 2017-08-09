from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector

from ScrapyParser.items import NovitaItemLoader, SpidersItem

from bs4 import BeautifulSoup


def _get_aviliablity_list(value):
    '''
    Create aviliability list
    :param value: list
    :return: list
    '''
    soup = BeautifulSoup(value, 'lxml')
    sizes_accepted = soup.find_all('td', {'class': 'tdforselect'})
    res = ['disabled' if 'disabled' in size_accepted['class'] else 'enabled'
           for size_accepted in sizes_accepted]
    return res


def _create_sizes_dict(color_list, sizes_list, sizes_accepted):
    '''
    Create dict of color and sizes of item
    :param color_list: list
    :param sizes_list: list
    :param sizes_accepted: list
    :return: dict
    '''
    i = 0
    temp_dict = dict()
    for color in color_list:
        temp_list = list()
        for item in sizes_accepted[i:i + len(sizes_list)]:
            temp_list.append(item)
            res = {color: temp_list}
            temp_dict.update(res)
        i += len(sizes_list)
    color_size = {color: sizes_list.copy() for color in color_list}
    for key, value in temp_dict.items():
        for item in range(len(value)):
            if value[item] == 'disabled':
                color_size[key].pop(temp_dict[key].index(value[item]))
    return color_size


def _prettify_color(value):
    res = list()
    for color in value:
        if color.strip() != 'Цвет/размер' and color.strip():
            res.append(color.strip())
    return res


class NovitaSpider(CrawlSpider):
    name = 'novita'

    start_urls = ['http://novita-nsk.ru/shop/zhenskie-platja-optom/',
                  'http://novita-nsk.ru/shop/bluzy/']
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
        loader = NovitaItemLoader(SpidersItem(), selector)
        loader.add_value('url', response.url)
        loader.add_xpath('name', '//h1/text()')
        loader.add_value('_type',
                         selector.xpath('//h1/text()').extract()[0].strip().replace(' ', '').split('-')[0].capitalize())
        loader.add_xpath('price', '//div[@class="price-value"]/div[@class="value"]/text()')
        color_list = _prettify_color(selector.xpath('//tr/td[@class="col-color"]/text()').extract())
        availiability_list = _get_aviliablity_list(selector.xpath('//html').extract()[0])
        loader.add_value('sizes', _create_sizes_dict(color_list=color_list,
                                                     sizes_list=selector.xpath(('//td[@class="inv"]'
                                                                                '/text()')).extract(),
                                                     sizes_accepted=availiability_list))
        loader.add_value('site', 'novita')
        loader.add_value('is_new', False)
        return loader.load_item()
