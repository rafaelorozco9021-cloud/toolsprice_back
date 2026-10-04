export interface Product {
  nombre: string;
  categoria: string;
  precio: number;
  moneda: string;
  unidadMedida: string;
  marca: string;
  caracteristicas: any;
  urlProducto: string;
  imagenUrl: string;
  tienda: string;
  disponibilidad: boolean;
  fechaActualizacion?: Date;
}

export interface ScraperResult {
  products: Product[];
  total: number;
}
