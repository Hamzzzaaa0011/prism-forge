from __future__ import annotations

from datetime import datetime, timezone

from app.extensions import db


class Analysis(db.Model):
    __tablename__ = "analyses"

    STATUSES = ("pending", "streaming", "complete", "failed")

    id = db.Column(db.Integer, primary_key=True)
    idea_id = db.Column(
        db.Integer, db.ForeignKey("ideas.id", ondelete="CASCADE"), nullable=False
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    composite_score = db.Column(db.Integer)
    verdict = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default="pending", index=True)
    model_used = db.Column(db.String(80), nullable=False, default="llama-3.3-70b-versatile")
    error_message = db.Column(db.Text)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    completed_at = db.Column(db.DateTime(timezone=True))

    idea = db.relationship("Idea", back_populates="analyses")
    user = db.relationship("User", back_populates="analyses")
    lens_results = db.relationship(
        "LensResult",
        back_populates="analysis",
        cascade="all, delete-orphan",
        lazy=True,
        order_by="LensResult.display_order",
    )

    __table_args__ = (
        db.CheckConstraint(
            "status in ('pending','streaming','complete','failed')",
            name="ck_analyses_status",
        ),
    )

    def to_dict(self, include_lenses: bool = False) -> dict:
        payload = {
            "id": self.id,
            "idea_id": self.idea_id,
            "idea_title": self.idea.title if self.idea else None,
            "idea_category": self.idea.category if self.idea else None,
            "composite_score": self.composite_score,
            "verdict": self.verdict,
            "status": self.status,
            "model_used": self.model_used,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
        if include_lenses:
            payload["lenses"] = [lens.to_dict() for lens in self.lens_results]
        return payload


class LensResult(db.Model):
    __tablename__ = "lens_results"

    LENSES = ("viability", "risk", "timing", "differentiation", "personal_fit")

    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(
        db.Integer, db.ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False
    )
    lens_name = db.Column(db.String(32), nullable=False)
    display_order = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    headline = db.Column(db.String(180), nullable=False)
    analysis_text = db.Column(db.Text, nullable=False)
    blind_spot = db.Column(db.Text, nullable=False)
    green_light = db.Column(db.Boolean, nullable=False)

    analysis = db.relationship("Analysis", back_populates="lens_results")

    __table_args__ = (
        db.CheckConstraint(
            "lens_name in ('viability','risk','timing','differentiation','personal_fit')",
            name="ck_lens_results_lens_name",
        ),
        db.CheckConstraint("score >= 0 and score <= 100", name="ck_lens_score_range"),
        db.UniqueConstraint("analysis_id", "lens_name", name="uq_lens_per_analysis"),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "lens_name": self.lens_name,
            "display_order": self.display_order,
            "score": self.score,
            "headline": self.headline,
            "analysis": self.analysis_text,
            "blind_spot": self.blind_spot,
            "green_light": self.green_light,
        }
