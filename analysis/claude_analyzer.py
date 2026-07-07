import base64
import json
import logging
from datetime import date

import httpx

from config.settings import settings

logger = logging.getLogger(__name__)

# ── Teto diário de chamadas de IA — protege contra estouro de custo ───────────
_MAX_AI_CALLS_PER_DAY = 400
_ai_calls_today = 0
_ai_calls_date = date.today()


def _ai_budget_ok() -> bool:
    global _ai_calls_today, _ai_calls_date
    today = date.today()
    if today != _ai_calls_date:
        _ai_calls_date = today
        _ai_calls_today = 0
    if _ai_calls_today >= _MAX_AI_CALLS_PER_DAY:
        logger.warning(f"[Budget] Teto diário de {_MAX_AI_CALLS_PER_DAY} chamadas atingido — usando mock")
        return False
    return True


def _count_ai_call():
    global _ai_calls_today
    _ai_calls_today += 1

def _mock_mode() -> bool:
    return not settings.gemini_api_key and not settings.anthropic_api_key

EXTRACT_PROMPT = """Especialista em camisetas esportivas de colecionador. JSON apenas, sem texto.

{{"player_name":"","club":"","year_era":"","is_autographed":false,"is_match_worn":false,"has_coa":false,"coa_type":null,"is_personalized_jersey":false,"condition":"boa","authenticity_score":50,"fake_suspicion":false,"fake_reason":""}}

Título: {title}
Descrição: {description}
Preço: R${price}

Retorne JSON com os campos acima preenchidos. is_personalized_jersey=true se for camisa nova de loja/nome impresso."""

VISION_PROMPT = """Analise autenticidade desta camisa esportiva autografada. JSON apenas.

{{"signature_looks_genuine":true,"signature_confidence":60,"autopen_suspected":false,"labels_consistent":true,"likely_fake":false,"visual_red_flags":[],"authenticity_score":60,"notes":""}}

Verifique: autógrafo é de mão (traço orgânico) ou impresso/autopen? COA visível? Camisa original ou réplica? Retorne JSON preenchido."""


def _mock_extract(listing: dict) -> dict:
    title = listing.get("title", "").lower()
    has_coa = any(k in title for k in ["psa", "beckett", "jsa", "coa", "certificad", "sb brasil", "fabricks"])
    is_autographed = any(k in title for k in ["autografad", "autógrafo", "autografo", "autograf", "assinad"])
    is_match_worn = any(k in title for k in ["match worn", "jogo", "usada em jogo"])
    has_match_context = any(k in title for k in ["jogo", "match worn", "usada em jogo", "player worn", "game worn"])
    is_personalized = (
        not has_match_context
        and any(k in title for k in ["puma", "nike", "adidas", "umbro"])
        and any(s in f" {title} " for s in [" m ", " g ", " gg ", " p ", " xl ", " xg "])
    )
    logger.info(f"[MOCK] Analisando: {listing.get('title', '')[:60]}")
    return {
        "player_name": "",
        "club": "",
        "year_era": "",
        "is_autographed": is_autographed,
        "is_match_worn": is_match_worn,
        "has_coa": has_coa,
        "coa_type": None,
        "is_personalized_jersey": is_personalized,
        "condition": "boa",
        "authenticity_score": 75 if has_coa else (50 if is_autographed else 20),
        "fake_suspicion": is_personalized,
        "fake_reason": "Parece camisa personalizada de loja" if is_personalized else "",
    }


def _mock_vision(image_urls: list) -> dict:
    logger.info(f"[MOCK] Analise visual: {len(image_urls)} imagens (modo mock)")
    return {
        "signature_looks_genuine": True,
        "signature_confidence": 60,
        "autopen_suspected": False,
        "labels_consistent": True,
        "likely_fake": False,
        "visual_red_flags": [],
        "authenticity_score": 60,
        "notes": "Modo mock — analise visual nao executada",
    }


def _parse_json(text: str) -> dict:
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end == 0:
        return {}
    return json.loads(text[start:end])


GEMINI_MODEL = "gemini-2.0-flash-lite"

_HAIKU = "claude-haiku-4-5-20251001"


async def _gemini_text(prompt: str) -> str:
    from google import genai
    client = genai.Client(api_key=settings.gemini_api_key)
    response = await client.aio.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    return response.text


async def _gemini_vision(images_b64: list[tuple[str, str]], prompt: str) -> str:
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=settings.gemini_api_key)
    parts = [
        types.Part.from_bytes(data=base64.b64decode(data), mime_type=mime)
        for data, mime in images_b64
    ]
    parts.append(prompt)
    response = await client.aio.models.generate_content(model=GEMINI_MODEL, contents=parts)
    return response.text


async def _call_anthropic_text(prompt: str, model: str = _HAIKU) -> str:
    import anthropic
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    msg = await client.messages.create(
        model=model,
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


# Só vale chamar AI se o item reivindica autógrafo, COA ou match worn.
# Itens retro sem essas flags → mock (sem custo de token).
_NEEDS_AI_SIGNALS = [
    "autografad", "autógrafo", "autografo", "autograf", "assinad", "firmad",
    "signed", "autographed", "signe",
    "match worn", "usada em jogo", "usada no jogo", "player worn", "game worn", "match issue",
    "coa", "psa", "beckett", "jsa", "certificad", "sb brasil", "fabricks",
]


async def extract_listing_data(listing: dict) -> dict:
    if _mock_mode():
        return _mock_extract(listing)

    # Sem sinal de autógrafo/COA → não vale o custo de AI
    title_lower = (listing.get("title") or "").lower()
    if not any(s in title_lower for s in _NEEDS_AI_SIGNALS):
        logger.debug(f"[AI] Sem sinal auth — skip AI: {listing.get('title','')[:50]}")
        return _mock_extract(listing)

    # Teto diário de custo — estourou, volta pro mock (heurística por título)
    if not _ai_budget_ok():
        return _mock_extract(listing)

    # Limita descrição a 400 chars para economizar tokens de input
    prompt = EXTRACT_PROMPT.format(
        title=listing.get("title", ""),
        description=(listing.get("description") or "")[:400],
        price=listing.get("price", 0),
    )

    # Gemini Flash Lite primeiro (~13x mais barato que Haiku); Haiku só como fallback
    text = None
    if settings.gemini_api_key:
        try:
            text = await _gemini_text(prompt)
            _count_ai_call()
            logger.debug("[AI] Gemini OK")
        except Exception as e:
            logger.warning(f"[AI] Gemini falhou: {e}")

    if text is None and settings.anthropic_api_key:
        try:
            text = await _call_anthropic_text(prompt, _HAIKU)
            _count_ai_call()
            logger.debug("[AI] Haiku fallback OK")
        except Exception as e:
            logger.warning(f"[AI] Haiku fallback falhou: {e}")

    if text is None:
        logger.warning("[AI] Todas as APIs falharam — usando mock")
        return _mock_extract(listing)

    try:
        result = _parse_json(text)
        logger.info(
            f"[AI] {listing.get('title', '')[:50]} → "
            f"autografado={result.get('is_autographed')} "
            f"personalizada={result.get('is_personalized_jersey')} "
            f"score={result.get('authenticity_score')}"
        )
        return result
    except Exception as e:
        logger.warning(f"[AI] JSON parse falhou: {e} | raw: {text[:200]}")
        return _mock_extract(listing)


async def analyze_images(image_urls: list, listing: dict | None = None) -> dict:
    if _mock_mode() or not image_urls:
        return _mock_vision(image_urls)

    # Visão só vale a pena se houver autógrafo ou COA declarado no título.
    # Para itens vintage/player issue sem autógrafo explícito, pular visão economiza custo.
    title_lower = (listing.get("title") or "").lower() if listing else ""
    _needs_vision = any(s in title_lower for s in [
        "autografad", "assinad", "signed", "autographed", "signe",
        "coa", "psa", "beckett", "jsa", "match worn",
    ])
    if not _needs_vision:
        return {"authenticity_score": 55, "likely_fake": False, "visual_red_flags": []}

    if not _ai_budget_ok():
        return {"authenticity_score": 50, "likely_fake": False, "visual_red_flags": []}

    images_b64 = []
    async with httpx.AsyncClient(timeout=15) as client:
        for url in image_urls[:1]:  # 1 imagem basta para triagem — corta custo pela metade
            try:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = base64.standard_b64encode(resp.content).decode()
                    mime = resp.headers.get("content-type", "image/jpeg").split(";")[0]
                    images_b64.append((data, mime))
            except Exception:
                continue

    if not images_b64:
        return {"authenticity_score": 30, "likely_fake": False, "visual_red_flags": ["IMAGES_UNAVAILABLE"]}

    # Visão APENAS no Gemini Flash Lite. Sem fallback pro Haiku Vision —
    # imagem no Haiku custa ~10x mais; se o Gemini falhar, seguimos sem visão.
    text = None
    if settings.gemini_api_key:
        try:
            text = await _gemini_vision(images_b64, VISION_PROMPT)
            _count_ai_call()
            logger.debug("[Vision] Gemini OK")
        except Exception as e:
            logger.warning(f"[Vision] Gemini falhou: {e}")

    if text is None:
        return {"authenticity_score": 50, "likely_fake": False, "visual_red_flags": []}

    try:
        result = _parse_json(text)
        if result.get("autopen_suspected"):
            result.setdefault("visual_red_flags", []).append("AUTOPEN_SUSPECTED")
        if result.get("likely_fake"):
            result.setdefault("visual_red_flags", []).append("LIKELY_FAKE_VISUAL")
        return result
    except Exception as e:
        logger.warning(f"[Vision] JSON parse falhou: {e}")
        return {"authenticity_score": 50, "likely_fake": False, "visual_red_flags": []}
