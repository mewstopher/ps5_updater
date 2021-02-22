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
    TARGET_STORE_SELECT = "[data-test*='storeId-store-name"
    TARGET_AREA_SELECT = "[id*='zipOrCityState'"
    TARGET_STORE_CONFIRM = '[data-test*="storeId-listItem-confirmStore"'
    TARGET_PS5_MAIN = '[class*="ActionIconWrapper'
    TARGET_STOCK_XPATH = '//*[@id="viewport"]/div[4]/div/div[2]/div[3]/div[1]/div/div/div'
    BB = 'https://www.bestbuy.com'
    BB_ITEM = 'playstation 5 console'
    BB_OOS = 'sold out'
    BB_STORE_DD = 'Store Locator'
    BB_STORE_SELECT = "[title*='Enter city and state or ZIP Code']"
    BB_STERLING = '#shop-location-card-e303c9aa-c85e-4953-82cf-18958ecc4c51 > div > div.make-this-store-container > button'
    BB_POPUP = '//*[@id="widgets-view-email-modal-mount"]/div/div/div[''1]/div/div/div/div/button'
    BB_STATUS = "[id*='fulfillment-fulfillment-summary'"
    BB_STORE_DD_ALT = "[id*='shop-location-tooltip"


class TargetCrawler(Crawler):
    driver = Crawler.get_driver()
    target_logger = logging.getLogger('target')

    def store(self):
        return 'Target'

    def select_store(self, zip_code):
        """
        select my area code
        """
        counter = 0
        self.target_logger.info('Getting store from zip code')
        while counter < 11:
            try:
                WebDriverWait(self.driver, Constants.DELAY.value).until(Ec.element_to_be_clickable(
                    (By.CSS_SELECTOR, Constants.TARGET_STORE_SELECT.value))).click()
                self.target_logger.info('Area code button selected')
                time.sleep(5)
                store_zip = WebDriverWait(self.driver, 20).until(Ec.presence_of_element_located(
                    (By.CSS_SELECTOR, Constants.TARGET_AREA_SELECT.value)))
                time.sleep(2)
                store_zip.send_keys(zip_code)
                self.target_logger.info('Area code was input')
                store_zip.send_keys(Keys.RETURN)
                WebDriverWait(self.driver, Constants.DELAY.value).until(Ec.presence_of_element_located(
                    (By.CSS_SELECTOR, Constants.TARGET_STORE_CONFIRM.value))).click()
                self.target_logger.info('Store selected')
                return
            except (NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException):
                self.target_logger.info('One of the elements not yet available.. retrying in 5 seconds')
                time.sleep(5)
                counter += 1
        raise PageTimeoutError

    def initialize_site(self):
        self.target_logger.info('getting webpage')
        self.driver.get(Constants.TARGET.value)

    def find_ps5_page(self):
        """
        navigate to item page
        """
        search = self.driver.find_element_by_id('search')
        self.target_logger.info('Searching for item')
        search.send_keys(Constants.ITEM.value)
        search.send_keys(Keys.RETURN)
        time.sleep(10)
        WebDriverWait(self.driver, 20).until(
            Ec.element_to_be_clickable((By.CSS_SELECTOR, Constants.TARGET_PS5_MAIN.value))).click()
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

    def cycle_stores(self) -> bool:
        zip_codes = [20190, 22202, 23457]
        for code in zip_codes:
            self.select_store(code)
            self.driver.back()
            self.find_ps5_page()
            in_stock = self.get_status()
            if in_stock:
                return True
        return False

    def select_store(self, zip_code):
        self.best_logger.info('opening store drop-down menu')
        time.sleep(3)
        try:
            WebDriverWait(self.driver, 20).until(
                Ec.element_to_be_clickable((By.LINK_TEXT, Constants.BB_STORE_DD.value))).click()
        except NoSuchElementException:
            WebDriverWait(self.driver, 20).until(
                Ec.element_to_be_clickable((By.ID, Constants.BB_STORE_DD_ALT.value))).click()
        zip_search = self.driver.find_element_by_css_selector(Constants.BB_STORE_SELECT.value)
        zip_search.send_keys(zip_code)
        zip_search.send_keys(Keys.RETURN)
        try:
            self.driver.find_element_by_css_selector(Constants.BB_STERLING.value).click()
        except NoSuchElementException:
            self.best_logger.info('Correct store already selected')

    def initialize_site(self):
        self.best_logger.debug('Getting best buy web page')
        self.driver.get(Constants.BB.value)
        try:
            self.driver.find_element_by_xpath(Constants.BB_POPUP.value).click()
            self.best_logger.info('Disabling pop-up window')
        except NoSuchElementException:
            self.best_logger.debug('No popup window detected')

    def find_ps5_page(self):
        search = self.driver.find_element_by_id('gh-search-input')
        self.best_logger.info('Searching for item')
        search.send_keys(Constants.BB_ITEM.value)
        time.sleep(2)
        search.send_keys(Keys.RETURN)

    def get_status(self) -> bool:
        in_stock = False
        status = self.driver.find_element_by_css_selector(Constants.BB_STATUS.value)
        if status.text.lower() != Constants.BB_OOS.value:
            in_stock = True
        return in_stock
