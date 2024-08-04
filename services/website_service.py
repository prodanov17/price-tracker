from repositories.website_repository import WebsiteRepository
from data_access.models.website import Website

class WebsiteService:
    def __init__(self, website_repository: WebsiteRepository = None):
        self.website_repo = website_repository or WebsiteRepository()

    def add_website(self, display_name, url, scraper_name, search_url, enabled=True):
        website = Website(
            display_name=display_name,
            url=url,
            scraper_name=scraper_name,
            search_url=search_url,
            enabled=enabled
        )
        return self.website_repo.add_website(website)

    def get_all_websites(self):
        return self.website_repo.get_all_websites()

    def get_website_by_name(self, name):
        return self.website_repo.get_website_by_name(name)

    def get_websites_by_search_name(self, search_name):
        return self.website_repo.get_websites_by_search_name(search_name)

    def get_website_by_id(self, id):
        return self.website_repo.get_website_by_id(id)

    def update_website(self, id, updates):
        return self.website_repo.update_website(id, updates)

    def delete_website(self, id):
        return self.website_repo.delete_website(id)

    # Additional business logic methods can be added as needed
