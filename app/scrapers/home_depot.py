from app.schemas.product import ProductSchema

class StoreScraper(BaseScraper):
    @property
    def name(self) -> str:
        return "Home Depot"

    async def search(self, query: str):
        # Implement scraping logic for Home Depot
        pass

    async def get_product_details(self, url: str):
        # Implement scraping logic for Home Depot
        pass

```