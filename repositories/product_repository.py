from data_access.database import SessionLocal
from data_access.models.product import Product
from data_access.models.product_price import ProductPrice
from sqlalchemy.orm import joinedload


class ProductRepository:
    def add_product(self, product: Product):
        with SessionLocal() as session:
            session.add(product)
            session.commit()
            session.refresh(product)

            return product

    def get_product_by_name(self, name):
        with SessionLocal() as session:
            return session.query(Product).filter(Product.search_name == name).options(joinedload(Product.prices)).options(joinedload(Product.website)).all()

    def get_product_by_display_name(self, name):
        with SessionLocal() as session:
            product = session.query(Product).filter(Product.name == name).options(
                joinedload(Product.prices),
                joinedload(Product.website)
            ).first()


            return product

    def get_product_by_display_name_and_url(self, name, url):
        with SessionLocal() as session:
            product = session.query(Product).filter(Product.name == name).filter(Product.url == url).options(
                joinedload(Product.prices),
                joinedload(Product.website)
            ).first()


            return product

    def update_product(self, product_id: int, **kwargs):
        with SessionLocal() as session:
            product = session.query(Product).filter(Product.id == product_id).first()
            if not product:
                return None
            for key, value in kwargs.items():
                if hasattr(product, key):
                    setattr(product, key, value)
            session.commit()
            session.refresh(product)
            return product

    def search_by_filter(self, **kwargs):
        with SessionLocal() as session:
            query = session.query(Product).options(joinedload(Product.prices)).options(joinedload(Product.website))
            for key, value in kwargs.items():
                if hasattr(Product, key):
                    query = query.filter(getattr(Product, key) == value)
            return query.all()
    def add_product_price(self, product_price: ProductPrice):
        with SessionLocal() as session:
            session.add(product_price)
            session.commit()
            session.refresh(product_price)
            return product_price

    def get_all_products(self):
        with SessionLocal() as session:
            return session.query(Product).options(joinedload(Product.prices)).options(joinedload(Product.website)).all()

    def get_unique_search_products(self):
        with SessionLocal() as session:
            return session.query(Product.search_name).distinct().all()
