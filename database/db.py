from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from config.settings import settings
from .models import Base


def _build_url(raw: str) -> str:
    """Converte URLs do Railway/Heroku para o formato asyncio correto."""
    if raw.startswith("postgres://"):
        raw = raw.replace("postgres://", "postgresql+asyncpg://", 1)
    elif raw.startswith("postgresql://") and "+asyncpg" not in raw:
        raw = raw.replace("postgresql://", "postgresql+asyncpg://", 1)
    return raw


_url = _build_url(settings.database_url)
_is_sqlite = "sqlite" in _url

engine = create_async_engine(
    _url,
    echo=False,
    **({} if not _is_sqlite else {"connect_args": {"check_same_thread": False}}),
)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    if _is_sqlite:
        await _sqlite_migrations()


async def _sqlite_migrations():
    """Migrações de colunas novas — somente SQLite (Postgres usa create_all)."""
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
                pass


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
