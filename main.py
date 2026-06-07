import asyncio
import logging

import uvicorn

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("hunter_master")


async def _run_bot_only():
    """Modo sem dashboard — apenas o bot com scheduler."""
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.interval import IntervalTrigger
    from bot_core import run_health_check, run_hunter_cycle, run_daily_report
    from bot_core import scrape_tier3_prices  # noqa: F401
    from config.settings import settings
    from database.db import init_db

    await init_db()
    logger.info("Banco de dados inicializado (modo bot)")

    scheduler = AsyncIOScheduler()
    scheduler.add_job(run_hunter_cycle, IntervalTrigger(minutes=settings.scan_interval_minutes))
    scheduler.add_job(run_daily_report, CronTrigger(hour=20, minute=0))
    scheduler.add_job(run_health_check, IntervalTrigger(hours=2))
    scheduler.start()

    await run_hunter_cycle()

    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "dashboard.app:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info",
    )
