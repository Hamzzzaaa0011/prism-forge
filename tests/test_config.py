from app.config import database_engine_options, normalize_database_uri


def test_normalize_database_uri_supports_postgres_scheme():
    uri = "postgres://user:pass@example.com:5432/db"

    assert normalize_database_uri(uri) == "postgresql://user:pass@example.com:5432/db"


def test_normalize_database_uri_leaves_other_schemes_unchanged():
    uri = "sqlite:///prism.db"

    assert normalize_database_uri(uri) == uri


def test_database_engine_options_enable_pre_ping_for_postgres():
    options = database_engine_options("postgresql://user:pass@example.com/db")

    assert options["pool_pre_ping"] is True
    assert options["pool_recycle"] == 300


def test_database_engine_options_leave_sqlite_default_pooling():
    assert database_engine_options("sqlite:///prism.db") == {}
