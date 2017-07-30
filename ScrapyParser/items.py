# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Join, Compose

class BigmodaItem(scrapy.Item):
    url = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    sizes = scrapy.Field()


class BigmodaItemloader(ItemLoader):
    url_out = TakeFirst()
    name_out = TakeFirst()
    price_in = TakeFirst()
    price_out = Compose(lambda x: x[0].strip().replace(',', '').split('.'), price_in)
    sizes_out = MapCompose(lambda x: x.strip())
