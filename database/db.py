from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from config.settings import settings
from .models import Base

engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await _run_migrations()


async def _run_migrations():
    """Adiciona colunas novas sem destruir dados existentes."""
    migrations = [
        "ALTER TABLE listings ADD COLUMN purchased BOOLEAN DEFAULT 0",
        "ALTER TABLE listings ADD COLUMN purchased_at DATETIME",
        "ALTER TABLE listings ADD COLUMN purchase_notes TEXT",
        "ALTER TABLE listings ADD COLUMN discarded BOOLEAN DEFAULT 0",
    ]
    async with engine.begin() as conn:
        for sql in migrations:
            try:
                await conn.execute(text(sql))
            except Exception:
                pass  # Coluna já existe — ignora


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
