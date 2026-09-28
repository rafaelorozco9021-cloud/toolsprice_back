from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any
import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright


class BaseScraper(ABC):
    """Interfaz común para scrapers de tiendas."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def search(self, query: str) -> List[Dict[str, Any]]:
        """Buscar productos por query."""
        pass

    @abstractmethod
    async def get_product_details(self, url: str) -> Dict[str, Any]:
        """Obtener detalles completos de un producto."""
        pass

    def normalize_product(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizar datos al modelo común."""
        return {
            "nombre": raw_data.get("nombre", ""),
            "categoria": raw_data.get("categoria", ""),
            "precio": float(raw_data.get("precio", 0)),
            "moneda": raw_data.get("moneda", "MXN"),
            "unidad_medida": raw_data.get("unidad_medida", "unidad"),
            "marca": raw_data.get("marca", ""),
            "caracteristicas": raw_data.get("caracteristicas", {}),
            "url_producto": raw_data.get("url_producto", ""),
            "imagen_url": raw_data.get("imagen_url", ""),
            "tienda": self.name,
            "disponibilidad": raw_data.get("disponibilidad", True),
            "fecha_actualizacion": datetime.utcnow(),
        }


class AsyncScraperMixin:
    """Mixin para scraping asíncrono con HTTPX."""

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "es-MX,es;q=0.9",
        }

    async def fetch_html(self, url: str, timeout: int = 30) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, timeout=timeout)
            response.raise_for_status()
            return response.text


class PlaywrightScraper(ABC):
    """Base para sitios que requieren JavaScript."""

    async def fetch_with_playwright(self, url: str, timeout: int = 30000) -> str:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle")
            content = await page.content()
            await browser.close()
            return content