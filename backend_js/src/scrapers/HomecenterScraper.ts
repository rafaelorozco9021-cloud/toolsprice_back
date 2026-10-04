import axios from 'axios';
import * as cheerio from 'cheerio';
import { BaseScraper } from './BaseScraper';
import { Product } from '../types/product';
import { cacheGet, cacheSet } from '../services/cache';

export class HomecenterScraper extends BaseScraper {
  readonly name = 'Homecenter';

  private readonly baseUrl = 'https://www.homecenter.com.co';
  private readonly headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'es-CO,es;q=0.9',
  };

  async search(query: string, categoria?: string): Promise<Product[]> {
    const cacheKey = `search:homecenter:${query}:${categoria || 'all'}`;
    const cached = await cacheGet(cacheKey);
    if (cached) return cached;

    const searchUrl = `${this.baseUrl}/homecenter-co/search/?Ntt=${encodeURIComponent(query)}`;
    
    try {
      const { data: html } = await axios.get(searchUrl, { headers: this.headers, timeout: 8000 });
      
      const nextDataMatch = html.match(/<script id="__NEXT_DATA__" type="application\/json">(.*?)<\/script>/);
      if (nextDataMatch && nextDataMatch[1]) {
        const json = JSON.parse(nextDataMatch[1]);
        const results = json?.props?.pageProps?.searchProps?.searchData?.results || [];
        
        if (results.length > 0) {
          const products = results.slice(0, 24).map((item: any) => {
            const prices = item.prices || [];
            const price = prices[0]?.priceWithoutFormatting || 0;
            const media = item.media || {};
            const img = media.id ? `https://media.falabella.com/sodimacCO/${media.id}/public` : (item.mediaUrls?.[0] || '');
            const sku = item.productId || item.skuId || '';

            return this.normalizeProduct({
              nombre: item.displayName || item.name,
              categoria: 'Materiales de Construcción',
              precio: price,
              moneda: 'COP',
              marca: item.brand,
              urlProducto: `${this.baseUrl}/homecenter-co/product/${sku}/`,
              imagenUrl: img,
              caracteristicas: { sku },
            });
          });
          
          await cacheSet(cacheKey, products, 3600); // Cache por 1 hora
          return products;
        }
      }

      const $ = cheerio.load(html);
      const products: Product[] = [];
      
      $('div.product-card').each((_, el) => {
        const title = $(el).find('h3').text().trim();
        const priceText = $(el).find('.price').text().trim();
        const price = parseFloat(priceText.replace(/[^\d]/g, '')) || 0;
        const link = $(el).find('a').attr('href');
        const img = $(el).find('img').attr('src');

        if (title && price) {
          products.push(this.normalizeProduct({
            nombre: title,
            precio: price,
            urlProducto: link ? (link.startsWith('http') ? link : `${this.baseUrl}${link}`) : '',
            imagenUrl: img,
          }));
        }
      });

      const result = products.slice(0, 24);
      await cacheSet(cacheKey, result, 3600);
      return result;
    } catch (error) {
      console.error(`[HomecenterScraper] Search error: ${error}`);
      return [];
    }
  }

  async getProductDetails(url: string): Promise<Product | null> {
    const cacheKey = `details:homecenter:${url}`;
    const cached = await cacheGet(cacheKey);
    if (cached) return cached;

    try {
      const { data: html } = await axios.get(url, { headers: this.headers, timeout: 8000 });
      const nextDataMatch = html.match(/<script id="__NEXT_DATA__" type="application\/json">(.*?)<\/script>/);
      
      if (nextDataMatch && nextDataMatch[1]) {
        const json = JSON.parse(nextDataMatch[1]);
        const productData = json?.props?.pageProps?.productProps?.result || json?.props?.pageProps?.initialData?.product;
        
        if (productData) {
          const product = this.normalizeProduct({
            nombre: productData.name,
            precio: productData.price || productData.currentPrice || 0,
            marca: productData.brand,
            caracteristicas: productData.attributes || productData.specifications || {},
            urlProducto: url,
            imagenUrl: productData.image || '',
          });
          await cacheSet(cacheKey, product, 86400); // Cache por 24 horas
          return product;
        }
      }
      return null;
    } catch (error) {
      console.error(`[HomecenterScraper] Detail error: ${error}`);
      return null;
    }
  }
}
