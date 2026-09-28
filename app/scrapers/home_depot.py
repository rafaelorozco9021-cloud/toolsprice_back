from app.schemas.product import ProductSchema
from app.scrapers.base_scraper import BaseScraper


class StoreScraper(BaseScraper):
    @property
    def name(self) -> str:
        return "Home Depot"

    async def search(self, query: str):
        raise NotImplementedError

    async def get_product_details(self, url: str):
        raise NotImplementedError
