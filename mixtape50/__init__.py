import os

from flask import Flask, render_template, request, jsonify

from mixtape50.db import get_db
from mixtape50.utils import remove_punctuation


TRACKS_DB = os.path.join(os.getcwd(), "mixtape50/static/spotify-tracks.db")


def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=TRACKS_DB,
        TEMPLATES_AUTO_RELOAD=True,
        SESSION_TYPE="filesystem",
        SESSION_PERMANENT=False,
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Register `close_db`; and remaining Blueprints with app
    from . import db

    db.init_app(app)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/about")
    def about():
        return render_template("about.html")

    @app.route("/search")
    def search():
        """
        Searches tracks.db (1.2 million songs from Spotify from the Kaggle
        database) to return a list of songs (name & id) which match the
        query.

        https://www.kaggle.com/rodolfofigueroa/spotify-12m-songs
        """
        db = get_db()
        query = request.args.get("q")
        results = db.execute(
            "SELECT name, id FROM tracks WHERE name_cleaned = ?",
            [remove_punctuation(query)],
        ).fetchall()
        results = list(map(lambda item: {"name": item[0], "id": item[1]}, results))
        return jsonify(results)

    return app
