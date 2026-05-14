from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field

from app.extensions import db
from app.models import Analysis, LensResult


LENS_ORDER = ["viability", "risk", "timing", "differentiation", "personal_fit"]
LENS_WEIGHTS = {
    "viability": 0.25,
    "risk": 0.20,
    "timing": 0.20,
    "differentiation": 0.20,
    "personal_fit": 0.15,
}


class LensPayload(BaseModel):
    score: int = Field(ge=0, le=100)
    headline: str = Field(min_length=1, max_length=180)
    analysis: str = Field(min_length=1)
    blind_spot: str = Field(min_length=1)
    green_light: bool


class PrismAnalysisPayload(BaseModel):
    viability: LensPayload
    risk: LensPayload
    timing: LensPayload
    differentiation: LensPayload
    personal_fit: LensPayload
    composite_score: int = Field(ge=0, le=100)
    verdict: str = Field(min_length=1)


def compute_composite_score(payload: PrismAnalysisPayload) -> int:
    total = 0.0
    for lens_name, weight in LENS_WEIGHTS.items():
        total += getattr(payload, lens_name).score * weight
    return round(total)


def store_analysis_result(
    analysis: Analysis, payload: PrismAnalysisPayload, model_used: str
) -> Analysis:
    analysis.composite_score = compute_composite_score(payload)
    analysis.verdict = payload.verdict.strip()
    analysis.status = "complete"
    analysis.model_used = model_used
    analysis.error_message = None
    analysis.completed_at = datetime.now(timezone.utc)

    for existing in list(analysis.lens_results):
        db.session.delete(existing)

    for order, lens_name in enumerate(LENS_ORDER):
        lens_payload = getattr(payload, lens_name)
        db.session.add(
            LensResult(
                analysis=analysis,
                lens_name=lens_name,
                display_order=order,
                score=lens_payload.score,
                headline=lens_payload.headline.strip(),
                analysis_text=lens_payload.analysis.strip(),
                blind_spot=lens_payload.blind_spot.strip(),
                green_light=lens_payload.green_light,
            )
        )

    db.session.commit()
    return analysis


def mark_analysis_failed(analysis: Analysis, message: str) -> Analysis:
    analysis.status = "failed"
    analysis.error_message = message[:1000]
    analysis.completed_at = datetime.now(timezone.utc)
    db.session.commit()
    return analysis
