from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from data_access.database import Base
from data_access.models.product_price import ProductPrice
from datetime import datetime

class Product(Base):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True)
    search_name = Column(String, nullable=False)
    name = Column(String, default=search_name)
    website_id = Column(Integer, ForeignKey('website.id'))
    url = Column(String)
    image_url = Column(String, default="https://developers.elementor.com/docs/assets/img/elementor-placeholder-image.png")
    active = Column(Boolean, default=True)
    in_stock = Column(Boolean, default=False)
    last_scraped = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    website = relationship("Website", back_populates="products")
    prices = relationship(ProductPrice, back_populates="product")

    def __init__(self, search_name, name, url, active=True, in_stock=False, last_scraped=None, image_url=None, **kw):
        super().__init__(**kw)
        self.search_name = search_name
        self.name = name
        self.url = url
        self.active = active
        self.in_stock = in_stock
        self.image_url = image_url
        self.last_scraped = last_scraped

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'active': self.active,
            'image_url': self.image_url,
            'search_name': self.search_name,
            'in_stock': self.in_stock,
            'last_scraped': self.last_scraped.isoformat() if self.last_scraped else None,  # Convert datetime to ISO format
            'created_at': self.created_at.isoformat() if self.created_at else None,  # Convert datetime to ISO format
            'website': self.website.serialize() if self.website else None,  # Assuming Website model has a serialize method
            'prices': [price.serialize() for price in self.prices]  # Assuming ProductPrice model has a serialize method
        }

    def flat_serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'active': self.active,
            'search_name': self.search_name,
            'image_url': self.image_url,
            'in_stock': self.in_stock,
            'last_scraped': self.last_scraped.isoformat() if self.last_scraped else None,  # Convert datetime to ISO format
            'created_at': self.created_at.isoformat() if self.created_at else None,  # Convert datetime to ISO format
            'website': self.website.serialize() if self.website else None,  # Assuming Website model has a serialize method
            'price': self.sorted_prices[0].price if self.sorted_prices else None  # Use sorted_prices
        }

    @property
    def sorted_prices(self):
        return sorted(self.prices, key=lambda p: p.timestamp, reverse=True)