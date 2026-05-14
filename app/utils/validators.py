from __future__ import annotations

import hashlib
import re

from app.models.idea import Idea


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ValidationError(ValueError):
    pass


def normalize_email(email: str) -> str:
    email = (email or "").strip().lower()
    if not EMAIL_RE.match(email):
        raise ValidationError("Enter a valid email address.")
    return email


def validate_password(password: str) -> str:
    if len(password or "") < 8:
        raise ValidationError("Password must be at least 8 characters.")
    return password


def clean_username(username: str) -> str:
    username = (username or "").strip()
    if not 3 <= len(username) <= 40:
        raise ValidationError("Username must be 3-40 characters.")
    if not re.match(r"^[A-Za-z0-9_-]+$", username):
        raise ValidationError("Use letters, numbers, underscores, or hyphens.")
    return username


def validate_idea_payload(payload: dict) -> dict:
    title = (payload.get("title") or "").strip()
    description = (payload.get("description") or "").strip()
    category = (payload.get("category") or "").strip().lower()
    context = (payload.get("context") or "").strip()

    if not 3 <= len(title) <= 140:
        raise ValidationError("Title must be 3-140 characters.")
    if not 20 <= len(description) <= 2000:
        raise ValidationError("Description must be 20-2000 characters.")
    if category not in Idea.CATEGORIES:
        raise ValidationError("Choose a supported category.")
    if len(context) > 1000:
        raise ValidationError("Context must be 1000 characters or less.")

    return {
        "title": title,
        "description": description,
        "category": category,
        "context": context or None,
        "text_hash": hash_idea_text(title, description, category, context),
    }


def hash_idea_text(title: str, description: str, category: str, context: str | None) -> str:
    normalized = "\n".join(
        [
            title.strip().lower(),
            description.strip().lower(),
            category.strip().lower(),
            (context or "").strip().lower(),
        ]
    )
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
