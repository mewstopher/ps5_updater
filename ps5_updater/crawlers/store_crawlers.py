from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.support import expected_conditions as Ec
from ps5_updater.crawlers.helper_functions import wait_to_click
from selenium.webdriver.support.ui import WebDriverWait
from ps5_updater.exceptions import PageTimeoutError
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from ps5_updater.crawlers import Crawler
from decouple import config
from enum import Enum
import logging
import time


class Constants(Enum):
    DELAY = 20
    TARGET = 'https://www.target.com'
    TARGET_OOS = 'sold out'
    ITEM = 'playstation 5'
    TARGET_STORE_SELECT = 'storeId-utilityNavBtn'
    TARGET_AREA_SELECT = 'zipOrCityState'
    TARGET_STORE_CONFIRM = '/html/body/div[9]/div/div/div/div/div[3]/div[2]/div[1]/button'
    TARGET_PS5_MAIN = '//*[@id="mainContainer"]/div[3]/div/a/div[2]/h2/span/span'
    TARGET_STOCK_XPATH = '//*[@id="viewport"]/div[4]/div/div[2]/div[3]/div[1]/div/div/div'
    BB = 'https://www.bestbuy.com'
    BB_ITEM = 'playstation 5 console'
    BB_OOS = 'sold out'
    BB_STORE_DD = '//*[@id="lt-container"]/div/div/span/span/button'
    BB_STORE_SELECT = '//*[@id="store-loc-overlay"]/div[1]/div/a'
    BB_STERLING = '//*[@id="shop-location-card-12957af6-a275-44ca-9f33-0104abafb6d6"]/div/div/h3/button'
    BB_POPUP = '//*[@id="widgets-view-email-modal-mount"]/div/div/div[''1]/div/div/div/div/button'


class TargetCrawler(Crawler):
    driver = Crawler.get_driver()
    target_logger = logging.getLogger('target')

    def store(self):
        return 'Target'

    def select_store(self):
        """
        select my area code
        """
        counter = 0
        while counter < 11:
            try:
                WebDriverWait(self.driver, Constants.DELAY.value).until(Ec.element_to_be_clickable(
                    (By.ID, Constants.TARGET_STORE_SELECT.value))).click()
                self.target_logger.info('Area code button selected')
                time.sleep(5)
                store_zip = WebDriverWait(self.driver, 20).until(Ec.presence_of_element_located(
                    (By.ID, Constants.TARGET_AREA_SELECT.value)))
                #store_zip = self.driver.find_element_by_id(Constants.TARGET_AREA_SELECT.value)
                store_zip.send_keys(config('AREA_CODE'))
                self.target_logger.info('Area code was input')
                store_zip.send_keys(Keys.RETURN)
                WebDriverWait(self.driver, Constants.DELAY.value).until(Ec.presence_of_element_located(
                    (By.XPATH, Constants.TARGET_STORE_CONFIRM.value))).click()
                self.target_logger.info('Store selected')
                return
            except (NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException):
                self.target_logger.info('One of the elements not yet available.. retrying in 5 seconds')
                time.sleep(5)
                counter += 1
        raise PageTimeoutError

    def find_ps5_page(self):
        """
        navigate to item page
        """
        self.target_logger.info('getting webpage')
        self.driver.get(Constants.TARGET.value)
        search = self.driver.find_element_by_id('search')
        self.target_logger.info('Searching for item')
        search.send_keys(Constants.ITEM.value)
        search.send_keys(Keys.RETURN)
        self.target_logger.info('getting store by area code')
        self.select_store()
        WebDriverWait(self.driver, 20).until(
            Ec.element_to_be_clickable((By.XPATH, Constants.TARGET_PS5_MAIN.value))).click()
        WebDriverWait(self.driver, 20).until(
            Ec.element_to_be_clickable((By.LINK_TEXT, 'PlayStation 5 Console'))).click()
        self.target_logger.info('item main page selected')

    def get_status(self) -> bool:
        """
        get status of item

        RETURNS
        -------
        in_stock: bool
            True if target has something other than
            'out of stock' label  otherwise return False
        """
        in_stock = False
        self.target_logger.info('Getting status from main page')
        status = WebDriverWait(self.driver, 20).until(
            Ec.element_to_be_clickable((By.XPATH, Constants.TARGET_STOCK_XPATH.value)))
        self.target_logger.info(f'Status is {status.text}')
        if status.text.lower() != Constants.TARGET_OOS.value:
            in_stock = True
        return in_stock


class BestBuyCrawler(Crawler):
    best_logger = logging.getLogger('best_logger')
    driver = Crawler.get_driver()

    def store(self):
        return 'Best Buy'

    def select_store(self):
        self.driver.find_element_by_xpath(Constants.BB_STORE_DD.value).click()
        self.driver.find_element_by_xpath(Constants.BB_STORE_SELECT.value).click()
        zip_search = self.driver.find_element_by_id('input-shop-location-zip-code-form-0779447c-2050-421a-a070-78f5e8135b02')
        zip_search.send_keys(config('AREA_CODE'))
        zip_search.send_keys(Keys.RETURN)
        self.driver.find_element_by_xpath('//*[@id="shop-location-card-12957af6-a275-44ca-9f33-0104abafb6d6"]/div/div[2]/button').click()

    def find_ps5_page(self):
        self.best_logger.debug('Getting best buy web page')
        self.driver.get(Constants.BB.value)
        try:
            self.driver.find_element_by_xpath(Constants.BB_POPUP.value).click()
            self.best_logger.info('Disabling pop-up window')
        except NoSuchElementException:
            self.best_logger.debug('No popup window detected')
        self.select_store()
        self.driver.back()
        search = self.driver.find_element_by_id('gh-search-input')
        self.best_logger.info('Searching for item')
        search.send_keys(Constants.BB_ITEM.value)
        search.send_keys(Keys.RETURN)


    def get_status(self) -> bool:
        in_stock = False
        status = self.driver.find_element_by_xpath('//*[@id="fulfillment-fulfillment-summary-9405df97-3b04-497e-8610-6724f1e7d08f"]/div/div/div/div[1]/strong')
        if status.text.lower() != Constants.BB_OOS.value:
            in_stock = True
        return in_stock
