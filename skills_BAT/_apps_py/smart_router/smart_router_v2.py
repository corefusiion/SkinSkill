"""
Smart Router V2 — Scoring-based classification for optimal model routing.
Robust, extensible, configurable. Replaces regex fragility with weighted scoring.
"""

import re
from dataclasses import dataclass
from typing import Any, List, Dict, Optional
from abc import ABC, abstractmethod

from loguru import logger


@dataclass
class RoutingDecision:
    &quot;&quot;&quot;Result of the smart routing classification.&quot;&quot;&quot;
    tier: str           # &quot;light&quot;, &quot;default&quot;, &quot;heavy&quot;
    model: str          # Model to use
    reason: str         # Why this tier was chosen
    score: float = 0.0  # Total score (0-100)  # NEW: Transparency


@dataclass
class ScorerResult:
    &quot;&quot;&quot;Individual scorer output for logging.&quot;&quot;&quot;
    name: str
    score: float
    reason: str


class BaseScorer(ABC):
    &quot;&quot;&quot;Pluggable scoring strategy (SRP).&quot;&quot;&quot;

    @abstractmethod
    def score(self, message: str) -> ScorerResult:
        pass


class LengthScorer(BaseScorer):
    &quot;&quot;&quot;Score based on message length (simple heuristic).&quot;&quot;&quot;

    MAX_LIGHT_LEN = 50
    MAX_SCORE_LEN = 1000

    def score(self, message: str) -> ScorerResult:
        length = len(message.strip())
        if length &lt; self.MAX_LIGHT_LEN:
            score = 10.0
            reason = f&quot;Short ({length} chars)&quot;
        else:
            score = min(20.0 * (length / self.MAX_SCORE_LEN), 20.0)
            reason = f&quot;Length-based ({length} chars)&quot;
        return ScorerResult(&quot;Length&quot;, score, reason)


class KeywordScorer(BaseScorer):
    &quot;&quot;&quot;Score based on simple vs complex keywords.&quot;&quot;&quot;

    SIMPLE_PATTERNS = re.compile(
        r&quot;\b(oi|olá|hey|hi|hello|sim|não|ok|thanks|bye|blz|legal|tchau)\b&quot;,
        re.IGNORECASE
    )
    COMPLEX_INDICATORS = [
        r&quot;\b(analis[ae]|criac?ão|crie|gere|pesquis[ae]|c[oó]digo|script|database|deploy|configur[ae])\b&quot;
    ]
    COMPLEX_PATTERN = re.compile(&quot;|&quot;.join(COMPLEX_INDICATORS), re.IGNORECASE)

    def score(self, message: str) -> ScorerResult:
        clean = message.lower()
        if self.SIMPLE_PATTERNS.search(clean):
            score = -30.0
            reason = &quot;Simple greeting/ack&quot;
        elif self.COMPLEX_PATTERN.search(clean):
            score = 50.0
            reason = &quot;Complex task indicators&quot;
        else:
            score = 0.0
            reason = &quot;Neutral keywords&quot;
        return ScorerResult(&quot;Keywords&quot;, score, reason)


class SmartRouterV2:
    &quot;&quot;&quot;V2: Scoring-based router with pluggable scorers.&quot;&quot;&quot;

    DEFAULT_THRESHOLDS = {&quot;light&quot;: 30, &quot;heavy&quot;: 70}
    DEFAULT_WEIGHTS = {&quot;length&quot;: 0.3, &quot;keywords&quot;: 0.7}  # Extensível

    def __init__(
        self,
        default_model: str,
        light_model: str = &quot;google/gemini-2.0-flash-lite&quot;,
        heavy_model: str | None = None,
        enabled: bool = True,
        thresholds: Optional[Dict[str, float]] = None,
        weights: Optional[Dict[str, float]] = None,
    ):
        self.default_model = default_model
        self.light_model = light_model
        self.heavy_model = heavy_model or default_model
        self.enabled = enabled
        self.thresholds = thresholds or self.DEFAULT_THRESHOLDS
        self.weights = weights or self.DEFAULT_WEIGHTS
        self.scorers: List[BaseScorer] = [LengthScorer(), KeywordScorer()]
        self._stats = {&quot;light&quot;: 0, &quot;default&quot;: 0, &quot;heavy&quot;: 0, &quot;avg_scores&quot;: {}}

    def add_scorer(self, scorer: BaseScorer, weight: float):
        &quot;&quot;&quot;Extensível: Add custom scorer.&quot;&quot;&quot;
        self.scorers.append(scorer)
        self.weights[scorer.__class__.__name__.lower()] = weight

    def _aggregate_scores(self, results: List[ScorerResult]) -> tuple[float, List[ScorerResult]]:
        &quot;&quot;&quot;Weighted sum (0-100).&quot;&quot;&quot;
        total = 0.0
        for res in results:
            w = self.weights.get(res.name.lower(), 1.0)
            total += res.score * w
        total = max(0, min(100, total))  # Clamp
        return total, results

    def classify(self, message: str) -> RoutingDecision:
        if not self.enabled:
            return RoutingDecision(&quot;default&quot;, self.default_model, &quot;Disabled&quot;, 50.0)

        clean_msg = message.strip()
        results = [scorer.score(clean_msg) for scorer in self.scorers]
        score, breakdown = self._aggregate_scores(results)

        if score &lt; self.thresholds[&quot;light&quot;]:
            tier, model, reason = &quot;light&quot;, self.light_model, f&quot;Low complexity (score: {score:.1f})&quot;
            self._stats[&quot;light&quot;] += 1
        elif score &gt; self.thresholds[&quot;heavy&quot;]:
            tier, model, reason = &quot;heavy&quot;, self.heavy_model, f&quot;High complexity (score: {score:.1f})&quot;
            self._stats[&quot;heavy&quot;] += 1
        else:
            tier, model, reason = &quot;default&quot;, self.default_model, f&quot;Medium (score: {score:.1f})&quot;
            self._stats[&quot;default&quot;] += 1

        logger.debug(
            &quot;RouterV2: {} | score={:.1f} | breakdown={}&quot;,
            reason, score, [(r.name, r.score) for r in breakdown]
        )
        self._stats[&quot;avg_scores&quot;].setdefault(tier, []).append(score)

        return RoutingDecision(tier, model, reason, score)

    def get_stats(self) -> Dict[str, Any]:
        total = sum(self._stats[k] for k in [&quot;light&quot;, &quot;default&quot;, &quot;heavy&quot;]) or 1
        avg_scores = {
            tier: sum(scores)/len(scores) if scores else 0
            for tier, scores in self._stats[&quot;avg_scores&quot;].items()
        }
        return {
            &quot;enabled&quot;: self.enabled,
            &quot;models&quot;: {
                &quot;light&quot;: self.light_model,
                &quot;default&quot;: self.default_model,
                &quot;heavy&quot;: self.heavy_model,
            },
            &quot;thresholds&quot;: self.thresholds,
            &quot;stats&quot;: {
                &quot;total&quot;: total,
                **{k: {&quot;count&quot;: v, &quot;pct&quot;: f&quot;{v/total*100:.0f}%&quot;} for k, v in self._stats.items() if k != &quot;avg_scores&quot;},
                &quot;avg_scores&quot;: avg_scores,
            },
        }