import Redis from 'ioredis';

const redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');

export async function cacheGet(key: string): Promise<any | null> {
  const data = await redis.get(key);
  return data ? JSON.parse(data) : null;
}

export async function cacheSet(key: string, value: any, ttl = 3600): Promise<void> {
  await redis.set(key, JSON.stringify(value), 'EX', ttl);
}

export async function cacheDel(key: string): Promise<void> {
  await redis.del(key);
}

export default redis;
