from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import current_user
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect


db = SQLAlchemy()
csrf = CSRFProtect()
migrate = Migrate()
login_manager = LoginManager()


def _rate_limit_key() -> str:
    if current_user.is_authenticated:
        return f"user:{current_user.get_id()}"
    return get_remote_address()


limiter = Limiter(key_func=_rate_limit_key)
