import re
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

from app.scrapers.base_scraper import BaseScraper, AsyncScraperMixin


CATEGORIA_MATERIALES = "https://www.homecenter.com.co/homecenter-co/category/cat5510023/materiales-de-construccion/"
# subcategorias por tipo de presupuesto - todas las categorías activas
CATEGORIA_CONSTRUCCION = CATEGORIA_MATERIALES
CATEGORIA_SOLDADURA = "https://www.homecenter.com.co/homecenter-co/category/cat1670263/adhesivos-soldaduras-y-teflones/"
CATEGORIA_PINTURA = "https://www.homecenter.com.co/homecenter-co/category/cat1680181/pintura-para-interior/"
CATEGORIA_PLOMERIA = "https://www.homecenter.com.co/homecenter-co/category/cat10796/plomeria/"
CATEGORIA_HERRAMIENTAS = "https://www.homecenter.com.co/homecenter-co/category/cat450028/rodillos-brochas-y-accesorios-para-pintar/"
SUBCAT_CEMENTO = "https://www.homecenter.com.co/homecenter-co/category/cat5510024/cementos-concreto-y-morteros/"

CATEGORY_MAP = {
    # Construcción
    "cemento": SUBCAT_CEMENTO,
    "concreto": SUBCAT_CEMENTO,
    "mortero": SUBCAT_CEMENTO,
    "arena": "https://www.homecenter.com.co/homecenter-co/category/cat1420007/arenas-y-gravas/",
    "grava": "https://www.homecenter.com.co/homecenter-co/category/cat1420007/arenas-y-gravas/",
    "ladrillo": "https://www.homecenter.com.co/homecenter-co/category/cat1320005/ladrillos-arcilla-y-bloques-construccion/",
    "bloque": "https://www.homecenter.com.co/homecenter-co/category/cat1320005/ladrillos-arcilla-y-bloques-construccion/",
    "varilla": "https://www.homecenter.com.co/homecenter-co/category/cat10580/varillas-de-hierro-y-acero/",
    "construccion": CATEGORIA_CONSTRUCCION,
    "construcción": CATEGORIA_CONSTRUCCION,
    # Soldadura
    "soldadura": CATEGORIA_SOLDADURA,
    "soldar": CATEGORIA_SOLDADURA,
    "electrodo": CATEGORIA_SOLDADURA,
    "inversor": CATEGORIA_SOLDADURA,
    # Pintura
    "pintura": CATEGORIA_PINTURA,
    "vinilo": CATEGORIA_PINTURA,
    "viniltex": CATEGORIA_PINTURA,
    "esmalte": CATEGORIA_PINTURA,
    # Plomería
    "plomeria": CATEGORIA_PLOMERIA,
    "plomería": CATEGORIA_PLOMERIA,
    "tubo": CATEGORIA_PLOMERIA,
    "tuberia": CATEGORIA_PLOMERIA,
    "griferia": CATEGORIA_PLOMERIA,
    "sanitario": CATEGORIA_PLOMERIA,
    # Herramientas - brocha/rodillo
    "brocha": CATEGORIA_HERRAMIENTAS,
    "rodillo": CATEGORIA_HERRAMIENTAS,
    "pincel": CATEGORIA_HERRAMIENTAS,
    "herramienta": CATEGORIA_HERRAMIENTAS,
    "herramientas": CATEGORIA_HERRAMIENTAS,
    "taladro": "https://www.homecenter.com.co/homecenter-co/category/cat300012/herramientas-y-maquinaria-para-construccion/",
}

# Categorías para búsqueda amplia (cuando query no matchea mapa, se prueban todas)
ALL_CATEGORIES = [CATEGORIA_CONSTRUCCION, CATEGORIA_SOLDADURA, CATEGORIA_PINTURA, CATEGORIA_PLOMERIA, CATEGORIA_HERRAMIENTAS]


class HomecenterScraper(BaseScraper, AsyncScraperMixin):
    """Scraper para Homecenter Colombia (homecenter.com.co).

    Respeta robots.txt: evita golpear /search? en cada request; prefiere
    categorías de 'Materiales de Construcción' y productos individuales.
    Si no hay mapping de categoría, hace fallback a search?Ntt= con rate limiting.
    Precios y características se extraen de ld+json + __NEXT_DATA__.
    """

    @property
    def name(self) -> str:
        return "Homecenter"

    def _headers(self):
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept-Language": "es-CO,es;q=0.9",
            "Accept": "text/html,application/xhtml+xml",
            "Referer": "https://www.homecenter.com.co/",
        }

    async def _fetch(self, url: str, timeout: int = 20) -> str:
        import httpx
        async with httpx.AsyncClient(follow_redirects=True, timeout=timeout, headers=self._headers()) as c:
            r = await c.get(url)
            r.raise_for_status()
            # rate limiting amable
            await asyncio.sleep(0.8)
            return r.text

    def _parse_ldjson_search(self, html: str, categoria_hint: str = "Materiales de Construcción") -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html, "html.parser")
        # 1) Intentar extraer de __NEXT_DATA__ searchData.results (búsqueda por texto Ntt) — más preciso para "tubo pvc"
        products: List[Dict[str, Any]] = []
        nxt = soup.find("script", id="__NEXT_DATA__")
        if nxt and nxt.string:
            try:
                jdata = json.loads(nxt.string)
                search_data = jdata.get("props", {}).get("pageProps", {}).get("searchProps", {}).get("searchData", {})
                results = search_data.get("results") or []
                if isinstance(results, list) and results:
                    for item in results[:30]:
                        name = item.get("displayName") or item.get("name") or ""
                        brand = item.get("brand") or ""
                        sku = str(item.get("productId") or item.get("skuId") or "")
                        # precio
                        price = 0
                        prices = item.get("prices") or []
                        if prices and isinstance(prices, list):
                            # priceWithoutFormatting es el numérico sin puntos
                            price = prices[0].get("priceWithoutFormatting") or 0
                            if not price:
                                price = float(re.sub(r"[^\d]", "", prices[0].get("price","") or "0") or 0)
                        # imagen
                        media = item.get("media", {})
                        img = ""
                        if media and media.get("id"):
                            img = f"https://media.falabella.com/sodimacCO/{media['id']}/public"
                        elif item.get("mediaUrls"):
                            img = item["mediaUrls"][0] if isinstance(item["mediaUrls"], list) else ""
                        url_prod = f"https://www.homecenter.com.co/homecenter-co/product/{sku}/" if sku else ""
                        # categoría desde merchantCategoryId o hint
                        cats = jdata.get("props", {}).get("pageProps", {}).get("categoryProps", {})
                        cat_name = cats.get("name") if isinstance(cats, dict) else None
                        categoria_final2 = cat_name or categoria_hint
                        products.append(self.normalize_product({
                            "nombre": name,
                            "categoria": categoria_final2,
                            "precio": float(price),
                            "moneda": "COP",
                            "unidad_medida": "unidad",
                            "marca": brand,
                            "caracteristicas": {"sku": sku, "merchantCategoryId": item.get("merchantCategoryId","")},
                            "url_producto": url_prod,
                            "imagen_url": img,
                            "disponibilidad": True,
                        }))
                    if products:
                        return products
            except Exception as e:
                print(f"[Homecenter] NEXT_DATA search parse fail: {e}")

        # 2) Fallback a ld+json WebPage (categorías) — intentar extraer categoría real desde breadcrumb JSON si existe
        breadcrumb_cat = None
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string or "")
                if isinstance(data, dict) and data.get("@type") == "WebPage" and data.get("breadcrumb"):
                    crumbs = data["breadcrumb"].get("itemListElement", [])
                    cats = [c["item"]["name"] for c in crumbs if "item" in c]
                    if cats:
                        breadcrumb_cat = cats[-1] if len(cats) >= 2 else cats[0]
                        break
            except:
                continue
        categoria_final = breadcrumb_cat or categoria_hint

        # 3) Parseo ld+json clásico
        products = []
        for script in soup.find_all("script", type="application/ld+json"):
            txt = script.string or ""
            if not txt.strip():
                continue
            try:
                data = json.loads(txt)
            except:
                continue
            candidates = []
            if isinstance(data, dict) and data.get("@type") == "WebPage":
                offers = data.get("mainEntity", {}).get("offers", {})
                item_offered = offers.get("itemOffered", [])
                candidates = item_offered if isinstance(item_offered, list) else [item_offered]
            elif isinstance(data, dict) and data.get("@type") == "Product":
                candidates = [data]
            elif isinstance(data, list):
                candidates = [d for d in data if d.get("@type") == "Product"]

            for item in candidates:
                if not isinstance(item, dict) or item.get("@type") != "Product":
                    continue
                name = item.get("name") or ""
                brand = (item.get("brand") or {}).get("name", "") if isinstance(item.get("brand"), dict) else str(item.get("brand") or "")
                offers = item.get("offers") or {}
                price_raw = offers.get("price") or "0"
                try:
                    price = float(re.sub(r"[^\d]", "", str(price_raw)) or 0)
                except:
                    price = 0
                availability = offers.get("availability", "")
                disp = "InStock" in str(availability)
                sku = item.get("sku") or ""
                img = item.get("image") or ""
                if isinstance(img, list):
                    img = img[0] if img else ""
                url_prod = offers.get("url") or item.get("url") or f"/homecenter-co/product/{sku}/"
                if url_prod.startswith("/"):
                    url_prod = "https://www.homecenter.com.co" + url_prod
                products.append(self.normalize_product({
                    "nombre": name,
                    "categoria": categoria_final,
                    "precio": price,
                    "moneda": offers.get("priceCurrency") or "COP",
                    "unidad_medida": "saco 50kg" if "50kg" in name else "unidad",
                    "marca": brand,
                    "caracteristicas": {"sku": sku, "availability": availability},
                    "url_producto": url_prod,
                    "imagen_url": img,
                    "disponibilidad": disp,
                }))
        return products

    def _category_for_query(self, query: str) -> str | None:
        q = query.lower()
        for k, url in CATEGORY_MAP.items():
            if k in q:
                return url
        return None

    # Mapeo URL -> label humano para mostrar categoría donde se encontró
    CATEGORY_LABELS = {
        CATEGORIA_CONSTRUCCION: "Construcción",
        SUBCAT_CEMENTO: "Construcción > Cementos",
        "https://www.homecenter.com.co/homecenter-co/category/cat1420007/arenas-y-gravas/": "Construcción > Arenas y Gravas",
        "https://www.homecenter.com.co/homecenter-co/category/cat1320005/ladrillos-arcilla-y-bloques-construccion/": "Construcción > Ladrillos",
        "https://www.homecenter.com.co/homecenter-co/category/cat10580/varillas-de-hierro-y-acero/": "Construcción > Varillas",
        CATEGORIA_SOLDADURA: "Soldadura",
        CATEGORIA_PINTURA: "Pintura",
        CATEGORIA_PLOMERIA: "Plomería",
        CATEGORIA_HERRAMIENTAS: "Herramientas",
        "https://www.homecenter.com.co/homecenter-co/category/cat300012/herramientas-y-maquinaria-para-construccion/": "Herramientas",
    }

    async def search(self, query: str, categoria: str | None = None) -> List[Dict[str, Any]]:
        query = query.strip()
        if not query:
            return []
        # Siempre buscar en TODAS las categorías para cumplir "busque en todas las categorias"
        # y luego filtrar por query con coincidencia de todos los tokens
        from rapidfuzz import fuzz

        qlow = query.lower()
        tokens = [t for t in re.split(r"\s+", qlow) if t]

        # Prioridad: búsqueda directa por texto (mejor para queries específicas como "tubo pvc") + todas las categorías como respaldo
        urls_with_label = [
            (f"https://www.homecenter.com.co/homecenter-co/search/?Ntt={quote_plus(query)}", "Búsqueda Homecenter"),
            (f"https://www.homecenter.com.co/homecenter-co/search/?text={quote_plus(query)}", "Búsqueda Homecenter"),
        ]
        if categoria and categoria.lower() in ("construccion","soldadura","pintura","plomeria","herramientas"):
            cat_map = {
                "construccion": CATEGORIA_CONSTRUCCION,
                "soldadura": CATEGORIA_SOLDADURA,
                "pintura": CATEGORIA_PINTURA,
                "plomeria": CATEGORIA_PLOMERIA,
                "herramientas": CATEGORIA_HERRAMIENTAS,
            }
            urls_with_label.append((cat_map[categoria.lower()], self.CATEGORY_LABELS.get(cat_map[categoria.lower()], categoria.capitalize())))
        else:
            # búsqueda multicategoría: agregar las 5 categorías como respaldo
            for url in ALL_CATEGORIES:
                label = self.CATEGORY_LABELS.get(url, "General")
                if (url, label) not in urls_with_label:
                    urls_with_label.append((url, label))

        all_products: List[Dict[str, Any]] = []
        seen = set()
        for url, label in urls_with_label:
            try:
                html = await self._fetch(url)
                products = self._parse_ldjson_search(html, categoria_hint=label)
                for p in products:
                    key = p.get("url_producto")
                    if key in seen:
                        continue
                    seen.add(key)
                    text = f"{p['nombre']} {p['marca']} {p['categoria']}".lower()
                    matched = sum(1 for tok in tokens if tok in text)
                    # requerir al menos 1 token exacto; descartar productos sin ningún token (evita "Alambre" para "brocha")
                    if matched == 0:
                        continue
                    score = fuzz.partial_ratio(qlow, text)
                    p["_score"] = score + matched*20
                    all_products.append(p)
            except Exception as e:
                print(f"[Homecenter] search fail {url}: {e}")
                continue

        # ordenar por relevancia (más tokens coincidentes primero) y devolver top 24
        all_products.sort(key=lambda x: x.get("_score", 0), reverse=True)
        for p in all_products:
            p.pop("_score", None)
        return all_products[:24]

    async def search_all_categories(self, query: str) -> List[Dict[str, Any]]:
        """Busca en las 5 categorías y agrega resultados para cobertura total."""
        tasks = [self.search(query, cat) for cat in ["construccion", "soldadura", "pintura", "plomeria", "herramientas"]]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        merged: List[Dict[str, Any]] = []
        seen = set()
        for res in results:
            if isinstance(res, list):
                for p in res:
                    key = p.get("url_producto")
                    if key not in seen:
                        seen.add(key)
                        merged.append(p)
        # también búsqueda directa sin categoría
        direct = await self.search(query)
        for p in direct:
            if p.get("url_producto") not in seen:
                merged.append(p)
        return merged[:24]

    async def get_product_details(self, url: str) -> Dict[str, Any]:
        try:
            html = await self._fetch(url)
            soup = BeautifulSoup(html, "html.parser")
            # ld+json Product
            name = ""
            price = 0
            marca = ""
            imagen = ""
            categoria = "Materiales de Construcción"
            disponibilidad = True
            caracteristicas: Dict[str, Any] = {}
            moneda = "COP"

            for script in soup.find_all("script", type="application/ld+json"):
                txt = script.string or ""
                try:
                    data = json.loads(txt)
                except:
                    continue
                # could be list or dict
                objs = data if isinstance(data, list) else [data]
                for obj in objs:
                    if obj.get("@type") == "product" or obj.get("@type") == "Product":
                        name = obj.get("name") or name
                        marca = (obj.get("brand") or {}).get("name", marca) if isinstance(obj.get("brand"), dict) else marca
                        imagen = obj.get("image") or imagen
                        if isinstance(imagen, list):
                            imagen = imagen[0] if imagen else ""
                        offers = obj.get("offers") or {}
                        if isinstance(offers, dict):
                            p = offers.get("price")
                            if p:
                                try:
                                    price = float(re.sub(r"[^\d]", "", str(p)) or 0)
                                except:
                                    pass
                                moneda = offers.get("priceCurrency", moneda)
                            disponibilidad = "InStock" in str(offers.get("availability", ""))
                    if obj.get("@type") == "WebPage" and obj.get("breadcrumb"):
                        try:
                            crumbs = obj["breadcrumb"]["itemListElement"]
                            # categoria es el segundo nivel Materiales de Construcción + sub
                            cats = [c["item"]["name"] for c in crumbs if "item" in c]
                            if cats:
                                categoria = " > ".join(cats[1:3])  # ej. Materiales de Construcción > Cementos
                        except:
                            pass

            # __NEXT_DATA__ para atributos detallados
            nxt = soup.find("script", id="__NEXT_DATA__")
            if nxt and nxt.string:
                try:
                    jdata = json.loads(nxt.string)
                    jstr = json.dumps(jdata)
                    # buscar productProps
                    props = jdata.get("props", {}).get("pageProps", {})
                    # variantes: productProps.result.attributes
                    prod = props.get("productProps", {}).get("result") or props.get("initialData", {}).get("product") or {}
                    attrs = prod.get("attributes") or prod.get("specifications") or []
                    # attributes es lista de {name, values, group} - solo nos interesan visibles
                    for a in attrs if isinstance(attrs, list) else []:
                        if a.get("group") != "AttributesSortedMap":
                            continue
                        n = a.get("name")
                        vals = a.get("values") or a.get("value") or []
                        if isinstance(vals, list):
                            vals = ", ".join([str(v) for v in vals])
                        if n and n not in ("provider_code","provider_id","backoffice_status","provider_name","is_multi_product","is_domestic","is_marketplace_product"):
                            caracteristicas[n] = vals
                    # fallback regex si sigue vacío (solo AttributesSortedMap)
                    if not caracteristicas:
                        for m in re.finditer(r'"name"\s*:\s*"([^"]+)"\s*,\s*"values"\s*:\s*\[([^\]]+)\].*?"group"\s*:\s*"AttributesSortedMap"', jstr):
                            n = m.group(1)
                            if n in ("provider_code","provider_id","backoffice_status","provider_name"):
                                continue
                            vals = m.group(2).replace('"','').strip()
                            if n not in caracteristicas:
                                caracteristicas[n] = vals
                    # precio en NEXT_DATA: buscar variants pricing o prices - solo valores numéricos puros
                    if price == 0:
                        try:
                            variants = prod.get("variants") or []
                            for v in variants:
                                for pk in ("price","prices","currentPrice","bestPrice","salePrice"):
                                    if pk in v and v[pk] is not None:
                                        pv = v[pk]
                                        if isinstance(pv, dict):
                                            pv = pv.get("value") or pv.get("price") or pv.get("amount") or 0
                                        # pv debe ser numero o string numerico corto
                                        if isinstance(pv, (int, float)) and pv > 1000:
                                            price = float(pv)
                                            break
                                        if isinstance(pv, str) and pv.strip().isdigit():
                                            price = float(pv)
                                            break
                                if price:
                                    break
                            if price == 0:
                                for pk in ("price","currentPrice","salePrice","bestPrice"):
                                    if pk in prod and prod[pk] is not None:
                                        pv = prod[pk]
                                        if isinstance(pv, dict):
                                            pv = pv.get("value") or pv.get("amount") or 0
                                        if isinstance(pv, (int, float)) and pv > 1000:
                                            price = float(pv)
                                            break
                                        if isinstance(pv, str) and pv.strip().replace(".","",1).isdigit():
                                            price = float(re.sub(r"[^\d]", "", pv))
                                            break
                            if price == 0:
                                m = re.search(r'"price"\s*:\s*"?(\d{4,6})"?', jstr)
                                if m:
                                    price = float(m.group(1))
                        except:
                            pass
                except Exception as e:
                    print(f"[Homecenter] detail NEXT_DATA parse fail: {e}")

            # fallback precio desde HTML si sigue 0 (buscar "$ 29.900" o meta)
            if price == 0:
                # meta product:price:amount
                meta = soup.find("meta", property="product:price:amount")
                if meta and meta.get("content"):
                    try:
                        price = float(re.sub(r"[^\d]", "", meta["content"]))
                    except:
                        pass
                if price == 0:
                    # buscar texto con $ 29.900
                    import re as _re
                    for txt in soup.stripped_strings:
                        if _re.search(r"\$\s*\d+[\.\d]*", txt):
                            m = _re.search(r"(\d[\d\.\,]+)", txt)
                            if m:
                                try:
                                    price = float(_re.sub(r"[^\d]", "", m.group(1)))
                                    if price > 1000:
                                        break
                                except:
                                    continue
            # fallbacks nombre/imagen
            if not name:
                h1 = soup.find("h1")
                if h1:
                    name = h1.get_text(strip=True)
            if not imagen:
                img = soup.find("img")
                if img and img.get("src"):
                    imagen = img["src"]

            unidad_medida = caracteristicas.get("Contenido") or caracteristicas.get("Presentación") or ("saco 50kg" if "50kg" in name else "unidad")

            return self.normalize_product({
                "nombre": name,
                "categoria": categoria,
                "precio": float(price) if price else 0,
                "moneda": moneda,
                "unidad_medida": unidad_medida,
                "marca": marca,
                "caracteristicas": caracteristicas,
                "url_producto": url if url.startswith("http") else "https://www.homecenter.com.co" + url,
                "imagen_url": imagen if imagen.startswith("http") else ("https:" + imagen if imagen.startswith("//") else imagen),
                "disponibilidad": disponibilidad,
            })
        except Exception as e:
            print(f"[Homecenter] get_product_details fail {url}: {e}")
            return {}
