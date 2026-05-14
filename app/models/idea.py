from __future__ import annotations

from datetime import datetime, timezone

from app.extensions import db


class Idea(db.Model):
    __tablename__ = "ideas"

    CATEGORIES = ("startup", "career", "creative", "financial", "personal")

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title = db.Column(db.String(140), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(32), nullable=False, index=True)
    context = db.Column(db.Text)
    text_hash = db.Column(db.String(64), index=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = db.relationship("User", back_populates="ideas")
    analyses = db.relationship(
        "Analysis", back_populates="idea", cascade="all, delete-orphan", lazy=True
    )

    __table_args__ = (
        db.CheckConstraint(
            "category in ('startup','career','creative','financial','personal')",
            name="ck_ideas_category",
        ),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "context": self.context,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
