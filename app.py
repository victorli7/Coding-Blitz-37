import os
from pathlib import Path

from flask import Flask
from flask import render_template

from feature_flags.api import create_flags_blueprint
from feature_flags.service import FlagService
from feature_flags.store import create_flag_store

DEFAULT_DB_PATH = Path(os.environ.get("FLAG_DB_PATH", "flags.db"))


def create_app(
    db_path: str | Path | None = None,
    database_url: str | None = None,
) -> Flask:
    app = Flask(__name__)
    resolved_database_url = (
        os.environ.get("DATABASE_URL")
        if database_url is None
        else database_url or None
    )
    store = create_flag_store(
        database_url=resolved_database_url,
        db_path=db_path or DEFAULT_DB_PATH,
    )
    service = FlagService(store)
    app.register_blueprint(create_flags_blueprint(service))

    @app.route("/")
    def hello_world():
        return render_template("index.html")

    return app


app = create_app()
