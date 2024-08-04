from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from data_access.database import Base
from data_access.models.product import Product

class Website(Base):
    __tablename__ = 'website'

    id = Column(Integer, primary_key=True, index=True)
    display_name = Column(String, nullable=False)
    enabled = Column(Boolean, default=True)  # 1 for enabled, 0 for disabled
    url = Column(String, nullable=False)
    scraper_name = Column(String, nullable=False)
    search_url = Column(String, nullable=False)

    products = relationship(Product, back_populates="website")

    def __init__(self, display_name, enabled, url, scraper_name, search_url, **kw):
        super().__init__(**kw)
        self.display_name = display_name
        self.enabled = enabled
        self.url = url
        self.scraper_name = scraper_name
        self.search_url = search_url


    def __repr__(self):
        return f"<Website(id={self.id}, display_name={self.display_name}, url={self.url})>"

    def serialize(self):
        return {
            'id': self.id,
            'display_name': self.display_name,
            'enabled': self.enabled,
            'url': self.url,
            'scraper_name': self.scraper_name,
            'search_url': self.search_url
        }