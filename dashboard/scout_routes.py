"""
Hunter Scout — avaliação de camisetas em campo via fotos + IA.

Fluxo: o sócio visita um colecionador, abre o PWA no celular, fotografa a
camisa (1-3 fotos) e recebe na hora: identificação, autenticidade estimada,
valor de mercado e faixa de oferta sugerida. Tudo fica salvo por "sessão de
visita" para revisão posterior no dashboard desktop.

Roteador isolado do app.py principal para manter o pipeline do radar
(scraping) e o pipeline de campo (Scout) desacoplados — mudanças em um não
arriscam quebrar o outro.
"""
import json
import logging
from datetime import datetime

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc, select

from dashboard.auth import require_user
from database.db import AsyncSessionLocal
from database.models import ScoutEvaluation, ScoutQuestion, ScoutSession
from scout.analyzer import ask_followup, evaluate_jersey
from scout.comparables import find_comparables
from scout.pricing import build_scout_result

logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="dashboard/templates")

router = APIRouter()

# ── Limites de upload — protege contra fotos gigantes de celular ──────────────
_MAX_IMAGES = 3
_MAX_IMAGE_BYTES = 5 * 1024 * 1024       # 5MB por imagem
_MAX_TOTAL_BYTES = 12 * 1024 * 1024      # 12MB no total


# ── Página do app (PWA) ───────────────────────────────────────────────────────

@router.get("/scout", response_class=HTMLResponse)
async def scout_app(request: Request):
    require_user(request)
    return templates.TemplateResponse(request, "scout.html", {})


@router.get("/scout/sw.js")
async def scout_service_worker():
    # Servido em /scout/sw.js (não /static/) para o escopo do service worker
    # cobrir /scout/* automaticamente, sem precisar do header Service-Worker-Allowed.
    return FileResponse("dashboard/static/scout/sw.js", media_type="application/javascript")


# ── Sessão de visita ───────────────────────────────────────────────────────────

@router.post("/scout/api/session/start")
async def start_session(
    request: Request,
    collector_name: str = Form(""),
    location: str = Form(""),
):
    require_user(request)
    async with AsyncSessionLocal() as session:
        s = ScoutSession(collector_name=collector_name.strip(), location=location.strip())
        session.add(s)
        await session.commit()
        await session.refresh(s)
        return JSONResponse({"ok": True, "session_id": s.id})


@router.post("/scout/api/session/close")
async def close_session(request: Request, session_id: int = Form(...)):
    require_user(request)
    async with AsyncSessionLocal() as session:
        row = await session.get(ScoutSession, session_id)
        if not row:
            raise HTTPException(status_code=404)
        row.closed_at = datetime.utcnow()
        await session.commit()
    return JSONResponse({"ok": True})


@router.get("/scout/api/session/{session_id}/evaluations")
async def session_evaluations(request: Request, session_id: int):
    require_user(request)
    async with AsyncSessionLocal() as session:
        rows = (await session.execute(
            select(ScoutEvaluation)
            .where(ScoutEvaluation.session_id == session_id)
            .order_by(desc(ScoutEvaluation.created_at))
        )).scalars().all()
    return JSONResponse({
        "ok": True,
        "evaluations": [_evaluation_summary(r) for r in rows],
        "total_offer_max": sum(r.offer_max or 0 for r in rows),
    })


def _evaluation_summary(r: ScoutEvaluation) -> dict:
    return {
        "id": r.id,
        "player_name": r.player_name,
        "club": r.club,
        "item_type": r.item_type,
        "recommendation": r.recommendation,
        "authenticity_score": r.authenticity_score,
        "sell_price_estimate": r.sell_price_estimate,
        "offer_min": r.offer_min,
        "offer_max": r.offer_max,
        "created_at": r.created_at.strftime("%H:%M") if r.created_at else "",
    }


# ── Avaliação ──────────────────────────────────────────────────────────────────

async def _read_and_validate_images(images: list[UploadFile]) -> list[tuple[bytes, str]]:
    if not images or all(img.filename == "" for img in images):
        raise HTTPException(status_code=400, detail="Envie pelo menos 1 foto.")
    if len(images) > _MAX_IMAGES:
        raise HTTPException(status_code=400, detail=f"Máximo de {_MAX_IMAGES} fotos por avaliação.")

    result: list[tuple[bytes, str]] = []
    total = 0
    for img in images:
        content_type = img.content_type or "image/jpeg"
        if not content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Arquivo enviado não é uma imagem.")
        data = await img.read()
        if len(data) > _MAX_IMAGE_BYTES:
            raise HTTPException(status_code=400, detail="Foto excede 5MB — reduza a qualidade/tamanho.")
        total += len(data)
        if total > _MAX_TOTAL_BYTES:
            raise HTTPException(status_code=400, detail="Total das fotos excede 12MB.")
        result.append((data, content_type))
    return result


@router.post("/scout/api/evaluate")
async def evaluate(
    request: Request,
    images: list[UploadFile] = File(...),
    user_notes: str = Form(""),
    session_id: str = Form(""),
):
    require_user(request)
    parsed_session_id = int(session_id) if session_id.strip().isdigit() else None

    image_bytes = await _read_and_validate_images(images)

    try:
        vision = await evaluate_jersey(image_bytes, user_notes)
        result = await build_scout_result(vision)
    except Exception as e:
        logger.error(f"[Scout] Erro na avaliação: {e}")
        raise HTTPException(status_code=502, detail="Falha ao analisar a imagem. Tente novamente.")

    import base64
    images_json = json.dumps([
        f"data:{mime};base64,{base64.standard_b64encode(data).decode()}"
        for data, mime in image_bytes
    ])

    async with AsyncSessionLocal() as session:
        row = ScoutEvaluation(
            session_id=parsed_session_id,
            images=images_json,
            user_notes=user_notes,
            player_name=result.player_name,
            club=result.club,
            year_era=result.year_era,
            item_type=result.item_type,
            condition=result.condition,
            is_autographed=result.is_autographed,
            is_match_worn=result.is_match_worn,
            has_coa=result.has_coa,
            signature_looks_genuine=result.signature_looks_genuine,
            replica_suspicion=result.replica_suspicion,
            authenticity_score=result.authenticity_score,
            identified_text=result.identified_text,
            ai_notes=result.ai_notes,
            raw_ai_json=result.model_dump_json(),
            sell_price_estimate=result.sell_price_estimate,
            offer_min=result.offer_min,
            offer_max=result.offer_max,
            recommendation=result.recommendation,
        )
        session.add(row)
        await session.commit()
        await session.refresh(row)

    payload = result.model_dump()
    payload["evaluation_id"] = row.id
    return JSONResponse({"ok": True, **payload})


# ── Pergunta de acompanhamento ────────────────────────────────────────────────
# Deixa o usuário pedir mais detalhes sobre uma avaliação já feita, sem
# precisar tirar foto de novo — reaproveita as mesmas fotos + contexto salvo.

# Termos que, se mencionados na pergunta, valem a pena somar na busca de
# comparáveis (diferenciam preço). Frase inteira NÃO — vira ruído na busca.
_CONTEXT_KEYWORDS = [
    "centenário", "centenario", "aniversário", "aniversario", "elenco",
    "squad", "edição limitada", "edicao limitada", "numerada", "final",
    "campeão", "campeao", "libertadores", "mundial", "copa",
]


def _extract_context_keywords(question: str) -> str:
    q = question.lower()
    found = [kw for kw in _CONTEXT_KEYWORDS if kw in q]
    return " ".join(found[:3])


def _decode_stored_images(images_json: str) -> list[tuple[bytes, str]]:
    import base64
    data_uris = json.loads(images_json) if images_json else []
    result = []
    for uri in data_uris:
        try:
            header, b64data = uri.split(",", 1)
            mime = header.split(":")[1].split(";")[0]
            result.append((base64.standard_b64decode(b64data), mime))
        except Exception:
            continue
    return result


@router.post("/scout/api/evaluation/{evaluation_id}/ask")
async def ask_about_evaluation(request: Request, evaluation_id: int, question: str = Form(...)):
    require_user(request)
    question = question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Digite uma pergunta.")

    async with AsyncSessionLocal() as session:
        row = await session.get(ScoutEvaluation, evaluation_id)
        if not row:
            raise HTTPException(status_code=404, detail="Avaliação não encontrada.")

        images = _decode_stored_images(row.images)
        context = {
            "player_name": row.player_name, "club": row.club, "year_era": row.year_era,
            "item_type": row.item_type, "is_autographed": row.is_autographed,
            "has_coa": row.has_coa, "authenticity_score": row.authenticity_score,
            "ai_notes": row.ai_notes,
        }

        # Mesma base de termos que já funciona na avaliação inicial — NÃO
        # jogar a pergunta inteira na busca (frase longa vira ruído e zera
        # os resultados do Vinted). Só extrai palavras-chave reconhecíveis
        # da pergunta que ajudam a refinar (ex: "centenário", "elenco").
        squad_term = "elenco autografado squad signed" if row.is_autographed and not row.player_name else ""
        keyword_term = _extract_context_keywords(question)
        comparables = await find_comparables(row.player_name, row.club, row.year_era, squad_term, keyword_term)

        answer = await ask_followup(
            images, context, question,
            comparables=[c.model_dump() for c in comparables],
        )

        q_row = ScoutQuestion(evaluation_id=evaluation_id, question=question, answer=answer)
        session.add(q_row)
        await session.commit()

    return JSONResponse({
        "ok": True,
        "question": question,
        "answer": answer,
        "comparables": [c.model_dump() for c in comparables],
    })


@router.get("/scout/api/evaluation/{evaluation_id}/questions")
async def list_questions(request: Request, evaluation_id: int):
    require_user(request)
    async with AsyncSessionLocal() as session:
        rows = (await session.execute(
            select(ScoutQuestion)
            .where(ScoutQuestion.evaluation_id == evaluation_id)
            .order_by(ScoutQuestion.created_at)
        )).scalars().all()
    return JSONResponse({
        "ok": True,
        "questions": [{"question": r.question, "answer": r.answer} for r in rows],
    })


# ── Histórico (desktop) ────────────────────────────────────────────────────────

@router.get("/scout/history", response_class=HTMLResponse)
async def scout_history(request: Request):
    require_user(request)
    async with AsyncSessionLocal() as session:
        sessions = (await session.execute(
            select(ScoutSession).order_by(desc(ScoutSession.started_at)).limit(50)
        )).scalars().all()

        recent = (await session.execute(
            select(ScoutEvaluation).order_by(desc(ScoutEvaluation.created_at)).limit(30)
        )).scalars().all()

    session_items = []
    for s in sessions:
        session_items.append({
            "id": s.id,
            "collector_name": s.collector_name or "Sem nome",
            "location": s.location,
            "started_at": s.started_at.strftime("%d/%m %H:%M") if s.started_at else "",
            "closed": s.closed_at is not None,
        })

    recent_items = []
    for r in recent:
        images = json.loads(r.images) if r.images else []
        recent_items.append({
            "id": r.id,
            "thumbnail": images[0] if images else "",
            "player_name": r.player_name or "Não identificado",
            "club": r.club,
            "item_type": r.item_type,
            "condition": r.condition,
            "recommendation": r.recommendation,
            "authenticity_score": r.authenticity_score,
            "sell_price_estimate": r.sell_price_estimate,
            "offer_min": r.offer_min,
            "offer_max": r.offer_max,
            "created_at": r.created_at.strftime("%d/%m %H:%M") if r.created_at else "",
        })

    return templates.TemplateResponse(request, "scout_history.html", {
        "sessions": session_items,
        "recent": recent_items,
        "active_page": "scout_history",
    })
