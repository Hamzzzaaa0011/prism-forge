from __future__ import annotations

from flask import Flask, Response, render_template, request
from flask_login import current_user, login_required
from flask_wtf.csrf import CSRFError
from werkzeug.exceptions import HTTPException

from app.models import Analysis
from flask import Blueprint
from app.utils.response import api_error


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def landing():
    if current_user.is_authenticated:
        recent = (
            Analysis.query.filter_by(user_id=current_user.id)
            .order_by(Analysis.created_at.desc())
            .limit(3)
            .all()
        )
    else:
        recent = []
    total_analyses = Analysis.query.filter_by(status="complete").count()
    return render_template(
        "pages/landing.html", recent=recent, total_analyses=total_analyses
    )


@main_bp.route("/dashboard")
@login_required
def dashboard():
    analyses = (
        Analysis.query.filter_by(user_id=current_user.id)
        .order_by(Analysis.created_at.desc())
        .all()
    )
    completed = [analysis for analysis in analyses if analysis.status == "complete"]
    average_score = (
        round(sum(a.composite_score or 0 for a in completed) / len(completed))
        if completed
        else None
    )
    return render_template(
        "pages/dashboard.html",
        analyses=analyses,
        completed_count=len(completed),
        average_score=average_score,
    )


@main_bp.route("/analyze")
@login_required
def analyze():
    return render_template("pages/analyze.html")


@main_bp.route("/results/<int:analysis_id>")
@login_required
def results(analysis_id: int):
    analysis = Analysis.query.filter_by(
        id=analysis_id, user_id=current_user.id
    ).first_or_404()
    should_stream = analysis.status in {"pending", "streaming"}
    return render_template(
        "pages/results.html", analysis=analysis, should_stream=should_stream
    )


@main_bp.route("/api/v1/health")
def health():
    return {"status": "ok", "version": "1.0.0"}


@main_bp.route("/robots.txt")
def robots_txt():
    sitemap_url = f"{request.host_url.rstrip('/')}/sitemap.xml"
    body = f"User-agent: *\nAllow: /\nSitemap: {sitemap_url}\n"
    return Response(body, mimetype="text/plain")


@main_bp.route("/sitemap.xml")
def sitemap_xml():
    base_url = request.host_url.rstrip("/")
    body = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{base_url}/</loc>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>{base_url}/auth/register</loc>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>{base_url}/auth/login</loc>
    <priority>0.5</priority>
  </url>
</urlset>
"""
    return Response(body, mimetype="application/xml")


def _is_api_request() -> bool:
    return request.path.startswith("/api/")


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(CSRFError)
    def csrf_error(error: CSRFError):
        message = "Your session expired. Refresh the page and try again."
        if _is_api_request():
            return api_error("CSRF_FAILED", message, 400)
        return render_template("pages/errors/500.html", error=error), 400

    @app.errorhandler(404)
    def not_found(error):
        if _is_api_request():
            return api_error("NOT_FOUND", "Endpoint not found.", 404)
        return render_template("pages/errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(error):
        if _is_api_request():
            return api_error("SERVER_ERROR", "Something went wrong.", 500)
        return render_template("pages/errors/500.html"), 500

    @app.errorhandler(HTTPException)
    def http_error(error: HTTPException):
        if _is_api_request():
            code = error.code or 500
            return api_error(error.name.upper().replace(" ", "_"), error.description, code)
        if error.code == 404:
            return render_template("pages/errors/404.html"), 404
        return render_template("pages/errors/500.html", error=error), error.code or 500
