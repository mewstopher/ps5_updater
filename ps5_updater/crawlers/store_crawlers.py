from selenium.webdriver.support import expected_conditions as Ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from ps5_updater.crawlers import Crawler
from decouple import config
from enum import Enum


class Constants(Enum):
    DELAY = 10
    TARGET = 'https://www.target.com'
    TARGET_OOS = 'out of stock'
    ITEM = 'playstation 5'
    TARGET_STORE_SELECT = 'storeId-utilityNavBtn'
    TARGET_AREA_SELECT = 'zipOrCityState'
    TARGET_STORE_CONFIRM = '/html/body/div[9]/div/div/div/div/div[3]/div[2]/div[1]/button'
    TARGET_PS5_MAIN = '//*[@id="mainContainer"]/div[3]/div/a/div[2]/h2/span/span'
    TARGET_STOCK_XPATH = '//*[@id="viewport"]/div[4]/div/div[2]/div[3]/div[1]/div/div/div'


class TargetCrawler(Crawler):
    driver = Crawler.get_driver()

    def select_store(self):
        """
        select my area code
        """
        WebDriverWait(self.driver, Constants.DELAY.value).until(Ec.element_to_be_clickable(
            (By.ID, Constants.TARGET_STORE_SELECT.value))).click()
        self.driver.find_element_by_id(Constants.TARGET_STORE_SELECT.value).click()
        store_zip = self.driver.find_element_by_id(Constants.TARGET_AREA_SELECT.value)
        store_zip.send_keys(config('AREA_CODE'))
        store_zip.send_keys(Keys.RETURN)
        WebDriverWait(self.driver, 20).until(Ec.element_to_be_clickable(
            (By.XPATH, Constants.TARGET_STORE_CONFIRM.value))).click()

    def find_ps5_page(self):
        """
        navigate to item page
        """
        self.driver.get(Constants.TARGET.value)
        search = self.driver.find_element_by_id('search')
        search.send_keys(Constants.ITEM.value)
        search.send_keys(Keys.RETURN)
        self.select_area()
        WebDriverWait(self.driver, 20).until(
            Ec.element_to_be_clickable((By.XPATH, Constants.TARGET_PS5_MAIN.value))).click()
        self.driver.find_element_by_link_text('PlayStation 5 Console').click()

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
        status = self.driver.find_element_by_xpath(Constants.TARGET_STOCK_XPATH.value)
        if status.lower() != Constants.TARGET_OOS.value:
            in_stock = True
        return in_stock
