from __future__ import annotations

from flask import Blueprint, request
from flask_login import current_user, login_required

from app.extensions import db, limiter
from app.models import Analysis, Idea
from app.utils.response import api_error, api_success
from app.utils.validators import ValidationError, validate_idea_payload


api_bp = Blueprint("api", __name__, url_prefix="/api/v1")


@api_bp.route("/ideas", methods=["GET"])
@login_required
def list_ideas():
    ideas = (
        Idea.query.filter_by(user_id=current_user.id)
        .order_by(Idea.created_at.desc())
        .all()
    )
    return api_success({"ideas": [idea.to_dict() for idea in ideas]})


@api_bp.route("/ideas", methods=["POST"])
@login_required
@limiter.limit("20 per hour")
def create_idea():
    payload = request.get_json(silent=True) or {}
    try:
        data = validate_idea_payload(payload)
    except ValidationError as exc:
        return api_error("VALIDATION_ERROR", str(exc), 400)

    idea = Idea(user_id=current_user.id, **data)
    db.session.add(idea)
    db.session.commit()
    return api_success({"idea": idea.to_dict()}, 201)


@api_bp.route("/analyze", methods=["POST"])
@login_required
@limiter.limit("10 per hour")
def create_analysis():
    payload = request.get_json(silent=True) or {}
    idea_id = payload.get("idea_id")
    if not isinstance(idea_id, int):
        return api_error("VALIDATION_ERROR", "idea_id must be an integer.", 400)

    idea = Idea.query.filter_by(id=idea_id, user_id=current_user.id).first()
    if not idea:
        return api_error("IDEA_NOT_FOUND", "Idea not found.", 404)

    analysis = Analysis(
        idea_id=idea.id,
        user_id=current_user.id,
        status="pending",
    )
    db.session.add(analysis)
    db.session.commit()
    return api_success({"analysis_id": analysis.id}, 201)


@api_bp.route("/analyses", methods=["GET"])
@login_required
def list_analyses():
    analyses = (
        Analysis.query.filter_by(user_id=current_user.id)
        .order_by(Analysis.created_at.desc())
        .all()
    )
    return api_success({"analyses": [analysis.to_dict() for analysis in analyses]})


@api_bp.route("/analyses/<int:analysis_id>", methods=["GET"])
@login_required
def get_analysis(analysis_id: int):
    analysis = Analysis.query.filter_by(
        id=analysis_id, user_id=current_user.id
    ).first()
    if not analysis:
        return api_error("ANALYSIS_NOT_FOUND", "Analysis not found.", 404)
    return api_success({"analysis": analysis.to_dict(include_lenses=True)})
