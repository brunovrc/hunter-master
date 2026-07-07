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


FOLLOWUP_PROMPT = """Você já analisou esta camisa esportiva de colecionador anteriormente, \
com o seguinte resultado (mesmas fotos anexadas agora):

Jogador: {player_name}
Clube: {club}
Época: {year_era}
Tipo: {item_type}
Autografada: {is_autographed}
COA: {has_coa}
Autenticidade: {authenticity_score}/100
Observações anteriores: {ai_notes}

ANÚNCIOS REAIS PARECIDOS ENCONTRADOS AGORA (banco próprio + busca ao vivo no Vinted):
{comparables}

O usuário tem uma pergunta de acompanhamento sobre esta MESMA camisa. Regras da resposta:
- Você JÁ TEM acesso a comparáveis reais (lista acima) — não diga "não consigo buscar na \
internet" ou "não tenho acesso a plataformas de leilão". Use os números da lista para \
sustentar sua resposta. Se a lista vier vazia, diga isso em uma frase e siga com o que \
souber pelo contexto — não transforme isso no assunto principal da resposta.
- Seja ASSERTIVO: dê uma faixa de valor ou resposta direta, não uma lista de "consulte X, \
verifique Y". Uma pessoa em pé na casa do vendedor precisa de uma resposta que sirva AGORA.
- Máximo 4-5 frases corridas ou uma lista curta de até 4 itens. Nunca escreva "##" ou \
títulos de seção — isso é um chat, não um relatório.
- Responda só o que foi perguntado. Não repita o que já foi dito na avaliação original.

Pergunta do usuário: {question}"""


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


def _format_comparables(comparables: list[dict] | None) -> str:
    if not comparables:
        return "(nenhum comparável encontrado agora)"
    lines = [
        f"- R${c['price']:,.0f} — {c['title']} ({c['platform']}) — {c['url']}"
        for c in comparables
    ]
    return "\n".join(lines)


async def ask_followup(
    images: list[tuple[bytes, str]],
    context: dict,
    question: str,
    comparables: list[dict] | None = None,
) -> str:
    """
    Responde uma pergunta de acompanhamento sobre uma avaliação já feita,
    reaproveitando as mesmas fotos + o resultado da análise original como
    contexto — sem precisar tirar foto de novo. `comparables` são anúncios
    reais já buscados (scout/comparables.py) — a IA usa como referência de
    preço em vez de alegar que não tem acesso à internet.
    """
    if not settings.gemini_api_key and not settings.anthropic_api_key:
        return "Nenhuma API de IA configurada — não é possível responder agora."

    prompt = FOLLOWUP_PROMPT.format(
        player_name=context.get("player_name") or "não identificado",
        club=context.get("club") or "não identificado",
        year_era=context.get("year_era") or "não identificada",
        item_type=context.get("item_type") or "desconhecido",
        is_autographed=context.get("is_autographed"),
        has_coa=context.get("has_coa"),
        authenticity_score=context.get("authenticity_score"),
        ai_notes=context.get("ai_notes") or "(nenhuma)",
        comparables=_format_comparables(comparables),
        question=question,
    )

    text = None
    if settings.gemini_api_key:
        try:
            text = await _gemini_vision(images, prompt)
            logger.info("[Scout] Pergunta de acompanhamento via Gemini OK")
        except Exception as e:
            logger.warning(f"[Scout] Pergunta via Gemini falhou: {e}")

    if text is None and settings.anthropic_api_key:
        try:
            text = await _anthropic_vision(images, prompt)
            logger.info("[Scout] Pergunta de acompanhamento via Haiku OK")
        except Exception as e:
            logger.warning(f"[Scout] Pergunta via Haiku falhou: {e}")

    return text or "Não foi possível obter resposta da IA agora. Tente novamente em instantes."
