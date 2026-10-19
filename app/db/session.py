import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.db.models.models import Base

DEFAULT_DATABASE_URL = "postgresql+asyncpg://toolsprece:toolsprece@db:5432/toolsprece"

SSLMODES = {
    "disable": False,
    "allow": "prefer",
    "prefer": "prefer",
    "require": "require",
    "verify-ca": "verify-ca",
    "verify-full": "verify-full",
}


def _prepare_url(url: str) -> tuple[str, dict]:
    """Normaliza el esquema de driver y traduce los params de query que asyncpg no entiende."""
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            url = url.replace(prefix, "postgresql+asyncpg://", 1)
            break

    base, _, query = url.partition("?")
    connect_args = {}
    for part in query.split("&"):
        key, _, value = part.partition("=")
        if key == "sslmode" and value:
            connect_args["ssl"] = SSLMODES.get(value, "require")
    return base, connect_args


DATABASE_URL, CONNECT_ARGS = _prepare_url(
    os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=20,
    # Render cierra conexiones inactivas sin avisar ("connection is closed").
    # pre_ping verifica cada conexión antes de usarla y recycle las rota.
    pool_recycle=300,
    pool_pre_ping=True,
    connect_args=CONNECT_ARGS,
)

async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncSession:
    async with async_session_factory() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Migración ligera: create_all no agrega columnas a tablas existentes
        try:
            from sqlalchemy import text
            await conn.execute(text(
                "ALTER TABLE toolsprice_budget_items "
                "ADD COLUMN IF NOT EXISTS seccion VARCHAR(20) DEFAULT 'materiales'"
            ))
        except Exception as e:
            print(f"Migration warning: {e}")
        # Catálogo Homecenter: índice trigram para búsqueda fuzzy rápida (< 200ms)
        try:
            from sqlalchemy import text
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
            await conn.execute(text(
                "CREATE INDEX IF NOT EXISTS ix_catalog_nombre_trgm "
                "ON toolsprice_catalog_products USING gin (nombre gin_trgm_ops)"
            ))
            await conn.execute(text(
                "CREATE INDEX IF NOT EXISTS ix_catalog_busqueda_trgm "
                "ON toolsprice_catalog_products USING gin "
                "((nombre || ' ' || coalesce(marca,'') || ' ' || coalesce(categoria,'')) gin_trgm_ops)"
            ))
        except Exception as e:
            print(f"Catalog index warning: {e}")
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