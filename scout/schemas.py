"""
Contratos de dados do Hunter Scout — tipados com Pydantic para validar
tanto a saída da IA (que pode alucinar campos) quanto a resposta da API.
"""
from typing import Optional

from pydantic import BaseModel, Field, field_validator

_VALID_CONDITIONS = {"excelente", "boa", "regular", "ruim"}
_VALID_ITEM_TYPES = {"autografada", "match_worn", "retro", "player_issue", "desconhecido"}


class VisionResult(BaseModel):
    """Saída bruta e validada da análise de imagem. Todo campo tem default
    seguro — se a IA devolver JSON incompleto, isso não derruba o pipeline."""

    player_name: str = ""
    club: str = ""
    year_era: str = ""
    item_type_guess: str = "desconhecido"
    is_autographed: bool = False
    is_match_worn: bool = False
    has_coa: bool = False
    signature_looks_genuine: Optional[bool] = None
    condition: str = "boa"
    authenticity_score: int = Field(default=50, ge=0, le=100)
    replica_suspicion: bool = False
    identified_text: str = ""
    notes: str = ""

    @field_validator("condition")
    @classmethod
    def _clamp_condition(cls, v: str) -> str:
        v = (v or "").lower().strip()
        return v if v in _VALID_CONDITIONS else "boa"

    @field_validator("item_type_guess")
    @classmethod
    def _clamp_item_type(cls, v: str) -> str:
        v = (v or "").lower().strip()
        return v if v in _VALID_ITEM_TYPES else "desconhecido"


class ScoutResult(BaseModel):
    """Resultado final mostrado ao usuário — vision + preço + oferta."""

    player_name: str
    club: str
    year_era: str
    item_type: str
    condition: str
    is_autographed: bool
    is_match_worn: bool
    has_coa: bool
    signature_looks_genuine: Optional[bool]
    replica_suspicion: bool
    authenticity_score: int
    identified_text: str
    ai_notes: str

    sell_price_estimate: float
    offer_min: float
    offer_max: float
    recommendation: str  # COMPRAR | NEGOCIAR | VERIFICAR
    recommendation_reason: str
