from __future__ import annotations

import json

from flask import Blueprint, Response, stream_with_context
from flask_login import current_user, login_required
from pydantic import ValidationError as PydanticValidationError

from app.extensions import db, limiter
from app.models import Analysis
from app.services.ai_service import AIService
from app.services.analysis_service import (
    PrismAnalysisPayload,
    mark_analysis_failed,
    store_analysis_result,
)


stream_bp = Blueprint("stream", __name__, url_prefix="/api/v1")


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"


@stream_bp.route("/analyze/stream/<int:analysis_id>", methods=["GET"])
@login_required
@limiter.limit("10 per hour")
def stream_analysis(analysis_id: int):
    user_id = current_user.id

    @stream_with_context
    def generate():
        analysis = Analysis.query.filter_by(id=analysis_id, user_id=user_id).first()
        if not analysis:
            yield _sse(
                {
                    "type": "failed",
                    "error": "Analysis not found or you do not have access.",
                }
            )
            return

        if analysis.status == "complete":
            yield _sse(
                {
                    "type": "complete",
                    "analysis": analysis.to_dict(include_lenses=True),
                }
            )
            return

        analysis.status = "streaming"
        analysis.error_message = None
        db.session.commit()
        yield _sse({"type": "started", "analysis_id": analysis.id})

        full_json = ""
        try:
            ai_service = AIService()
            for chunk in ai_service.stream_analysis(analysis.idea):
                full_json += chunk
                yield _sse({"type": "chunk", "chunk": chunk})

            payload = PrismAnalysisPayload.model_validate_json(full_json)
            store_analysis_result(analysis, payload, ai_service.model)
            yield _sse(
                {
                    "type": "complete",
                    "analysis": analysis.to_dict(include_lenses=True),
                }
            )
        except (PydanticValidationError, json.JSONDecodeError) as exc:
            mark_analysis_failed(analysis, "The model returned an invalid analysis.")
            yield _sse({"type": "failed", "error": str(exc)})
        except Exception as exc:
            mark_analysis_failed(analysis, str(exc))
            yield _sse({"type": "failed", "error": str(exc)})

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
