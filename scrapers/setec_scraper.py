from typing import Dict, List

from base_scraper import BaseScraper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import urllib.parse
import json

from utils.logger import Logger

SCRAPE_URL = "https://setec.mk/index.php?route=product/search&search="
BASE_URL = "https://setec.mk"

class SetecScraper(BaseScraper):
    def __init__(self) -> None:
        super().__init__()
        self.base_url = BASE_URL
        self.search_url = SCRAPE_URL
        self.enabled = True
        self.log = Logger()

    def scrape(self, name) -> List[Dict]:
        # Construct the search URL
        search_url = self.search_url + urllib.parse.quote(name)

        # Setup Selenium WebDriver
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(options=chrome_options)

        driver.implicitly_wait(0.5)

        # Fetch search results page
        driver.get(search_url)
        products = []

        try:
            elements = driver.find_elements(By.CLASS_NAME, "product")
            for element in elements:
                name_element = element.find_element(By.CSS_SELECTOR, ".name a")


                if name.lower() not in name_element.text.lower():
                    continue

                url = name_element.get_attribute("href")
                price_element = element.find_element(By.CSS_SELECTOR, ".price .price-new-new")

                image_element = element.find_element(By.CSS_SELECTOR, ".image img")
                image_url = image_element.get_attribute("src")

                lager_element = element.find_element(By.CSS_SELECTOR, ".lager")
                in_stock = lager_element.find_elements(By.CSS_SELECTOR, ".ima_zaliha")
                out_of_stock = lager_element.find_elements(By.CSS_SELECTOR, ".nema-zaliha")

                # Check stock status
                in_stock_status = bool(in_stock)
                out_of_stock_status = bool(out_of_stock)
                in_stock = in_stock_status and not out_of_stock_status


                # Collect product details
                product = {
                    'name': name_element.text,
                    'search_name': name,
                    'url': url,
                    'image_url': image_url,
                    'price': price_element.text.split(" ")[0],
                    'currency': 'MKD',  # Assuming Macedonian Denar
                    'in_stock': in_stock
                }
                products.append(product)
        finally:
            driver.quit()

        return products

    def rescrape(self, url) -> Dict:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(options=chrome_options)

        driver.get(url)
        product = {}

        try:
            name_element = driver.find_element(By.CSS_SELECTOR, "#title-page")
            price_element = driver.find_element(By.CSS_SELECTOR, "#price-special")

            lager_element = driver.find_element(By.CSS_SELECTOR, ".description > img")
            in_stock = lager_element.get_attribute("src").endswith("yes.png")

            product = {
                'name': name_element.text,
                'url': url,
                'price': price_element.text.split(" ")[0],
                'currency': 'MKD',
                'in_stock': in_stock,
                'source': url
            }
        except Exception as e:
            self.log.error(e.__str__() + " at " + url)
            # print(e)
            # print(url)

        finally:
            driver.quit()

        return product

