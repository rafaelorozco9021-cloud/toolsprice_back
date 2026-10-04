import Fastify from 'fastify';
import { HomecenterScraper } from './scrapers/HomecenterScraper';
import { authRoutes } from './routes/auth';
import { Product } from './types/product';

const fastify = Fastify({ logger: true });
const homecenter = new HomecenterScraper();

// Registrar Rutas de Autenticación
fastify.register(authRoutes, { prefix: '/api/auth' });

fastify.get('/products/search', async (request, reply) => {
  const { query } = request.query as { query: string };
  
  if (!query) {
    return reply.status(400).send({ error: 'Query is required' });
  }

  const products = await homecenter.search(query);
  
  return {
    products,
    total: products.length
  };
});

fastify.get('/products/search/live', async (request, reply) => {
  const { query } = request.query as { query: string };
  if (!query) return reply.status(400).send({ error: 'Query is required' });
  
  const products = await homecenter.search(query);
  return { products, total: products.length };
});

const start = async () => {
  try {
    await fastify.listen({ port: 3001, host: '0.0.0.0' });
    console.log('🚀 Backend JS running on http://localhost:3001');
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();

