from data_access.database import SessionLocal
from data_access.models.product import Product
from data_access.models.product_price import ProductPrice
from repositories.product_repository import ProductRepository
from repositories.website_repository import WebsiteRepository


class ProductService:
    def __init__(self):
        self.product_repo = ProductRepository()
        self.website_repo = WebsiteRepository()

    def add_product(self, name, website_name, search_name, url, price, in_stock, image_url):
        # Create a new session
        try:
            # Start a transaction
            with SessionLocal() as session:
                website = self.website_repo.get_website_by_name(website_name)

                # Ensure the website exists
                if not website:
                    raise ValueError(f"Website '{website_name}' not found")

                product = Product(name=name, search_name=search_name, website_id=website.id, url=url, in_stock=in_stock,
                                  image_url=image_url)

                existing_product = self.product_repo.get_product_by_display_name_and_url(name, url)
                print(existing_product)
                if existing_product is None or len(existing_product) == 0:
                    product_result = self.product_repo.add_product(product)
                else:
                    product_result = self.product_repo.get_product_by_display_name(name)

                self.add_price(product_result.id, price)

            # Commit the transaction
            session.commit()
            return product_result
        except Exception as e:
            # Rollback in case of error
            session.rollback()
            raise e
        finally:
            # Close the session
            session.close()

    def add_price(self, product_id, price):
        product_price = ProductPrice(price=self.parse_price(price), product_id=product_id)

        # Add product and product price to the database
        self.product_repo.add_product_price(product_price)

    def update_product(self, id, data):
        return self.product_repo.update_product(id, **data)

    def get_unique_search_products(self):
        return self.product_repo.get_unique_search_products()

    def get_all_products(self):
        return self.product_repo.get_all_products()

    def get_product_by_name(self, name):
        # Create a new session
        return self.product_repo.get_product_by_name(name)

    # Add other business logic methods as needed

    def get_product_by_display_name(self, name):
        return self.product_repo.get_product_by_display_name(name)

    def get_product_by_display_name_and_url(self, name, url):
        return self.product_repo.get_product_by_display_name_and_url(name, url)

    def parse_price(self, price_str):
        # Remove any whitespace
        price_str = price_str.strip()

        # Detect and handle different formats
        if ',' in price_str and '.' in price_str:
            # If both comma and period are present, assume the format with thousand separator
            if price_str.index(',') > price_str.index('.'):
                # Format: 49.900,00 (period as thousand separator, comma as decimal separator)
                price_str = price_str.replace('.', '').replace(',', '.')
            else:
                # Format: 49,000.00 (comma as thousand separator, period as decimal separator)
                price_str = price_str.replace(',', '')
        elif ',' in price_str:
            # Format: 49,000 or 49,000.00 (comma as thousand separator or decimal separator)
            parts = price_str.split(',')
            if len(parts) == 2 and len(parts[1]) == 2:
                # Likely a decimal part, keep comma as decimal separator
                price_str = price_str.replace(',', '.')
            else:
                # Only thousand separator
                price_str = price_str.replace(',', '')
        elif '.' in price_str:
            # Format: 49.000 or 49.000.00 (period as thousand separator or decimal separator)
            parts = price_str.split('.')
            if len(parts) == 2 and len(parts[1]) == 2:
                # Likely a decimal part, keep period as decimal separator
                price_str = price_str.replace('.', '')
            else:
                # Only thousand separator
                price_str = price_str.replace('.', '')

        # Convert to float
        try:
            return float(price_str)
        except ValueError:
            return None