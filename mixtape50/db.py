import sqlite3
from flask import current_app, g


def get_db():
    """
    Returns a connection to the database. Opens a new connection if there isn't
    one already, and stores it to the g object.
    """
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    """
    Closes the connection. Called after each request.
    """
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_app(app):
    """
    Registers the `close_db` function with the Flask app.
    Called by the application factory `create_app`.
    """
    app.teardown_appcontext(close_db)
