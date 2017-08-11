import os

from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

# Spiders
from ScrapyParser.spiders.bigmoda_spider import BigmodaSpider
from ScrapyParser.spiders.novita_spider import NovitaSpider
from ScrapyParser.spiders.wisell_spider import WisellSpider
from ScrapyParser.spiders.primalinea_spider import PrimalineaSpider
from ScrapyParser.spiders.avigal_spider import AvigalSpider

# WooCommerce REST API
from woocommerce import API

# Sync WooCommerce Module
from ScrapyParser.woo_sync_db import compare_dress, del_item

# Krasa CSV Parser
from ScrapyParser.krasa_parser import krasa_parse


def spiders_reactor():
    '''
    Run spiders in Twisted reactor
    :return: boolean
    '''
    configure_logging()
    runner = CrawlerRunner(get_project_settings())
    runner.crawl(BigmodaSpider)
    runner.crawl(NovitaSpider)
    runner.crawl(WisellSpider)
    runner.crawl(PrimalineaSpider)
    runner.crawl(AvigalSpider)
    d = runner.join()
    d.addBoth(lambda _: reactor.stop())
    reactor.run()
    return True


def create_woo_conn():
    '''
    Create connection with WooCommerce REST API
    :return: WooCommerce API connection
    '''
    files = ['добавить удалить размеры.txt', 'добавить удалить карточки.txt', 'errors.txt']
    for file in files:
        if os.path.exists(file):
            os.remove(file)

    with open('keys.txt', 'r') as file:
        keys = [line.strip() for line in file]

    consumer_key = keys[0]
    consumer_secret = keys[1]

    wcapi = API(
        url='http://big-moda.com',
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        wp_api=True,
        version="wc/v2",
    )
    return wcapi

if __name__ == '__main__':
    spiders_reactor()
