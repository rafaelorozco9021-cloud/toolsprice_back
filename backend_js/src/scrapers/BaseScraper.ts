import { Product } from '../types/product';

export abstract class BaseScraper {
  abstract readonly name: string;

  abstract search(query: string, categoria?: string): Promise<Product[]>;
  abstract getProductDetails(url: string): Promise<Product | null>;

  normalizeProduct(raw: any): Product {
    return {
      nombre: raw.nombre || '',
      categoria: raw.categoria || '',
      precio: parseFloat(raw.precio || 0),
      moneda: raw.moneda || 'COP',
      unidadMedida: raw.unidadMedida || 'unidad',
      marca: raw.marca || '',
      caracteristicas: raw.caracteristicas || {},
      urlProducto: raw.urlProducto || '',
      imagenUrl: raw.imagenUrl || '',
      tienda: this.name,
      disponibilidad: raw.disponibilidad !== undefined ? raw.disponibilidad : true,
      fechaActualizacion: new Date(),
    };
  }
}
