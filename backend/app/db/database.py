from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    "postgresql+asyncpg://toolsprece:toolsprece@db/toolsprece",
    echo=False,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
)
