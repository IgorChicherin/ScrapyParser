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


def _check_dress(items_list, item, _type, goods, site=None):
    if site == 'Новита' and item['_type'] == _type:
        for key in item['sizes'][0]:
            items_list.append(['%s %s %s' % (site, item['name'], key), item['sizes'][0][key], item['price'],
                               item['_type'], item['is_new']])
            goods.append('%s %s %s' % (site, item['name'], key))
    elif site != 'Новита' and item['_type'] == _type:
        if site == None:
            # print(item['name'], item['price'])
            try:
                items_list.append([item['name'], item['sizes'], item['price'], item['_type'], item['is_new']])
                goods.append('%s' % (item['name']))
            except KeyError:
                # print(item)
                pass
        else:
            items_list.append(['%s %s' % (site, item['name']), item['sizes'], item['price'], item['_type'],
                               item['is_new']])
            goods.append('%s %s' % (site, item['name']))

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
    goods_data = list()
    for item in result:
        if item['site'] == 'novita':
            _check_dress(novita_dress, item, _type='Платье', site='Новита', goods=goods_data)
            _check_dress(novita_blouse, item, _type='Блузка', site='Новита', goods=goods_data)
        elif item['site'] == 'avigal':
            _check_dress(avigal_dress,item, _type='Платье', site='Авигаль', goods=goods_data)
            _check_dress(avigal_blouse,item, _type='Блузка', site='Авигаль', goods=goods_data)
            _check_dress(avigal_blouse, item, _type='Туника', site='Авигаль', goods=goods_data)
        elif item['site'] == 'wisell':
            _check_dress(wisell_dress, item, _type='Платье', site='Визель', goods=goods_data)
            _check_dress(wisell_blouse, item, _type='Блуза', site='Визель', goods=goods_data)
            _check_dress(wisell_blouse, item, _type='Туника', site='Визель', goods=goods_data)
        elif item['site'] == 'primalinea':
            _check_dress(primalinea_dress, item, _type='Платье', site='Прима', goods=goods_data)
            _check_dress(primalinea_blouse, item, _type='Блуза', site='Прима', goods=goods_data)
            _check_dress(primalinea_blouse, item, _type='Туника', site='Прима', goods=goods_data)
        elif item['site'] == 'bigmoda':
            _check_dress(bigmoda_dress, item, _type='Платье', goods=goods_data)
            _check_dress(bigmoda_dress, item, _type='Костюм', goods=goods_data)
            _check_dress(bigmoda_blouse, item, _type='Блуза', goods=goods_data)
            _check_dress(bigmoda_blouse, item, _type='Блузка', goods=goods_data)

    return {'novita': {'dress': novita_dress, 'blouse': novita_blouse},
            'avigal': {'dress': avigal_dress, 'blouse': avigal_blouse},
            'wisell': {'dress': wisell_dress, 'blouse': wisell_blouse},
            'prima': {'dress': primalinea_dress, 'blouse': primalinea_blouse},
            'bigmoda': {'dress': bigmoda_dress,  'blouse': bigmoda_blouse},
            'goods_data': goods_data}


if __name__ == '__main__':
    # if os.path.exists('result.json'):
    #     os.remove('result.json')
    # spiders_reactor()
    result = _create_items_list()

