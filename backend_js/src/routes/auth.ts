import { FastifyInstance } from 'fastify';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { PrismaClient } from '@prisma/client';
import { z } from 'zod';

const prisma = new PrismaClient();
const JWT_SECRET = process.env.JWT_SECRET || 'super-secret-key-123';

export async function authRoutes(fastify: FastifyInstance) {
  
  // Registro
  fastify.post('/register', async (request, reply) => {
    const schema = z.object({
      name: z.string(),
      email: z.string().email(),
      password: z.string().min(6),
      password_confirm: z.string().min(6),
    });

    const body = schema.parse(request.body);

    if (body.password !== body.password_confirm) {
      return reply.status(400).send({ detail: 'Passwords do not match' });
    }

    const existingUser = await prisma.user.findUnique({ where: { email: body.email } });
    if (existingUser) {
      return reply.status(400).send({ detail: 'Email already registered' });
    }

    const passwordHash = await bcrypt.hash(body.password, 10);
    const user = await prisma.user.create({
      data: {
        name: body.name,
        email: body.email,
        password: passwordHash,
      },
    });

    return { id: user.id, name: user.name, email: user.email };
  });

  // Login
  fastify.post('/login', async (request, reply) => {
    // FastAPI usa OAuth2PasswordRequestForm (form-data: username, password)
    // Pero el frontend moderno suele enviar JSON. Soportaremos ambos.
    const body = request.body as any;
    const username = body.username || body.email;
    const password = body.password;

    if (!username || !password) {
      return reply.status(400).send({ detail: 'Email and password are required' });
    }

    const user = await prisma.user.findUnique({ where: { email: username } });

    if (!user || !(await bcrypt.compare(password, user.password))) {
      return reply.status(401).send({ 
        detail: 'Incorrect email or password' 
      });
    }

    const accessToken = jwt.sign(
      { sub: user.id, email: user.email }, 
      JWT_SECRET, 
      { expiresIn: '60m' }
    );

    const refreshToken = jwt.sign(
      { sub: user.id, email: user.email }, 
      JWT_SECRET, 
      { expiresIn: '30d' }
    );

    return {
      access_token: accessToken,
      refresh_token: refreshToken,
      token_type: 'bearer',
    };
  });
}
