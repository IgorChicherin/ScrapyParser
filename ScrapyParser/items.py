# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Compose, Identity


class BigmodaItem(scrapy.Item):
    url = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    sizes = scrapy.Field()
    site = scrapy.Field()


class BigmodaItemLoader(ItemLoader):
    site_out = TakeFirst()
    url_out = TakeFirst()
    name_out = TakeFirst()
    price_in = TakeFirst()
    price_out = Compose(lambda x: x[0].strip().replace(',', '').split('.'), price_in)
    sizes_out = MapCompose(lambda x: x.strip())


class NovitaItem(scrapy.Item):
    url = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    sizes = scrapy.Field()
    color = scrapy.Field()
    site = scrapy.Field()


class NovitaItemLoader(ItemLoader):
    site_out = TakeFirst()
    url_out = TakeFirst()
    name_out = Compose(lambda x: x[0].strip().replace(' ', '').split('-')[1], Compose())
    price_out = Compose(lambda x: x[0].strip().replace(',', '').split('.'), TakeFirst())
    color_out = Compose(lambda x: x[3].strip(), Identity())
    sizes_out = MapCompose()