from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, redirect, request, url_for

from .config import config_by_name
from .extensions import csrf, db, limiter, login_manager, migrate
from .utils.response import api_error


def create_app(config_name: str | None = None) -> Flask:
    instance_path = os.getenv("PRISM_INSTANCE_PATH")
    app_kwargs = {
        "instance_relative_config": True,
        "template_folder": "../templates",
        "static_folder": "../static",
    }
    if instance_path:
        app_kwargs["instance_path"] = instance_path
    app = Flask(__name__, **app_kwargs)
    app.config.from_object(config_by_name[config_name or "default"])

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    from .models import User

    if app.config["PRISM_AUTO_CREATE_DB"]:
        with app.app_context():
            db.create_all()

    @login_manager.user_loader
    def load_user(user_id: str) -> User | None:
        if not user_id.isdigit():
            return None
        return db.session.get(User, int(user_id))

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Sign in to continue."
    login_manager.login_message_category = "info"

    @login_manager.unauthorized_handler
    def unauthorized():
        if request.path.startswith("/api/"):
            return api_error("AUTH_REQUIRED", "Sign in to continue.", 401)
        next_path = request.full_path if request.query_string else request.path
        return redirect(url_for("auth.login", next=next_path))

    @app.context_processor
    def static_assets():
        def asset_url(filename: str) -> str:
            static_root = Path(app.static_folder or "")
            asset_path = static_root / filename
            try:
                version = str(int(asset_path.stat().st_mtime))
            except OSError:
                version = "1"
            return url_for("static", filename=filename, v=version)

        return {"asset_url": asset_url}

    from .routes import api_bp, auth_bp, main_bp, stream_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(stream_bp)

    from .routes.main import register_error_handlers

    register_error_handlers(app)

    @app.cli.command("init-db")
    def init_db_command():
        db.create_all()
        print("Initialized PRISM database.")

    return app
