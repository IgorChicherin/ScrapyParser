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


def main():
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


if __name__ == '__main__':
    main()




