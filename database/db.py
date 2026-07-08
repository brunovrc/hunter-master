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
    await _run_migrations()


# Colunas novas adicionadas ao longo do tempo.
# ADD COLUMN IF NOT EXISTS funciona em PostgreSQL 9.6+ e SQLite 3.35+.
_NEW_COLUMNS = [
    "ALTER TABLE listings ADD COLUMN IF NOT EXISTS purchased BOOLEAN DEFAULT FALSE",
    "ALTER TABLE listings ADD COLUMN IF NOT EXISTS purchased_at TIMESTAMP",
    "ALTER TABLE listings ADD COLUMN IF NOT EXISTS purchase_notes TEXT",
    "ALTER TABLE listings ADD COLUMN IF NOT EXISTS discarded BOOLEAN DEFAULT FALSE",
    "ALTER TABLE listings ADD COLUMN IF NOT EXISTS filters_json TEXT",
    "ALTER TABLE listings ADD COLUMN IF NOT EXISTS reasoning TEXT",
    "ALTER TABLE listings ADD COLUMN IF NOT EXISTS suggested_offer FLOAT",
]

_SQLITE_NEW_COLUMNS = [s.replace(" IF NOT EXISTS", "") for s in _NEW_COLUMNS]

# Correções de dados pontuais (não são schema, são bugs já corrigidos no
# código mas que deixaram registros ruins salvos). Idempotentes — depois de
# rodar uma vez o WHERE não bate mais em nada, então é seguro rodar sempre.
_DATA_FIXES = [
    # 800xN não é um preset válido no CDN do Enjoei (retornava 404) — só
    # presets quadrados (WxW) funcionam sob demanda. Ver scrapers/enrichment.py.
    "UPDATE listings SET images = REPLACE(images, '/800xN/', '/800x800/') WHERE images LIKE '%/800xN/%'",
]


async def _run_migrations():
    stmts = _SQLITE_NEW_COLUMNS if _is_sqlite else _NEW_COLUMNS
    async with engine.begin() as conn:
        for sql in stmts:
            try:
                await conn.execute(text(sql))
            except Exception:
                pass
        for sql in _DATA_FIXES:
            try:
                await conn.execute(text(sql))
            except Exception:
                pass


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
