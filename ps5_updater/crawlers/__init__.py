from abc import ABC, abstractmethod
from selenium import webdriver
from decouple import config


class Crawler(ABC):

    @property
    def store(self):
        raise NotImplementedError

    @staticmethod
    def get_driver(headless=True):
        """
        define a headless chrome driver
        """
        D_PATH = config('DRIVER_PATH')
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument("--disable-notifications")
        return webdriver.Chrome(D_PATH)

    @abstractmethod
    def find_ps5_page(self):
        """
        navigate to the page where ps5 exists
        """
        pass

    @abstractmethod
    def select_store(self):
        """
        select area to search in
        """
        pass

    @abstractmethod
    def get_status(self):
        """
        return the current status (in stock/not in stock)
        """
        pass

    def send_email(self):
        pass



