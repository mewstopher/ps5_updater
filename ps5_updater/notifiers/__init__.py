from abc import ABC, abstractmethod


class Notifier(ABC):
    """base class for crawlers"""

    @abstractmethod
    def crawler_factory(self):
        pass

    def send_notification(self):
        """
        do the same thing with any given crawler
        """
        crawler = self.crawler_factory()
        crawler.find_ps5_page()
        status = crawler.get_status()
        return status

