from data_access.database import SessionLocal
from data_access.models.product import Product
from data_access.models.website import Website
from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload


class WebsiteRepository:

    def add_website(self, website: Website):
        try:
            with SessionLocal() as session:
                session.add(website)
                session.commit()
                latest_website = session.query(Website).order_by(desc(Website.id)).first()
                return latest_website
        finally:
            session.close()
    def get_all_websites(self):
        try:
            with SessionLocal() as session:
                return session.query(Website).all()
        finally:
            session.close()

    def get_website_by_name(self, name: str):
        try:
            with SessionLocal() as session:
                return session.query(Website).filter_by(scraper_name=name).first()
        finally:
            session.close()

    def get_website_by_id(self, id: int):
        try:
            with SessionLocal() as session:
                return session.query(Website).filter_by(id=id).first()
        finally:
            session.close()


    def get_websites_by_search_name(self, search_name: str):
        try:
            with SessionLocal() as session:
                return session.query(Website).join(Website.products).options(joinedload(Website.products)).filter(Product.search_name == search_name).all()
        finally:
            session.close()


    def update_website(self, id: int, updates: dict):
        website = self.get_website_by_id(id)
        if not website:
            return None
        for key, value in updates.items():
            setattr(website, key, value)
        self.session.commit()
        return website

    def delete_website(self, id: int):
        website = self.get_website_by_id(id)
        if website:
            self.session.delete(website)
            self.session.commit()
            return True
        return False
