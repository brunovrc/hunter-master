"""
Análise de imagem para o Hunter Scout.

Diferente do analysis/claude_analyzer.py (que audita ANÚNCIOS já escritos por
terceiros e prioriza custo mínimo por rodar em alto volume), aqui o volume é
baixo — algumas dezenas de avaliações por visita — então priorizamos precisão:
usamos o Gemini Flash "cheio" (não o Lite) como modelo principal.
"""
import json
import logging

from config.settings import settings
from scout.schemas import VisionResult

logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-2.0-flash"
_HAIKU = "claude-haiku-4-5-20251001"


SCOUT_PROMPT = """Você é um autenticador experiente de camisetas esportivas de colecionador \
(futebol e basquete), avaliando peças em uma visita a um colecionador/acervo particular.

Analise as fotos anexadas (frente da camisa, e possivelmente etiqueta, autógrafo ou COA \
em close-up) e retorne APENAS um JSON, sem nenhum texto antes ou depois:

{{
  "player_name": "",
  "club": "",
  "year_era": "",
  "item_type_guess": "autografada|match_worn|retro|player_issue|desconhecido",
  "is_autographed": false,
  "is_match_worn": false,
  "has_coa": false,
  "signature_looks_genuine": null,
  "condition": "excelente|boa|regular|ruim",
  "authenticity_score": 50,
  "replica_suspicion": false,
  "identified_text": "",
  "notes": ""
}}

Instruções:
- player_name/club/year_era: identifique pelo escudo, número, nome nas costas, corte do \
tecido e patches visíveis. Deixe vazio se não conseguir identificar com confiança.
- signature_looks_genuine: true se o traço do autógrafo parece feito à mão (variação de \
pressão, tinta real); false se parece impresso/autopen/serigrafia; null se não há autógrafo \
visível nas fotos.
- has_coa: true se há certificado de autenticidade (COA), holograma (PSA/Beckett/JSA) ou \
selo de autenticação visível em alguma foto.
- condition: avalie o estado físico do tecido — manchas, furos, desbotamento, gola.
- authenticity_score (0-100): confiança geral de que é uma peça original e (se alegada) \
realmente autografada à mão. Réplica óbvia = score baixo (<20).
- replica_suspicion: true se a peça parece tailandesa/réplica/fake — corte errado, \
tecido brilhante demais, escudo bordado malfeito, fonte de número errada.
- identified_text: transcreva qualquer texto legível nas fotos (nome na etiqueta, \
inscrição no autógrafo, número de série do COA).

{context}
Contexto extra informado pelo usuário: {user_notes}

Retorne o JSON preenchido."""


def _parse_json(text: str) -> dict:
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end == 0:
        return {}
    return json.loads(text[start:end])


async def _gemini_vision(images: list[tuple[bytes, str]], prompt: str) -> str:
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=settings.gemini_api_key)
    parts = [
        types.Part.from_bytes(data=data, mime_type=mime)
        for data, mime in images
    ]
    parts.append(prompt)
    response = await client.aio.models.generate_content(model=GEMINI_MODEL, contents=parts)
    return response.text


async def _anthropic_vision(images: list[tuple[bytes, str]], prompt: str) -> str:
    import base64
    import anthropic
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    content = [
        {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": mime,
                "data": base64.standard_b64encode(data).decode(),
            },
        }
        for data, mime in images
    ]
    content.append({"type": "text", "text": prompt})
    msg = await client.messages.create(
        model=_HAIKU, max_tokens=700,
        messages=[{"role": "user", "content": content}],
    )
    return msg.content[0].text


def _mock_result(user_notes: str) -> VisionResult:
    logger.warning("[Scout] Nenhuma API de IA configurada — retornando resultado mock")
    return VisionResult(
        notes="Modo mock — configure GEMINI_API_KEY ou ANTHROPIC_API_KEY para análise real.",
    )


async def evaluate_jersey(images: list[tuple[bytes, str]], user_notes: str = "") -> VisionResult:
    """
    images: lista de (bytes, mime_type) — já redimensionadas no cliente.
    Tenta Gemini Flash primeiro (melhor leitura de imagem), cai para Haiku Vision
    se o Gemini falhar. Nunca lança — sempre devolve um VisionResult (mock em último caso).
    """
    if not settings.gemini_api_key and not settings.anthropic_api_key:
        return _mock_result(user_notes)

    prompt = SCOUT_PROMPT.format(context="", user_notes=user_notes or "(nenhum)")

    text = None
    if settings.gemini_api_key:
        try:
            text = await _gemini_vision(images, prompt)
            logger.info("[Scout] Avaliação via Gemini OK")
        except Exception as e:
            logger.warning(f"[Scout] Gemini falhou: {e}")

    if text is None and settings.anthropic_api_key:
        try:
            text = await _anthropic_vision(images, prompt)
            logger.info("[Scout] Avaliação via Haiku (fallback) OK")
        except Exception as e:
            logger.warning(f"[Scout] Haiku fallback falhou: {e}")

    if text is None:
        return _mock_result(user_notes)

    try:
        raw = _parse_json(text)
        return VisionResult(**raw)
    except Exception as e:
        logger.error(f"[Scout] Falha ao interpretar resposta da IA: {e} | raw: {text[:300]}")
        return VisionResult(notes="A IA retornou um formato inesperado — revise manualmente.")
