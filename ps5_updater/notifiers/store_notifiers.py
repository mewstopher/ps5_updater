from ps5_updater.crawlers.store_crawlers import TargetCrawler, BestBuyCrawler
from ps5_updater.notifiers import Notifier


class TargetNotifier(Notifier):
    def crawler_factory(self):
        return TargetCrawler()


class BestBuyNotifier(Notifier):
    def crawler_factory(self):
        return BestBuyCrawler()
