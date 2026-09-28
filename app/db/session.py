import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.db.models.models import Base

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://toolsprece:toolsprece@db:5432/toolsprece",
)

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
)

async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncSession:
    async with async_session_factory() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # seed mock products if empty
    try:
        from app.db.models.models import Product
        from app.services.seed import MOCK_PRODUCTS
        from sqlalchemy import select, func
        async with async_session_factory() as session:
            count = (await session.execute(select(func.count()).select_from(Product))).scalar()
            if count == 0:
                for p in MOCK_PRODUCTS:
                    prod = Product(
                        nombre=p["nombre"],
                        categoria=p["categoria"],
                        precio=p["precio"],
                        marca=p["marca"],
                        tienda=p["tienda"],
                        unidad_medida=p["unidad_medida"],
                        imagen_url=p["imagen_url"],
                        url_producto=p["url_producto"],
                        caracteristicas=str(p["caracteristicas"]),
                        moneda="MXN",
                        disponibilidad=True,
                    )
                    session.add(prod)
                await session.commit()
                print(f"Seeded {len(MOCK_PRODUCTS)} mock products")
    except Exception as e:
        print(f"Seed warning: {e}")