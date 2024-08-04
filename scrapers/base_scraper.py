from abc import ABC, abstractmethod
import json
from typing import List, Dict

class BaseScraper(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def scrape(self) -> List[Dict]:
        """
        Fetch search results from the website.
        This should return a list of dictionaries, each representing a product found in the search results.
        """
        pass

    @abstractmethod
    def rescrape(self) -> Dict:
        """
        Fetch search results from the website.
        This should return a dictionary representing a product found in the search results.
        :return:
        """
        pass

    def to_json(self, data: List[Dict]) -> str:
        """
        Convert the list of product details to JSON format.
        """
        return json.dumps(data, indent=4)
