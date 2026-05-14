from __future__ import annotations

from pathlib import Path

from flask import Flask

from .config import config_by_name
from .extensions import csrf, db, limiter, login_manager, migrate


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder="../templates",
        static_folder="../static",
    )
    app.config.from_object(config_by_name[config_name or "default"])

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id: str) -> User | None:
        if not user_id.isdigit():
            return None
        return db.session.get(User, int(user_id))

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Sign in to continue."
    login_manager.login_message_category = "info"

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
