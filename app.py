# Spotify API accessed via Spotipy library https://spotipy.readthedocs.io/en/2.19.0/

from crypt import methods
import os
import re
import sqlite3
import time
from urllib.request import HTTPBasicAuthHandler
import requests
import json

from flask import Flask, Response, flash, make_response, redirect, render_template, request, session, url_for, jsonify
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from markupsafe import escape

from helpers import search_message, announcer, CLIENT_SIDE_URL, PORT
from announcer import format_sse

# Configure app
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.route("/", methods = ["GET", "POST"])
def index():
    if request.method == "POST":

        message = request.form.get("message")
        results = search_message(message = message)

        if results:

            announcer.announce(format_sse(event = "send songs", data = json.dumps(results)))
            print("sse request sent")

        return render_template("index.html")
    
    else:
        return render_template("index.html")
    

@app.route("/listen")
def listen():
    
    def stream():
        messages = announcer.listen() # Queue object is created in announcer.listeners & returned to messages
        
        while True:
            message = messages.get(block=True) # If no messages in messages, "block" (pause) execution until it arrives
            yield message

    response = Response(stream(), mimetype="text/event-stream")
    return response


@app.route("/creating", methods = ["GET", "POST"])
def creating():

    return render_template("creating.html")