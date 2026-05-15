"""Smart Router — classifies message complexity and selects the optimal model.

Inspired by PicoClaw's smart routing: simple queries go to lightweight models,
saving API costs while maintaining quality for complex tasks.
"""

import re
from dataclasses import dataclass
from typing import Any

from loguru import logger


@dataclass
class RoutingDecision:
    """Result of the smart routing classification."""
    tier: str           # "light", "default", "heavy"
    model: str          # Model to use
    reason: str         # Why this tier was chosen


# Patterns that indicate a simple/greeting message
_SIMPLE_PATTERNS = re.compile(
    r"^(oi|olá|ola|hey|hi|hello|bom dia|boa tarde|boa noite|e aí|eai|"
    r"fala|salve|tudo bem|como vai|obrigado|obrigada|valeu|vlw|ok|"
    r"thanks|thank you|sim|não|nao|yes|no|blz|beleza|tchau|bye|"
    r"flw|falou|até|ate mais|bom|legal|show|massa|top|nice|👍|😊|🙂)[\s!?.]*$",
    re.IGNORECASE
)

# Patterns that indicate a complex task requiring tools
_COMPLEX_INDICATORS = [
    r"analis[ae]",
    r"criac?[ão]|crie|gere|gerar|criar",
    r"relat[oó]rio",
    r"c[oó]digo|script|programa",
    r"pesquis[ae]|busca|search",
    r"email|e-mail",
    r"agenda|calend[aá]rio",
    r"document|pdf|xlsx|docx|csv",
    r"execut[ae]|rodar|instalar",
    r"configur[ae]",
    r"deploy|servidor|vps|docker",
    r"banco de dados|database|supabase",
    r"curriculo|curr[ií]culo",
    r"planilha|spreadsheet",
]

_COMPLEX_PATTERN = re.compile("|".join(_COMPLEX_INDICATORS), re.IGNORECASE)


class SmartRouter:
    """Routes messages to the optimal model based on complexity analysis."""

    def __init__(
        self,
        default_model: str,
        light_model: str = "google/gemini-2.0-flash-lite",
        heavy_model: str | None = None,
        enabled: bool = True,
    ):
        self.default_model = default_model
        self.light_model = light_model
        self.heavy_model = heavy_model or default_model
        self.enabled = enabled
        self._stats = {"light": 0, "default": 0, "heavy": 0}

    def classify(self, message: str) -> RoutingDecision:
        """Classify a message and return the optimal model.

        Classification tiers:
        - light: Greetings, simple yes/no, short acknowledgments
        - default: Normal questions, moderate complexity
        - heavy: Multi-step tasks, code generation, analysis
        """
        if not self.enabled:
            return RoutingDecision(
                tier="default",
                model=self.default_model,
                reason="Smart routing disabled"
            )

        clean = message.strip()

        # Tier 1: Simple greetings and acknowledgments
        if _SIMPLE_PATTERNS.match(clean) or len(clean) < 15:
            self._stats["light"] += 1
            logger.debug("SmartRouter: LIGHT tier for '{}'", clean[:30])
            return RoutingDecision(
                tier="light",
                model=self.light_model,
                reason=f"Mensagem simples ({len(clean)} chars)"
            )

        # Tier 3: Complex tasks (tools, analysis, code)
        if _COMPLEX_PATTERN.search(clean) or len(clean) > 500:
            self._stats["heavy"] += 1
            logger.debug("SmartRouter: HEAVY tier for '{}'", clean[:30])
            return RoutingDecision(
                tier="heavy",
                model=self.heavy_model,
                reason="Tarefa complexa detectada"
            )

        # Tier 2: Default
        self._stats["default"] += 1
        return RoutingDecision(
            tier="default",
            model=self.default_model,
            reason="Complexidade padrão"
        )

    def get_stats(self) -> dict[str, Any]:
        """Return routing statistics."""
        total = sum(self._stats.values()) or 1
        return {
            "enabled": self.enabled,
            "models": {
                "light": self.light_model,
                "default": self.default_model,
                "heavy": self.heavy_model,
            },
            "stats": {
                "total": total,
                **{k: {"count": v, "pct": f"{v/total*100:.0f}%"} for k, v in self._stats.items()}
            }
        }
