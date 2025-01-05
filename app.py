# Spotify API accessed via Spotipy library
# https://spotipy.readthedocs.io/en/2.19.0/

import os
import re
import sqlite3
import time
from urllib.request import HTTPBasicAuthHandler
import requests
import json

from flask import (
    Flask,
    Response,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
    jsonify,
)

from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from markupsafe import escape

from helpers import (
    search_message,
    create_playlist,
    announcer,
    CLIENT_SIDE_URL,
    PORT,
    get_spotify_oauth,
)
from announcer import format_sse

# Configure app
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure server-side sessions to store user's Spotify credentials
# TODO: Currently using filesystem storage, but can be changed to Redis, etc.
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY")
app.config["SESSION_PERMANENT"] = False
Session(app)


@app.route("/", methods=["GET", "POST"])
def index():
    # POST: User submits message
    if request.method == "POST":
        message = request.form.get("message")
        results = search_message(message=message)

        # If successful, send results to /creating via SSE
        if results:
            announcer.announce(format_sse(event="send songs", data=json.dumps(results)))
            announcer.announce(
                format_sse(event="send playlist", data=create_playlist(results))
            )

        # Tell /creating via SSE that results failed
        else:
            announcer.announce(format_sse(event="failed"))

        return render_template("index.html")

    else:
        return render_template("index.html")


# DEBUG-ONLY: print current contents of session
# TODO: Remove before production
@app.route("/session")
def session_contents():
    return jsonify(session)


@app.route("/session-clear")
def session_clear():
    session.clear()
    return redirect("session")


@app.route("/login")
def login():
    sp = get_spotify_oauth(session)
    auth_url = sp.get_authorize_url()
    return redirect(auth_url)


@app.route("/callback")
def callback():
    sp = get_spotify_oauth(session)
    session.clear()
    code = request.args.get("code")
    _ = sp.get_access_token(code)  # Caches token --> session["token_info"]
    flash("You have been logged in.")
    return redirect(url_for("index"))


@app.route("/status")
def status():
    if session.get("token_info", None):
        return jsonify({"logged in": True, "token_info": session["token_info"]})
    return jsonify({"logged in": False})


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("index"))


@app.route("/listen")
def listen():

    def stream():
        # Queue object is created in announcer.listeners & returned to messages
        messages = announcer.listen()

        while True:
            # If no messages in messages, "block" (pause) execution until it
            # arrives
            message = messages.get(block=True)
            yield message

    response = Response(stream(), mimetype="text/event-stream")
    return response


@app.route("/creating", methods=["GET"])
def creating():
    return render_template("creating.html")


@app.route("/about")
def about():
    return render_template("about.html")
