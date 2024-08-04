from datetime import datetime

from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from data_access.database import Base

class ProductPrice(Base):
    __tablename__ = 'product_price'

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String, default='MKD')  # Default currency MKD for Macedonian Denar
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    product = relationship("Product", back_populates="prices")

    def __repr__(self):
        return (f"<ProductPrice(id={self.id}, product_id={self.product_id}, price={self.price}, "
                f"currency={self.currency}, timestamp={self.timestamp.isoformat()})>")

    def serialize(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "price": self.price,
            "currency": self.currency,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
