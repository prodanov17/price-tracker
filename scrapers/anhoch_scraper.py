import re
from typing import Dict, List

from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from base_scraper import BaseScraper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import urllib.parse
import json

from utils.logger import Logger

SCRAPE_URL = "https://www.anhoch.com/products?query="
BASE_URL = "https://anhoch.com"


class AnhochScraper(BaseScraper):
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

        driver.implicitly_wait(2)

        # Fetch search results page
        driver.get(search_url)
        products = []

        try:

            elements = driver.find_elements(By.CLASS_NAME, "product-card")

            for element in elements:
                try:
                    name_element = element.find_element(By.CSS_SELECTOR, ".product-name")

                    display_name = driver.execute_script("return arguments[0].innerText;",
                                                         name_element.find_element(By.TAG_NAME,
                                                                                   "h6")) if name_element else ""

                    # if name.lower() not in name_element.text.lower():
                    #     continue

                    # display_name = name_element.find_element(By.CSS_SELECTOR, "h6").text
                    url = name_element.get_attribute("href")
                    price_element = element.find_element(By.CSS_SELECTOR, ".product-card-bottom .product-price")

                    image = element.find_element(By.CSS_SELECTOR, ".product-image img")
                    image_url = image.get_attribute("src")

                    price = driver.execute_script("return arguments[0].innerText;", price_element) if price_element else ""

                    lager_element = element.find_elements(By.CSS_SELECTOR, ".product-card-top .product-badge > li")
                    in_stock = False if len(lager_element) > 0 else True

                    cleaned_price = re.sub(r'[^\d,.]', '', price)  # Remove non-numeric characters except commas
                    cleaned_price = cleaned_price.rstrip('.')
                except Exception as e:
                    self.log.error(e.__str__() + " scraping " + name)
                    continue

            # Collect product details
                product = {
                    'name': display_name,
                    'search_name': name,
                    'url': url,
                    'image_url': image_url,
                    'price': cleaned_price,
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
            # name_element = driver.find_element(By.CSS_SELECTOR, "#title-page")
            price_element = driver.find_element(By.CSS_SELECTOR, ".product-price")

            price = self.clean_price(price_element.text)

            # Check stock status
            try:
                in_stock_element = driver.find_element(By.CSS_SELECTOR, ".in-stock")
                in_stock = True if in_stock_element else False
            except:
                in_stock = False

            product = {
                'url': url,
                'price': price,
                'currency': 'MKD',
                'in_stock': in_stock,
                'source': url
            }
        except Exception as e:
            self.log.error(e.__str__() + " at " + url)
        finally:
            driver.quit()

        return product

    def clean_price(self, price):
        price = re.sub(r'[^\d,.]', '', price)
        price = price.rstrip('.')
        return price