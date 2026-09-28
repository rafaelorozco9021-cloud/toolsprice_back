from app.scrapers.base_scraper import BaseScraper, AsyncScraperMixin
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import asyncio
import re
from rapidfuzz import fuzz


class HomeDepotScraper(BaseScraper, AsyncScraperMixin):
    """Scraper para Home Depot."""

    @property
    def name(self) -> str:
        return "Home Depot"

    def _mock_search(self, query: str) -> List[Dict[str, Any]]:
        from app.services.seed import MOCK_PRODUCTS
        q = query.lower()
        scored = []
        for p in MOCK_PRODUCTS:
            if p["tienda"] != self.name:
                continue
            score = fuzz.partial_ratio(q, (p["nombre"] + " " + p["categoria"] + " " + p["marca"]).lower())
            # also boost if query is substring
            if q in p["nombre"].lower() or q in p["categoria"].lower():
                score += 20
            if score > 50:
                scored.append((score, self.normalize_product(p)))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [x[1] for x in scored[:10]] or [self.normalize_product(p) for p in MOCK_PRODUCTS if p["tienda"] == self.name][:3]

    async def search(self, query: str) -> List[Dict[str, Any]]:
        """Busca productos en Home Depot."""
        base_url = "https://www.homedepot.mx/s/"
        search_url = f"{base_url}?text={query.replace(' ', '+')}"

        try:
            html = await self.fetch_html(search_url, timeout=5)
            soup = BeautifulSoup(html, "html.parser")
            products = []
            for card in soup.select("div.product-grid-item"):
                title_elem = card.select_one("a.product-title")
                price_elem = card.select_one("span.price-current")
                img_elem = card.select_one("img.product-image")
                if title_elem and price_elem:
                    title = title_elem.get_text(strip=True)
                    price_str = price_elem.get_text(strip=True)
                    price = float(re.sub(r"[^\d.]", "", price_str)) if price_str else 0
                    products.append(self.normalize_product({
                        "nombre": title,
                        "precio": price,
                        "imagen_url": img_elem.get("src", "") if img_elem else "",
                        "url_producto": "https://www.homedepot.mx" + title_elem.get("href", ""),
                    }))
            if products:
                return products[:20]
        except Exception:
            pass
        return self._mock_search(query)

    async def get_product_details(self, url: str) -> Dict[str, Any]:
        """Obtiene detalles de un producto específico."""
        try:
            html = await self.fetch_html(url, timeout=30)
            soup = BeautifulSoup(html, "html.parser")

            title = soup.select_one("h1.product-title").get_text(strip=True) if soup.select_one("h1.product-title") else ""
            price_elem = soup.select_one("span.price-current")
            price = float(re.sub(r"[^\d.]", "", price_elem.get_text(strip=True))) if price_elem else 0
            brand = soup.select_one("span.brand-name").get_text(strip=True) if soup.select_one("span.brand-name") else ""
            image = soup.select_one("img.product-main-image")
            image_url = image.get("src", "") if image else ""

            specs = {}
            for row in soup.select("tr.product-specs-row"):
                key = row.select_one("td.spec-key").get_text(strip=True) if row.select_one("td.spec-key") else ""
                value = row.select_one("td.spec-value").get_text(strip=True) if row.select_one("td.spec-value") else ""
                if key:
                    specs[key] = value

            return self.normalize_product({
                "nombre": title,
                "precio": price,
                "marca": brand,
                "imagen_url": image_url,
                "caracteristicas": specs,
                "url_producto": url,
                "disponibilidad": bool(soup.select_one("span.in-stock")),
            })
        except Exception:
            return {}


class SodimacScraper(BaseScraper, AsyncScraperMixin):
    """Scraper para Sodimac."""

    @property
    def name(self) -> str:
        return "Sodimac"

    def _mock_search(self, query: str) -> List[Dict[str, Any]]:
        from app.services.seed import MOCK_PRODUCTS
        q = query.lower()
        scored = []
        for p in MOCK_PRODUCTS:
            if p["tienda"] != self.name:
                continue
            score = fuzz.partial_ratio(q, (p["nombre"] + " " + p["categoria"] + " " + p["marca"]).lower())
            if q in p["nombre"].lower() or q in p["categoria"].lower():
                score += 20
            if score > 50:
                scored.append((score, self.normalize_product(p)))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [x[1] for x in scored[:10]] or [self.normalize_product(p) for p in MOCK_PRODUCTS if p["tienda"] == self.name][:3]

    async def search(self, query: str) -> List[Dict[str, Any]]:
        """Busca productos en Sodimac."""
        base_url = "https://www.sodimac.com.mx/s/"
        search_url = f"{base_url}?text={query.replace(' ', '+')}"
        try:
            html = await self.fetch_html(search_url, timeout=5)
            soup = BeautifulSoup(html, "html.parser")
            products = []
            for card in soup.select("div.product-card"):
                title_elem = card.select_one("h3.product-title")
                price_elem = card.select_one("span.price-value")
                img_elem = card.select_one("img.product-image")
                if title_elem and price_elem:
                    title = title_elem.get_text(strip=True)
                    price_str = price_elem.get_text(strip=True)
                    price = float(re.sub(r"[^\d.]", "", price_str)) if price_str else 0
                    products.append(self.normalize_product({
                        "nombre": title,
                        "precio": price,
                        "imagen_url": img_elem.get("src", "") if img_elem else "",
                        "url_producto": "https://www.sodimac.com.mx" + title_elem.get("href", ""),
                    }))
            if products:
                return products[:20]
        except Exception:
            pass
        return self._mock_search(query)

    async def get_product_details(self, url: str) -> Dict[str, Any]:
        """Obtiene detalles de un producto específico."""
        try:
            html = await self.fetch_html(url, timeout=30)
            soup = BeautifulSoup(html, "html.parser")

            title = soup.select_one("h1.product-name").get_text(strip=True) if soup.select_one("h1.product-name") else ""
            price_elem = soup.select_one("span.price-value")
            price = float(re.sub(r"[^\d.]", "", price_elem.get_text(strip=True))) if price_elem else 0

            image = soup.select_one("img.product-main-image")
            image_url = image.get("src", "") if image else ""

            return self.normalize_product({
                "nombre": title,
                "precio": price,
                "imagen_url": image_url,
                "url_producto": url,
                "disponibilidad": bool(soup.select_one("span.in-stock")),
            })
        except Exception:
            return {}