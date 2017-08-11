import os
import json

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
    Create connection with WooCommerce REST API and remove log files
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


def _check_dress(items_list, item, _type, site=None):
    if site == 'Новита' and item['_type'] == _type:
        for key in item['sizes'][0]:
            items_list.append(['%s %s %s' % (site, item['name'], key), item['sizes'][0][key], item['price'],
                               item['_type'], item['is_new']])
    elif site != 'Новита' and item['_type'] == _type:
        if site == None:
            # print(item['name'], item['price'])
            try:
                items_list.append([item['name'], item['sizes'], item['price'], item['_type'], item['is_new']])
            except KeyError:
                print(item)
        else:
            items_list.append(['%s %s' % (site, item['name']), item['sizes'], item['price'], item['_type'],
                               item['is_new']])

    return items_list


def _check_blouse(items_list, item, _type, site=None):
    if site == 'Новита' and item['_type'] == _type:
        for key in item['sizes'][0]:
            items_list.append(['%s %s %s' % (site, item['name'], key), item['sizes'][0][key], item['price'],
                               item['_type'], item['is_new']])
    elif site != 'Новита' and item['_type'] == _type:
        if site == None:
            try:
                items_list.append([item['name'], item['sizes'], item['price'], item['_type'], item['is_new']])
            except KeyError:
                print(item)
        else:
            items_list.append(['%s %s' % (site, item['name']), item['sizes'], item['price'], item['_type'],
                               item['is_new']])
    return items_list


def _create_items_list():
    with open('result.json', 'r') as file:
        result = list()
        for item in file:
            result.append(json.loads(item))
    novita_dress, novita_blouse = list(), list()
    avigal_dress, avigal_blouse = list(), list()
    wisell_dress, wisell_blouse = list(), list()
    primalinea_dress, primalinea_blouse = list(), list()
    bigmoda_dress, bigmoda_blouse = list(), list()
    for item in result:
        if item['site'] == 'novita':
            _check_dress(items_list=novita_dress, item=item, _type='Платье', site='Новита')
            _check_blouse(items_list=novita_blouse, item=item, _type='Блузка', site='Новита')
        elif item['site'] == 'avigal':
            _check_dress(items_list=avigal_dress, item=item, _type='Платье', site='Авигаль')
            _check_blouse(items_list=avigal_blouse, item=item, _type='Блузка', site='Авигаль')
            _check_blouse(items_list=avigal_blouse, item=item, _type='Туника', site='Авигаль')
        elif item['site'] == 'wisell':
            _check_dress(items_list=wisell_dress, item=item, _type='Платье', site='Визель')
            _check_blouse(items_list=wisell_blouse, item=item, _type='Блуза', site='Визель')
            _check_blouse(items_list=wisell_blouse, item=item, _type='Туника', site='Визель')
        elif item['site'] == 'primalinea':
            _check_dress(items_list=primalinea_dress, item=item, _type='Платье', site='Прима')
            _check_blouse(items_list=primalinea_blouse, item=item, _type='Блуза', site='Прима')
            _check_blouse(items_list=primalinea_blouse, item=item, _type='Туника', site='Прима')
        elif item['site'] == 'bigmoda':
            _check_dress(items_list=bigmoda_dress, item=item, _type='Платье')
            _check_dress(items_list=bigmoda_dress, item=item, _type='Костюм')
            _check_blouse(items_list=bigmoda_blouse, item=item, _type='Блуза')
            _check_blouse(items_list=bigmoda_blouse, item=item, _type='Блузка')

    # print(bigmoda_dress)
    # print(bigmoda_blouse)


if __name__ == '__main__':
    # if os.path.exists('result.json'):
    #     os.remove('result.json')
    # spiders_reactor()
    _create_items_list()
