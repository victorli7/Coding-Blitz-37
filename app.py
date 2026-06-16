import os
from pathlib import Path

from flask import Flask
from flask import render_template

from feature_flags.api import create_flags_blueprint
from feature_flags.service import FlagService
from feature_flags.store import FlagStore

DEFAULT_DB_PATH = Path(os.environ.get("FLAG_DB_PATH", "flags.db"))


def create_app(db_path: str | Path | None = None) -> Flask:
    app = Flask(__name__)
    store = FlagStore(db_path or DEFAULT_DB_PATH)
    service = FlagService(store)
    app.register_blueprint(create_flags_blueprint(service))

    @app.route("/")
    def hello_world():
        return render_template("index.html")

    return app


app = create_app()
