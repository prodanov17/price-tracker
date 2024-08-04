# create_tables.py
from data_access.database import engine, Base
from data_access.models.website import Website
from data_access.models.product import Product
from data_access.models.product_price import ProductPrice

def main():
    # Create tables
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    main()
