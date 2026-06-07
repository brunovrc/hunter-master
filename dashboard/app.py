import asyncio
import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from sqlalchemy import desc, func, select

from config.settings import settings
from database.db import AsyncSessionLocal, init_db
from database.models import Listing, RunLog

logger = logging.getLogger(__name__)

# ── Auth ──────────────────────────────────────────────────────────────────────

_signer = URLSafeTimedSerializer(settings.dashboard_secret_key)


def _make_session_token(username: str) -> str:
    return _signer.dumps(username, salt="session")


def _verify_session_token(token: str) -> Optional[str]:
    try:
        return _signer.loads(token, salt="session", max_age=86400 * 7)
    except (BadSignature, SignatureExpired):
        return None


def _get_user(request: Request) -> Optional[str]:
    token = request.cookies.get("session")
    if not token:
        return None
    return _verify_session_token(token)


def _require_user(request: Request) -> str:
    user = _get_user(request)
    if not user:
        raise HTTPException(status_code=303, headers={"Location": "/login"})
    return user


# ── Bot state ─────────────────────────────────────────────────────────────────

_scheduler: Optional[AsyncIOScheduler] = None
_bot_stats = {
    "scraped": 0, "new": 0, "opportunities": 0,
    "buy": 0, "negotiate": 0, "flag": 0, "refuse": 0,
    "price_drops": 0, "errors": [],
}
_cycle_running = False
_last_cycle: Optional[datetime] = None
_next_cycle: Optional[datetime] = None


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _scheduler, _next_cycle

    logger.info("Hunter Master iniciando...")
    await init_db()
    logger.info("Banco de dados inicializado")

    from bot_core import run_hunter_cycle, run_daily_report, run_health_check
    from scrapers.tier3_pricer import scrape_tier3_prices

    _scheduler = AsyncIOScheduler()
    _scheduler.add_job(
        run_hunter_cycle,
        IntervalTrigger(minutes=settings.scan_interval_minutes),
        id="hunter_cycle",
    )
    _scheduler.add_job(scrape_tier3_prices, CronTrigger(hour=3, minute=0), id="tier3")
    _scheduler.add_job(run_daily_report, CronTrigger(hour=20, minute=0), id="daily_report")
    _scheduler.add_job(run_health_check, IntervalTrigger(hours=2), id="health_check")
    _scheduler.start()

    _next_cycle = datetime.now() + timedelta(minutes=settings.scan_interval_minutes)
    logger.info(f"Scheduler ativo — varredura a cada {settings.scan_interval_minutes}min")

    asyncio.create_task(run_hunter_cycle())

    yield

    _scheduler.shutdown()
    logger.info("Hunter Master encerrado")


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(title="Hunter Master", lifespan=lifespan)
templates = Jinja2Templates(directory="dashboard/templates")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_images(raw: Optional[str]) -> list[str]:
    if not raw:
        return []
    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _parse_filters(raw: Optional[str]) -> list:
    if not raw:
        return []
    try:
        from types import SimpleNamespace
        data = json.loads(raw)
        return [SimpleNamespace(**f) for f in data] if isinstance(data, list) else []
    except Exception:
        return []


def _listing_to_dict(l: Listing) -> dict:
    images = _parse_images(l.images)
    return {
        "id": l.id,
        "title": l.title or "",
        "price": l.price or 0,
        "score": l.score or 0,
        "recommendation": l.recommendation or "",
        "gross_margin": l.gross_margin,
        "sell_price_estimate": l.sell_price_estimate,
        "suggested_offer": l.suggested_offer,
        "platform": l.platform or "",
        "url": l.url or "",
        "player_name": l.player_name or "",
        "is_autographed": l.is_autographed,
        "is_match_worn": l.is_match_worn,
        "has_coa": l.has_coa,
        "thumbnail": images[0] if images else "",
        "purchased": l.purchased,
        "discarded": l.discarded,
        "created_at": l.created_at,
        "notified": l.notified,
        "reasoning": l.reasoning or "",
        "filters_data": _parse_filters(l.filters_json),
    }


def _rec_badge(rec: str) -> dict:
    m = {
        "COMPRAR AGORA": {"label": "COMPRAR", "css": "bg-green-500/20 text-green-400 border border-green-500/40"},
        "NEGOCIAR": {"label": "NEGOCIAR", "css": "bg-yellow-500/20 text-yellow-400 border border-yellow-500/40"},
        "FLAG AUTENTICADOR": {"label": "VERIFICAR", "css": "bg-orange-500/20 text-orange-400 border border-orange-500/40"},
        "RECUSAR": {"label": "RECUSADO", "css": "bg-slate-700 text-slate-400 border border-slate-600"},
    }
    return m.get(rec, {"label": rec, "css": "bg-slate-700 text-slate-400"})


# ── Auth routes ───────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    user = _get_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    return RedirectResponse("/feed", status_code=303)


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = ""):
    return templates.TemplateResponse(request, "login.html", {"error": error})


@app.post("/login")
async def do_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    if username == settings.dashboard_user and password == settings.dashboard_password:
        token = _make_session_token(username)
        resp = RedirectResponse("/feed", status_code=303)
        resp.set_cookie("session", token, httponly=True, max_age=86400 * 7, samesite="lax")
        return resp
    return RedirectResponse("/login?error=Usuário+ou+senha+inválidos", status_code=303)


@app.get("/logout")
async def logout(request: Request):
    resp = RedirectResponse("/login", status_code=303)
    resp.delete_cookie("session")
    return resp


# ── Feed ──────────────────────────────────────────────────────────────────────

@app.get("/feed", response_class=HTMLResponse)
async def feed(
    request: Request,
    filter: str = "all",
    page: int = 1,
    per_page: int = 20,
):
    _require_user(request)

    async with AsyncSessionLocal() as session:
        q = select(Listing).where(
            Listing.recommendation != "RECUSAR",
            Listing.discarded == False,
        )
        if filter == "buy":
            q = q.where(Listing.recommendation == "COMPRAR AGORA")
        elif filter == "negotiate":
            q = q.where(Listing.recommendation == "NEGOCIAR")
        elif filter == "flag":
            q = q.where(Listing.recommendation == "FLAG AUTENTICADOR")

        count_q = select(func.count()).select_from(q.subquery())
        total = (await session.execute(count_q)).scalar() or 0

        q = q.order_by(desc(Listing.score)).offset((page - 1) * per_page).limit(per_page)
        rows = (await session.execute(q)).scalars().all()

    listings = [_listing_to_dict(r) for r in rows]
    for item in listings:
        item["badge"] = _rec_badge(item["recommendation"])

    total_pages = max(1, (total + per_page - 1) // per_page)

    return templates.TemplateResponse(request, "feed.html", {
        "listings": listings,
        "filter": filter,
        "page": page,
        "total_pages": total_pages,
        "total": total,
        "active_page": "feed",
    })


# ── Stats ─────────────────────────────────────────────────────────────────────

@app.get("/stats", response_class=HTMLResponse)
async def stats(request: Request):
    _require_user(request)

    async with AsyncSessionLocal() as session:
        # Totals
        total_listings = (await session.execute(select(func.count(Listing.id)))).scalar() or 0
        total_opps = (await session.execute(
            select(func.count(Listing.id)).where(Listing.recommendation != "RECUSAR")
        )).scalar() or 0
        total_buy = (await session.execute(
            select(func.count(Listing.id)).where(Listing.recommendation == "COMPRAR AGORA")
        )).scalar() or 0
        total_negotiate = (await session.execute(
            select(func.count(Listing.id)).where(Listing.recommendation == "NEGOCIAR")
        )).scalar() or 0
        total_flag = (await session.execute(
            select(func.count(Listing.id)).where(Listing.recommendation == "FLAG AUTENTICADOR")
        )).scalar() or 0
        total_purchased = (await session.execute(
            select(func.count(Listing.id)).where(Listing.purchased == True)
        )).scalar() or 0

        # By platform
        platform_rows = (await session.execute(
            select(Listing.platform, func.count(Listing.id))
            .group_by(Listing.platform)
            .order_by(desc(func.count(Listing.id)))
        )).all()

        # Top players
        player_rows = (await session.execute(
            select(Listing.player_name, func.count(Listing.id))
            .where(Listing.player_name != "", Listing.player_name.isnot(None))
            .group_by(Listing.player_name)
            .order_by(desc(func.count(Listing.id)))
            .limit(10)
        )).all()

        # Last 7 days — opportunities per day
        days_data = []
        for i in range(6, -1, -1):
            day = datetime.utcnow().date() - timedelta(days=i)
            day_start = datetime(day.year, day.month, day.day)
            day_end = day_start + timedelta(days=1)
            cnt = (await session.execute(
                select(func.count(Listing.id)).where(
                    Listing.recommendation != "RECUSAR",
                    Listing.created_at >= day_start,
                    Listing.created_at < day_end,
                )
            )).scalar() or 0
            days_data.append({"label": day.strftime("%d/%m"), "count": cnt})

        # Recent runs
        run_rows = (await session.execute(
            select(RunLog).order_by(desc(RunLog.started_at)).limit(10)
        )).scalars().all()

    return templates.TemplateResponse(request, "stats.html", {
        "total_listings": total_listings,
        "total_opps": total_opps,
        "total_buy": total_buy,
        "total_negotiate": total_negotiate,
        "total_flag": total_flag,
        "total_purchased": total_purchased,
        "platform_rows": [(r[0], r[1]) for r in platform_rows],
        "player_rows": [(r[0], r[1]) for r in player_rows],
        "chart_labels": json.dumps([d["label"] for d in days_data]),
        "chart_data": json.dumps([d["count"] for d in days_data]),
        "run_rows": run_rows,
        "active_page": "stats",
    })


# ── Control ───────────────────────────────────────────────────────────────────

@app.get("/control", response_class=HTMLResponse)
async def control(request: Request):
    _require_user(request)

    from bot_core import scrapers

    scraper_status = []
    for s in scrapers:
        paused = getattr(getattr(s, "circuit_breaker", None), "paused_until", None)
        scraper_status.append({
            "name": s.name,
            "paused": bool(paused and paused > datetime.now()),
            "paused_until": paused.strftime("%H:%M") if paused and paused > datetime.now() else None,
        })

    next_run = None
    if _scheduler:
        job = _scheduler.get_job("hunter_cycle")
        if job and job.next_run_time:
            next_run = job.next_run_time.strftime("%H:%M:%S")

    async with AsyncSessionLocal() as session:
        run_rows = (await session.execute(
            select(RunLog).order_by(desc(RunLog.started_at)).limit(15)
        )).scalars().all()

    return templates.TemplateResponse(request, "control.html", {
        "scheduler_running": _scheduler.running if _scheduler else False,
        "cycle_running": _cycle_running,
        "next_run": next_run,
        "last_cycle": _last_cycle.strftime("%d/%m %H:%M") if _last_cycle else "–",
        "run_rows": run_rows,
        "scraper_status": scraper_status,
        "scan_interval": settings.scan_interval_minutes,
        "active_page": "control",
    })


# ── History ───────────────────────────────────────────────────────────────────

@app.get("/history", response_class=HTMLResponse)
async def history(request: Request):
    _require_user(request)

    async with AsyncSessionLocal() as session:
        rows = (await session.execute(
            select(Listing)
            .where(Listing.purchased == True)
            .order_by(desc(Listing.purchased_at))
        )).scalars().all()

    items = []
    for r in rows:
        margin_pct = None
        if r.sell_price_estimate and r.price:
            margin_pct = ((r.sell_price_estimate - r.price) / r.price) * 100
        items.append({
            "id": r.id,
            "title": r.title or "",
            "price": r.price or 0,
            "sell_estimate": r.sell_price_estimate,
            "margin_pct": margin_pct,
            "platform": r.platform or "",
            "url": r.url or "",
            "player_name": r.player_name or "",
            "purchased_at": r.purchased_at,
            "notes": r.purchase_notes or "",
            "thumbnail": (_parse_images(r.images) or [""])[0],
        })

    total_invested = sum(i["price"] for i in items)
    total_estimate = sum(i["sell_estimate"] or 0 for i in items)

    return templates.TemplateResponse(request, "history.html", {
        "items": items,
        "total_invested": total_invested,
        "total_estimate": total_estimate,
        "count": len(items),
        "active_page": "history",
    })


# ── API endpoints ─────────────────────────────────────────────────────────────

@app.post("/api/purchased")
async def mark_purchased(request: Request, listing_id: int = Form(...), notes: str = Form("")):
    _require_user(request)
    async with AsyncSessionLocal() as session:
        row = await session.get(Listing, listing_id)
        if not row:
            raise HTTPException(status_code=404)
        row.purchased = True
        row.purchased_at = datetime.utcnow()
        row.purchase_notes = notes or None
        await session.commit()
    return JSONResponse({"ok": True})


@app.post("/api/discard")
async def mark_discarded(request: Request, listing_id: int = Form(...)):
    _require_user(request)
    async with AsyncSessionLocal() as session:
        row = await session.get(Listing, listing_id)
        if not row:
            raise HTTPException(status_code=404)
        row.discarded = True
        await session.commit()
    return JSONResponse({"ok": True})


@app.post("/api/restore")
async def restore_discarded(request: Request, listing_id: int = Form(...)):
    _require_user(request)
    async with AsyncSessionLocal() as session:
        row = await session.get(Listing, listing_id)
        if not row:
            raise HTTPException(status_code=404)
        row.discarded = False
        await session.commit()
    return JSONResponse({"ok": True, "message": "Item restaurado no feed"})


@app.get("/discarded", response_class=HTMLResponse)
async def discarded_page(request: Request, page: int = 1, per_page: int = 24):
    _require_user(request)

    async with AsyncSessionLocal() as session:
        count_q = select(func.count(Listing.id)).where(Listing.discarded == True)
        total = (await session.execute(count_q)).scalar() or 0

        q = (
            select(Listing)
            .where(Listing.discarded == True)
            .order_by(desc(Listing.score))
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        rows = (await session.execute(q)).scalars().all()

    listings = [_listing_to_dict(r) for r in rows]
    for item in listings:
        item["badge"] = _rec_badge(item["recommendation"])

    total_pages = max(1, (total + per_page - 1) // per_page)

    return templates.TemplateResponse(request, "discarded.html", {
        "listings": listings,
        "page": page,
        "total_pages": total_pages,
        "total": total,
        "active_page": "discarded",
    })


@app.post("/api/trigger")
async def trigger_cycle(request: Request):
    _require_user(request)
    global _cycle_running
    if _cycle_running:
        return JSONResponse({"ok": False, "message": "Ciclo já em andamento"})

    from bot_core import run_hunter_cycle
    asyncio.create_task(run_hunter_cycle())
    return JSONResponse({"ok": True, "message": "Ciclo iniciado"})


@app.get("/api/status")
async def bot_status(request: Request):
    _require_user(request)
    next_run = None
    if _scheduler:
        job = _scheduler.get_job("hunter_cycle")
        if job and job.next_run_time:
            next_run = job.next_run_time.isoformat()
    return JSONResponse({
        "running": _scheduler.running if _scheduler else False,
        "cycle_running": _cycle_running,
        "next_run": next_run,
        "last_cycle": _last_cycle.isoformat() if _last_cycle else None,
    })
