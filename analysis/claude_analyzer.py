import base64
import json
import logging

import httpx

from config.settings import settings

logger = logging.getLogger(__name__)

def _mock_mode() -> bool:
    return not settings.gemini_api_key and not settings.anthropic_api_key

EXTRACT_PROMPT = """Você é um especialista em camisetas esportivas de colecionador.
Analise este anúncio e responda APENAS com JSON, sem texto adicional.

Determine se é um item genuíno de colecionador (autógrafo real de mão, match worn, certificado real)
ou uma camisa personalizada/de loja (nome impresso, produto de prateleira).

{{
  "player_name": "nome do jogador se mencionado, string vazia se não",
  "club": "clube",
  "year_era": "ano ou era (ex: 1994, anos 80)",
  "is_autographed": true se tem autógrafo REAL de mão (não impresso),
  "is_match_worn": true se foi usada em jogo real,
  "has_coa": true se tem certificado de autenticidade real (PSA, Beckett, JSA, SB Brasil, Fabricks),
  "coa_type": "PSA, Beckett, JSA, SB Brasil, Fabricks ou null",
  "is_personalized_jersey": true se é camisa nova personalizada/de loja (nome impresso, não autógrafo real),
  "condition": "nova, boa, regular ou ruim",
  "authenticity_score": número de 0 a 100,
  "fake_suspicion": true ou false,
  "fake_reason": "motivo se houver suspeita, string vazia se não"
}}

Anúncio:
Título: {title}
Descrição: {description}
Preço: R$ {price}"""

VISION_PROMPT = """Você é um especialista em autenticidade de camisetas esportivas autografadas.
Analise estas fotos e responda APENAS com JSON.

Verifique:
1. O autógrafo parece de mão (traço orgânico, pressão variável) ou impresso/autopen?
2. Há certificado de autenticidade visível?
3. A camisa parece original ou réplica?
4. Há etiquetas, holograma ou outros indicadores de autenticidade?

{{
  "signature_looks_genuine": true ou false,
  "signature_confidence": número de 0 a 100,
  "autopen_suspected": true se o traço parece mecânico/uniforme demais,
  "labels_consistent": true se etiquetas batem com a era declarada,
  "likely_fake": true ou false,
  "visual_red_flags": ["lista de problemas encontrados"],
  "authenticity_score": número de 0 a 100,
  "notes": "observações relevantes"
}}"""


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

_SONNET = "claude-sonnet-4-6"
_HAIKU  = "claude-haiku-4-5-20251001"

# Sonnet apenas para ícones absolutos COM certificação no mesmo título.
# Qualquer lenda sem PSA/Beckett/COA → Haiku (muito mais barato, qualidade suficiente).
_SONNET_REQUIRED = [
    "psa", "beckett", "jsa",  # certificação de terceiros reconhecida
]
_ICON_NAMES = [
    "pelé", "pele", "maradona", "michael jordan", "kobe bryant", "garrincha",
]


def _select_model(listing: dict) -> str:
    title = (listing.get("title") or "").lower()
    has_cert = any(s in title for s in _SONNET_REQUIRED)
    has_icon = any(s in title for s in _ICON_NAMES)
    if has_cert and has_icon:
        return _SONNET
    return _HAIKU


async def _gemini_text(prompt: str) -> str:
    from google import genai
    client = genai.Client(api_key=settings.gemini_api_key)
    response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
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
    response = client.models.generate_content(model=GEMINI_MODEL, contents=parts)
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


async def _call_anthropic_vision(images_b64: list[tuple[str, str]], prompt: str, model: str = _HAIKU) -> str:
    import anthropic
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    content = [
        {"type": "image", "source": {"type": "base64", "media_type": m, "data": d}}
        for d, m in images_b64
    ]
    content.append({"type": "text", "text": prompt})
    msg = await client.messages.create(
        model=model, max_tokens=512,
        messages=[{"role": "user", "content": content}],
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

    # Limita descrição a 400 chars para economizar tokens de input
    prompt = EXTRACT_PROMPT.format(
        title=listing.get("title", ""),
        description=(listing.get("description") or "")[:400],
        price=listing.get("price", 0),
    )

    # Anthropic Haiku — rápido e barato. Sonnet apenas para ícones absolutos com COA/PSA.
    text = None
    if settings.anthropic_api_key:
        model = _select_model(listing)
        try:
            text = await _call_anthropic_text(prompt, model)
            logger.debug(f"[AI] Anthropic OK ({model})")
        except Exception as e:
            logger.warning(f"[AI] Anthropic falhou: {e}")

    if text is None:
        logger.warning("[AI] Anthropic falhou — usando mock")
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

    images_b64 = []
    async with httpx.AsyncClient(timeout=15) as client:
        for url in image_urls[:2]:  # máx 2 imagens — reduz custo
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

    # Sempre Haiku para visão — Sonnet vision é 12x mais caro sem ganho relevante
    text = None
    if settings.anthropic_api_key:
        try:
            text = await _call_anthropic_vision(images_b64, VISION_PROMPT, _HAIKU)
        except Exception as e:
            logger.warning(f"[Vision] Anthropic falhou: {e}")

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
