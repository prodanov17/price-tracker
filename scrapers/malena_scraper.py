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

SCRAPE_URL = "https://malenasupplements.mk/?product_cat=0&s="
BASE_URL = "https://malenasupplements.mk"


class MalenaScraper(BaseScraper):
    def __init__(self) -> None:
        super().__init__()
        self.base_url = BASE_URL
        self.search_url = SCRAPE_URL
        self.enabled = True
        self.log = Logger()

    def scrape(self, name: str) -> List[Dict]:
        # Construct the search URL
        search_url = self.search_url + urllib.parse.quote(name) + "&post_type=product"

        # Setup Selenium WebDriver
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(options=chrome_options)

        driver.implicitly_wait(2)

        # Fetch search results page
        driver.get(search_url)
        driver.page_source.encode('utf-8')
        products = []

        try:
            # Locate the product items
            items = driver.find_elements(By.CSS_SELECTOR, "li.product")

            for item in items:
                try:
                    # Extract product details
                    name_element = item.find_element(By.CSS_SELECTOR, ".woocommerce-loop-product__title a")
                    display_name = name_element.text if name_element else ""

                    url_element = item.find_element(By.CSS_SELECTOR, "a.woocommerce-loop-product__link")
                    url = url_element.get_attribute("href") if url_element else ""

                    price_element = item.find_elements(By.CSS_SELECTOR, ".woocommerce-Price-amount bdi")
                    price = price_element[-1].text if price_element else ""

                    image_url = item.find_element(By.CSS_SELECTOR, "img").get_attribute("src")

                    # Check for in-stock status
                    in_stock = True

                    # Clean price
                    cleaned_price = re.sub(r'[^\d,]', '', price)  # Remove non-numeric characters except commas
                    cleaned_price = cleaned_price.rstrip('.')

                    # Collect product details
                    product = {
                        'name': display_name,
                        'search_name': name,
                        'url': url,
                        'image_url': image_url,
                        'price': cleaned_price,
                        'currency': 'MKD',  # Macedonian Denar
                        'in_stock': in_stock
                    }
                    products.append(product)
                except Exception as e:
                    # print(f"Error processing item: {e}")
                    self.log.error(f"Error processing item: {name} at Malena {e.__str__()}")
                    continue
        finally:
            driver.quit()

        return products

    def rescrape(self, url) -> Dict:
        return {}

    def clean_price(self, price):
        price = re.sub(r'[^\d,.]', '', price)
        price = price.rstrip('.')
        return price
