import sys
import json

from scrapers.ananas_scraper import AnanasScraper
from scrapers.anhoch_scraper import AnhochScraper
from scrapers.malena_scraper import MalenaScraper
from scrapers.nolimit_scraper import NoLimitScraper
from scrapers.setec_scraper import SetecScraper
from utils.logger import Logger


def get_scraper_for_website(website_name: str):
    # Map website names to their respective scraper classes
    scrapers = {
        "setec": SetecScraper,
        "anhoch": AnhochScraper,
        "ananas": AnanasScraper,
        "malena": MalenaScraper,
        "nolimit": NoLimitScraper,
    }
    return scrapers.get(website_name.lower())


def main():
    if len(sys.argv) < 3:
        print("Usage: python main.py <website_name> <product_name> <scrape_type> [url]")
        sys.exit(1)

    website_name = sys.argv[1]
    product_name = sys.argv[2]
    scrape_type = sys.argv[3]  # "scrape" or "rescrape"

    # Optional URL argument for rescrape
    url = sys.argv[4] if len(sys.argv) > 4 else None

    scraper_class = get_scraper_for_website(website_name)

    log = Logger()

    if not scraper_class:
        log.warn(f"No scraper found for website: {website_name}")
        sys.exit(1)

    scraper = scraper_class()

    if scrape_type == "scrape":
        results = scraper.scrape(product_name)
        log.info(f"Scraping results for {product_name}")
    elif scrape_type == "rescrape":
        if not url:
            log.warn("URL must be provided for rescrape.")
            sys.exit(1)
        results = scraper.rescrape(url)
        log.info(f"Scraping results for {product_name}")
    else:
        log.warn(f"Unknown scrape type {scrape_type}")
        sys.exit(1)

    validated_results = []

    for result in results:
        if result.get('name') is not None and len(result.get('name')) > 0:
            if result.get('price') is not None and len(result.get('price')) > 0:
                validated_results.append(result)

    print(json.dumps(validated_results, indent=2))


if __name__ == "__main__":
    main()
